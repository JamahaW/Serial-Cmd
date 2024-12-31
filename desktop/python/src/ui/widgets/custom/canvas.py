import dearpygui.dearpygui as dpg

from ui.widgets.abc import ItemID
from ui.widgets.dpg.impl import Axis
from ui.widgets.dpg.impl import LineSeries
from ui.widgets.dpg.impl import Plot


class Canvas(Plot):

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.axis = Axis(dpg.mvXAxis)

    def placeRaw(self, parent_id: ItemID) -> None:
        super().placeRaw(parent_id)
        self.add(self.axis)

    def addSeries(self, series: LineSeries) -> None:
        """Добавить график"""
        self.axis.add(series)
