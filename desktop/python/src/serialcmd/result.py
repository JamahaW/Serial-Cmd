from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, kw_only=True)
class Result[U, E]:
    """Результат"""

    _value: U = None
    error: E = None

    @classmethod
    def err(cls, error: E) -> Result:
        """Создать результат ошибки"""
        return cls(error=error)

    @classmethod
    def ok(cls, value: U) -> Result:
        """Создать результат ошибки"""
        return cls(_value=value)

    def isErr(self) -> bool:
        """Является ли ошибкой"""
        return self.error is not None

    def isOk(self) -> bool:
        """Является ли значением"""
        return not self.isErr()

    def unwrap(self, default: U = None) -> U:
        """Получить значение или выйти с ошибкой"""
        if self.isOk():
            return self._value

        elif default is None:
            raise ValueError(f"Cannot unwrap an error Result. Error: {self.error}")

        return default
