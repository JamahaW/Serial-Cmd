from serialcmd.policy.connect import ConnectPolicy
from serialcmd.policy.respond import RespondPolicy
from serialcmd.protocol.master import MasterProtocol
from serialcmd.result import Result
from serialcmd.resultenum import ResultEnum
from serialcmd.serializers import i16
from serialcmd.serializers import i32
from serialcmd.serializers import i8
from serialcmd.serializers import u8
from serialcmd.streams.abc import Stream


class ServoMotorResult(ResultEnum):
    ok = 0x00
    fail = 0x01

    @classmethod
    def getOk(cls) -> ResultEnum:
        return cls.ok


class ServoMotorMasterProtocol(MasterProtocol[ServoMotorResult, bool, int]):

    def __init__(self, stream: Stream) -> None:
        super().__init__(
            stream,
            ConnectPolicy(command_code_primitive=u8, startup_serializer=u8),
            RespondPolicy(result_enum=ServoMotorResult, result_primitive=u8)
        )

        self._set_motor_speed = self.addCommand("setCommandSpeed", i16, None)
        self._get_encoder_position = self.addCommand("getEncoderPosition", None, i32)
        self._get_encoder_speed = self.addCommand("getEncoderSpeed", None, i8)

    def setMotorSpeed(self, speed: int) -> Result[None, ServoMotorResult]:
        """Установить скорость мотора"""
        return self._set_motor_speed.send(speed)

    def getEncoderPosition(self) -> Result[int, ServoMotorResult]:
        """Запросить положение энкодера"""
        return self._get_encoder_position.send(None)

    def getEncoderSpeed(self) -> Result[int, ServoMotorResult]:
        """Запросить скорость энкодера"""
        return self._get_encoder_speed.send(None)
