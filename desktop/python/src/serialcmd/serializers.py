import struct
from abc import ABC
from abc import abstractmethod
from itertools import chain
from typing import Final
from typing import Iterable
from typing import Sequence

from serialcmd.streams.abc import Stream


class _Format:
    I8: Final[str] = "b"
    I16: Final[str] = "h"
    I32: Final[str] = "l"
    I64: Final[str] = "q"

    U8: Final[str] = "B"
    U16: Final[str] = "H"
    U32: Final[str] = "L"
    U64: Final[str] = "Q"

    F32: Final[str] = "f"
    F64: Final[str] = "d"

    @classmethod
    def getSigned(cls) -> Iterable[str]:
        """Все знаковые форматы"""
        return cls.I8, cls.I16, cls.I32, cls.I64

    @classmethod
    def getUnsigned(cls) -> Iterable[str]:
        """Все форматы без знака"""
        return cls.U8, cls.U16, cls.U32, cls.U64

    @classmethod
    def getExponential(cls) -> Iterable[str]:
        """Все экспоненциальные форматы"""
        return cls.F32, cls.F64

    @classmethod
    def getAll(cls) -> Iterable[str]:
        """Все типы"""
        return chain(cls.getExponential(), cls.getSigned(), cls.getUnsigned())

    @classmethod
    def matchPrefix(cls, fmt: str) -> str:
        """Подобрать префикс"""
        match fmt:
            case _ if fmt in cls.getExponential():
                return "f"

            case _ if fmt in cls.getSigned():
                return "i"

            case _ if fmt in cls.getUnsigned():
                return "u"

        raise ValueError(fmt)


_Ser_primitive = int | float | bool
_Ser_struct = tuple[_Ser_primitive, ...]
Serializable = _Ser_primitive | _Ser_struct | None
"""Serializable тип"""


class Serializer[T: Serializable](ABC):
    """Serializer - упаковка, распаковка данных"""

    def __init__(self, _format: str) -> None:
        self._struct = struct.Struct(f"<{_format}")

    @abstractmethod
    def pack(self, value: T) -> bytes:
        """Упаковать значение в соответсвующее байтовое представление"""

    @abstractmethod
    def unpack(self, buffer: bytes) -> T:
        """Получить значение из соответствующего байтового представления"""

    def write(self, stream: Stream, value: T) -> None:
        """Записать значение в стрим"""
        stream.write(self.pack(value))

    def readBytes(self, stream: Stream) -> bytes:
        """Считать размер упаковщика"""
        return stream.read(self.getSize())

    def read(self, stream: Stream) -> T:
        """Считать значение из стрима"""
        return self.unpack(self.readBytes(stream))

    def getSize(self) -> int:
        """Получить размер данных в байтах"""
        return self._struct.size

    def getFormat(self) -> str:
        """Получить спецификатор формата"""
        return self._struct.format.strip("<>")


class Primitive[T: _Ser_primitive](Serializer[T]):
    """Примитивные типы"""

    def pack(self, value: T) -> bytes:
        return self._struct.pack(value)

    def unpack(self, buffer: bytes) -> T:
        return self._struct.unpack(buffer)[0]

    def __str__(self) -> str:
        return f"{_Format.matchPrefix(self.getFormat())}{self.getSize() * 8}"


class Struct(Serializer[_Ser_struct]):
    """Объединение нескольких примитивов"""

    def __init__(self, fields: Sequence[Primitive]) -> None:
        super().__init__(''.join(map(lambda f: f.getFormat(), fields)))
        self._fields = fields

    def unpack(self, buffer: bytes) -> _Ser_struct:
        return self._struct.unpack(buffer)

    def pack(self, fields: _Ser_struct) -> bytes:
        return self._struct.pack(*fields)

    def __str__(self) -> str:
        return f"{{{', '.join(map(str, self._fields))}}}"


u8 = Primitive[int | bool](_Format.U8)
u16 = Primitive[int](_Format.U16)
u32 = Primitive[int](_Format.U32)
u64 = Primitive[int](_Format.U64)

i8 = Primitive[int](_Format.I8)
i16 = Primitive[int](_Format.I16)
i32 = Primitive[int](_Format.I32)
i64 = Primitive[int](_Format.I64)

f32 = Primitive[float](_Format.F32)
f64 = Primitive[float](_Format.F64)


def _test():
    s = Struct((u32, u16, u8))
    s.pack((1, 2, 3))

    print(s)

    r = s.unpack(bytes((0xA4, 0xA3, 0xA2, 0xA1, 0xB2, 0xB1, 0x69,)))  # r: tuple[int, int, int]
    print(r)


if __name__ == '__main__':
    _test()
