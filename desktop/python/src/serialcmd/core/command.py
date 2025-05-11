from dataclasses import dataclass
from typing import Optional

from serialcmd.core.instruction import Instruction
from serialcmd.policy.respond import RespondPolicy
from serialcmd.result import Result
from serialcmd.resultenum import ResultEnum
from serialcmd.serializers import Serializable
from serialcmd.serializers import Serializer
from serialcmd.streams.abc import Stream


@dataclass(frozen=True)
class Command[S: Serializable, R: Serializable, E: ResultEnum]:
    """Команда (Возвращающая результат инструкция)"""

    instruction: Instruction[S]
    """Инструкция"""
    returns: Optional[Serializer[R]]
    """Возвращаемое значение"""
    respond_policy: RespondPolicy[E]
    """Обработчик ответа"""

    def send(self, stream: Stream, value: S) -> Result[R, E]:
        """Отправить команду в поток и получить ответ"""
        self.instruction.send(stream, value)
        return self.respond_policy.read(stream, self.returns)

    def __str__(self) -> str:
        return f"{self.instruction} -> {self.respond_policy.display(self.returns)}"


def _test():
    from serialcmd.serializers import Struct
    from serialcmd.serializers import f32
    from serialcmd.serializers import u32
    from serialcmd.serializers import u8
    from serialcmd.streams.mock import MockStream
    from io import BytesIO

    class TestErr(ResultEnum):
        ok = 0x00
        bad = 0x69

        @classmethod
        def getOk(cls) -> ResultEnum:
            return cls.ok

    _out = BytesIO()
    _in = BytesIO()

    u8.write(_in, TestErr.ok)
    u32.write(_in, 123456789)
    _in.seek(0)

    stream = MockStream(input=_in, output=_out)

    c = Command[tuple[float, float], int, TestErr](Instruction(b"\xFF", Struct((f32, f32)), "set_motors"), u32, RespondPolicy(TestErr, u8))
    print(c)

    result = c.send(stream, (-12.34, +56.78))

    print(_out.getvalue().hex())

    try:
        print(result.unwrap())

    except ValueError as e:
        print(e)


if __name__ == '__main__':
    _test()
