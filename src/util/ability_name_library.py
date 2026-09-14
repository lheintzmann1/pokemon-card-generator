import argparse
from functools import lru_cache
import json
import os
import random
import re
import string

from games.game import Game
from mechanics.ability import Ability
from util.gpt_call import gpt_client

COST_ADJECTIVES = ["weak, basic", "standard", "strong", "devastating, ultimate"]


def ability_key(ability: Ability) -> str:
    return f"{ability.element.slug}_{ability.cost}"


@lru_cache(maxsize=None)
def load_ability_names(path: str) -> dict[str, list[str]]:
    if not os.path.exists(path):
        return {}
    with open(path, "r") as f:
        return json.load(f)


def get_ability_name(ability: Ability, game: Game, exclude: set[str] = frozenset()) -> str:
    key = ability_key(ability)
    names = load_ability_names(game.ability_names_path).get(key, [])
    candidates = [name for name in names if name not in exclude] or names
    if candidates:
        return random.choice(candidates)

    # No AI fallback here on purpose: it would cost one request per ability.
    print(f"Could not find ability name for {key}")
    return f"{ability.element.name} Strike"


def generate_all_ability_names_to_file(game: Game, path: str, per_key: int = 4):
    ability_name_map = {}
    all_ability_names = set()

    for element in game.elements:
        for cost in [1, 2, 3, 4]:
            ability = Ability(name="Ability", element=element, cost=cost)
            # Generate more names for expensive abilities.
            names = generate_ability_names(ability, game, per_key + cost)
            unique_names = [name for name in names if name not in all_ability_names]
            ability_name_map[ability_key(ability)] = unique_names
            all_ability_names.update(unique_names)

            # Save each step so we don't lose progress if something goes wrong.
            with open(path, "w") as f:
                json.dump(ability_name_map, f, indent=2)


def generate_ability_names(ability: Ability, game: Game, n: int) -> list[str]:
    words = "(single-word names only)" if ability.cost <= 2 else "(max 1-3 words per name)"
    prompt = game.ability_prompt.format(
        n=n,
        power=COST_ADJECTIVES[ability.cost - 1],
        element=ability.element.name,
        words=words,
    )
    response = gpt_client().get_completion(prompt, max_tokens=512, n=n)

    names = []
    for choice in response.choices:
        name = re.sub(r"[^\w\s'!.-]", "", choice.text).strip(" .-")
        if re.search(r"[a-zA-Z]", name):
            names.append(string.capwords(name))

    print(f"Prompt: {prompt}\n")
    print(f"Generated {len(names)} ability names: {names}\n")
    return names


if __name__ == "__main__":
    from games.registry import GAMES, get_game

    parser = argparse.ArgumentParser(description="Regenerate ability names with AI.")
    parser.add_argument("-g", "--game", choices=sorted(GAMES), default="tf2")
    parser.add_argument("-o", "--output", default=None, help="Output JSON path.")
    args = parser.parse_args()
    selected_game = get_game(args.game)
    generate_all_ability_names_to_file(
        selected_game, args.output or f"data/{selected_game.key}/generated_ability_names.json"
    )
