from collections.abc import Callable
from typing import Iterable

from serialcmd.policy.connect import ConnectPolicy
from serialcmd.serializers import Primitive
from serialcmd.serializers import Serializable
from serialcmd.streams.abc import Stream

_COMMAND_FUNC_MARK = "_command_address"


def command(address: int):
    """Декоратор для маркировки команд"""

    def _wrapper(func: Callable[[Stream], None]):
        setattr(func, _COMMAND_FUNC_MARK, address)
        return func

    return _wrapper


class SlaveProtocol[S: Serializable, P: Serializable]:
    """Протокол связи Slave устройства"""

    def __init__(
            self,
            stream: Stream,
            connect_policy: ConnectPolicy[P, S]
    ) -> None:
        self._stream = stream
        self._connect_policy = connect_policy

        self._commands = self._genCommandTable(self._connect_policy.command_code_primitive)
        self._command_index_max = len(self._commands) - 1

    def begin(self, data: P) -> None:
        """
        Отправить данные инициализации
        @param data: Соответствующий `[T]` пакет данных
        """
        self._connect_policy.startup_serializer.write(self._stream, data)

    def pull(self) -> None:
        """Обработка принимаемых в порт команд от master"""
        command_index = self._connect_policy.command_code_primitive.read(self._stream)

        if command_index > self._command_index_max:
            return

        self._commands[command_index](self._stream)

    def getCommands(self) -> Iterable[str]:
        """Получить человеко читаемый список команд"""
        return map(self._commandFuncToStr, self._commands.items())

    @staticmethod
    def _commandFuncToStr(__x: tuple[bytes, Callable]) -> str:
        address, func = __x
        return f"{address.hex()} -> {func.__name__}"

    def _genCommandTable(self, command_index_primitive: Primitive) -> dict[bytes, Callable[[Stream], None]]:
        ret = dict()

        for attr_name in dir(self):
            command_handler = getattr(self, attr_name)
            address_num = getattr(command_handler, _COMMAND_FUNC_MARK, None)

            if address_num is None:
                continue

            address_bytes = command_index_primitive.pack(address_num)

            if address_bytes in ret.keys():
                raise ValueError(f"{address_bytes.hex()} already used!")

            ret[address_bytes] = command_handler

        return ret
