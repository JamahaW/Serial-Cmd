from serialcmd.policy.respond import RespondPolicy
from serialcmd.result import Result
from serialcmd.resultenum import ResultEnum
from serialcmd.protocol.master import MasterProtocol
from serialcmd.serializers import i16
from serialcmd.serializers import i32
from serialcmd.serializers import u8
from serialcmd.streams.abc import Stream


class MotorEncoderResult(ResultEnum):
    ok = 0x00
    fail = 0x01

    @classmethod
    def getOk(cls) -> ResultEnum:
        return cls.ok


class MotorEncoderMasterProtocol(MasterProtocol[MotorEncoderResult, bool]):

    def __init__(self, stream: Stream) -> None:
        super().__init__(RespondPolicy(MotorEncoderResult, u8), u8, stream, u8)
        self._set_motor_speed = self.addCommand("set_motor_speed", i16, None)
        self._get_encoder_ticks = self.addCommand("get_encoder_ticks", None, i32)

    def setMotorSpeed(self, speed: int) -> Result[None, MotorEncoderResult]:
        """Установить скорость мотора"""
        return self._set_motor_speed.send(speed)

    def getEncoderTicks(self) -> Result[None, MotorEncoderResult]:
        """Получить положение энкодера"""
        return self._get_encoder_ticks.send(None)
