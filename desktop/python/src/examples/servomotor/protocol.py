from serialcmd.policy.connect import ConnectPolicy
from serialcmd.policy.respond import RespondPolicy
from serialcmd.protocol.master import MasterProtocol
from serialcmd.resultenum import ResultEnum
from serialcmd.serializers import i16
from serialcmd.serializers import i32
from serialcmd.serializers import u8
from serialcmd.streams.abc import Stream


class ServoMotorResult(ResultEnum):
    ok = 0x00
    fail = 0x01

    @classmethod
    def getOk(cls) -> ResultEnum:
        return cls.ok


# class PIDSubProtocol(SubProtocol):
#
#     def __init__(self, master: MasterProtocol, sub_name: str, primitive: Primitive) -> None:
#         super().__init__(master, sub_name)


class ServoMotorMasterProtocol(MasterProtocol[ServoMotorResult, bool, int]):

    def __init__(self, stream: Stream) -> None:
        super().__init__(
            stream,
            ConnectPolicy(command_code_primitive=u8, startup_serializer=u8),
            RespondPolicy(result_enum=ServoMotorResult, result_primitive=u8)
        )

        self.set_pwm = self.addSetter("pwm", i16)
        self.get_current_pos = self.addCommand("current_pos", None, i32)
