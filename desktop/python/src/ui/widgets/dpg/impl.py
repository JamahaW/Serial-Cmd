from __future__ import annotations

from os import PathLike
from pathlib import Path
from typing import Callable
from typing import Iterable
from typing import Sequence

from dearpygui import dearpygui as dpg

Vertices = tuple[Iterable[float], Iterable[float]]

from ui.widgets.abc import Color3i
from ui.widgets.abc import Container
from ui.widgets.abc import ItemID
from ui.widgets.abc import Placeable
from ui.color import DRAG_LINE
from ui.widgets.dpg.abc import DPGItem
from ui.widgets.dpg.abc import RangedDPGItem
from ui.widgets.dpg.abc import VariableDPGItem


class Group(DPGItem, Container, Placeable):
    """Группа элементов"""

    def __init__(self, **kwargs) -> None:
        super().__init__()
        self.__kwargs = kwargs

    def placeRaw(self, parent_id: ItemID) -> None:
        self.setItemID(dpg.add_group(parent=parent_id, **self.__kwargs))
        del self.__kwargs


class CollapsingHeader(Container, DPGItem, Placeable):

    def __init__(self, label: str, *, default_open: bool = False) -> None:
        super().__init__()
        self.__label = label
        self.__default_open = default_open

    def placeRaw(self, parent_id: ItemID) -> None:
        self.setItemID(dpg.add_collapsing_header(label=self.__label, parent=parent_id, default_open=self.__default_open))
        del self.__label
        del self.__default_open


class Menu(Container, DPGItem, Placeable):

    def __init__(self, label: str) -> None:
        super().__init__()
        self.__label = label

    def placeRaw(self, parent_id: ItemID) -> None:
        self.setItemID(dpg.add_menu(label=self.__label, parent=parent_id))
        del self.__label


class Plot(Container, DPGItem, Placeable):

    def placeRaw(self, parent_id: ItemID) -> None:
        with dpg.plot(width=-1, height=-1, equal_aspects=True, anti_aliased=True, parent=parent_id) as plot:
            self.setItemID(plot)
            dpg.add_plot_legend(outside=True)


class Text(VariableDPGItem[str], Placeable):

    def __init__(self, label: str = None) -> None:
        super().__init__()
        self.__label = label

    def placeRaw(self, parent_id: ItemID) -> None:
        self.setItemID(dpg.add_text(self.__label, parent=parent_id))
        del self.__label


class SliderInt[T: (float, int)](Placeable, RangedDPGItem[T]):

    def __init__(self, label: str, on_change: Callable[[T], None] = None, *, value_range: tuple[T, T] = (0, 10), default_value: T = 0):
        super().__init__()
        self.__callback = None if on_change is None else lambda: on_change(self.getValue())
        self.__label = label
        self.__default_value = default_value
        self.__min_value, self.__max_value = value_range

    def placeRaw(self, parent_id: ItemID) -> None:
        self.setItemID(dpg.add_slider_int(label=self.__label, callback=self.__callback, min_value=self.__min_value, max_value=self.__max_value, parent=parent_id, default_value=self.__default_value, ))
        del self.__callback
        del self.__label
        del self.__default_value
        del self.__min_value
        del self.__max_value


class Button(DPGItem, Placeable):

    def __init__(self, label: str, on_click: Callable[[], None]) -> None:
        super().__init__()
        self.__label = label
        self.__callback = lambda: on_click()

    def placeRaw(self, parent_id: ItemID) -> None:
        self.setItemID(dpg.add_button(label=self.__label, callback=self.__callback, parent=parent_id))
        del self.__label
        del self.__callback


class FileDialog(DPGItem):

    def __init__(self, label: str, on_select: Callable[[Sequence[Path]], None], extensions: Iterable[tuple[str, str]], default_path: PathLike) -> None:
        super().__init__()
        self.__label = label
        self.__default_path = default_path

        self._extensions = extensions
        self._on_select = on_select

    def build(self) -> None:
        """Построить"""

        def _callback(_, app_data: dict[str, dict]):
            paths = app_data.get("selections").values()

            if len(paths) == 0:
                return

            self._on_select(tuple(map(Path, paths)))

        with dpg.file_dialog(label=self.__label, callback=_callback, directory_selector=False, show=False, width=900, height=600, default_path=self.__default_path, modal=True) as f:
            self.setItemID(f)

            for extension, text in self._extensions:
                dpg.add_file_extension(f".{extension}", color=(255, 160, 80, 255), custom_text=f"[{text}]")

        del self.__label
        del self.__default_path


class DragLine(VariableDPGItem[float], Placeable):

    def __init__(self, is_vertical: bool, on_change: Callable[[float], None] = None) -> None:
        super().__init__()
        self.__is_vertical = is_vertical
        self.__on_change = None if on_change is None else lambda: on_change(self.getValue())

    def placeRaw(self, parent_id: ItemID) -> None:
        self.setItemID(dpg.add_drag_line(color=DRAG_LINE.toTuple(), vertical=self.__is_vertical, callback=self.__on_change, parent=parent_id))
        del self.__is_vertical
        del self.__on_change


class ChildWindow(Container, DPGItem, Placeable):

    def __init__(self, **kwargs) -> None:
        super().__init__()
        self.__kwargs = kwargs

    def placeRaw(self, parent_id: ItemID) -> None:
        self.setItemID(dpg.add_child_window(**self.__kwargs))
        del self.__kwargs

    def add(self, item: Placeable) -> Container:
        return super().add(item)


class DragPoint(VariableDPGItem[tuple[float, float]], Placeable):
    DEFAULT_COLOR = (0, 0X74, 0xFF)

    def __init__(self, on_move: Callable[[tuple[float, float]], None] = None, *, default_value: tuple[float, float] = (0, 0), label: str = None, color: Color3i = DEFAULT_COLOR, thickness: float = 1.0

                 ):
        super().__init__()

        self.__callback = None if on_move is None else lambda: on_move(self.getValue())
        self.__default_value = default_value
        self.__label = label
        self.__color = color
        self.__thickness = thickness

    def getValue(self) -> tuple[float, float]:
        value = super().getValue()
        x, y, *trash = value
        return x, y

    def setValue(self, value: tuple[float, float]) -> None:
        super().setValue((*value, 0, 0))

    def placeRaw(self, parent_id: ItemID) -> None:
        self.setItemID(dpg.add_drag_point(label=self.__label, parent=parent_id, callback=self.__callback, default_value=self.__default_value, color=self.__color, thickness=self.__thickness))
        del self.__callback
        del self.__default_value,
        del self.__label
        del self.__color,
        del self.__thickness


class Axis(DPGItem, Placeable, Container):

    def __init__(self, axis_type: int) -> None:
        super().__init__()
        self.__type = axis_type

    def placeRaw(self, parent_id: ItemID) -> None:
        self.setItemID(dpg.add_plot_axis(self.__type, parent=parent_id))
        del self.__type


class LineSeries(VariableDPGItem[Vertices], Placeable, Container):

    def __init__(self, label: str = None) -> None:
        super().__init__()
        self.__label = label

    def placeRaw(self, parent_id: ItemID) -> None:
        self.setItemID(dpg.add_line_series(tuple(), tuple(), label=self.__label, parent=parent_id, ))
        del self.__label


class Checkbox(VariableDPGItem[bool], Placeable):

    def __init__(self, on_change: Callable[[bool], None] = None, *, label: str = None, default_value: bool = False):
        super().__init__()

        self.__callback = None if on_change is None else lambda: on_change(self.getValue())
        self.__label = label
        self.__default_value = default_value

    def placeRaw(self, parent_id: ItemID) -> None:
        self.setItemID(dpg.add_checkbox(label=self.__label, parent=parent_id, callback=self.__callback, default_value=self.__default_value))
        del self.__callback
        del self.__label
        del self.__default_value


class Separator(DPGItem, Placeable):

    def placeRaw(self, parent_id: ItemID) -> None:
        self.setItemID(dpg.add_separator(parent=parent_id))

    def __init__(self) -> None:
        super().__init__()


class InputInt(RangedDPGItem[int], Placeable):

    def __init__(
            self,
            label: str,
            on_change: Callable[[int], None] = None,
            *,
            width: int = 100,
            value_range: tuple[int, int] = (0, 100),
            default_value: int = 0,
            step: int = 1,
            step_fast: int = 10
    ) -> None:
        super().__init__()
        self.__label = label
        self.__width = width
        self.__min_value, self.__max_value = value_range
        self.__default_value = default_value
        self.__step = step
        self.__step_fast = step_fast
        self.__callback = None if on_change is None else lambda: on_change(self.getValue())

    def placeRaw(self, parent_id: ItemID) -> None:
        self.setItemID(dpg.add_input_int(
            parent=parent_id,
            step_fast=self.__step_fast,
            label=self.__label,
            width=self.__width,
            min_value=self.__min_value,
            max_value=self.__max_value,
            default_value=self.__default_value,
            step=self.__step,
            callback=self.__callback,
            max_clamped=True,
            min_clamped=True,
        ))
        del self.__label
        del self.__width
        del self.__min_value
        del self.__max_value
        del self.__default_value,
        del self.__step_fast
        del self.__step
        del self.__callback
