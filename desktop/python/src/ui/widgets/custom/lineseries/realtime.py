from time import time
from typing import Optional

from ui.widgets.abc import Placeable
from ui.widgets.dpg.impl import Axis
from ui.widgets.dpg.impl import LineSeries


class RealTimeLineSeries(LineSeries):

    def __init__(self, max_points: int = 100) -> None:
        super().__init__()
        self._max_points = max_points
        self._x_buffer = list[float]()
        self._y_buffer = list[float]()
        self._start_time = time()
        self._axis: Optional[Axis] = None

    def setMaxPoints(self, max_points: int) -> None:
        """Установить кол-во точек"""
        self._max_points = max_points

    def addValue(self, value: float) -> None:
        """Добавить в график новое значение"""
        self._x_buffer.append(self._calcRelativeTime())
        self._y_buffer.append(value)

        if len(self._x_buffer) > self._max_points:
            self._x_buffer.pop(0)
            self._y_buffer.pop(0)

        self.update()

    def place(self, parent: Axis = None) -> Placeable:
        self._axis = parent
        return super().place(parent)

    def reset(self) -> None:
        """Сбросить значение графика"""
        self._start_time = time()
        self._x_buffer.clear()
        self._y_buffer.clear()
        self.update()

    def update(self) -> None:
        """Обновить показания графика"""
        if len(self._x_buffer) > 0:
            self._axis.setLimit(self._x_buffer[0], self._x_buffer[-1])

        self.setValue(self.getValue())

    def getValue(self) -> tuple[list[float], list[float]]:
        return self._x_buffer, self._y_buffer

    def _calcRelativeTime(self):
        return time() - self._start_time
