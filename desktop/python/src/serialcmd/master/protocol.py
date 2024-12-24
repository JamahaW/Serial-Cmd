from typing import Iterable
from typing import Optional

from serialcmd.master.bind import CommandBind
from serialcmd.core.command import Command
from serialcmd.core.instruction import Instruction
from serialcmd.core.respond import RespondPolicy
from serialcmd.resultenum import ResultEnum
from serialcmd.serializers import Primitive
from serialcmd.serializers import Serializable
from serialcmd.serializers import Serializer
from serialcmd.streams.abc import Stream


class Protocol[E: type[ResultEnum], T: Serializable]:
    """Протокол - набор команд для последовательной связи"""

    def __init__(
            self,
            respond_policy:
            RespondPolicy[E],
            command_code_primitive: Primitive,
            stream: Stream,
            startup_package: Serializer[T]
    ) -> None:
        """
        @param respond_policy: Политика обработки ответов
        @param command_code_primitive: Примитивный тип упаковки индексов команд
        @param stream: Стрим (Канал связи)
        """
        self._commands = list[CommandBind]()
        self._respond_policy = respond_policy
        self._command_code_primitive = command_code_primitive
        self._stream = stream
        self._startup_package = startup_package

    def begin(self) -> T:
        """Начать общение с slave устройством"""
        return self._startup_package.read(self._stream)

    def addCommand[S: Serializable, R: Serializable](
            self, name: str,
            signature: Optional[Serializer[S]],
            returns: Optional[Serializer[R]]
    ) -> CommandBind[S, R, E]:
        """
        Добавить команду
        @param name Имя команды для отладки
        @param signature: Сигнатура (типы) входных аргументов
        @param returns: тип выходного значения
        """
        ret = CommandBind(
            Command(Instruction(self._getNextInstructionCode(), signature, name), returns, self._respond_policy),
            self._stream
        )
        self._commands.append(ret)
        return ret

    def getCommands(self) -> Iterable[CommandBind]:
        """Получить список команд"""
        return self._commands

    def _getNextInstructionCode(self) -> bytes:
        return self._command_code_primitive.pack(len(self._commands))


def _test():
    from io import BytesIO
    from serialcmd.streams.mock import MockStream
    from serialcmd.serializers import u8

    class TestError(ResultEnum):
        ok = 0x00
        bad = 0x01

        @classmethod
        def getOk(cls) -> ResultEnum:
            return cls.ok

    _in = BytesIO()
    _out = BytesIO()

    # startup
    u8.write(_in, True)

    # 1
    u8.write(_in, TestError.ok)

    # 2
    u8.write(_in, TestError.ok)

    # 3
    u8.write(_in, TestError.ok)
    u8.write(_in, 255)

    # 4
    u8.write(_in, TestError.ok)
    u8.write(_in, 100)

    _in.seek(0)
    stream = MockStream(_in, _out)

    protocol = Protocol[TestError, bool](RespondPolicy(TestError, u8), u8, stream, u8)

    cmd_1 = protocol.addCommand("cmd_1", None, None)
    cmd_2 = protocol.addCommand("cmd_2", u8, None)
    cmd_3 = protocol.addCommand("cmd_3", None, u8)
    cmd_4 = protocol.addCommand("cmd_4", u8, u8)

    print("\n".join(map(str, protocol.getCommands())))

    startup = protocol.begin()
    print(startup)

    cmd_1.send(None)
    cmd_2.send(0x69)
    print(cmd_3.send(None).unwrap())
    print(cmd_4.send(0xBB).unwrap())

    print(_out.getvalue().hex())
    print(_in.getvalue().hex())

    return


if __name__ == '__main__':
    _test()
