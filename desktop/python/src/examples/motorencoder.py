from serialcmd.core.respond import RespondPolicy
from serialcmd.core.result import Result
from serialcmd.errorenum import ErrorEnum
from serialcmd.protocol import Protocol
from serialcmd.serializers import i16
from serialcmd.serializers import i32
from serialcmd.serializers import u8
from serialcmd.streams.abc import Stream


class MotorEncoderError(ErrorEnum):
    ok = 0x00
    fail = 0x01

    @classmethod
    def getOk(cls) -> ErrorEnum:
        return cls.ok


class MotorEncoderProtocol(Protocol[MotorEncoderError, bool]):

    def __init__(self, stream: Stream) -> None:
        super().__init__(RespondPolicy[MotorEncoderError](MotorEncoderError, u8), u8, stream, u8)
        self._set_motor_speed = self.addCommand("set_motor_speed", i16, None)
        self._get_encoder_ticks = self.addCommand("get_encoder_ticks", None, i32)

    def setMotorSpeed(self, speed: int) -> Result[None, MotorEncoderError]:
        """Установить скорость мотора"""
        return self._set_motor_speed.send(speed)

    def getEncoderTicks(self) -> Result[None, MotorEncoderError]:
        """Получить положение энкодера"""
        return self._get_encoder_ticks.send(None)
