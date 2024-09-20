"""
Local drone GUI. Not used in threading mode.
"""

from typing import Dict, Optional
from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QImage, QPixmap
import numpy as np

from common.logger_helper import init_logger
from common.common_gui import CommonGUI

from . import constants as c
from .controller import Controller

logger = init_logger()


class DroneApp(QMainWindow, CommonGUI):
    """
    Local drone GUI
    """

    def __init__(self, controller: Optional[Controller]):
        """
        Initialises the drone app

        Args:
            controller[Optional[Controller]]: The controller object or None.
            If none, the GUI will run in limited mode.
        """
        super().__init__()

        self.controller = controller
        self.limited_mode = controller is None

        self._init_gui()
        self.update_drone_feed()

    def _init_gui(self) -> None:
        """
        Initialises the GUI window and widgets
        """

        logger.info("Initialising GUI")

        self.setWindowTitle("Drone App")

        self.main_widget = QWidget(self)
        self.setCentralWidget(self.main_widget)

        self.layout = QVBoxLayout()

        self.drone_video_label = QLabel(self)
        self.drone_video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.drone_video_label)

        self.quit_button = QPushButton("Quit", self)
        self.quit_button.clicked.connect(self.quit)
        self.layout.addWidget(self.quit_button)

        self._init_menu()

        # Window size
        logger.info("Configuring window size")
        self.setGeometry(100, 100, 800, 600)
        self.setMinimumSize(c.WIN_MIN_WIDTH, c.WIN_MIN_HEIGHT)

    def _init_menu(self) -> None:
        """
        Initialises the menu bar
        """
        logger.info("Initialising menu bar")

        menu_bar = self.menuBar()
        self.file_menu = menu_bar.addMenu("File")

        self._add_menu_action(self.file_menu, "Quit", self.close_app)

        logger.info("Menu bar initialised")

    def _init_timers(self) -> Dict[str, QTimer]:
        """
        Initialise the timers for the gui

        Returns:
            Dict[str, QTimer]: The timers configuration in an OmegaConf object
        """
        if self.limited_mode:
            logger.info("Running in limited mode. No timers required")
            return {}

        timers_conf = {
            "drone_feed": {"callback": self.update_drone_feed, "fps": self.controller.model.video_fps},
        }

        return {name: self._configure_timer(name, **conf) for name, conf in timers_conf.items()}

    def update_drone_feed(self):
        """
        Updates the video feed
        """
        frame = self.controller.model.read_camera()
        if frame is None:
            logger.trace("No frame returned from camera")
            return

        self._set_pixmap(self.drone_video_label, frame)

    def _set_pixmap(self, label: QLabel, frame: np.ndarray) -> None:
        """
        Set the pixmap of the label to the frame

        Args:
            label: The QLabel to update
            frame: The frame to display

        Returns:
            None
        """
        q_img = self._convert_frame_to_qimage(frame)
        label.setPixmap(QPixmap.fromImage(q_img))

    def _convert_frame_to_qimage(self, frame: np.ndarray) -> QImage:
        """
        Convert the frame to a QImage

        Args:
            frame (np.ndarray): The frame to convert

        Returns:
            QImage: The converted frame
        """

        height, width, channel = frame.shape
        bytes_per_line = 3 * width
        return QImage(frame.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)

    def close_app(self) -> None:
        """
        Stop the GUI and close the app
        """
        logger.info("Closing GUI")
        self.close()
