from dataclasses import dataclass
from time import sleep
from typing import BinaryIO
from typing import Final

from serialcmd.streams.abc import Stream


@dataclass
class MockStream(Stream):
    """Реализация-Затычка для тестов"""

    input: BinaryIO
    """Входной поток"""
    output: BinaryIO
    """Выходной поток"""

    BYTE_WAIT_DURATION: Final[int] = 0.001

    # TODO сделать двухстороннюю коммуникацию

    def write(self, data: bytes) -> None:
        self.output.write(data)

    def read(self, size: int = 1) -> bytes:
        ret = bytearray()

        while len(ret) < size:
            chunk = self.input.read(size - len(ret))

            if not chunk:
                sleep(self.BYTE_WAIT_DURATION)

            else:
                ret.extend(chunk)

        return bytes(ret)

    def __str__(self) -> str:
        return f"MockStream@{id(self):x}"


def _test():
    from io import BytesIO
    _in = BytesIO(
        # b"\xAB\xCD\xDE\xFF"
    )
    _out = BytesIO()
    stream = MockStream(_in, _out)

    # stream.write(b"\x12\x34\x56\x78")

    from serialcmd.serializers import Struct
    from serialcmd.serializers import u32
    from serialcmd.serializers import u16
    from serialcmd.serializers import u8

    # stream.write(u32.pack(0x12345678))

    Struct((u32, u16, u8)).write(stream, (
        0x12345678,
        0xABCD,
        0x69
    ))

    # print(_in.getvalue().hex())
    print(_out.getvalue().hex())


if __name__ == '__main__':
    _test()
