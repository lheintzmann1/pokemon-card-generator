import argparse
from functools import lru_cache
import json
import pathlib

from PIL import Image, ImageDraw, ImageFont

import card_layout as L
from games.game import Game
from games.registry import GAMES, get_game
from mechanics.ability import Ability
from mechanics.card import Card
from mechanics.element import Element
from util.colors import darken, hex_to_rgb, lighten

FONT_BOLD = "resources/font/Cabin-Bold.ttf"
FONT_REGULAR = "resources/font/Cabin-Regular.ttf"
FONT_CONDENSED = "resources/font/Cabin_Condensed-Regular.ttf"
FONT_SYMBOLS = "resources/font/NotoSansSymbols2-Regular.ttf"

# (symbol, font size) per rarity index.
RARITY_SYMBOLS = [("⬤", 11), ("◆", 16), ("★", 24)]
SYMBOL_OUTLINE = (30, 24, 20)


@lru_cache(maxsize=None)
def font(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size)


def fitted_font(text: str, path: str, size: int, max_width: float, min_size: int = 12):
    """Shrinks the font until the text fits in max_width."""
    while size > min_size and font(path, size).getlength(text) > max_width:
        size -= 1
    return font(path, size)


@lru_cache(maxsize=None)
def element_icon(path: str, size: int) -> Image.Image:
    return Image.open(path).convert("RGBA").resize((size, size), Image.LANCZOS)


def render_cards(collection_path: str, game_key: str | None = None):
    collection_path = pathlib.Path(collection_path)
    render_path = collection_path / "renders"
    render_path.mkdir(parents=True, exist_ok=True)

    for card_path in sorted((collection_path / "cards").glob("*.json")):
        data = json.loads(card_path.read_text())
        game = get_game(data.get("game") or game_key or "tf2")
        card = card_from_json(data, game)
        render_card(card, game, collection_path).save(render_path / card.image_file)


def render_card(card: Card, game: Game, collection_path: str | pathlib.Path) -> Image.Image:
    print(f"Rendering {card.name}")
    template = Image.open(game.card_template_path(card.element)).convert("RGBA")
    card_image = Image.new("RGBA", template.size, (0, 0, 0, 0))

    art_path = pathlib.Path(collection_path, "images", card.image_file)
    if art_path.exists():
        art = fit_art(Image.open(art_path))
    else:
        print(f"\033[93m [WARN] {art_path} not found, using a placeholder.\033[0m")
        art = placeholder_art(game, card.element)

    # The template has a transparent window where the artwork shows through.
    card_image.paste(art, L.ART_BOX[:2])
    card_image.alpha_composite(template)

    render_header(card, game, card_image)
    render_banner(card, game, card_image)
    render_abilities(card, game, card_image)
    render_weakness_and_resist(card, game, card_image)
    render_rarity(card, game, card_image)
    render_footer(card, game, card_image)
    return card_image


def art_size() -> tuple[int, int]:
    x0, y0, x1, y1 = L.ART_BOX
    return x1 - x0, y1 - y0


def fit_art(image: Image.Image) -> Image.Image:
    """Scales the artwork to cover the art window, then crops it centered."""
    width, height = art_size()
    image = image.convert("RGBA")
    scale = max(width / image.width, height / image.height)
    resized = image.resize(
        (max(width, round(image.width * scale)), max(height, round(image.height * scale))),
        Image.LANCZOS,
    )
    left = (resized.width - width) // 2
    top = (resized.height - height) // 2
    return resized.crop((left, top, left + width, top + height))


def placeholder_art(game: Game, element: Element) -> Image.Image:
    width, height = art_size()
    accent = hex_to_rgb(element.color)
    top = Image.new("RGBA", (width, height), darken(accent, 0.25) + (255,))
    bottom = Image.new("RGBA", (width, height), darken(accent, 0.7) + (255,))
    art = Image.composite(bottom, top, Image.linear_gradient("L").resize((width, height)))

    icon_size = 170
    icon = element_icon(game.element_icon_path(element), icon_size).copy()
    icon.putalpha(icon.getchannel("A").point(lambda alpha: int(alpha * 0.3)))
    art.alpha_composite(icon, ((width - icon_size) // 2, (height - icon_size) // 2))
    return art


def render_header(card: Card, game: Game, image: Image.Image):
    theme = game.theme
    draw = ImageDraw.Draw(image)

    hp_text = f"{card.hp} HP"
    hp_font = font(FONT_CONDENSED, 26)
    hp_color = lighten(card.element.color, 0.45)
    draw.text((L.HP_RIGHT, L.HEADER_MID_Y), hp_text, font=hp_font, fill=hp_color, anchor="rm")

    name = card.name.upper() if theme.uppercase_names else card.name
    max_name_width = L.HP_RIGHT - hp_font.getlength(hp_text) - 16 - L.NAME_X
    name_font = fitted_font(name, FONT_BOLD, 28, max_name_width)
    draw.text(
        (L.NAME_X, L.HEADER_MID_Y), name, font=name_font, fill=theme.title_color, anchor="lm"
    )

    icon = element_icon(game.element_icon_path(card.element), L.ICON_SIZE)
    image.alpha_composite(
        icon, (L.ICON_CENTER[0] - L.ICON_SIZE // 2, L.ICON_CENTER[1] - L.ICON_SIZE // 2)
    )


def render_banner(card: Card, game: Game, image: Image.Image):
    draw = ImageDraw.Draw(image)
    text = f"{card.element.name} {game.subject_type}".upper()
    draw.text(
        (L.CARD_WIDTH // 2, L.BANNER_MID_Y),
        text,
        font=font(FONT_BOLD, 15),
        fill=game.theme.banner_text_color,
        anchor="mm",
    )


def render_abilities(card: Card, game: Game, image: Image.Image):
    n = len(card.abilities)
    total_height = n * L.ABILITY_HEIGHT + (n - 1) * L.ABILITY_GAP
    y_origin = L.ABILITY_CENTER_Y - total_height // 2
    x = (image.width - L.ABILITY_WIDTH) // 2

    # Draw the abilities in reverse order so that the first ability is at the bottom.
    for i, ability in enumerate(reversed(card.abilities)):
        y = y_origin + i * (L.ABILITY_HEIGHT + L.ABILITY_GAP)
        image.alpha_composite(render_ability(ability, game), (x, y))

    draw = ImageDraw.Draw(image)
    for i in range(1, n):
        line_y = y_origin + i * (L.ABILITY_HEIGHT + L.ABILITY_GAP) - L.ABILITY_GAP // 2
        panel_x0, _, panel_x1, _ = L.ABILITY_PANEL_BOX
        draw.line(
            ((panel_x0 + 14, line_y), (panel_x1 - 14, line_y)),
            fill=game.theme.line_color,
            width=2,
        )


def render_ability(ability: Ability, game: Game) -> Image.Image:
    theme = game.theme
    ability_image = Image.new("RGBA", (L.ABILITY_WIDTH, L.ABILITY_HEIGHT), (0, 0, 0, 0))
    ability_image.alpha_composite(
        render_element_cost(game, ability.cost_elements(game.neutral))
    )

    draw = ImageDraw.Draw(ability_image)
    name_area = L.ABILITY_WIDTH - L.ABILITY_COST_WIDTH - L.ABILITY_POWER_WIDTH
    name_font = fitted_font(ability.name, FONT_BOLD, 24, name_area - 12)
    draw.text(
        (L.ABILITY_COST_WIDTH + name_area // 2, L.ABILITY_HEIGHT // 2),
        ability.name,
        font=name_font,
        fill=theme.text_color,
        anchor="mm",
    )
    draw.text(
        (L.ABILITY_WIDTH - 12, L.ABILITY_HEIGHT // 2),
        str(ability.power),
        font=font(FONT_CONDENSED, 32),
        fill=theme.text_color,
        anchor="rm",
    )
    return ability_image


def render_element_cost(game: Game, elements: list[Element]) -> Image.Image:
    cost_canvas = Image.new("RGBA", (L.ABILITY_COST_WIDTH, L.ABILITY_HEIGHT), (0, 0, 0, 0))

    # 1 icon: centered. 2: side by side. 3: triangle. 4: square.
    size, gap = L.ELEMENT_SIZE, L.ELEMENT_GAP
    center_x = L.ABILITY_COST_WIDTH // 2
    center_y = L.ABILITY_HEIGHT // 2
    left = center_x - (size + gap) // 2
    right = center_x + (size + gap) // 2
    top = center_y - (size + gap) // 2
    bottom = center_y + (size + gap) // 2

    positions = {
        1: [(center_x, center_y)],
        2: [(left, center_y), (right, center_y)],
        3: [(left, top), (right, top), (center_x, bottom)],
        4: [(left, top), (right, top), (left, bottom), (right, bottom)],
    }[len(elements)]

    for (x, y), element in zip(positions, elements):
        icon = element_icon(game.element_icon_path(element), size)
        cost_canvas.alpha_composite(icon, (x - size // 2, y - size // 2))
    return cost_canvas


def render_weakness_and_resist(card: Card, game: Game, image: Image.Image):
    theme = game.theme
    statuses = [
        game.weakness.get(card.element),
        game.resistance.get(card.element),
        game.neutral,  # Retreat cost.
    ]
    draw = ImageDraw.Draw(image)
    size = L.STATUS_ICON_SIZE
    for x, label, element in zip(L.STATUS_XS, theme.status_labels, statuses):
        draw.text(
            (x, L.STATUS_LABEL_Y), label, font=font(FONT_BOLD, 13), fill=theme.text_color, anchor="mm"
        )
        if element is None:
            draw.text(
                (x, L.STATUS_ICON_Y), "—", font=font(FONT_BOLD, 16), fill=theme.muted_color, anchor="mm"
            )
            continue
        icon = element_icon(game.element_icon_path(element), size)
        image.alpha_composite(icon, (x - size // 2, L.STATUS_ICON_Y - size // 2))


def render_rarity(card: Card, game: Game, image: Image.Image):
    theme = game.theme
    draw = ImageDraw.Draw(image)
    x0, y0, x1, y1 = L.RARITY_BOX

    draw.rounded_rectangle((x0 + 10, y0 + 6, x0 + 14, y1 - 6), radius=2, fill=card.rarity.color)
    rarity_text = f"{card.rarity.name} {card.element.name} {game.subject_type.capitalize()}"
    draw.text(
        (x0 + 24, L.RARITY_MID_Y),
        rarity_text,
        font=font(FONT_CONDENSED, 17),
        fill=theme.text_color,
        anchor="lm",
    )

    symbol, size = RARITY_SYMBOLS[min(card.rarity.index, len(RARITY_SYMBOLS) - 1)]
    draw.text(
        (x1 - 20, L.RARITY_MID_Y),
        symbol,
        font=font(FONT_SYMBOLS, size),
        fill=card.rarity.color,
        anchor="mm",
        stroke_width=1,
        stroke_fill=SYMBOL_OUTLINE,
    )


def render_footer(card: Card, game: Game, image: Image.Image):
    theme = game.theme
    draw = ImageDraw.Draw(image)
    footer_font = font(FONT_REGULAR, 11)
    left_x, right_x = L.FOOTER_X
    draw.text(
        (left_x, L.FOOTER_Y),
        f"{game.title} · #{card.index:03d}",
        font=footer_font,
        fill=theme.muted_color,
        anchor="lm",
    )
    draw.text(
        (right_x, L.FOOTER_Y), theme.footer, font=footer_font, fill=theme.muted_color, anchor="rm"
    )


def card_from_json(data: dict, game: Game) -> Card:
    card = Card(
        index=data["index"],
        name=data["name"],
        description=data["description"],
        element=game.element_by_name(data["element"]),
        rarity=game.rarity_by_name(data["rarity"]),
        hp=data["hp"],
        game=game.key,
    )
    card.abilities = [ability_from_json(ability, game) for ability in data["abilities"]]
    return card


def ability_from_json(data: dict, game: Game) -> Ability:
    return Ability(
        name=data["name"],
        element=game.element_by_name(data["element"]),
        cost=data["cost"],
        is_mixed_element=data["is_mixed_element"],
    )


def main():
    argparser = argparse.ArgumentParser(description="Render generated cards to PNG.")
    argparser.add_argument(
        "-g",
        "--game",
        choices=sorted(GAMES),
        default=None,
        help="Game of the collection (default: read from the card files, else tf2).",
    )
    argparser.add_argument(
        "--collection",
        default=None,
        help="Path to the collection folder (default: output/<game collection>).",
    )
    args = argparser.parse_args()
    collection_path = args.collection or f"output/{get_game(args.game or 'tf2').collection_name}"
    render_cards(collection_path, args.game)


if __name__ == "__main__":
    main()
