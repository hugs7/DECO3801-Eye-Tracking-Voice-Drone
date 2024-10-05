"""
Defines common methods for the GUI
"""

from typing import Optional, Dict, Union, Callable

from PyQt6.QtWidgets import QApplication, QMenu, QPushButton, QLabel, QVBoxLayout
from PyQt6.QtGui import QAction, QPalette
from PyQt6.QtCore import Qt, QTimer

from common import constants as cc

from .logger_helper import init_logger
from .gui_helper import fps_to_ms

logger = init_logger()


class CommonGUI:
    def __init__(self):
        self.layout: Optional[QVBoxLayout] = None
        self.timers: Dict[str, QTimer] = dict()

    def init_palette(self) -> None:
        """Initialise the palette and theme"""
        palette = QApplication.palette()
        # Determine if the theme is dark or light
        self.theme = "dark" if palette.color(QPalette.ColorRole.Window).lightness() < 128 else "light"

        if self.theme == "dark":
            self.text_color = "white"
        else:
            self.text_color = "black"

    def __check_layout(self):
        if self.layout is None:
            raise ValueError("Layout must be set before adding a widget")

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

    def _add_button(self, label: str, callback) -> None:
        """
        Add a button to the main window

        Args:
            label: The label for the button
            callback: The callback function to run when the button is clicked

        Returns:
            None
        """
        self.__check_layout()

        button = QPushButton(label)
        button.clicked.connect(callback)
        self.layout.addWidget(button)

    def _add_label(self, text: str) -> None:
        """
        Add a label to the preferences dialog

        Args:
            text: Label text
        """
        label = QLabel(text)
        self.layout.addWidget(label)

    def _add_label_with_alignment(self, alignment: Qt.AlignmentFlag) -> QLabel:
        """
        Add a label to the preferences dialog

        Args:
            text: Label text

        Returns:
            The label widget
        """
        self.__check_layout()

        label = QLabel(self)
        label.setAlignment(alignment)
        self.layout.addWidget(label)

        return label

    def _configure_timers(self, timers_conf: Dict[str, Dict[str, Union[Callable, int]]]):
        """
        Configure timers given a configuration dictionary.

        Args:
            timers_conf: Configuration dictionary
        """

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
        logger.info(f"Configuring timer: {name}")
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
            logger.error(f"Timer not found: {name}")

        return timer

    def wrap_show(self) -> None:
        """
        Wrapper for showing the current window, raising it to the front
        of the window stack and activating it.
        """

        self.show()
        self.raise_()
        self.activateWindow()
