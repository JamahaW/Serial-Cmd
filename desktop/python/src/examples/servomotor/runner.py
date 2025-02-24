from threading import Thread
from time import sleep

import dearpygui.dearpygui

from examples.servomotor.protocol import ServoMotorMasterProtocol
from ui.application import Application
from ui.widgets.abc import ItemID
from ui.widgets.custom.canvas import Canvas
from ui.widgets.custom.lineseries.realtime import RealTimeLineSeries
from ui.widgets.dpg.impl import InputInt
from ui.widgets.dpg.impl import Tab


class SpeedControllerTab(Tab):

    def __init__(self, protocol: ServoMotorMasterProtocol):
        super().__init__("test")

        self._protocol = protocol

        self._render_thread = Thread(target=self._render)
        self._series = RealTimeLineSeries(max_points=1000)

        self._set_pwm_input = InputInt("setPWM", self._protocol.set_pwm.send, value_range=(-255, 255), step_fast=16, step=4)
        self._update_period_ms_input = InputInt("Update Period (ms)", value_range=(10, 1000), default_value=50, step_fast=50, step=10)

        self._last_pos: int = 0

    def _calcSpeed(self, dt: float) -> float:
        current_speed = self._protocol.get_current_pos.send(None).unwrap(0)
        speed = (current_speed - self._last_pos) / dt
        self._last_pos = current_speed
        return speed

    def _render(self) -> None:
        while True:
            try:
                delta_time_seconds = self._update_period_ms_input.getValue() * 0.001

                self._series.addValue(self._calcSpeed(delta_time_seconds))

                sleep(delta_time_seconds)

            except KeyboardInterrupt:
                break

    def placeRaw(self, parent_id: ItemID) -> None:
        super().placeRaw(parent_id)

        self.add(self._update_period_ms_input)

        self.add(self._set_pwm_input)

        canvas = Canvas(equal_aspects=False)

        self.add(canvas)

        canvas.addSeries(self._series)
        self._render_thread.start()


class Runner(Application):

    def __init__(self, protocol: ServoMotorMasterProtocol) -> None:
        self._speed_pid_tab = SpeedControllerTab(protocol)

    def build(self) -> None:
        with dearpygui.dearpygui.tab_bar():
            self._speed_pid_tab.place()
