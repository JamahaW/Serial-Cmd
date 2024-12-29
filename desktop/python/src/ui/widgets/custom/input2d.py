from typing import Callable
from typing import ClassVar
from typing import Optional

from ui.widgets.abc import ItemID
from ui.widgets.abc import VariableItem
from ui.widgets.dpg.impl import Button
from ui.widgets.dpg.impl import Group
from ui.widgets.dpg.impl import InputInt
from ui.widgets.dpg.impl import Separator
from ui.widgets.dpg.impl import Text

type Vec2 = tuple[int, int]


class InputInt2D(Group, VariableItem[Vec2]):
    DEFAULT_RANGE: ClassVar[tuple[int, int]] = (-10000, 10000)

    def __init__(
            self, /,
            label: str,
            on_change: Callable[[Vec2], None] = None,
            *,
            default_value: Vec2 = (0, 0),
            value_range: tuple[int, int] = DEFAULT_RANGE,
            is_horizontal: bool = False,
            x_label: str = "x",
            y_label: str = "y",
            input_width: int = 150,
            step: int = 1,
            step_fast: int = 10,
            reset_button: bool = False,
            reset_button_label: str = "Сброс"
    ) -> None:
        super().__init__(horizontal=is_horizontal)
        self.__label = label
        self._on_change = on_change

        default_x, default_y = self.__default_value = default_value

        self._input_x = InputInt(
            x_label,
            (None if on_change is None else (lambda x: on_change((x, self.getValueY())))),
            width=input_width,
            value_range=value_range,
            default_value=default_x,
            step=step,
            step_fast=step_fast
        )

        self._input_y = InputInt(
            y_label,
            (None if on_change is None else (lambda y: on_change((self.getValueX(), y)))),
            width=input_width,
            value_range=value_range,
            default_value=default_y,
            step=step,
            step_fast=step_fast
        )

        self._reset_button: Optional[Button] = Button(reset_button_label, self.reset) if reset_button else None

    def reset(self) -> None:
        self.setValue(self.__default_value)

    def getValueY(self) -> int:
        return self._input_y.getValue()

    def getValueX(self) -> int:
        return self._input_x.getValue()

    def setValue(self, value: Vec2) -> None:
        x, y = value
        self._on_change(value)
        self._input_x.setValue(x)
        self._input_y.setValue(y)

    def getValue(self) -> Vec2:
        return self.getValueX(), self.getValueY()

    def placeRaw(self, parent_id: ItemID) -> None:
        super().placeRaw(parent_id)
        self.add(Text(self.__label))
        del self.__label

        self.add(self._input_x)
        self.add(self._input_y)

        if self._reset_button is not None:
            self.add(self._reset_button)

        self.add(Separator())
