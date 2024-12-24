from dataclasses import dataclass
from typing import Iterable
from typing import Optional

from serialcmd.core.command import Command
from serialcmd.core.instruction import Instruction
from serialcmd.policy.connect import ConnectPolicy
from serialcmd.policy.respond import RespondPolicy
from serialcmd.result import Result
from serialcmd.resultenum import ResultEnum
from serialcmd.serializers import Serializable
from serialcmd.serializers import Serializer
from serialcmd.streams.abc import Stream


@dataclass(frozen=True)
class CommandBind[S: Serializable, R: Serializable, E: ResultEnum]:
    """Ассоциированная с потоком Команда"""

    _command: Command[S, R, E]
    """Исполняемая команда"""
    _stream: Stream
    """Привязанный стрим"""

    def send(self, value: S) -> Result[R, E]:
        """Отправить команду в поток"""
        return self._command.send(self._stream, value)

    def __str__(self) -> str:
        return f"({self._stream}) <-> {self._command}"


class MasterProtocol[E: type[ResultEnum], P: Serializable, S: Serializable]:
    """Протокол - набор команд для последовательной связи"""

    def __init__(
            self,
            stream: Stream,
            connect_policy: ConnectPolicy[P, S],
            respond_policy: RespondPolicy[E]
    ) -> None:
        self._stream = stream
        self._respond_policy = respond_policy
        self._connect_policy = connect_policy
        self._commands = list[CommandBind]()

    def begin(self) -> S:
        """Начать общение с slave устройством"""
        return self._connect_policy.startup_serializer.read(self._stream)

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
        ret = CommandBind(Command(Instruction(self._getNextInstructionCode(), signature, name), returns, self._respond_policy), self._stream)
        self._commands.append(ret)
        return ret

    def getCommands(self) -> Iterable[CommandBind]:
        """Получить список команд"""
        return self._commands

    def _getNextInstructionCode(self) -> bytes:
        return self._connect_policy.command_code.pack(len(self._commands))


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

    protocol = MasterProtocol[TestError, bool](RespondPolicy(TestError, u8), u8, stream, u8)

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
