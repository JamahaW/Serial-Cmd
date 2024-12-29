from time import sleep

from examples.servomotor.protocol import ServoMotorMasterProtocol
from examples.servomotor.runner import Runner
from serialcmd.streams.serials import Serial


def _run_test_0(motor_encoder: ServoMotorMasterProtocol) -> None:
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


def _run_test_1(motor_encoder: ServoMotorMasterProtocol) -> None:
    import keyboard

    pos_set: int = 0
    pk = 0.3

    def _clamp(new_val, rg):
        clam = min(rg, max(-rg, new_val))
        return clam

    def _update_target_pos(d: int):
        nonlocal pos_set
        pos_set = _clamp(pos_set + d, 100000)

    def _calc_pid(_in: int) -> int:
        err = pos_set - _in
        u = int(err * pk)
        return u

    while True:

        try:
            sleep(0.05)
            if keyboard.is_pressed("up"):
                _update_target_pos(1000)

            if keyboard.is_pressed("down"):
                _update_target_pos(-1000)

            position = motor_encoder.getEncoderPosition().unwrap()
            speed = motor_encoder.getEncoderSpeed().unwrap()

            new_speed = _calc_pid(position)
            motor_encoder.setMotorSpeed(_clamp(new_speed, 255))

            print(f"\r{position=:.>10} (тик) {speed=:.>5} (тик / мс) {pos_set=:.>10} (тик)", end="")

        except KeyboardInterrupt:
            motor_encoder.setMotorSpeed(0)
            break


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
