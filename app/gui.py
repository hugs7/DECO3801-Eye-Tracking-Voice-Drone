"""
Handles GUI for the application using PyQt5
"""

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QImage, QPixmap
import cv2
import numpy as np

from common.logger_helper import init_logger
import constants as c
from conf_helper import safe_get
from gui_helper import fps_to_ms

logger = init_logger()


class MainApp(QMainWindow):
    def __init__(self, shared_data, stop_event):
        super().__init__()
        self.shared_data = shared_data
        self.stop_event = stop_event

        self.swap_feeds = False

        self.initUI()
        self.setupVideoFeed()

    def initUI(self) -> None:
        """
        Initialises the main window layout

        Returns:
            None
        """

        logger.info("Initialising GUI")

        # Set up the main window layout
        self.setWindowTitle(c.WINDOW_TITLE)

        # Main widget container
        self.main_widget = QWidget(self)
        self.setCentralWidget(self.main_widget)

        self.layout = QVBoxLayout(self.main_widget)

        # Main video feed display
        self.main_video_label = QLabel(self)
        self.main_video_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.main_video_label, 1, 2)  # span 1 row, 2 columns

        # Side video feed display
        self.side_video_label = QLabel(self)
        self.side_video_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.side_video_label, 1, 1)  # span 1 row, 1 column

        # Button to switch video feeds
        self.switch_button = QPushButton("Switch", self)

        # Quit button
        self.quit_button = QPushButton("Quit", self)
        self.quit_button.clicked.connect(self.close_app)
        self.layout.addWidget(self.quit_button)

        # Window size
        logger.info("Configuring window size")
        self.setGeometry(100, 100, 800, 600)
        self.setMinimumSize(c.WIN_MIN_HEIGHT, c.WIN_MIN_WIDTH)

        logger.info("GUI initialised")

    def setupVideoFeed(self) -> None:
        """
        Set up the QTimer to update the video feed at a fixed interval

        Returns:
            None
        """
        logger.info("Initialising video feeds")

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_video_feed)
        self.timer.start(fps_to_ms(30))

    def update_video_feed(self) -> None:
        """
        Update the video feed on the GUI

        Returns:
            None
        """
        main_frame = self.get_webcam_feed()
        small_frame = self.get_webcam_feed()

        if main_frame is not None and small_frame is not None:
            if self.swap_feeds:
                main_frame, small_frame = small_frame, main_frame

            self.set_pixmap(self.main_video_label, main_frame)
            self.set_pixmap(self.side_video_label, small_frame)

    def set_pixmap(self, label: QLabel, frame: np.ndarray) -> None:
        """
        Set the pixmap of the label to the frame

        Args:
            label: The QLabel to update
            frame: The frame to display

        Returns:
            None
        """
        q_img = self.convert_frame_to_qimage(frame)
        label.setPixmap(QPixmap.fromImage(q_img))

    def convert_frame_to_qimage(self, frame: np.ndarray) -> QImage:
        """
        Convert the frame to a QImage

        Args:
            frame: The frame to convert

        Returns:
            QImage: The converted frame
        """

        height, width, channel = frame.shape
        bytes_per_line = 3 * width
        return QImage(frame.data, width, height, bytes_per_line, QImage.Format_RGB888)

    def get_webcam_feed(self) -> np.ndarray:
        """
        Retrieves the webcam feed from the shared data of the eye tracking module.
        Decodes the buffer and returns the frame as a numpy array.

        Returns:
            np.ndarray: The webcam feed as a numpy array
        """
        eye_tracking_data = self.shared_data.eye_tracking
        buffer = safe_get(eye_tracking_data, "video_frame")

        if buffer is None:
            return None

        webcam_frame = self.decode_feed_buffer(buffer)
        return webcam_frame

    def decode_feed_buffer(self, buffer: bytes) -> np.ndarray:
        """
        Decodes the buffer into a numpy array and decodes the frame into an RGB format.

        Args:
            buffer: The buffer to decode

        Returns:
            np.ndarray: The decoded frame
        """
        try:
            nparr = np.frombuffer(buffer, np.uint8)
        except Exception as e:
            logger.error(f"Error decoding buffer: {e}")
            return None

        try:
            video_frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            return cv2.cvtColor(video_frame, cv2.COLOR_BGR2RGB)
        except Exception as e:
            logger.error(f"Error decoding frame: {e}")
            return None

    def close_app(self) -> None:
        """
        Stop the application and signal other threads to stop

        Returns:
            None
        """
        self.stop_event.set()
        self.close()


def run_gui(shared_data, stop_event) -> None:
    """
    Run the GUI application

    Args:
        shared_data: Shared data between threads
        stop_event: Event to signal stop

    Returns:
        None
    """

    app = QApplication(sys.argv)
    main_window = MainApp(shared_data, stop_event)
    main_window.show()
    sys.exit(app.exec_())
