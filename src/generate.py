#!/usr/bin/env python3

import argparse
import random

from games.game_collection import GameCollection
from games.registry import GAMES, get_game
from util.gpt_call import gpt_client


def main():
    argparser = argparse.ArgumentParser(
        description="Generate Team Fortress 2 / Counter-Strike trading cards."
    )
    argparser.add_argument(
        "-g",
        "--game",
        choices=sorted(GAMES),
        default="tf2",
        help="Which game to generate cards for.",
    )
    argparser.add_argument(
        "-n",
        "--n-series",
        type=int,
        default=1,
        help="Number of card series to generate per element.",
    )
    argparser.add_argument(
        "-e",
        "--element",
        type=str,
        default=None,
        help="Only generate cards for this element (TF2 class / CS weapon category).",
    )
    argparser.add_argument(
        "-s",
        "--subject",
        type=str,
        default=None,
        help="Character override (e.g. 'pirate captain', 'armored chicken').",
    )
    argparser.add_argument("--seed", type=int, default=None, help="Random seed.")
    argparser.add_argument(
        "--offline",
        action="store_true",
        help="Don't call the AI at all (built-in names and descriptions).",
    )
    argparser.add_argument(
        "--batch-size",
        type=int,
        default=10,
        help="Cards named per AI request (1 request per batch).",
    )

    args = argparser.parse_args()
    game = get_game(args.game)
    collection = GameCollection.for_game(game)

    element = None
    if args.element is not None:
        try:
            element = game.element_by_name(args.element)
        except KeyError as error:
            raise SystemExit(error.args[0])

    random.seed(args.seed if args.seed is not None else random.randint(0, 1000000))
    all_elements = collection.elements
    n_to_generate = args.n_series if element else args.n_series * len(all_elements)

    for i in range(n_to_generate):
        current_element = element if element else all_elements[i % len(all_elements)]
        collection.generate_random_cards(
            element=current_element, subject_override=args.subject
        )

    if args.offline:
        print("Offline mode: using built-in names and descriptions.")
    elif gpt_client().is_openrouter_enabled:
        n_requests = collection.enrich_with_ai(batch_size=max(1, args.batch_size))
        print(f"AI: {n_requests} request(s) for {len(collection.cards)} cards.")

    print(*collection.cards, sep="\n\n")
    collection.export()


if __name__ == "__main__":
    main()
