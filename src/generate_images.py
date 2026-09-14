#!/usr/bin/env python3

import argparse
import io
import json
import pathlib
import random
import time

from PIL import Image

from games.registry import GAMES, get_game
from util.image_gen import PROVIDERS, ImageGenerationError, clean_prompt, generate_image


def generate_collection_images(
    collection_path: str | pathlib.Path,
    provider: str = "pollinations",
    force: bool = False,
    delay: float = 2.0,
) -> int:
    """Generates the artwork of every card that has no image yet. Returns the count."""
    collection_path = pathlib.Path(collection_path)
    images_path = collection_path / "images"
    images_path.mkdir(parents=True, exist_ok=True)

    created = 0
    for card_path in sorted((collection_path / "cards").glob("*.json")):
        data = json.loads(card_path.read_text())
        target = images_path / data["image_file"]
        if target.exists() and not force:
            print(f"Skipping {data['name']}: {target.name} already exists.")
            continue

        prompt = clean_prompt(data["image_prompt"])
        print(f"[{provider}] {data['name']}: {prompt}")
        try:
            raw_image = generate_image(provider, prompt, seed=random.randint(0, 2**31 - 1))
        except ImageGenerationError as error:
            print(f"\033[91m [ERROR] {data['name']}: {error}\033[0m")
            continue

        Image.open(io.BytesIO(raw_image)).convert("RGB").save(target)
        created += 1
        if delay:
            time.sleep(delay)  # Be gentle with free rate limits.

    print(f"Generated {created} image(s) in {images_path}")
    return created


def main():
    argparser = argparse.ArgumentParser(description="Generate the card artwork from the image prompts.")
    argparser.add_argument("-g", "--game", choices=sorted(GAMES), default="tf2")
    argparser.add_argument(
        "--collection",
        default=None,
        help="Path to the collection folder (default: output/<game collection>).",
    )
    argparser.add_argument("-p", "--provider", choices=sorted(PROVIDERS), default="pollinations")
    argparser.add_argument("--force", action="store_true", help="Regenerate existing images.")
    argparser.add_argument("--delay", type=float, default=2.0, help="Seconds between requests.")
    args = argparser.parse_args()

    collection_path = args.collection or f"output/{get_game(args.game).collection_name}"
    generate_collection_images(collection_path, args.provider, args.force, args.delay)


if __name__ == "__main__":
    main()
