from dataclasses import dataclass, field

from mechanics.element import Element
from mechanics.rarity import Rarity

RGB = tuple[int, int, int]


def indefinite_article(phrase: str) -> str:
    return "an" if phrase[:1].lower() in "aeiou" else "a"


@dataclass
class Detail:
    """Something describing the card's subject, e.g. 'holding a rocket launcher'."""

    relation: str
    detail: str
    quantifier: str | None = None  # "a" picks "a"/"an" automatically.

    def text(self, adjective: str | None = None) -> str:
        phrase = " ".join(word for word in (adjective, self.detail) if word)
        if self.quantifier == "a":
            phrase = f"{indefinite_article(phrase)} {phrase}"
        elif self.quantifier:
            phrase = f"{self.quantifier} {phrase}"
        return f"{self.relation} {phrase}"

    def __hash__(self) -> int:
        return hash((self.relation, self.detail))


def holding(detail: str, quantifier: str | None = "a") -> Detail:
    return Detail("holding", detail, quantifier)


def wearing(detail: str, quantifier: str | None = "a") -> Detail:
    return Detail("wearing", detail, quantifier)


def with_(detail: str, quantifier: str | None = None) -> Detail:
    return Detail("with", detail, quantifier)


@dataclass
class Subject:
    """The main character of a card (e.g. 'patriotic drill sergeant')."""

    name: str
    details: list[Detail] = field(default_factory=list)

    def __hash__(self) -> int:
        return hash(self.name)


@dataclass(kw_only=True)
class CardTheme:
    """Text colors and labels used by the renderer (shapes live in the SVG templates)."""

    title_color: RGB
    text_color: RGB
    muted_color: RGB
    line_color: RGB
    banner_text_color: RGB
    status_labels: tuple[str, str, str]
    footer: str
    uppercase_names: bool = False


@dataclass(kw_only=True)
class Game:
    key: str  # Also the resources/ and data/ folder name.
    title: str
    collection_name: str

    # Prompt building blocks: "a <adjectives> <subject> <subject_type> <subject_suffix>".
    subject_type: str
    subject_suffix: str
    element_adjective: str  # Formatted with {element}.
    neutral_adjective: str
    environment_sentence: str  # Formatted with {environment}.

    elements: list[Element]  # The neutral element must be first.
    rarities: list[Rarity]

    subjects: dict[Element, list[Subject]]
    default_details: list[Detail]  # Used for custom --subject values.
    environments: dict[Element, list[str]]
    ambience: dict[Element, list[str]]  # The last one is reserved for final forms.
    global_detail_adjectives: list[str]
    detail_adjectives: dict[Element, list[str]]
    rarity_adjectives: list[list[str]]
    series_adjectives: list[list[str]]
    style_suffixes: dict[int | None, list[str]]
    prompt_suffix: str

    weakness: dict[Element, Element]
    resistance: dict[Element, Element]
    hp_modifier: dict[Element, int] = field(default_factory=dict)

    # AI instructions (see games/prompts.py and util/ability_name_library.py).
    name_rules: str
    description_rules: str
    ability_prompt: str
    fallback_names: list[str]  # Used when AI generation is disabled.

    theme: CardTheme

    @property
    def neutral(self) -> Element:
        return next(element for element in self.elements if element.is_neutral)

    def element_by_name(self, name: str) -> Element:
        wanted = name.lower().strip()
        for element in self.elements:
            if wanted in (element.name.lower(), element.slug):
                return element
        valid = ", ".join(element.slug for element in self.elements)
        raise KeyError(f"Unknown element '{name}' for {self.title}. Valid: {valid}")

    def rarity_by_name(self, name: str) -> Rarity:
        for rarity in self.rarities:
            if rarity.name.lower() == name.lower():
                return rarity
        return self.rarities[-1]

    def find_subject(self, name: str) -> Subject | None:
        for subjects in self.subjects.values():
            for subject in subjects:
                if subject.name.lower() == name.lower():
                    return subject
        return None

    @property
    def resources_dir(self) -> str:
        return f"resources/{self.key}"

    def card_template_path(self, element: Element) -> str:
        return f"{self.resources_dir}/cards/{element.slug}_card.png"

    def element_icon_path(self, element: Element) -> str:
        return f"{self.resources_dir}/elements/{element.slug}_element.png"

    @property
    def ability_names_path(self) -> str:
        return f"data/{self.key}/ability_names.json"
