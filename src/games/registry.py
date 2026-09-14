from games.cs import CS
from games.game import Game
from games.tf2 import TF2

GAMES: dict[str, Game] = {game.key: game for game in (TF2, CS)}


def get_game(key: str) -> Game:
    if key not in GAMES:
        raise SystemExit(f"Unknown game '{key}'. Valid choices: {', '.join(GAMES)}")
    return GAMES[key]
