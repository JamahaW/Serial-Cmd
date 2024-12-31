from dataclasses import dataclass
from threading import Lock
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
    _mutex: Lock
    """Мьютекс для корректной работы команды в многопоточном режиме"""

    def send(self, value: S) -> Result[R, E]:
        """Отправить команду в поток"""
        self._mutex.acquire()
        result = self._command.send(self._stream, value)
        self._mutex.release()
        return result

    def __str__(self) -> str:
        return f"({self._stream}) <-> {self._command}"


class _SupportAddCommands[E: type[ResultEnum], P: Serializable, T: Serializable]:
    """Поддерживает добавление команд"""
    type SerRet[S: Serializable] = Optional[Serializer[S]]

    def addCommand[S: Serializable, R: Serializable](
            self,
            name: str,
            signature: SerRet[S],
            returns: SerRet[R]
    ) -> CommandBind[S, R, E]:
        """
        Добавить команду
        @param name: Наименование команды для отладки
        @param signature: Сигнатура входных аргументов
        @param returns: Возвращаемое значение
        """

    def addSetter[S: Serializable](self, name: str, signature: SerRet[S]) -> CommandBind[S, None, E]:
        """
        Добавить setter-команду
        @param name: Наименование команды для отладки
        @param signature: Сигнатура входных аргументов
        """
        return self.addCommand(f"set_{name}", signature, None)

    def addGetter[R: Serializable](self, name: str, returns: SerRet[R]) -> CommandBind[None, R, E]:
        """
        Добавить getter-команду
        @param name:
        @param returns:
        @return:
        """
        return self.addCommand(f"get_{name}", None, returns)


class MasterProtocol[E: type[ResultEnum], P: Serializable, T: Serializable](_SupportAddCommands[E, P, T]):
    """Протокол - набор команд для последовательной связи"""

    def __init__(self, stream: Stream, connect_policy: ConnectPolicy[P, T], respond_policy: RespondPolicy[E]) -> None:
        self._stream = stream
        self._respond_policy = respond_policy
        self._connect_policy = connect_policy
        self._commands = list[CommandBind]()
        self._mutex = Lock()

    def begin(self) -> T:
        """Начать общение с slave устройством"""
        return self._connect_policy.startup_serializer.read(self._stream)

    def addCommand[S: Serializable, R: Serializable](self, name: str, signature: Optional[Serializer[S]], returns: Optional[Serializer[R]]) -> CommandBind[S, R, E]:
        ret = CommandBind(Command(Instruction(self._getNextInstructionCode(), signature, name), returns, self._respond_policy), self._stream, self._mutex)
        self._commands.append(ret)
        return ret

    def getCommands(self) -> Iterable[CommandBind]:
        """Получить список команд"""
        return self._commands

    def _getNextInstructionCode(self) -> bytes:
        return self._connect_policy.command_code_primitive.pack(len(self._commands))


class SubProtocol[E: type[ResultEnum], P: Serializable, T: Serializable](_SupportAddCommands[E, P, T]):
    """Под протокол"""

    def __init__(self, master: MasterProtocol[E, P, T], sub_name: str) -> None:
        self._master = master
        self._sub_name = sub_name

    def addCommand[S: Serializable, R: Serializable](self, name: str, signature: Optional[Serializer[S]], returns: Optional[Serializer[R]]) -> CommandBind[S, R, E]:
        """Добавить команду в под-протокол"""
        return self._master.addCommand(self._makeName(name), signature, returns)

    def _makeName(self, name: str) -> str:
        return f"{self._sub_name}_{name}"
