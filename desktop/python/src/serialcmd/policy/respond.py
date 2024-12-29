from dataclasses import dataclass
from typing import Optional

from serialcmd.result import Result
from serialcmd.resultenum import ResultEnum
from serialcmd.serializers import Primitive
from serialcmd.serializers import Serializable
from serialcmd.serializers import Serializer
from serialcmd.streams.abc import Stream


@dataclass(frozen=True, kw_only=True)
class RespondPolicy[E: ResultEnum]:
    """Политика обработки ответа"""

    result_enum: type[E]
    """enum-класс ошибок (коды результата)"""

    result_primitive: Primitive
    """примитивный тип"""

    def read[R: Optional[Serializable]](self, stream: Stream, returns: Optional[Serializer[R]]) -> Result[R, E]:
        """Считать результат с потока (получить ответ)"""
        code = self.result_enum(self.result_primitive.read(stream))

        if code != self.result_enum.getOk():
            return Result.err(code)

        if returns is None:
            return Result.ok(None)

        return Result.ok(returns.read(stream))

    def toStr(self, ret: Serializer) -> str:
        """Получить строковое представление для отладки"""
        return f"({ret}, {self.result_enum.__name__}<{self.result_primitive}>)"


def _test():
    from serialcmd.streams.mock import MockStream
    from serialcmd.serializers import u8
    from serialcmd.serializers import u16
    from io import BytesIO

    class TestResult(ResultEnum):
        ok = 0x69
        bad = 0x42

        @classmethod
        def getOk(cls) -> ResultEnum:
            return cls.ok

    stream = MockStream(input=BytesIO(b"\x69\x39\x30"), output=BytesIO())
    responder = RespondPolicy(TestResult, u8)

    result = responder.read(stream, u16)

    try:
        print(f"{result.isOk()=}, {result.isErr()=}, {result.unwrap()=}")

    except ValueError as e:
        print(e)

    return


if __name__ == '__main__':
    _test()
