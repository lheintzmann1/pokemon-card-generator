RGB = tuple[int, int, int]


def hex_to_rgb(value: str | RGB) -> RGB:
    if isinstance(value, tuple):
        return value
    value = value.lstrip("#")
    return tuple(int(value[i : i + 2], 16) for i in (0, 2, 4))


def to_hex(color: str | RGB) -> str:
    r, g, b = hex_to_rgb(color)
    return f"#{r:02X}{g:02X}{b:02X}"


def mix(a: str | RGB, b: str | RGB, t: float) -> RGB:
    a, b = hex_to_rgb(a), hex_to_rgb(b)
    return tuple(round(x + (y - x) * t) for x, y in zip(a, b))


def darken(color: str | RGB, amount: float) -> RGB:
    return mix(color, (0, 0, 0), amount)


def lighten(color: str | RGB, amount: float) -> RGB:
    return mix(color, (255, 255, 255), amount)
