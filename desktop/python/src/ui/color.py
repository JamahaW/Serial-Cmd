from __future__ import annotations


class Color:
    """Цвет"""

    def __init__(self, r: int, g: int, b: int, a: int = 0xFF) -> None:
        self.r, self.g, self.b, self.a = map(lambda x: min(255, max(0, int(x))), (r, g, b, a))

    def toTuple(self) -> tuple[int, int, int, int]:
        """Представить в виде кортежа RGBA"""
        return self.r, self.g, self.b, self.a

    def brighter(self, k: float = 1.5) -> Color:
        """Получить цвет ярче"""
        return self._modify(k)

    def darker(self, k: float = 0.5) -> Color:
        """Получить цвет темнее"""
        return self._modify(k)

    def _modify(self, k: float) -> Color:
        return Color(self.r * k, self.g * k, self.b * k, self.a)

    def __str__(self) -> str:
        return f"#{self.r:X}{self.g:X}{self.b:X}{self.a:X}"

    def _key(self) -> int:
        return self.r | (self.g << 8) | (self.b << 16) | (self.a << 24)

    def __eq__(self, other: Color) -> bool:
        return self._key() == other._key()

    def __hash__(self) -> int:
        return self._key()


DRAG_LINE = Color(0x10, 0x90, 0x90)
WORK_AREA = DRAG_LINE.brighter()
