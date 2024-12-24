from examples.motorencoder import MotorEncoderMasterProtocol
from serialcmd.streams.serials import Serial


def _launch() -> str:
    ports = Serial.getPorts()
    print(f"{ports}")

    if len(ports) == 0:
        return "Нет доступных портов"

    motor_encoder = MotorEncoderMasterProtocol(Serial(ports[0], 115200))

    print("\n".join(map(str, motor_encoder.getCommands())))

    startup = motor_encoder.begin()

    if startup != 0x01:
        return f"Недействительный код инициализации {startup}"

    print(f"Пакет ответа инициализации ведомого устройства: {startup}")


if __name__ == '__main__':
    print(_launch())
