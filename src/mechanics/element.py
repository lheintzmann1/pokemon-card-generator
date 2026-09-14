from dataclasses import dataclass
import re


@dataclass
class Element:
    name: str
    ascii_color: str = None
    is_neutral: bool = False
    color: str = "#888888"  # Accent color (hex) used by the card templates and icons.

    def with_ascii_color(self, text: str) -> str:
        if self.ascii_color is None:
            return text
        return f"{self.ascii_color}{text}\033[0m"

    def __repr__(self):
        return self.name

    def ascii_name(self):
        return self.with_ascii_color(self.name)

    @property
    def slug(self) -> str:
        """File-system friendly name, e.g. 'Mann Co.' -> 'mann_co'."""
        return re.sub(r"[^a-z0-9]+", "_", self.name.lower()).strip("_")

    def __hash__(self) -> int:
        return hash(self.name)


# Static constant for a Neutral Element (only used for terminal colors).
NEUTRAL = Element("Neutral", is_neutral=True, ascii_color="\033[37m")
