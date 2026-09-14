#!/usr/bin/env python

import argparse
import random
from pokemon_content.pokemon_collection import PokemonCollection
from pokemon_content.pokemon_elements import PokemonElements
from content.style import Style
from pokemon_content.pokemon_rarity import PokemonRarity

COLLECTION_POKEMON = "pokemon"

def build_collection(collection_name: str):
    style = Style(subject_type="pokemon", style_suffix="--niji")
    return PokemonCollection(
        "pokemon-classic",
        theme_style=style,
        elements=PokemonElements.ALL,
        rarities=PokemonRarity.ALL,
    )


def main():

    argparser = argparse.ArgumentParser()
    argparser.add_argument(
        "-n",
        "--n_monsters",
        type=int,
        default=1,
        help="Number of monsters to generate per element.",
    )

    argparser.add_argument(
        "-e",
        "--element",
        type=str,
        default=None,
        help="Which element to generate cards for.",
    )

    argparser.add_argument(
        "-s",
        "--subject",
        type=str,
        default=None,
        help="Creature type override (e.g. fox, peacock, tiger).",
    )

    args = argparser.parse_args()
    number_of_monsters = args.n_monsters
    subject_override = args.subject
    collection_name = COLLECTION_POKEMON

    current_collection = build_collection(collection_name)

    # Resolve element after the collection is built so we know which elements exist.
    element = None
    if args.element is not None:
        element_name = args.element.lower()
        elements_by_name = {e.name.lower(): e for e in current_collection.elements}
        if element_name not in elements_by_name:
            valid = ", ".join(elements_by_name.keys())
            raise SystemExit(
                f"Unknown element '{args.element}' for collection '{collection_name}'. "
                f"Valid choices: {valid}"
            )
        element = elements_by_name[element_name]

    collection_seed = random.randint(0, 1000000)
    random.seed(collection_seed)
    all_elements = current_collection.elements

    if element is None:
        n_to_generate = number_of_monsters * len(all_elements)
    else:
        n_to_generate = number_of_monsters

    for i in range(n_to_generate):
        current_element = element if element else all_elements[i % len(all_elements)]
        cards = current_collection.generate_random_cards(
            element=current_element, subject_override=subject_override
        )
        print(*cards, sep="\n\n")

    current_collection.export()


if __name__ == "__main__":
    main()
