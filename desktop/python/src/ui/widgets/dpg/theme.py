from __future__ import annotations

import dearpygui.dearpygui as dpg

from ui.widgets.abc import ItemID
from ui.color import Color


class LineSeriesTheme:
    """Реестр тем графиков"""

    __instance: LineSeriesTheme = None

    @classmethod
    def getInstance(cls) -> LineSeriesTheme:
        """Получить экземпляр объекта реестра стилей"""
        if cls.__instance is None:
            cls.__instance = cls()

        return cls.__instance

    def __init__(self) -> None:
        self._themes = dict[tuple[Color, bool]]()

    def get(self, color: Color, *, has_dots: bool = False) -> ItemID:
        """Получить тему для графика"""
        key = (color, has_dots)
        if (ret := self._themes.get(key)) is None:
            ret = self._themes[key] = self._create(color, has_dots)

        return ret

    def _create(self, color: Color, has_dots: bool) -> ItemID:
        return self._createDots(color) if has_dots else self._createLine(color)

    @staticmethod
    def _createDots(color: Color) -> ItemID:
        with dpg.theme() as theme:
            with dpg.theme_component(dpg.mvLineSeries):
                dpg.add_theme_color(dpg.mvPlotCol_Line, color.toTuple(), category=dpg.mvThemeCat_Plots)
                dpg.add_theme_style(dpg.mvPlotStyleVar_Marker, dpg.mvPlotMarker_Circle, category=dpg.mvThemeCat_Plots)
                dpg.add_theme_style(dpg.mvPlotStyleVar_MarkerSize, 3, category=dpg.mvThemeCat_Plots)

        return theme

    @staticmethod
    def _createLine(color: Color) -> ItemID:
        with dpg.theme() as theme:
            with dpg.theme_component(dpg.mvLineSeries):
                dpg.add_theme_color(dpg.mvPlotCol_Line, color.toTuple(), category=dpg.mvThemeCat_Plots)

        return theme
