from collections.abc import Callable

from serialcmd.serializers import Primitive
from serialcmd.serializers import Serializable
from serialcmd.serializers import Serializer
from serialcmd.streams.abc import Stream


class Protocol[T: Serializer, P: Serializable]:
    """Протокол связи Slave устройства"""

    def __init__(
            self,
            stream: Stream,
            startup_serializer: Serializer[T],
            command_index_primitive: Primitive[P]
    ) -> None:
        #             commands: Sequence[Callable[[Stream], None]],
        self._stream = stream
        self._startup_serializer = startup_serializer
        self._command_index_primitive: Primitive[P] = command_index_primitive

    def begin(self, data: Serializable[T]) -> None:
        """
        Отправить данные инициализации
        @param data: Соответствующий `[T]` пакет данных
        """
        self._startup_serializer.write(self._stream, data)

    def pull(self) -> None:
        """Обработка принимаемых в порт команд от master"""
        command_index = self._command_index_primitive.read(self._stream)

        if command_index > self._command_index_max:
            return

        self._commands[command_index](self._stream)


def _test():
    from serialcmd.streams.mock import MockStream
    from serialcmd.resultenum import ResultEnum
    from io import BytesIO

    class MyProtocol:
        def __init__(self) -> None:
            self.commands = list[Callable[[Stream], None]]

        @instruction
        def test(self, stream: Stream) -> None:
            pass

    _in = BytesIO()
    _out = BytesIO()
    _stream = MockStream(_in, _out)

    class TestResult(ResultEnum):
        ok = 0x00
        fail = 0x01

    def instruction(func: Callable[[Stream], None]) -> Callable[[object, Stream], None]:

        def wrapper(self: MyProtocol, stream: Stream) -> None:
            if not isinstance(self, MyProtocol):
                raise AttributeError("Объект не имеет атрибута 'commands' типа list")

            return func(self, stream)  # Вызов оригинальной функции

        return wrapper

    class MyProtocol:
        def __init__(self) -> None:
            self.commands: list[Callable[[Stream], None]] = []  # Явное указание типа

        @instruction
        def test(self, stream: Stream) -> None:
            print("Вызван метод test")

        @instruction
        def another_test(self, stream: Stream) -> None:
            print("Вызван метод another_test")

        def yet_another_method(self, stream: Stream) -> None:  # Без декоратора
            print("Вызван метод yet_another_method")

    # Пример использования
    protocol = MyProtocol()
    s = Stream()

    protocol.test(s)
    protocol.another_test(s)
    protocol.yet_another_method(s)  # Этот метод не будет добавлен в commands

    print("Список команд:")
    for cmd in protocol.commands:
        print(cmd.__name__)
        # Если нужно вызвать команды из списка:
        # cmd(protocol, s) # Раскомментируйте, если хотите выполнить команды из списка


if __name__ == '__main__':
    _test()
