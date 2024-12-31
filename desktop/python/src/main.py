from examples.servomotor.protocol import ServoMotorMasterProtocol
from examples.servomotor.runner import Runner
from serialcmd.streams.serials import Serial


def _launch() -> str:
    ports = Serial.getPorts()
    print(f"{ports}")

    if len(ports) == 0:
        return "Нет доступных портов"

    servomotor = ServoMotorMasterProtocol(Serial(ports[0], 115200))

    print("\n".join(map(str, servomotor.getCommands())))

    startup = servomotor.begin()

    if startup != 0x01:
        return f"Недействительный код инициализации {startup}"

    print(f"Пакет ответа инициализации ведомого устройства: {startup}")

    Runner(servomotor).run("Serial-Cmd", (1600, 900))

    return "Успешное завершение"


if __name__ == '__main__':
    print(_launch())
