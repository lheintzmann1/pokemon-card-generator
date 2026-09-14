# Card geometry, shared by the SVG template builder and the card renderer.
# Boxes are (x0, y0, x1, y1) in pixels.

CARD_WIDTH, CARD_HEIGHT = 474, 659

# Header: card name (left), HP and element icon (right).
HEADER_BOX = (24, 22, 450, 74)
HEADER_MID_Y = 48
NAME_X = 40
HP_RIGHT = 396
ICON_CENTER = (424, 48)
ICON_SIZE = 36

# Artwork window (3:2). The template is transparent inside this box.
ART_BOX = (42, 84, 432, 344)

# Ribbon under the artwork (e.g. "SOLDIER MERCENARY").
BANNER_BOX = (48, 352, 426, 376)
BANNER_MID_Y = 364

# Abilities.
ABILITY_PANEL_BOX = (28, 384, 446, 530)
ABILITY_CENTER_Y = 457
ABILITY_WIDTH = 370
ABILITY_HEIGHT = 66
ABILITY_GAP = 8
ABILITY_COST_WIDTH = 76
ABILITY_POWER_WIDTH = 64
ELEMENT_SIZE = 28
ELEMENT_GAP = 4

# Weakness / resistance / retreat.
STATUS_LINE_Y = 538
STATUS_LABEL_Y = 552
STATUS_ICON_Y = 573
STATUS_ICON_SIZE = 22
STATUS_XS = (82, 237, 392)

# Rarity strip and footer.
RARITY_BOX = (40, 590, 434, 618)
RARITY_MID_Y = 604
FOOTER_Y = 635
FOOTER_X = (44, 430)
