from dataclasses import dataclass
import random

from content.collection import Collection
from content.style import Style
from games.game import Game, Subject
from games.prompts import (
    enrich_cards_with_ai,
    fallback_description,
    fallback_name,
    get_image_prompt,
    get_visual_description,
)
from mechanics.ability import Ability
from mechanics.card import Card
from mechanics.element import Element
from mechanics.rarity import Rarity
from util.ability_name_library import get_ability_name

MIN_HP = 30


@dataclass
class GameCollection(Collection):
    game: Game | None = None

    BASE_POINTS = 4
    ABILITY_TO_HP_PTS = 2  # 1 ability cost is worth 2 HP points.
    NEUTRAL_ELEMENT_CHANCE = 0.5
    MIXED_ELEMENT_CHANCE = 0.5

    @classmethod
    def for_game(cls, game: Game) -> "GameCollection":
        return cls(
            game.collection_name,
            theme_style=Style(subject_type=game.subject_type, style_suffix=game.prompt_suffix),
            elements=game.elements,
            rarities=game.rarities,
            game=game,
        )

    def generate_card(
        self,
        element: Element,
        rarity: Rarity,
        inherited_style: Style = None,
        series_index: int | None = None,
        subject_override: str = None,
    ) -> Card:
        # Cards in a series start weaker, but get stronger as the series progresses.
        max_ability_points = self.get_points_budget(
            rarity.index, series_index if series_index is not None else 1
        )
        hp_points = random.randint(0, max_ability_points // 2)
        ability_points = max_ability_points - hp_points
        ability_costs = self.get_ability_points_costs(ability_points, rarity.index)
        abilities = self.generate_abilities(element, ability_costs)

        used_names = set()
        for ability in abilities:
            ability.name = get_ability_name(ability, self.game, exclude=used_names)
            used_names.add(ability.name)

        bonus_hp_points = max_ability_points + (hp_points * self.ABILITY_TO_HP_PTS)
        hp = max(MIN_HP, 10 * bonus_hp_points + self.game.hp_modifier.get(element, 0))

        style = self.generate_style(
            inherited_style, element, rarity, series_index, subject_override
        )
        card = Card(
            index=len(self.cards) + 1,
            name="Untitled Card",
            element=element,
            rarity=rarity,
            abilities=abilities,
            hp=hp,
            style=style,
            game=self.game.key,
        )

        # Offline name/description; enrich_with_ai() can replace them later in batches.
        card.visual_description = get_visual_description(card, self.game)
        card.name = fallback_name(self.game, self.card_names_seen)
        card.description = fallback_description(card)
        card.image_prompt = get_image_prompt(card, self.game)

        self.card_names_seen.add(card.name)
        self.cards.append(card)
        return card

    def enrich_with_ai(self, batch_size: int = 10) -> int:
        """Names and describes every card with AI. Returns the number of requests used."""
        return enrich_cards_with_ai(self.cards, self.game, self.card_names_seen, batch_size)

    def pick_subject(self, element: Element, subject_override: str | None) -> Subject:
        if subject_override is not None:
            return self.game.find_subject(subject_override) or Subject(
                subject_override, self.game.default_details
            )

        potential_subjects = self.game.subjects[element]
        unseen_subjects = [s for s in potential_subjects if s.name not in self.subjects_seen]
        subject = random.choice(unseen_subjects or potential_subjects)
        self.subjects_seen.add(subject.name)
        return subject

    def generate_style(
        self,
        inherited_style: Style,
        element: Element,
        rarity: Rarity,
        series_index: int | None = None,
        subject_override: str = None,
    ) -> Style:
        game = self.game
        style = Style(
            subject_type=game.subject_type,
            style_prefix=self.theme_style.style_prefix,
            style_suffix=self.theme_style.style_suffix,
        )

        if inherited_style is not None:
            style.subject = inherited_style.subject
            style.detail = inherited_style.detail
            style.environment = inherited_style.environment
        else:
            subject = self.pick_subject(element, subject_override)
            style.subject = subject.name
            adjective = random.choice(
                game.global_detail_adjectives + game.detail_adjectives.get(element, [])
            )
            style.detail = random.choice(subject.details or game.default_details).text(adjective)
            style.environment = random.choice(game.environments[element])

        # Pick adjective(s) for the subject.
        rarity_prefix = random.choice(
            game.rarity_adjectives[min(rarity.index, len(game.rarity_adjectives) - 1)]
        )
        if element.is_neutral:
            element_prefix = game.neutral_adjective
        else:
            element_prefix = game.element_adjective.format(element=element.name)

        if series_index is not None:
            size_prefix = random.choice(
                game.series_adjectives[min(series_index, len(game.series_adjectives) - 1)]
            )
            if rarity.index >= 2:
                size_prefix += f" {rarity_prefix}"
        else:
            size_prefix = rarity_prefix

        style.subject_adjectives = [
            *self.theme_style.subject_adjectives,
            size_prefix,
            element_prefix,
        ]

        # The last ambience is reserved for the final card of a rare series.
        ambiences = game.ambience[element]
        if rarity.index >= 2 and series_index == 2:
            style.ambience = ambiences[-1]
        else:
            style.ambience = random.choice(ambiences[:-1])

        suffixes = game.style_suffixes.get(series_index, game.style_suffixes[None])
        style.style_suffix = f"{random.choice(suffixes)} {game.prompt_suffix}".strip()
        return style

    def generate_abilities(self, element: Element, ability_costs: list[int]):
        abilities = []
        for i, cost in enumerate(ability_costs):
            is_primary = i == 0
            if not is_primary and random.random() < self.NEUTRAL_ELEMENT_CHANCE:
                ability_element = self.get_default_element()
            else:
                ability_element = element
            abilities.append(self.generate_ability(ability_element, cost))
        return abilities

    @classmethod
    def get_points_budget(cls, rarity_index: int, series_index: int) -> int:
        return cls.BASE_POINTS + rarity_index + (series_index - 1)

    @classmethod
    def generate_ability(cls, element: Element, cost: int) -> Ability:
        is_mix = (
            not element.is_neutral
            and cost > 1
            and random.random() < cls.MIXED_ELEMENT_CHANCE
        )
        return Ability(name="New Ability", element=element, cost=cost, is_mixed_element=is_mix)

    @staticmethod
    def get_ability_points_costs(ability_points: int, rarity_index: int) -> list[int]:
        # Determine how many abilities the card will have, and how much each one costs.
        if ability_points >= 6:
            return [4, ability_points - 4]
        elif ability_points >= 4:
            first_ability_cost = random.choice([3, 4])
            if first_ability_cost == 4:
                return [4]
            return [first_ability_cost, ability_points - first_ability_cost]
        elif ability_points == 3:
            if rarity_index < 1:
                return [2, 1]
            return [3] if random.random() < 0.5 else [2, 1]
        return [ability_points]

    def to_json(self):
        return {"game": self.game.key, **super().to_json()}
