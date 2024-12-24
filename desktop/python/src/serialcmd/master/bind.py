from dataclasses import dataclass

from serialcmd.core.command import Command
from serialcmd.result import Result
from serialcmd.resultenum import ResultEnum
from serialcmd.serializers import Serializable
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
