from __future__ import annotations

from enum import IntEnum


class ResultEnum(IntEnum):
    """Перечисление ошибок"""

    @classmethod
    def getOk(cls) -> ResultEnum:
        """Получить код успешного значения"""
        return cls(0)
