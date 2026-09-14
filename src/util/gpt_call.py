from dataclasses import dataclass
from functools import cached_property
import os

from dotenv import load_dotenv
from openai import OpenAI
from retry import retry


@dataclass
class CompletionChoice:
    text: str


@dataclass
class CompletionResponse:
    choices: list[CompletionChoice]


class OpenRouterClient:
    SINGLETON_CLIENT = None

    @cached_property
    def is_openrouter_enabled(self):
        load_dotenv()
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            print("\033[91mWARNING: OpenRouter API key not found. AI generation will not be used.\033[0m")
            return False
        return True

    @cached_property
    def client(self):
        load_dotenv()
        api_key = os.getenv("OPENROUTER_API_KEY")
        return OpenAI(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1",
            default_headers={
                "HTTP-Referer": os.getenv("OPENROUTER_HTTP_REFERER", "http://localhost"),
                "X-Title": os.getenv("OPENROUTER_APP_NAME", "Pokemon Card Generator"),
            },
        )

    @cached_property
    def model(self):
        return os.getenv("OPENROUTER_MODEL", "openrouter/free")

    @retry(tries=3, delay=3.0)
    def get_completion(self, prompt: str, max_tokens: int = 128, n: int = 1):
        """Call OpenRouter and return a small compatibility wrapper.

        The original project expects Completion-style `choice.text` values.
        OpenRouter uses chat completions, so this adapter keeps the rest of the
        project largely unchanged.
        """
        if not self.is_openrouter_enabled:
            return CompletionResponse(choices=[])

        request_prompt = prompt
        if n > 1:
            request_prompt += (
                f"\n\nReturn exactly {n} different candidates, one per line, "
                "with no numbering, bullets, quotes, or explanation."
            )

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a creative writer helping generate original fan-made creature card content. Follow formatting instructions exactly.",
                },
                {"role": "user", "content": request_prompt},
            ],
            max_tokens=max_tokens,
            temperature=0.9,
        )

        content = response.choices[0].message.content or ""
        if n > 1:
            candidates = [line.strip() for line in content.splitlines() if line.strip()]
            candidates = candidates[:n]
        else:
            candidates = [content.strip()]

        return CompletionResponse(
            choices=[CompletionChoice(text=value) for value in candidates]
        )


def gpt_client():
    if OpenRouterClient.SINGLETON_CLIENT is None:
        OpenRouterClient.SINGLETON_CLIENT = OpenRouterClient()
    return OpenRouterClient.SINGLETON_CLIENT
