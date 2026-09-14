"""Text-to-image providers used to create the card artwork.

- pollinations: free, no API key (https://pollinations.ai). Optional POLLINATIONS_TOKEN
  for higher rate limits, POLLINATIONS_MODEL to pick the model (default: flux).
- openrouter: image models on OpenRouter (paid, needs credits). Model set with
  OPENROUTER_IMAGE_MODEL (default: google/gemini-2.5-flash-image).
"""

import base64
import io
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request

from dotenv import load_dotenv
from PIL import Image

POLLINATIONS_URL = "https://image.pollinations.ai/prompt/"
POLLINATIONS_LOGO_STRIP = 48  # Pixels cropped off the bottom (watermark).
IMAGE_SIZE = (768, 512)  # 3:2, like the card's art window.


class ImageGenerationError(Exception):
    pass


def clean_prompt(prompt: str) -> str:
    """Strips Midjourney-only syntax: 'Name::0' prefix, '::1.8' weights and --params."""
    prompt = re.sub(r"^[^,]*?::0\s+", "", prompt)
    prompt = re.sub(r"::\d+(\.\d+)?", "", prompt)
    prompt = re.sub(r"\s--\w+(\s+[^\s-]\S*)?", "", prompt)
    return re.sub(r"\s+", " ", prompt).strip(" ,")


def crop_bottom(raw_image: bytes, pixels: int) -> bytes:
    image = Image.open(io.BytesIO(raw_image)).convert("RGB")
    cropped = image.crop((0, 0, image.width, image.height - pixels))
    output = io.BytesIO()
    cropped.save(output, format="PNG")
    return output.getvalue()


def generate_pollinations(prompt: str, seed: int, retries: int = 4) -> bytes:
    load_dotenv()
    params = {
        "width": IMAGE_SIZE[0],
        # The free tier stamps a logo in the bottom-right corner: render a taller
        # image and crop that strip off, which gives back an exact 3:2 image.
        "height": IMAGE_SIZE[1] + POLLINATIONS_LOGO_STRIP,
        "seed": seed,
        "nologo": "true",
        "model": os.getenv("POLLINATIONS_MODEL", "flux"),
    }
    url = f"{POLLINATIONS_URL}{urllib.parse.quote(prompt, safe='')}?{urllib.parse.urlencode(params)}"
    headers = {"User-Agent": "tf2-cs-card-generator"}
    if os.getenv("POLLINATIONS_TOKEN"):
        headers["Authorization"] = f"Bearer {os.getenv('POLLINATIONS_TOKEN')}"

    for attempt in range(1, retries + 1):
        try:
            request = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(request, timeout=180) as response:
                content_type = response.headers.get_content_type()
                if not content_type.startswith("image/"):
                    raise ImageGenerationError(f"unexpected content type '{content_type}'")
                return crop_bottom(response.read(), POLLINATIONS_LOGO_STRIP)
        except (urllib.error.URLError, TimeoutError, ImageGenerationError) as error:
            if attempt == retries:
                raise ImageGenerationError(f"Pollinations failed: {error}") from error
            wait = 10 * attempt  # Back off (the free tier is rate limited).
            print(f"\033[93m [WARN] Pollinations failed ({error}), retrying in {wait}s...\033[0m")
            time.sleep(wait)


def generate_openrouter(prompt: str, seed: int) -> bytes:
    from util.gpt_call import gpt_client

    client = gpt_client()
    if not client.is_openrouter_enabled:
        raise ImageGenerationError("OPENROUTER_API_KEY is missing.")

    response = client.client.chat.completions.create(
        model=os.getenv("OPENROUTER_IMAGE_MODEL", "google/gemini-2.5-flash-image"),
        messages=[{"role": "user", "content": f"Generate a 3:2 landscape image: {prompt}"}],
        extra_body={"modalities": ["image", "text"], "seed": seed},
    )
    message = response.choices[0].message
    images = getattr(message, "images", None) or (message.model_extra or {}).get("images") or []
    for image in images:
        url = image["image_url"]["url"] if isinstance(image, dict) else image.image_url.url
        if url.startswith("data:"):
            return base64.b64decode(url.split(",", 1)[1])
    raise ImageGenerationError("No image in the OpenRouter response.")


PROVIDERS = {
    "pollinations": generate_pollinations,
    "openrouter": generate_openrouter,
}


def generate_image(provider: str, prompt: str, seed: int) -> bytes:
    return PROVIDERS[provider](prompt, seed)
