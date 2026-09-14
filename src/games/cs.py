from games.game import CardTheme, Game, Subject, holding, wearing, with_
from mechanics.element import Element
from mechanics.rarity import Rarity

# Elements: weapon categories, plus a neutral "Economy" element (the $ energy).
ECONOMY = Element("Economy", ascii_color="\033[37m", is_neutral=True, color="#5FAF4E")
RIFLE = Element("Rifle", ascii_color="\033[33m", color="#E08A2E")
SNIPER = Element("Sniper", ascii_color="\033[36m", color="#3FA7A0")
SMG = Element("SMG", ascii_color="\033[33m", color="#CDBB35")
PISTOL = Element("Pistol", ascii_color="\033[37m", color="#7F8FA6")
UTILITY = Element("Utility", ascii_color="\033[35m", color="#9A6BD1")
KNIFE = Element("Knife", ascii_color="\033[31m", color="#D64545")

ELEMENTS = [ECONOMY, RIFLE, SNIPER, SMG, PISTOL, UTILITY, KNIFE]

# Rarities follow CS skin grades.
MIL_SPEC = Rarity("Mil-Spec", 0, (75, 105, 255))
CLASSIFIED = Rarity("Classified", 1, (211, 44, 230))
COVERT = Rarity("Covert", 2, (235, 75, 75))

GEAR = [
    wearing("tactical balaclava"),
    wearing("pair of night vision goggles"),
    wearing("kevlar vest"),
    wearing("combat helmet"),
]

SUBJECTS = {
    ECONOMY: [
        Subject("black-market arms dealer", [holding("briefcase full of cash"), holding("Zeus taser"), wearing("heavy gold chain")]),
        Subject("armored chicken", [wearing("tiny kevlar vest"), wearing("party hat"), with_("golden feathers")]),
        Subject("hostage negotiator", [holding("megaphone"), holding("defuse kit"), wearing("kevlar vest")]),
    ],
    RIFLE: [
        Subject("SAS commando", [holding("M4 carbine"), holding("assault rifle"), *GEAR]),
        Subject("Phoenix Connexion thug", [holding("AK-47 rifle"), holding("C4 bomb"), wearing("bandana")]),
        Subject("Balkan fighter", [holding("Galil rifle"), holding("AK-47 rifle"), wearing("tracksuit jacket")]),
    ],
    SNIPER: [
        Subject("GSG-9 marksman", [holding("AWP sniper rifle"), holding("scoped rifle"), *GEAR]),
        Subject("Sabre mercenary", [holding("AWP sniper rifle"), wearing("ghillie hood"), wearing("tactical headset")]),
        Subject("guerrilla sharpshooter", [holding("SSG 08 scout rifle"), wearing("jungle camouflage")]),
    ],
    SMG: [
        Subject("FBI SWAT agent", [holding("MP9 submachine gun"), holding("P90"), *GEAR]),
        Subject("Elite Crew mobster", [holding("MAC-10"), wearing("pair of aviator sunglasses"), wearing("gold chain")]),
        Subject("professional heist robber", [holding("UMP-45"), wearing("clown mask"), holding("bag of loot")]),
    ],
    PISTOL: [
        Subject("GIGN gendarme", [holding("USP pistol with a silencer"), holding("Desert Eagle"), *GEAR]),
        Subject("Elite Crew enforcer", [holding("pair of dual Berettas"), wearing("leather jacket")]),
        Subject("undercover FBI agent", [holding("Five-SeveN pistol"), wearing("sharp black suit")]),
    ],
    UTILITY: [
        Subject("SEAL frogman", [holding("smoke grenade"), holding("flashbang"), wearing("diving mask")]),
        Subject("Guerrilla Warfare rebel", [holding("molotov cocktail"), holding("HE grenade"), wearing("bandana")]),
        Subject("bomb-squad technician", [holding("defuse kit"), holding("decoy grenade"), wearing("blast suit")]),
    ],
    KNIFE: [
        Subject("Balkan knife-fighter", [holding("karambit knife"), holding("butterfly knife"), wearing("tracksuit jacket")]),
        Subject("ninja-like SAS infiltrator", [holding("bayonet"), holding("gut knife"), *GEAR]),
        Subject("anarchist knife artist", [holding("butterfly knife"), wearing("skull mask")]),
    ],
}

DUST = "a sun-bleached Middle Eastern town with sandy archways"
MIRAGE = "a sunlit Moroccan palace market"
INFERNO = "a quaint Italian village with narrow cobblestone alleys"
NUKE = "a nuclear power plant full of rusty pipes"
TRAIN = "a Soviet train yard at dusk"
OVERPASS = "a concrete canal park under a highway overpass"
VERTIGO = "an unfinished skyscraper high above the city"
ANCIENT = "an overgrown jungle temple"
ANUBIS = "riverside Egyptian ruins with sandstone statues"
OFFICE = "a snowy office building at night"
BAZAAR = "a dim back-alley arms bazaar"

ENVIRONMENTS = {
    ECONOMY: [BAZAAR, OFFICE, INFERNO],
    RIFLE: [DUST, MIRAGE, ANCIENT],
    SNIPER: [DUST, VERTIGO, ANUBIS],
    SMG: [OFFICE, OVERPASS, NUKE],
    PISTOL: [INFERNO, OFFICE, TRAIN],
    UTILITY: [NUKE, MIRAGE, OVERPASS],
    KNIFE: [ANCIENT, TRAIN, VERTIGO],
}

COMMON_AMBIENCE = [
    "harsh midday sun",
    "volumetric dust in the air",
    "cold blue moonlight",
    "drifting smoke grenade haze",
]


def _ambience(final: str) -> list[str]:
    return [*COMMON_AMBIENCE, final]


AMBIENCE = {
    ECONOMY: _ambience("raining dollar bills, golden light"),
    RIFLE: _ambience("muzzle flash and flying brass casings, dramatic backlight"),
    SNIPER: _ambience("sharp scope glint, dramatic rim light"),
    SMG: _ambience("streaks of tracer fire"),
    PISTOL: _ambience("single spotlight, noir shadows"),
    UTILITY: _ambience("blinding flashbang burst of light"),
    KNIFE: _ambience("slow-motion knife glint, crimson rim light"),
}

# Detail adjectives are weapon skin finishes.
DETAIL_ADJECTIVES = {
    ECONOMY: ["gold-plated", "diamond-studded"],
    RIFLE: ["Redline", "Vulcan-patterned", "Fire Serpent"],
    SNIPER: ["Dragon Lore", "Asiimov", "Medusa-patterned"],
    SMG: ["neon-painted", "Hyper Beast"],
    PISTOL: ["Blaze-patterned", "Printstream", "engraved"],
    UTILITY: ["hazard-striped", "sticker-covered"],
    KNIFE: ["Fade", "Doppler", "Crimson Web", "Case Hardened"],
}

CS = Game(
    key="cs",
    title="Counter-Strike",
    collection_name="cs-operators",
    subject_type="operator",
    subject_suffix="from Counter-Strike 2",
    element_adjective="{element}-specialist",
    neutral_adjective="",
    environment_sentence="It usually operates in {environment}.",
    elements=ELEMENTS,
    rarities=[MIL_SPEC, CLASSIFIED, COVERT],
    subjects=SUBJECTS,
    default_details=[holding("assault rifle"), *GEAR],
    environments=ENVIRONMENTS,
    ambience=AMBIENCE,
    global_detail_adjectives=["battle-scarred", "factory-new", "StatTrak", "field-tested", "black"],
    detail_adjectives=DETAIL_ADJECTIVES,
    rarity_adjectives=[
        ["disciplined", "ordinary"],
        ["elite", "decorated"],
        ["legendary", "notorious", "tier-one"],
    ],
    series_adjectives=[
        ["recruit", "rookie"],
        ["field-tested", "hardened"],
        ["battle-scarred veteran", "elite"],
    ],
    style_suffixes={
        0: ["Counter-Strike 2 style, clean 3D render, studio lighting"],
        1: ["Counter-Strike 2 agent render, cinematic lighting, detailed"],
        2: ["Counter-Strike 2 key art, cinematic, ultra-detailed, dramatic rim lighting"],
        None: ["Counter-Strike 2 agent art, cinematic lighting"],
    },
    prompt_suffix="--v 7 --style raw",
    weakness={
        ECONOMY: KNIFE,
        RIFLE: SNIPER,
        SNIPER: UTILITY,
        SMG: RIFLE,
        PISTOL: SMG,
        UTILITY: SMG,
        KNIFE: PISTOL,
    },
    resistance={
        RIFLE: SMG,
        SNIPER: RIFLE,
        SMG: PISTOL,
        PISTOL: SNIPER,
        UTILITY: SNIPER,
    },
    hp_modifier={SNIPER: -10, PISTOL: -10, KNIFE: -10, ECONOMY: 10},
    name_rules=(
        "an original, creative Counter-Strike operator callsign, "
        "never the weapon category or the word 'operator'"
    ),
    description_rules=(
        "a gritty 2-3 sentence classified operator dossier mentioning one habit "
        "between rounds, without repeating the play names"
    ),
    ability_prompt=(
        "Generate {n} unique, punchy Counter-Strike style play names for a {power} "
        "{element} move {words}. Use CS slang, weapon names and pro-scene terms."
    ),
    fallback_names=[
        "Viper", "Ghost", "Havoc", "Nomad", "Reaper", "Echo", "Blitz", "Cipher",
        "Wraith", "Falcon", "Rook", "Vandal", "Sable", "Onyx", "Specter", "Maverick",
        "Warden", "Talon", "Kodiak", "Jackal", "Bishop", "Raptor", "Nova", "Frost",
        "Grim", "Hex", "Titan", "Striker", "Shade", "Vortex",
    ],
    theme=CardTheme(
        title_color=(236, 239, 241),
        text_color=(222, 226, 230),
        muted_color=(130, 138, 146),
        line_color=(70, 78, 86),
        banner_text_color=(12, 14, 17),
        status_labels=("weakness", "resistance", "rotate"),
        footer="Fan-made card · not affiliated with Valve",
        uppercase_names=True,
    ),
)
