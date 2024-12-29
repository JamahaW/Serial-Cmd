from abc import ABC
from abc import abstractmethod

import dearpygui.dearpygui as dpg

type Vec2i = tuple[int, int]


class Application(ABC):
    """Приложение Dear Py Gui"""

    @abstractmethod
    def build(self) -> None:
        """Метод для строительства приложений"""

    def run(self, title: str, resolution: Vec2i) -> None:
        """Запустить приложение"""
        w, h = resolution

        dpg.create_context()
        dpg.create_viewport(title=title, width=w, height=h)

        with dpg.window() as main_window:
            dpg.set_primary_window(main_window, True)
            self.build()

        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.start_dearpygui()
        dpg.destroy_context()
