from io import BytesIO

from serialcmd.policy.connect import ConnectPolicy
from serialcmd.policy.respond import RespondPolicy
from serialcmd.protocol.master import MasterProtocol
from serialcmd.protocol.slave import SlaveProtocol
from serialcmd.protocol.slave import command
from serialcmd.result import Result
from serialcmd.resultenum import ResultEnum
from serialcmd.serializers import Struct
from serialcmd.serializers import u8
from serialcmd.streams.abc import Stream
from serialcmd.streams.mock import MockStream


class MyResult(ResultEnum):
    ok = 0x00
    fail = 0x01


class MySlaveProtocol(SlaveProtocol[int, int]):

    @command(0x01)
    def add(self, stream: Stream) -> None:
        a = u8.read(stream)
        b = u8.read(stream)
        ret = a * b

        u8.write(stream, MyResult.ok)
        u8.write(stream, ret)

    @command(0x02)
    def div(self, stream: Stream) -> None:
        a = u8.read(stream)
        b = u8.read(stream)

        if b == 0:
            u8.write(stream, MyResult.fail)
            return

        ret = a / b

        u8.write(stream, MyResult.ok)
        u8.write(stream, ret)


class MyMasterProtocol(MasterProtocol[MyResult, int, int]):
    def __init__(self, stream: Stream, connect_policy: ConnectPolicy):
        super().__init__(stream, connect_policy, RespondPolicy(MyResult, u8))
        self._add = self.addCommand("add", Struct((u8, u8)), u8)
        self._div = self.addCommand("div", Struct((u8, u8)), u8)

    def add(self, a: int, b: int) -> Result[MyResult, int]:
        return self._add.send((a, b))

    def div(self, a: int, b: int) -> Result[MyResult, int]:
        return self._div.send((a, b))


def _slave(slave: SlaveProtocol[int, int]):
    print("\n".join(slave.getCommands()))

    slave.begin(123)

    while True:
        slave.pull()


def _master(master: MyMasterProtocol):
    print("\n".join(map(str, master.getCommands())))

    startup = master.begin()

    print(f"{startup=}")

    print(master.add(2, 3).unwrap())


def _main():
    _master_in___slave_out = BytesIO()
    _master_out__slave__in = BytesIO()

    connect_policy = ConnectPolicy(u8, u8)

    _slave(MySlaveProtocol(MockStream(_master_out__slave__in, _master_in___slave_out), connect_policy))

    print(_master_in___slave_out.getvalue().hex())
    _master_in___slave_out.seek(0)

    _master(MyMasterProtocol(MockStream(_master_in___slave_out, _master_out__slave__in), connect_policy))


_main()
