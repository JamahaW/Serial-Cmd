from time import sleep

from examples.motorencoder import MotorEncoderMasterProtocol
from serialcmd.streams.serials import Serial


def _run(motor_encoder: MotorEncoderMasterProtocol) -> None:
    import keyboard

    pwm_set: int = 0

    def _update_speed(d: int):
        nonlocal pwm_set
        pwm_set = min(255, max(-255, pwm_set + d))
        motor_encoder.setMotorSpeed(pwm_set)

    while True:

        try:
            sleep(0.05)
            if keyboard.is_pressed("up"):
                _update_speed(8)

            if keyboard.is_pressed("down"):
                _update_speed(-8)

            position = motor_encoder.getEncoderPosition().unwrap()
            speed = motor_encoder.getEncoderSpeed().unwrap()
            print(f"\r{position=:.>10} (тик) {speed=:.>5} (тик / мс) {pwm_set=:.>5} (ШИМ)", end="")

        except KeyboardInterrupt:
            motor_encoder.setMotorSpeed(0)
            break


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

    _run(motor_encoder)

    return "Успешное завершение"


if __name__ == '__main__':
    print(_launch())
