from examples.servomotor.protocol import ServoMotorMasterProtocol
from ui.application import Application
from ui.widgets.dpg.impl import CollapsingHeader


class Runner(Application):

    def __init__(self, protocol: ServoMotorMasterProtocol) -> None:
        self._protocol = protocol

    def build(self) -> None:
        (
            CollapsingHeader("Status", default_open=True).place()
        )


def _test():
    from serialcmd.streams.mock import MockStream
    from io import BytesIO
    Runner(ServoMotorMasterProtocol(MockStream(BytesIO(), BytesIO()))).run("Runner-Test", (1600, 900))


if __name__ == '__main__':
    _test()
