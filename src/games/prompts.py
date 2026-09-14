import json
import random
import re

from games.game import Game, indefinite_article
from mechanics.card import Card
from util.gpt_call import gpt_client

MAX_NAME_LENGTH = 32


def _clean(text: str) -> str:
    text = re.sub(r"\s+", " ", text)
    return text.replace(" ,", ",").replace(" .", ".").strip()


def get_subject_description(card: Card, game: Game) -> str:
    words = [*card.style.subject_adjectives, card.style.subject, card.style.subject_type]
    body = _clean(" ".join(word for word in words if word))
    return _clean(f"{indefinite_article(body)} {body} {game.subject_suffix}")


def get_detail_description(card: Card) -> str:
    # Basic (common) cards stay simple.
    if card.style.detail and card.rarity.index > 0:
        return ", " + card.style.detail
    return ""


def get_visual_description(card: Card, game: Game) -> str:
    subject_line = get_subject_description(card, game) + get_detail_description(card)
    environment = game.environment_sentence.format(environment=card.style.environment)
    return _clean(f"{subject_line}. {environment}")


def get_image_prompt(card: Card, game: Game) -> str:
    subject_line = get_subject_description(card, game)
    if card.rarity.index == 1:
        subject_line += "::1.8"
    if card.rarity.index >= 2:
        subject_line += "::2.5"
    subject_line += get_detail_description(card)

    segments = [
        subject_line,
        f"in {card.style.environment}",
        card.style.ambience,
        card.style.style_suffix,
    ]
    message = _clean(", ".join(segments) + " --ar 3:2")
    return f"{card.name}::0 {message}"


def fallback_name(game: Game, seen_names: set[str]) -> str:
    available = [name for name in game.fallback_names if name not in seen_names]
    if available:
        return random.choice(available)
    base = random.choice(game.fallback_names)
    suffix = 2
    while f"{base} {suffix}" in seen_names:
        suffix += 1
    return f"{base} {suffix}"


def fallback_description(card: Card) -> str:
    return f"{card.name} is {card.visual_description}"


# --------------------------------------------------------------------------
# AI naming: one request names and describes a whole batch of cards, which
# keeps a full collection within a few requests (OpenRouter free tier ~50/day).
# --------------------------------------------------------------------------


def build_batch_prompt(cards: list[Card], game: Game, taken_names: set[str]) -> str:
    lines = [
        f"You are writing {len(cards)} fan-made {game.title} trading cards.",
        f"For EACH card, invent a name ({game.name_rules}) "
        f"and a description ({game.description_rules}).",
        "All names must be different from each other"
        + (f" and from: {', '.join(sorted(taken_names))}." if taken_names else "."),
        "",
        "Cards:",
    ]
    for card in cards:
        length = "short single-word name" if card.rarity.index == 0 else "1-2 word name"
        moves = ", ".join(ability.name for ability in card.abilities)
        lines.append(
            f"- index {card.index} ({card.rarity.name}, {length}): "
            f"{card.visual_description} Moves: {moves}."
        )
    lines += [
        "",
        "Answer ONLY with a JSON array, no markdown, in this exact format:",
        '[{"index": 1, "name": "...", "description": "..."}]',
    ]
    return "\n".join(lines)


def parse_batch_response(text: str) -> dict[int, dict]:
    """Extracts {index: {"name", "description"}} from a (possibly messy) JSON answer."""
    text = re.sub(r"```(?:json)?", "", text)
    start, end = text.find("["), text.rfind("]")
    if start == -1 or end <= start:
        return {}
    try:
        data = json.loads(text[start : end + 1])
    except json.JSONDecodeError:
        return {}

    entries = {}
    for entry in data if isinstance(data, list) else []:
        if not isinstance(entry, dict):
            continue
        try:
            index = int(entry.get("index"))
        except (TypeError, ValueError):
            continue
        name = "".join(c for c in str(entry.get("name", "")) if c.isalnum() or c in " -'.")
        entries[index] = {
            "name": _clean(name)[:MAX_NAME_LENGTH],
            "description": _clean(str(entry.get("description", ""))),
        }
    return entries


def enrich_cards_with_ai(
    cards: list[Card], game: Game, seen_names: set[str], batch_size: int = 10
) -> int:
    """Replaces the offline names/descriptions with AI ones. Returns the request count."""
    requests = 0
    for start in range(0, len(cards), batch_size):
        batch = cards[start : start + batch_size]
        batch_indexes = {card.index for card in batch}
        taken_names = {card.name for card in cards if card.index not in batch_indexes}
        taken_names |= seen_names - {card.name for card in batch}
        prompt = build_batch_prompt(batch, game, taken_names)

        entries = {}
        for attempt in range(2):  # One retry if the answer can't be parsed.
            requests += 1
            response = gpt_client().get_completion(prompt, max_tokens=200 * len(batch))
            text = response.choices[0].text if response.choices else ""
            entries = parse_batch_response(text)
            if entries:
                break
            print(f"\033[93m [WARN] Could not parse the AI answer (attempt {attempt + 1}/2).\033[0m")

        for card in batch:
            entry = entries.get(card.index)
            if not entry:
                continue
            name = entry["name"]
            if name and name not in taken_names:
                seen_names.discard(card.name)
                card.name = name
                seen_names.add(name)
                taken_names.add(name)
            card.description = entry["description"] or fallback_description(card)
            card.image_prompt = get_image_prompt(card, game)
    return requests
