"""
Defines common methods for the GUI
"""

from typing import Dict, Union, Callable

from PyQt6.QtWidgets import QApplication, QMenu
from PyQt6.QtGui import QAction, QPalette
from PyQt6.QtCore import QTimer

from . import constants as cc
from .common_widgets import CommonWidgets

from .logger_helper import init_logger
from .gui_helper import fps_to_ms

logger = init_logger()


class CommonGUI(CommonWidgets):
    def __init__(self):
        self.timers: Dict[str, QTimer] = dict()
        super().__init__()

    def init_palette(self) -> None:
        """Initialise the palette and theme"""
        palette = QApplication.palette()
        # Determine if the theme is dark or light
        self.theme = cc.DARK_THEME if palette.color(
            QPalette.ColorRole.Window).lightness() < 128 else cc.LIGHT_THEME

        self.font_size = "14px"
        if self.theme == cc.DARK_THEME:
            self.text_color = cc.TEXT_WHITE
            self.surface_color = cc.SURFACE_DARK
        else:
            self.text_color = cc.TEXT_BLACK
            self.surface_color = cc.SURFACE_LIGHT

    def _add_menu_action(self, menu: QMenu, action_name: str, callback: Callable) -> None:
        """
        Add an action to the menu

        Args:
            menu: The menu to add the action to
            action_name: The name of the action
            callback: The callback function to run when the action is triggered

        Returns:
            None
        """

        action = QAction(action_name, self)
        action.triggered.connect(callback)
        menu.addAction(action)

    def _configure_timers(self, timers_conf: Dict[str, Dict[str, Union[Callable, int]]]):
        """
        Configure timers given a configuration dictionary.

        Args:
            timers_conf: Configuration dictionary
        """

        logger.debug("Configuring %d timers", len(timers_conf))
        for timer_name, conf in timers_conf.items():
            if conf.get(cc.THREAD_CALLBACK) is None:
                raise ValueError(f"Timer callback not found: {timer_name}")

            if conf.get(cc.THREAD_FPS) is None:
                raise ValueError(f"Timer fps not found: {timer_name}")

            self._configure_timer(timer_name, **conf)

    def _configure_timer(self, name: str, callback: Callable, fps: int, *args) -> QTimer:
        """
        Configures a QTimer with the given parameters

        Args:
            name: The name of the timer
            callback: The callback function to run
            fps: The frames per second
            *args: Additional arguments for the callback function

        Returns:
            QTimer: The configured QTimer
        """
        logger.debug("Configuring timer: %s", name)
        timer = QTimer(self)
        timer.timeout.connect(lambda: callback(*args))
        timer.start(fps_to_ms(fps))
        self.timers[name] = timer
        return timer

    def _get_timer(self, name: str) -> QTimer:
        """
        Get the timer with the given name

        Args:
            name: The name of the timer

        Returns:
            QTimer: The timer
        """
        timer = self.timers.get(name, None)
        if timer is None:
            logger.error("Timer not found: %s", name)

        return timer

    def _delayed_callback(self, name: str, callback: Callable, delay_ms: int, *args) -> QTimer:
        """
        Configures a QTimer that triggers the callback only once after the delay.

        Args:
            name: The name of the timer
            callback: The callback function to run
            delay_ms: The delay in milliseconds before triggering the callback
            *args: Additional arguments for the callback function

        Returns:
            QTimer: The configured QTimer
        """
        logger.info(
            "Configuring single-shot timer: %s with delay %d", name, delay_ms)

        return QTimer.singleShot(delay_ms, lambda: callback(*args))

    def wrap_show(self) -> None:
        """
        Wrapper for showing the current window, raising it to the front
        of the window stack and activating it.
        """

        self.show()
        self.raise_()
        self.activateWindow()
