# Form implementation generated from reading ui file '.\ui\main.ui'
#
# Created by: PyQt6 UI code generator 6.7.1
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.

from typing import Optional

from PyQt6 import QtCore
from PyQt6.QtWidgets import QMainWindow, QLabel, QWidget, QVBoxLayout
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt

from common.logger_helper import init_logger

logger = init_logger()


class MainGui(QMainWindow):
    def __init__(self):
        self.timers = dict()

    def _init_gui(self):
        super().__init__()
        self.setObjectName("MainWindow")
        self.resize(635, 523)

        self.drone_video_label = QLabel("drone_feed", self)
        self.drone_video_label.setScaledContents(True)
        self.drone_video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.__resize_drone_frame()

        self.centralwidget = QWidget(self)
        self.setCentralWidget(self.centralwidget)

        self.recentCommand = QLabel("Recent command", self.centralwidget)
        self.recentCommand.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.recentCommand.setStyleSheet("color: red; font-size: 14px;")

        self.webcam_video_label = QLabel("webcam", self.centralwidget)
        self.webcam_video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.webcam_video_label.setScaledContents(True)
        self.webcam_video_label.setStyleSheet("color: red; font-size: 14px;")
        self._resize_and_position_webcam_label()

        self.layout = QVBoxLayout(self.centralwidget)
        self.layout.addWidget(self.recentCommand)
        self.centralwidget.setLayout(self.layout)

        self.drone_video_label.lower()
        self.centralwidget.raise_()

    def _init_qpixmaps(self) -> None:
        """
        Initialises qpixmaps for the video feeds.
        """

        self.webcam_pixmap: Optional[QPixmap] = None
        self.drone_pixmap: Optional[QPixmap] = None

    def _resize_and_position_webcam_label(self):
        """
        Resize and position the webcam label at the bottom center of the window,
        keeping the 16:9 aspect ratio and using 20% of the window's area.
        """
        # Get the current window size
        window_width = self.width()
        window_height = self.height()

        desired_area_fraction = 0.20
        target_area = window_width * window_height * desired_area_fraction

        aspect_ratio = 16 / 9
        target_height = int((target_area / aspect_ratio) ** 0.5)
        target_width = int(target_height * aspect_ratio)

        x_pos = (window_width - target_width) // 2
        y_pos = window_height - target_height - 20

        self.webcam_video_label.setGeometry(
            x_pos, y_pos, target_width, target_height)

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.drone_video_label.setText(
            _translate("MainWindow", "Main drone feed"))
        self.webcam_video_label.setText(_translate("MainWindow", "Video feed"))
        self.recentCommand.setText(_translate("MainWindow", "Recent command"))
        # self.menuFile.setTitle(_translate("MainWindow", "File"))
        # self.menuHelp.setTitle(_translate("MainWindow", "Help"))
        # self.actionNew.setText(_translate("MainWindow", "New "))
        # self.actionOptions.setText(_translate("MainWindow", "Options"))
        # self.actionQuit.setText(_translate("MainWindow", "Quit"))
        # self.actionAbout.setText(_translate("MainWindow", "About"))

    def __resize_drone_frame(self) -> None:
        """Resizes the drone label to the frame size"""
        self.drone_video_label.resize(self.width(), self.height())

    def resizeEvent(self, event):
        """
        Handles the event where the window gets resized
        """

        self.__resize_drone_frame()
        self._resize_and_position_webcam_label()

        return super().resizeEvent(event)
