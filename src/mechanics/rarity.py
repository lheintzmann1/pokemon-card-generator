from dataclasses import dataclass


@dataclass
class Rarity:
    name: str
    index: int
    color: tuple[int, int, int] = (0, 0, 0)
