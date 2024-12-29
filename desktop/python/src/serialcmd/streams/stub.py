from serialcmd.streams.abc import Stream


class StubStream(Stream):
    """Заглушка"""
    def write(self, data: bytes) -> None:
        pass

    def read(self, size: int = 1) -> bytes:
        return b"\x00"
