import string
from mechanics.card import Card
from util.gpt_call import gpt_client


def get_visual_description(card: Card) -> str:
    segments = []
    subject_line = get_full_subject_description(card)
    segments.append(subject_line)
    segments.append(f"It can be found in {card.style.environment}-like environments.")
    message = " ".join(segments)
    return message


def get_image_prompt(card: Card):
    segments = []
    subject_line = get_subject_description(card)
    if card.rarity.index == 1:
        subject_line += "::1.8"
    if card.rarity.index >= 2:
        subject_line += "::2.5"
    subject_line += get_detail_description(card)
    segments.append(subject_line)
    segments.append(f"in a {card.style.environment} environment")
    segments.append(card.style.ambience)
    segments.append(card.style.style_suffix)
    message = ", ".join(segments)
    message += " --ar 3:2"
    message = message.replace("  ", " ")
    message = message.replace(" ,", ",")
    message = f"{card.name}::0 " + message
    return message


def get_subject_description(card: Card):
    subject_section = ["a"]
    subject_section.extend(card.style.subject_adjectives)
    subject_section.append(card.style.subject)
    subject_section.append(card.style.subject_type)
    subject_line = " ".join(subject_section)
    subject_line = subject_line.replace(" ,", ",")
    return subject_line


def get_detail_description(card: Card) -> str:
    if card.style.detail and card.rarity.index > 0:
        return ", " + card.style.detail
    return ""


def get_full_subject_description(card: Card):
    return get_subject_description(card) + get_detail_description(card)


def generate_card_name(card: Card, seen_names: set[str], max_attempts: int = 4) -> str:
    if not gpt_client().is_openrouter_enabled:
        return "Untitled Card"

    additional_modifier = "short, single-word, " if card.rarity.index == 0 else "single-word, "
    prompt = (
        f"Generate a unique, original, creative, {additional_modifier} "
        f"{card.style.subject_type} name for a {get_visual_description(card)}"
    )
    prompt += (
        f" (without using the word {card.style.subject_type.lower()} "
        f"or {card.element.name.lower()}):"
    )
    print(prompt)

    all_potential_names = set()
    for attempt in range(max_attempts):
        response = gpt_client().get_completion(prompt, max_tokens=256, n=5)
        for potential_name in response.choices:
            name = potential_name.text.strip()
            name = "".join(c for c in name if c.isalpha() or c == " " or c == "-")
            name = string.capwords(name)
            if name:
                all_potential_names.add(name)

        filtered_names = all_potential_names - seen_names
        if filtered_names:
            return sorted(filtered_names, key=lambda x: len(x))[0]

        if attempt < max_attempts - 1:
            print(
                f"No usable/unseen name after attempt {attempt + 1}/{max_attempts}, retrying..."
            )

    # Exhausted retries without finding a name that isn't already used.
    # Prefer any valid generated name over giving up entirely.
    if all_potential_names:
        return sorted(all_potential_names, key=lambda x: len(x))[0]

    return "Untitled Card"


def generate_desc(card: Card) -> str:
    if not gpt_client().is_openrouter_enabled:
        return "No description available."

    prompt = (
        f"Generate a short, original, creative Pokedex description for {card.name}, "
        f"{get_visual_description(card)}. "
        f"It has the following abilities: {', '.join([ability.name for ability in card.abilities])}. "
        "Be creative about its day-to-day life. "
        f"(do not use the word {card.style.subject.lower()} or "
        f"{card.element.name.lower()} or the ability names):"
    )
    print(prompt)
    response = gpt_client().get_completion(prompt, max_tokens=256)
    return response.choices[0].text.strip() if response.choices else "No description available."