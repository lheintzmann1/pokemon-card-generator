"""Generates the SVG card templates and element icons of every game, then
rasterizes them to the PNGs used by render_cards.py.

    python src/build_resources.py            # all games
    python src/build_resources.py -g cs      # a single game

Output (per game):
    resources/<game>/svg/cards/<element>_card.svg      (sources)
    resources/<game>/svg/elements/<element>_element.svg
    resources/<game>/cards/<element>_card.png          (used by the renderer)
    resources/<game>/elements/<element>_element.png

Rasterizing needs `rsvg-convert` (librsvg) or the `cairosvg` Python package.
"""

import argparse
import math
import pathlib
import shutil
import subprocess
from typing import Callable

import card_layout as L
from games.game import Game
from games.registry import GAMES
from mechanics.element import Element
from util.colors import darken, lighten, to_hex

ICON_PX = 128
W, H = L.CARD_WIDTH, L.CARD_HEIGHT

Glyph = Callable[[str, str], str]  # (foreground, background) -> SVG markup in a 100x100 box.


def svg_document(width: int, height: int, body: str) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}">\n{body}\n</svg>\n'
    )


def points(coordinates) -> str:
    return " ".join(f"{x:.1f},{y:.1f}" for x, y in coordinates)


def box_rect(box, inset: float = 0, **attrs) -> str:
    x0, y0, x1, y1 = box
    extra = " ".join(f'{k.replace("_", "-")}="{v}"' for k, v in attrs.items())
    return (
        f'<rect x="{x0 - inset}" y="{y0 - inset}" width="{x1 - x0 + 2 * inset}" '
        f'height="{y1 - y0 + 2 * inset}" {extra}/>'
    )


def art_hole_mask() -> str:
    return (
        f'<mask id="art-hole"><rect width="{W}" height="{H}" fill="#fff"/>'
        f'{box_rect(L.ART_BOX, fill="#000")}</mask>'
    )


# --------------------------------------------------------------------------
# Glyphs (drawn in a 100x100 box, centered on 50,50).
# --------------------------------------------------------------------------


def glyph_cog(fg: str, bg: str) -> str:
    teeth, r_out, r_in = 8, 36, 27
    coordinates = []
    for k in range(teeth):
        angle = 2 * math.pi * k / teeth
        for offset, radius in ((-0.25, r_in), (-0.16, r_out), (0.16, r_out), (0.25, r_in)):
            a = angle + offset
            coordinates.append((50 + radius * math.cos(a), 50 + radius * math.sin(a)))
    return (
        f'<polygon points="{points(coordinates)}" fill="{fg}"/>'
        f'<circle cx="50" cy="50" r="11" fill="{bg}"/>'
    )


def glyph_bat(fg: str, bg: str) -> str:
    return (
        f'<g transform="rotate(40 50 50)">'
        f'<path d="M46.5,80 L46.5,54 L42,26 Q42,13 50,13 Q58,13 58,26 L53.5,54 L53.5,80 Z" fill="{fg}"/>'
        f'<circle cx="50" cy="84" r="6" fill="{fg}"/>'
        f'<rect x="45" y="66" width="10" height="2.5" fill="{bg}"/>'
        f'<rect x="45" y="72" width="10" height="2.5" fill="{bg}"/></g>'
    )


def glyph_rocket(fg: str, bg: str) -> str:
    return (
        f'<g transform="rotate(45 50 50)">'
        f'<path d="M50,10 C58,18 61,28 61,36 L61,68 L39,68 L39,36 C39,28 42,18 50,10 Z" fill="{fg}"/>'
        f'<path d="M39,54 L28,74 L39,70 Z M61,54 L72,74 L61,70 Z" fill="{fg}"/>'
        f'<rect x="43" y="68" width="14" height="6" fill="{fg}"/>'
        f'<path d="M44,77 L50,92 L56,77 Z" fill="{fg}" fill-opacity="0.6"/>'
        f'<rect x="39" y="38" width="22" height="4" fill="{bg}"/></g>'
    )


def glyph_flame(fg: str, bg: str) -> str:
    return (
        f'<path d="M50,12 C58,28 73,37 71,58 C70,75 60,86 50,86 C40,86 30,76 29,61 '
        f'C28,48 35,42 40,33 C42,43 46,48 50,49 C47,36 45,25 50,12 Z" fill="{fg}"/>'
        f'<path d="M50,58 C55,64 59,69 58,75 C57,80 54,83 50,83 C46,83 43,80 42,75 '
        f'C42,69 46,64 50,58 Z" fill="{bg}"/>'
    )


def glyph_bomb(fg: str, bg: str) -> str:
    star = [(80, 10), (82.5, 17.5), (90, 20), (82.5, 22.5), (80, 30), (77.5, 22.5), (70, 20), (77.5, 17.5)]
    return (
        f'<circle cx="45" cy="59" r="25" fill="{fg}"/>'
        f'<rect x="55" y="28" width="13" height="14" rx="2" fill="{fg}" transform="rotate(40 61.5 35)"/>'
        f'<path d="M64,30 Q69,19 76,21" fill="none" stroke="{fg}" stroke-width="4" stroke-linecap="round"/>'
        f'<polygon points="{points(star)}" fill="{fg}"/>'
        f'<circle cx="36" cy="50" r="6" fill="{bg}" fill-opacity="0.45"/>'
    )


def glyph_minigun(fg: str, bg: str) -> str:
    return (
        f'<rect x="12" y="36" width="48" height="7" rx="3" fill="{fg}"/>'
        f'<rect x="12" y="46.5" width="48" height="7" rx="3" fill="{fg}"/>'
        f'<rect x="12" y="57" width="48" height="7" rx="3" fill="{fg}"/>'
        f'<rect x="24" y="32" width="7" height="36" rx="2" fill="{fg}"/>'
        f'<rect x="56" y="29" width="28" height="42" rx="7" fill="{fg}"/>'
        f'<path d="M68,70 L80,70 L84,88 L74,88 Z" fill="{fg}"/>'
        f'<circle cx="70" cy="50" r="7" fill="{bg}"/>'
    )


def glyph_wrench(fg: str, bg: str) -> str:
    return (
        f'<g transform="rotate(45 50 50)">'
        f'<rect x="44" y="38" width="12" height="50" rx="6" fill="{fg}"/>'
        f'<circle cx="50" cy="27" r="17" fill="{fg}"/>'
        f'<rect x="44.5" y="6" width="11" height="21" rx="2" fill="{bg}"/></g>'
    )


def glyph_cross(fg: str, bg: str) -> str:
    return (
        f'<rect x="39" y="18" width="22" height="64" rx="3" fill="{fg}"/>'
        f'<rect x="18" y="39" width="64" height="22" rx="3" fill="{fg}"/>'
    )


def glyph_crosshair(fg: str, bg: str) -> str:
    return (
        f'<circle cx="50" cy="50" r="25" fill="none" stroke="{fg}" stroke-width="6"/>'
        f'<path d="M50,12 V38 M50,62 V88 M12,50 H38 M62,50 H88" stroke="{fg}" '
        f'stroke-width="6" stroke-linecap="round"/>'
        f'<circle cx="50" cy="50" r="4.5" fill="{fg}"/>'
    )


def glyph_mask(fg: str, bg: str) -> str:
    return (
        f'<path d="M14,44 C18,30 40,30 50,40 C60,30 82,30 86,44 C89,58 77,68 65,66 '
        f'C58,65 54,60 50,57 C46,60 42,65 35,66 C23,68 11,58 14,44 Z" fill="{fg}"/>'
        f'<ellipse cx="34" cy="49" rx="9" ry="6" fill="{bg}"/>'
        f'<ellipse cx="66" cy="49" rx="9" ry="6" fill="{bg}"/>'
    )


def glyph_dollar(fg: str, bg: str) -> str:
    return (
        f'<path d="M50,12 V88" stroke="{fg}" stroke-width="7" stroke-linecap="round"/>'
        f'<path d="M66,32 C62,25 56,23 50,23 C41,23 34,28 34,36 C34,45 43,47 50,49 '
        f'C58,51 66,54 66,63 C66,72 59,77 50,77 C43,77 37,74 33,68" fill="none" '
        f'stroke="{fg}" stroke-width="9" stroke-linecap="round"/>'
    )


def _bullet(fg: str, bg: str) -> str:
    return (
        f'<path d="M40,42 C40,26 45,16 50,12 C55,16 60,26 60,42 Z" fill="{fg}"/>'
        f'<rect x="39" y="45" width="22" height="33" rx="1.5" fill="{fg}"/>'
        f'<rect x="36" y="80" width="28" height="7" rx="1.5" fill="{fg}"/>'
    )


def glyph_bullet(fg: str, bg: str) -> str:
    return _bullet(fg, bg)


def glyph_bullets(fg: str, bg: str) -> str:
    return "".join(
        f'<g transform="translate({x} 50) scale(0.62) translate(-50 -50)">{_bullet(fg, bg)}</g>'
        for x in (26, 50, 74)
    )


def glyph_pistol(fg: str, bg: str) -> str:
    return (
        f'<rect x="12" y="30" width="72" height="18" rx="2" fill="{fg}"/>'
        f'<path d="M58,46 L82,46 L88,86 L66,86 Z" fill="{fg}"/>'
        f'<path d="M44,48 C44,61 52,65 61,63" fill="none" stroke="{fg}" stroke-width="5"/>'
        f'<rect x="18" y="35" width="36" height="3" fill="{bg}"/>'
    )


def glyph_grenade(fg: str, bg: str) -> str:
    return (
        f'<ellipse cx="50" cy="61" rx="22" ry="25" fill="{fg}"/>'
        f'<rect x="41" y="27" width="18" height="11" rx="2" fill="{fg}"/>'
        f'<path d="M59,30 L71,30 L66,58" fill="none" stroke="{fg}" stroke-width="5" '
        f'stroke-linecap="round" stroke-linejoin="round"/>'
        f'<circle cx="35" cy="25" r="7" fill="none" stroke="{fg}" stroke-width="4"/>'
        f'<path d="M29,53 H71 M28,68 H72 M50,39 V86" stroke="{bg}" stroke-width="3"/>'
    )


def glyph_knife(fg: str, bg: str) -> str:
    return (
        f'<g transform="rotate(35 50 50)">'
        f'<path d="M43,56 L43,20 C43,13 50,9 59,6 C59,26 59,44 57,56 Z" fill="{fg}"/>'
        f'<rect x="35" y="56" width="30" height="6" rx="2" fill="{fg}"/>'
        f'<rect x="44" y="62" width="12" height="28" rx="4" fill="{fg}"/>'
        f'<path d="M47,24 V52" stroke="{bg}" stroke-width="2.5"/></g>'
    )


GLYPHS: dict[str, dict[str, Glyph]] = {
    "tf2": {
        "mann_co": glyph_cog,
        "scout": glyph_bat,
        "soldier": glyph_rocket,
        "pyro": glyph_flame,
        "demoman": glyph_bomb,
        "heavy": glyph_minigun,
        "engineer": glyph_wrench,
        "medic": glyph_cross,
        "sniper": glyph_crosshair,
        "spy": glyph_mask,
    },
    "cs": {
        "economy": glyph_dollar,
        "rifle": glyph_bullet,
        "sniper": glyph_crosshair,
        "smg": glyph_bullets,
        "pistol": glyph_pistol,
        "utility": glyph_grenade,
        "knife": glyph_knife,
    },
}


def scaled(glyph_markup: str, scale: float) -> str:
    return f'<g transform="translate(50 50) scale({scale}) translate(-50 -50)">{glyph_markup}</g>'


# --------------------------------------------------------------------------
# Team Fortress 2: warm parchment, 1960s poster look, class-colored rim.
# --------------------------------------------------------------------------

TF2_INK = "#3B2E25"
TF2_CREAM = "#F4E9D0"


def tf2_icon_svg(element: Element, glyph: Glyph) -> str:
    accent = element.color
    body = (
        f'<circle cx="50" cy="50" r="46" fill="{accent}" stroke="{TF2_INK}" stroke-width="6"/>'
        f'<circle cx="50" cy="50" r="38.5" fill="none" stroke="{TF2_CREAM}" '
        f'stroke-opacity="0.45" stroke-width="2"/>'
        + scaled(glyph(TF2_CREAM, accent), 0.74)
    )
    return svg_document(100, 100, body)


def tf2_card_svg(element: Element) -> str:
    accent = element.color
    accent_dark = to_hex(darken(accent, 0.35))
    accent_light = to_hex(lighten(accent, 0.3))
    ink = TF2_INK
    ax0, ay0, ax1, ay1 = L.ART_BOX
    bx0, by0, bx1, by1 = L.BANNER_BOX
    corners = [(ax0 - 4, ay0 - 4), (ax1 + 4, ay0 - 4), (ax0 - 4, ay1 + 4), (ax1 + 4, ay1 + 4)]
    rivets = "".join(
        f'<circle cx="{x}" cy="{y}" r="5" fill="#D9C08A" stroke="{ink}" stroke-width="1.5"/>'
        for x, y in corners
    )
    paper = f'x="11" y="11" width="{W - 22}" height="{H - 22}" rx="16"'
    body = f"""<defs>
  <linearGradient id="paper" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#F4E8CC"/><stop offset="1" stop-color="#DEC79B"/>
  </linearGradient>
  <linearGradient id="rim" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="{accent_light}"/><stop offset="0.5" stop-color="{accent}"/>
    <stop offset="1" stop-color="{accent_dark}"/>
  </linearGradient>
  <linearGradient id="header" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#4A3A2E"/><stop offset="1" stop-color="#2A201A"/>
  </linearGradient>
  <pattern id="stripes" width="16" height="16" patternUnits="userSpaceOnUse" patternTransform="rotate(35)">
    <rect width="8" height="16" fill="{accent}" fill-opacity="0.07"/>
  </pattern>
  <radialGradient id="vignette" cx="0.5" cy="0.5" r="0.72">
    <stop offset="0.55" stop-color="#5A3E22" stop-opacity="0"/>
    <stop offset="1" stop-color="#5A3E22" stop-opacity="0.3"/>
  </radialGradient>
  {art_hole_mask()}
</defs>
<g mask="url(#art-hole)">
  <rect width="{W}" height="{H}" rx="24" fill="url(#rim)"/>
  <rect x="7" y="7" width="{W - 14}" height="{H - 14}" rx="19" fill="{ink}"/>
  <rect {paper} fill="url(#paper)"/>
  <rect {paper} fill="url(#stripes)"/>
  <rect {paper} fill="url(#vignette)"/>
  {box_rect(L.HEADER_BOX, rx=9, fill="url(#header)")}
  <rect x="{L.HEADER_BOX[0] + 8}" y="{L.HEADER_BOX[3] - 5}" width="{L.HEADER_BOX[2] - L.HEADER_BOX[0] - 16}" height="3" rx="1.5" fill="{accent}"/>
  <polygon points="{points([(bx0 - 12, by0 + 4), (bx0 + 12, by0 + 4), (bx0 + 12, by1 + 4), (bx0 - 12, by1 + 4), (bx0 - 4, (by0 + by1) / 2 + 4)])}" fill="{accent_dark}" stroke="{ink}" stroke-width="2"/>
  <polygon points="{points([(bx1 + 12, by0 + 4), (bx1 - 12, by0 + 4), (bx1 - 12, by1 + 4), (bx1 + 12, by1 + 4), (bx1 + 4, (by0 + by1) / 2 + 4)])}" fill="{accent_dark}" stroke="{ink}" stroke-width="2"/>
  {box_rect(L.BANNER_BOX, fill=accent, stroke=ink, stroke_width=2)}
  {box_rect(L.ABILITY_PANEL_BOX, rx=10, fill="#FFFFFF", fill_opacity=0.3, stroke=ink, stroke_opacity=0.35, stroke_width=1.5)}
  <line x1="40" y1="{L.STATUS_LINE_Y}" x2="{W - 40}" y2="{L.STATUS_LINE_Y}" stroke="{ink}" stroke-width="2"/>
  {box_rect(L.RARITY_BOX, rx=6, fill=ink, fill_opacity=0.08, stroke=ink, stroke_width=1.5)}
</g>
{box_rect(L.ART_BOX, inset=3, fill="none", stroke=accent, stroke_width=6)}
{box_rect(L.ART_BOX, inset=1, fill="none", stroke=ink, stroke_width=2)}
{box_rect(L.ART_BOX, inset=7, fill="none", stroke=ink, stroke_width=2)}
{rivets}"""
    return svg_document(W, H, body)


# --------------------------------------------------------------------------
# Counter-Strike: dark tactical HUD, chamfered corners, weapon-colored accents.
# --------------------------------------------------------------------------

CS_BASE = "#101317"


def chamfer(box, cut: float, all_corners: bool = True) -> str:
    x0, y0, x1, y1 = box
    if all_corners:
        coordinates = [
            (x0 + cut, y0), (x1 - cut, y0), (x1, y0 + cut), (x1, y1 - cut),
            (x1 - cut, y1), (x0 + cut, y1), (x0, y1 - cut), (x0, y0 + cut),
        ]
    else:  # Top-left and bottom-right only.
        coordinates = [(x0 + cut, y0), (x1, y0), (x1, y1 - cut), (x1 - cut, y1), (x0, y1), (x0, y0 + cut)]
    return points(coordinates)


def hexagon(radius: float) -> str:
    return points(
        (50 + radius * math.cos(math.radians(a)), 50 + radius * math.sin(math.radians(a)))
        for a in range(-90, 270, 60)
    )


def cs_icon_svg(element: Element, glyph: Glyph) -> str:
    accent = element.color
    body = (
        f'<polygon points="{hexagon(45)}" fill="{CS_BASE}" stroke="{accent}" '
        f'stroke-width="7" stroke-linejoin="round"/>'
        + scaled(glyph(to_hex(lighten(accent, 0.15)), CS_BASE), 0.64)
    )
    return svg_document(100, 100, body)


def cs_card_svg(element: Element) -> str:
    accent = element.color
    ax0, ay0, ax1, ay1 = L.ART_BOX
    bx0, by0, bx1, by1 = L.BANNER_BOX
    hx0, hy0, _, hy1 = L.HEADER_BOX
    inner = (5, 5, W - 5, H - 5)
    arm, o = 24, 7  # Corner bracket length and offset around the artwork.
    brackets = " ".join(
        [
            f"M{ax0 - o},{ay0 - o + arm} V{ay0 - o} H{ax0 - o + arm}",
            f"M{ax1 + o - arm},{ay0 - o} H{ax1 + o} V{ay0 - o + arm}",
            f"M{ax0 - o},{ay1 + o - arm} V{ay1 + o} H{ax0 - o + arm}",
            f"M{ax1 + o - arm},{ay1 + o} H{ax1 + o} V{ay1 + o - arm}",
        ]
    )
    center_x = (ax0 + ax1) / 2
    body = f"""<defs>
  <linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#232A31"/><stop offset="1" stop-color="#0E1114"/>
  </linearGradient>
  <radialGradient id="glow" cx="0.9" cy="0" r="0.9">
    <stop offset="0" stop-color="{accent}" stop-opacity="0.3"/>
    <stop offset="1" stop-color="{accent}" stop-opacity="0"/>
  </radialGradient>
  <pattern id="grid" width="12" height="12" patternUnits="userSpaceOnUse">
    <path d="M12,0 H0 V12" fill="none" stroke="#FFFFFF" stroke-opacity="0.045" stroke-width="1"/>
  </pattern>
  <pattern id="hazard" width="10" height="10" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
    <rect width="5" height="10" fill="{CS_BASE}"/>
  </pattern>
  {art_hole_mask()}
</defs>
<g mask="url(#art-hole)">
  <polygon points="{chamfer((0, 0, W, H), 26)}" fill="#060708"/>
  <polygon points="{chamfer(inner, 22)}" fill="url(#bg)"/>
  <polygon points="{chamfer(inner, 22)}" fill="url(#grid)"/>
  <polygon points="{chamfer(inner, 22)}" fill="url(#glow)"/>
  <polygon points="{chamfer(inner, 22)}" fill="none" stroke="{accent}" stroke-width="2"/>
  <polygon points="{chamfer(L.HEADER_BOX, 12, all_corners=False)}" fill="#050607" fill-opacity="0.8" stroke="#FFFFFF" stroke-opacity="0.1"/>
  <rect x="{hx0}" y="{hy0 + 14}" width="5" height="{hy1 - hy0 - 14}" fill="{accent}"/>
  {box_rect(L.BANNER_BOX, fill=accent)}
  <rect x="{bx0}" y="{by0}" width="34" height="{by1 - by0}" fill="url(#hazard)"/>
  <rect x="{bx1 - 34}" y="{by0}" width="34" height="{by1 - by0}" fill="url(#hazard)"/>
  <polygon points="{chamfer(L.ABILITY_PANEL_BOX, 14, all_corners=False)}" fill="#FFFFFF" fill-opacity="0.04" stroke="#FFFFFF" stroke-opacity="0.12"/>
  <line x1="40" y1="{L.STATUS_LINE_Y}" x2="{W - 40}" y2="{L.STATUS_LINE_Y}" stroke="#FFFFFF" stroke-opacity="0.18" stroke-width="1.5"/>
  <polygon points="{chamfer(L.RARITY_BOX, 8, all_corners=False)}" fill="#000000" fill-opacity="0.35" stroke="#FFFFFF" stroke-opacity="0.12"/>
</g>
{box_rect(L.ART_BOX, inset=2, fill="none", stroke="#000000", stroke_width=4)}
<path d="{brackets}" fill="none" stroke="{accent}" stroke-width="4"/>
<path d="M{center_x - 12},{ay0 - o} H{center_x + 12} M{center_x - 12},{ay1 + o} H{center_x + 12}" stroke="{accent}" stroke-width="2"/>"""
    return svg_document(W, H, body)


BUILDERS = {
    "tf2": (tf2_card_svg, tf2_icon_svg),
    "cs": (cs_card_svg, cs_icon_svg),
}


# --------------------------------------------------------------------------
# Build.
# --------------------------------------------------------------------------


def rasterize(svg_path: pathlib.Path, png_path: pathlib.Path, width: int, height: int):
    if shutil.which("rsvg-convert"):
        subprocess.run(
            ["rsvg-convert", "-w", str(width), "-h", str(height), "-o", str(png_path), str(svg_path)],
            check=True,
        )
        return
    try:
        import cairosvg
    except ImportError:
        raise SystemExit("Install librsvg (rsvg-convert) or `pip install cairosvg` to rasterize SVGs.")
    cairosvg.svg2png(url=str(svg_path), write_to=str(png_path), output_width=width, output_height=height)


def build_game(game: Game):
    card_svg, icon_svg = BUILDERS[game.key]
    root = pathlib.Path(game.resources_dir)
    for folder in ("svg/cards", "svg/elements", "cards", "elements"):
        (root / folder).mkdir(parents=True, exist_ok=True)

    for element in game.elements:
        icon_path = root / "svg" / "elements" / f"{element.slug}_element.svg"
        icon_path.write_text(icon_svg(element, GLYPHS[game.key][element.slug]))
        rasterize(icon_path, pathlib.Path(game.element_icon_path(element)), ICON_PX, ICON_PX)

        card_path = root / "svg" / "cards" / f"{element.slug}_card.svg"
        card_path.write_text(card_svg(element))
        rasterize(card_path, pathlib.Path(game.card_template_path(element)), W, H)
        print(f"[{game.key}] {element.name}: {card_path.name}, {icon_path.name}")


def main():
    parser = argparse.ArgumentParser(description="Build SVG card templates and icons.")
    parser.add_argument("-g", "--game", choices=sorted(GAMES), default=None)
    args = parser.parse_args()
    for key in [args.game] if args.game else GAMES:
        build_game(GAMES[key])


if __name__ == "__main__":
    main()
