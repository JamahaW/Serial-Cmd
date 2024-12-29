from io import StringIO

from ui.widgets.abc import ItemID
from ui.widgets.abc import Placeable
from ui.widgets.dpg.impl import Button
from ui.widgets.dpg.impl import ChildWindow
from ui.widgets.dpg.impl import Text


class LoggerWidget(StringIO, Placeable):

    def __init__(self) -> None:
        super().__init__()
        self._text = Text()
        self._window = ChildWindow()

    def placeRaw(self, parent_id: ItemID) -> None:
        Button("Clear", self.clearLogs).placeRaw(parent_id)
        self._window.placeRaw(parent_id)
        self._window.add(self._text)

    def clearLogs(self) -> None:
        """Очистить лог"""
        self.truncate(0)
        self.seek(0)
        self._text.setValue("")

    def write(self, message: str):
        """Записать и отобразить"""
        ret = super().write(f">>> {message}\n")
        self._text.setValue(self.getvalue())
        return ret
