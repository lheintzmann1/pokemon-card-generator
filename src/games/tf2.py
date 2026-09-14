from games.game import CardTheme, Game, Subject, holding, wearing, with_
from mechanics.element import Element
from mechanics.rarity import Rarity

# Elements: one per class, plus a neutral "Mann Co." element.
MANN_CO = Element("Mann Co.", ascii_color="\033[37m", is_neutral=True, color="#8A7A63")
SCOUT = Element("Scout", ascii_color="\033[33m", color="#D1A23A")
SOLDIER = Element("Soldier", ascii_color="\033[32m", color="#6B6A3A")
PYRO = Element("Pyro", ascii_color="\033[31m", color="#C8402A")
DEMOMAN = Element("Demoman", ascii_color="\033[34m", color="#3D5A8C")
HEAVY = Element("Heavy", ascii_color="\033[31m", color="#7E2F2A")
ENGINEER = Element("Engineer", ascii_color="\033[33m", color="#B8652A")
MEDIC = Element("Medic", ascii_color="\033[36m", color="#3F8C86")
SNIPER = Element("Sniper", ascii_color="\033[32m", color="#4F7A3A")
SPY = Element("Spy", ascii_color="\033[35m", color="#5B4A7E")

ELEMENTS = [MANN_CO, SCOUT, SOLDIER, PYRO, DEMOMAN, HEAVY, ENGINEER, MEDIC, SNIPER, SPY]

# Rarities follow TF2 item qualities.
UNIQUE = Rarity("Unique", 0, (255, 215, 0))
STRANGE = Rarity("Strange", 1, (207, 106, 50))
UNUSUAL = Rarity("Unusual", 2, (134, 80, 172))

# Cosmetics anyone can wear.
COSMETICS = [
    wearing("comically tall top hat"),
    wearing("team-colored scarf"),
    wearing("festive holiday sweater"),
    wearing("pair of oversized aviator goggles"),
]

SUBJECTS = {
    MANN_CO: [
        Subject("Mann vs. Machine robot", [holding("giant bomb"), with_("glowing eyes"), wearing("tank-tread belt")]),
        Subject("bowler-hatted civilian", [holding("umbrella"), wearing("bowler hat"), holding("briefcase")]),
        Subject("mustachioed Mann Co. executive", [holding("briefcase full of money"), wearing("pith helmet"), holding("gold-plated contract")]),
        Subject("supply-crate mimic", [with_("key-shaped padlock", "a"), with_("rows of sharp teeth"), wearing("shipping label")]),
    ],
    SCOUT: [
        Subject("fast-talking Boston kid", [holding("scattergun"), holding("baseball bat"), wearing("backwards baseball cap"), *COSMETICS]),
        Subject("hyperactive baseball fanatic", [holding("can of radioactive energy drink"), holding("baseball bat"), wearing("pair of headphones")]),
        Subject("street-smart sprinter", [holding("sawed-off shotgun"), wearing("dog tag"), wearing("pair of running shoes")]),
    ],
    SOLDIER: [
        Subject("patriotic drill sergeant", [holding("rocket launcher"), holding("shovel"), wearing("helmet pulled over the eyes")]),
        Subject("rocket-jumping maniac", [holding("rocket launcher"), holding("bugle"), wearing("bandolier of grenades")]),
        Subject("shell-shocked veteran", [holding("battle banner"), holding("pickaxe"), wearing("stack of war medals"), *COSMETICS]),
    ],
    PYRO: [
        Subject("mysterious masked firebug", [holding("flamethrower"), holding("fire axe"), wearing("gas mask")]),
        Subject("cheerful fire-starter", [holding("flare gun"), holding("giant lollipop"), wearing("rubber duck on a string")]),
        Subject("rubber-suited arsonist", [holding("rainbow flamethrower"), holding("sledgehammer"), wearing("fireproof suit"), *COSMETICS]),
    ],
    DEMOMAN: [
        Subject("one-eyed explosives expert", [holding("grenade launcher"), holding("sticky bomb launcher"), wearing("eye patch")]),
        Subject("Scottish demolitionist", [holding("bottle of scrumpy"), holding("frag grenade"), wearing("tam o' shanter")]),
        Subject("sword-swinging demoknight", [holding("claymore"), holding("round wooden shield"), wearing("tartan kilt"), *COSMETICS]),
    ],
    HEAVY: [
        Subject("giant Russian bruiser", [holding("gigantic minigun"), wearing("pair of boxing gloves"), wearing("bullet belt")]),
        Subject("gentle bear-like strongman", [holding("sandwich"), wearing("ushanka"), holding("bear-sized minigun")]),
        Subject("minigun-loving juggernaut", [holding("rotary minigun"), wearing("steel knuckle gloves"), *COSMETICS]),
    ],
    ENGINEER: [
        Subject("good-ol'-boy Texan inventor", [holding("wrench"), holding("shotgun"), wearing("hard hat")]),
        Subject("soft-spoken gadgeteer", [holding("robotic hand"), holding("rolled blueprint"), wearing("pair of welding goggles")]),
        Subject("sentry-building mechanic", [with_("sentry gun at their side", "a"), holding("toolbox"), wearing("hard hat"), *COSMETICS]),
    ],
    MEDIC: [
        Subject("mad German doctor", [holding("medi gun"), holding("bonesaw"), wearing("blood-stained lab coat")]),
        Subject("cheerful battlefield surgeon", [holding("syringe gun"), with_("pet dove on the shoulder", "a"), wearing("surgical mask")]),
        Subject("unlicensed experimenter", [holding("glowing medi gun"), holding("crossbow"), wearing("round spectacles"), *COSMETICS]),
    ],
    SNIPER: [
        Subject("laconic Australian bushman", [holding("sniper rifle"), holding("kukri"), wearing("slouch hat")]),
        Subject("camper-van marksman", [holding("longbow"), holding("jar of mysterious liquid"), wearing("pair of aviator sunglasses")]),
        Subject("patient outback hunter", [holding("scoped rifle"), wearing("crocodile-leather vest"), *COSMETICS]),
    ],
    SPY: [
        Subject("suave French infiltrator", [holding("revolver"), holding("butterfly knife"), wearing("balaclava")]),
        Subject("chain-smoking secret agent", [holding("cigarette case"), holding("electric sapper"), wearing("pinstripe suit")]),
        Subject("master of disguise", [holding("disguise kit"), holding("pocket watch"), wearing("fake paper mask"), *COSMETICS]),
    ],
}

DESERT_FORT = "a sun-baked desert fort with a wooden bridge"
RAIL_YARD = "a dusty railway yard with a bomb cart"
SAWMILL = "a misty alpine sawmill"
SNOW_BASE = "a snowy mountain base"
FARM = "a rustic farm with red barns"
FACTORY = "a Mann Co. factory floor"
HARBOR = "a foggy harbor with shipping containers"
CASTLE = "a haunted Halloween castle"
LAIR = "a spy-fi villain's volcano lair"
OUTBACK = "a sun-bleached Australian outback"
INFIRMARY = "a gleaming underground infirmary"
QUARRY = "a gravel quarry with rusty cranes"

ENVIRONMENTS = {
    MANN_CO: [FACTORY, LAIR, CASTLE],
    SCOUT: [DESERT_FORT, FARM, RAIL_YARD],
    SOLDIER: [QUARRY, RAIL_YARD, SNOW_BASE],
    PYRO: [SAWMILL, CASTLE, FARM],
    DEMOMAN: [QUARRY, HARBOR, CASTLE],
    HEAVY: [SNOW_BASE, FACTORY, RAIL_YARD],
    ENGINEER: [DESERT_FORT, FACTORY, SAWMILL],
    MEDIC: [INFIRMARY, LAIR, SNOW_BASE],
    SNIPER: [OUTBACK, DESERT_FORT, SAWMILL],
    SPY: [LAIR, HARBOR, DESERT_FORT],
}

COMMON_AMBIENCE = [
    "warm late-afternoon sunlight",
    "bright stylized daylight",
    "dusty golden-hour haze",
    "soft overcast light",
]


def _ambience(final: str) -> list[str]:
    return [*COMMON_AMBIENCE, final]


AMBIENCE = {
    MANN_CO: _ambience("unusual golden sunbeams particle effect"),
    SCOUT: _ambience("unusual sparkling stars particle effect"),
    SOLDIER: _ambience("unusual burning flames particle effect"),
    PYRO: _ambience("unusual purple energy flames particle effect"),
    DEMOMAN: _ambience("unusual green energy particle effect"),
    HEAVY: _ambience("unusual sunbeams particle effect"),
    ENGINEER: _ambience("unusual circling gears particle effect"),
    MEDIC: _ambience("unusual orbiting planets particle effect"),
    SNIPER: _ambience("unusual scorching flames particle effect"),
    SPY: _ambience("unusual haunted ghosts particle effect"),
}

DETAIL_ADJECTIVES = {
    MANN_CO: ["gold-plated", "mechanical"],
    SCOUT: ["team-colored", "dented"],
    SOLDIER: ["battle-worn", "star-spangled"],
    PYRO: ["rainbow", "scorched"],
    DEMOMAN: ["tartan", "explosive"],
    HEAVY: ["gigantic", "steel"],
    ENGINEER: ["custom-built", "brass"],
    MEDIC: ["glowing", "surgical"],
    SNIPER: ["weathered", "camouflaged"],
    SPY: ["invisible-shimmering", "elegant"],
}

TF2 = Game(
    key="tf2",
    title="Team Fortress 2",
    collection_name="tf2-mercenaries",
    subject_type="mercenary",
    subject_suffix="from Team Fortress 2",
    element_adjective="{element}-class",
    neutral_adjective="Mann Co.",
    environment_sentence="It is usually seen fighting in {environment}.",
    elements=ELEMENTS,
    rarities=[UNIQUE, STRANGE, UNUSUAL],
    subjects=SUBJECTS,
    default_details=[holding("shotgun"), *COSMETICS],
    environments=ENVIRONMENTS,
    ambience=AMBIENCE,
    global_detail_adjectives=["strange", "festive", "australium", "vintage", "decorated", "killstreak-glowing"],
    detail_adjectives=DETAIL_ADJECTIVES,
    rarity_adjectives=[
        ["scrappy", "everyday"],
        ["notorious", "decorated", "renowned"],
        ["legendary", "infamous", "mythical"],
    ],
    series_adjectives=[
        ["rookie", "fresh-recruit"],
        ["seasoned", "battle-hardened"],
        ["grizzled veteran", "hulking"],
    ],
    style_suffixes={
        0: ["Team Fortress 2 art style, stylized cartoon proportions, painterly shading, clean background"],
        1: ["Team Fortress 2 loading screen art, painterly illustration"],
        2: ["epic Team Fortress 2 promotional poster, 1960s commercial illustration, dramatic composition"],
        None: ["Team Fortress 2 art style, painterly illustration"],
    },
    prompt_suffix="--v 7",
    weakness={
        MANN_CO: HEAVY,
        SCOUT: ENGINEER,
        SOLDIER: PYRO,
        PYRO: SOLDIER,
        DEMOMAN: SCOUT,
        HEAVY: SNIPER,
        ENGINEER: DEMOMAN,
        MEDIC: SPY,
        SNIPER: SPY,
        SPY: PYRO,
    },
    resistance={
        SCOUT: HEAVY,
        SOLDIER: ENGINEER,
        PYRO: SPY,
        DEMOMAN: ENGINEER,
        HEAVY: SCOUT,
        ENGINEER: SCOUT,
        SNIPER: HEAVY,
        SPY: SNIPER,
    },
    hp_modifier={HEAVY: 30, SOLDIER: 10, SCOUT: -10, ENGINEER: -10, SNIPER: -10, SPY: -10},
    name_rules=(
        "an original, creative Team Fortress 2 style mercenary nickname, "
        "never the class name or the word 'mercenary'"
    ),
    description_rules=(
        "a funny 2-3 sentence Mann Co. personnel file entry mentioning a quirky habit "
        "between matches, without repeating the move names"
    ),
    ability_prompt=(
        "Generate {n} unique, punchy Team Fortress 2 style move names for a {power} "
        "{element} attack {words}. Mix real TF2 weapon or taunt names with original ones."
    ),
    fallback_names=[
        "Boomer", "Sarge", "Sparky", "Scrapper", "Tinhead", "Bonkers", "Hawkeye",
        "Doc", "Sawbones", "Tex", "Crumpet", "Frenchie", "Bushman", "Kaboomski",
        "Cinder", "Moxie", "Grizzle", "Nitro", "Buckshot", "Gearhead", "Wisp",
        "Stitches", "Pops", "Dusty", "Brick", "Rocketeer", "Spanner", "Smokey",
        "Jolly", "Ratchet",
    ],
    theme=CardTheme(
        title_color=(244, 233, 208),
        text_color=(59, 46, 37),
        muted_color=(125, 104, 84),
        line_color=(59, 46, 37),
        banner_text_color=(244, 233, 208),
        status_labels=("weakness", "resistance", "respawn"),
        footer="Fan-made card · not affiliated with Valve",
    ),
)
