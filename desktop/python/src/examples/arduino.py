"""
Пример протокола для базовых функций Ардуино
"""

from serialcmd.core.respond import RespondPolicy
from serialcmd.result import Result
from serialcmd.resultenum import ResultEnum
from serialcmd.master.protocol import Protocol
from serialcmd.serializers import Struct
from serialcmd.serializers import u32
from serialcmd.serializers import u8
from serialcmd.streams.abc import Stream


class ArduinoResult(ResultEnum):
    ok = 0x00
    """Команда выполнена успешно"""

    fail = 0x01
    """Произошла ошибка"""


class ArduinoProtocol(Protocol[ArduinoResult, bool]):
    """Пример подключения к Arduino с минимальным набором команд"""

    def __init__(self, stream: Stream) -> None:
        super().__init__(RespondPolicy(ArduinoResult, u8), u8, stream, u8)
        self._pin_mode = self.addCommand("pinMode", Struct((u8, u8)), None)
        self._digital_write = self.addCommand("digitalWrite", Struct((u8, u8)), None)
        self._digital_read = self.addCommand("digitalRead", u8, u8)
        self._millis = self.addCommand("millis", None, u32)
        self._delay = self.addCommand("delay", u32, None)

    def pinMode(self, pin: int, mode: int) -> Result[None, ArduinoResult]:
        """Установить режим пина"""
        return self._pin_mode.send((pin, mode))

    def digitalWrite(self, pin: int, state: bool) -> Result[None, ArduinoResult]:
        """Установить состояние пина"""
        return self._digital_write.send((pin, state))

    def digitalRead(self, pin: int) -> Result[int, ArduinoResult]:
        """Считать состояние пина"""
        return self._digital_read.send(pin)

    def millis(self) -> Result[int, ArduinoResult]:
        """Получить время на плате в мс"""
        return self._millis.send(None)

    def delay(self, duration_ms: int) -> Result[None, ArduinoResult]:
        """Оставить ведомое устройство ожидать заданное время"""
        return self._delay.send(duration_ms)


INPUT = 0x0
OUTPUT = 0x1
INPUT_PULLUP = 0x2
LED_BUILTIN = 13


def _test() -> str:
    from serialcmd.streams.serials import Serial
    ports = Serial.getPorts()
    print(f"{ports=}")

    if len(ports) == 0:
        return "Нет доступных портов"

    arduino = ArduinoProtocol(Serial(ports[0], 115200))

    # print("\n".join(map(str, arduino.getCommands())))

    startup = arduino.begin()

    if startup != 0x01:
        return f"Недействительный код инициализации {startup=}"

    print(f"Пакет ответа инициализации ведомого устройства: {startup=}")

    #

    arduino.pinMode(LED_BUILTIN, OUTPUT)

    print(f"{arduino.digitalWrite(LED_BUILTIN, True)=}")
    # print(f"{arduino.digitalWrite(100, True)=}")

    # def _blink():
    #     arduino.digitalWrite(LED_BUILTIN, True)
    #     arduino.digitalWrite(LED_BUILTIN, False)
    #
    # def _test():
    #     # arduino.delay(500)
    #
    #     print(arduino.millis())
    #
    #     return
    #
    # def calc(f: Callable[[], None], n: int = 1000) -> float:
    #     return timeit.timeit(f, number=n) / n
    #
    # # t = calc(_blink)
    # t = calc(_test, 10)
    # print(f"{t * 1000.0} ms ({1 / t})")

    return "Успешное завершение"
