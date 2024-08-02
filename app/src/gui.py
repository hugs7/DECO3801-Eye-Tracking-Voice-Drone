"""
Handles GUI for the application using PyQt5
"""

from typing import Dict
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel, QMenuBar, QMenu, QAction
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QImage, QPixmap, QKeyEvent
import cv2
import numpy as np
from threading import Event, Lock
from omegaconf import OmegaConf
from multiprocessing import Queue as MPQueue
from queue import Queue

from common.logger_helper import init_logger

from common_gui import CommonGUI
from options import PreferencesDialog

import constants as c
import utils.file_handler as file_handler
from utils.gui_helper import fps_to_ms


logger = init_logger("DEBUG")


class MainApp(QMainWindow, CommonGUI):
    def __init__(self, stop_event: Event, thread_data: Dict, data_lock: Lock, interprocess_data: Dict):
        super().__init__()
        self.stop_event = stop_event
        self.thread_data = thread_data
        self.data_lock = data_lock
        self.interprocess_data = interprocess_data

        self.swap_feeds = False

        self.config = self._init_config()
        self._init_gui()
        self.timers: Dict[str, QTimer] = self._init_timers()
        self._init_keyboard_queue()

    def _init_config(self) -> OmegaConf:
        """
        Initialise the configuration object

        Returns:
            OmegaConf: The configuration object
        """

        logger.info("Initialising configuration")
        configs_folder = file_handler.get_configs_folder()
        gui_config = configs_folder / "gui.yaml"
        if not gui_config.exists():
            raise FileNotFoundError(f"GUI configuration file not found: {gui_config}")

        config = OmegaConf.load(gui_config)
        logger.info("Configuration initialised")

        return config

    def _init_gui(self) -> None:
        """
        Initialises the main window layout
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
        self.layout.addWidget(self.main_video_label)

        # Side video feed display
        self.side_video_label = QLabel(self)
        self.side_video_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.side_video_label)

        # Button to switch video feeds
        self.switch_button = QPushButton("Switch", self)
        self.switch_button.clicked.connect(self._switch_feeds)
        self.layout.addWidget(self.switch_button)

        # Quit button
        self.quit_button = QPushButton("Quit", self)
        self.quit_button.clicked.connect(self.close_app)
        self.layout.addWidget(self.quit_button)

        self._init_menu()

        # Window size
        logger.info("Configuring window size")
        self.setGeometry(100, 100, 800, 600)
        self.setMinimumSize(c.WIN_MIN_HEIGHT, c.WIN_MIN_WIDTH)

        logger.info("GUI initialised")

    def _init_menu(self) -> None:
        """
        Initialises the menu bar
        """

        logger.info("Initialising menu bar")

        menu_bar = self.menuBar()
        self.file_menu = menu_bar.addMenu("File")

        self._add_menu_action(self.file_menu, "Options", self._open_options)
        self.file_menu.addSeparator()
        self._add_menu_action(self.file_menu, "Quit", self.close_app)

        logger.info("Menu bar initialised")

    def _init_timers(self) -> Dict[str, QTimer]:
        """
        Initialise the timers for the gui

        Returns:
            Dict[str, QTimer]: The timers configuration in an OmegaConf object
        """
        timers_conf = {
            "webcam": {"callback": self.update_webcam_feed, "fps": self.config.timers.webcam},
            "voice_command": {"callback": self.get_next_voice_command, "fps": self.config.timers.voice_command},
        }

        return {name: self.__configure_timer(name, **conf) for name, conf in timers_conf.items()}

    def _init_keyboard_queue(self) -> None:
        """
        Initialise the keyboard queue. Not assigned to any
        particular module since any thread can "subscribe" to this queue.
        """
        with self.data_lock:
            self.thread_data["keyboard_queue"] = Queue()

    def get_timer(self, name: str) -> QTimer:
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

    def __configure_timer(self, name: str, callback: callable, fps: int, *args) -> QTimer:
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
        return timer

    def keyPressEvent(self, event: QKeyEvent) -> None:
        """
        Handle key press events

        Args:
            event: The key press event

        Returns:
            None
        """
        key = event.key()
        logger.info(f"Key pressed: {key}")

        if key == Qt.Key_Escape or key == Qt.Key_Q:
            self.close_app()

        # Any other key goes into the keyboard queue
        with self.data_lock:
            logger.debug(f"Adding key to queue: {key}")
            keyboard_queue: Queue = self.thread_data["keyboard_queue"]
            keyboard_queue.put(key)

    def _open_options(self) -> None:
        """
        Open the options window

        Returns:
            None
        """
        logger.info("Opening options window")
        dialog = PreferencesDialog()
        dialog.exec_()

    def update_webcam_feed(self) -> None:
        """
        Update the video feed on the GUI

        Returns:
            None
        """
        try:
            main_frame = self.get_webcam_feed()
            small_frame = self.get_webcam_feed()

            if main_frame is not None and small_frame is not None:
                if self.swap_feeds:
                    main_frame, small_frame = small_frame, main_frame

                self._set_pixmap(self.main_video_label, main_frame)
                self._set_pixmap(self.side_video_label, small_frame)
        except KeyboardInterrupt:
            logger.critical("Interrupted! Stopping all threads...")
            self.close_app()

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
        return QImage(frame.data, width, height, bytes_per_line, QImage.Format_RGB888)

    def get_webcam_feed(self) -> np.ndarray:
        """
        Retrieves the webcam feed from the shared data of the eye tracking module.
        Decodes the buffer and returns the frame as a numpy array.

        Returns:
            np.ndarray: The webcam feed as a numpy array
        """
        eye_tracking_data: Dict = self.thread_data["eye_tracking"]
        buffer = eye_tracking_data.get("video_frame", None)
        if buffer is None:
            return None

        webcam_frame = self._decode_feed_buffer(buffer)
        return webcam_frame

    def get_next_voice_command(self) -> list[tuple[str, int]]:
        """
        Gets the voice command from the IPC shared data of the voice control
        module.

        Returns:
            list(tuple[str, int]): The voice command
        """

        voice_data = self.interprocess_data["voice_control"]
        if not voice_data:
            return None

        command_queue: MPQueue = voice_data.get("command_queue", None)
        if command_queue is None:
            logger.error("Voice command queue not found")
            return None

        if not command_queue.empty():
            logger.info(f"Voice command queue size: {command_queue.qsize()}")
            next_command = command_queue.get()
            logger.info(f"Next voice command: {next_command}")

            return next_command

    def _decode_feed_buffer(self, buffer: bytes) -> np.ndarray:
        """
        Decodes the byte buffer into a numpy array then decodes the frame into an RGB format.

        Args:
            buffer (bytes): The buffer to decode

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

    def _switch_feeds(self) -> None:
        """
        Switch the main and side video feeds

        Returns:
            None
        """
        self.swap_feeds = not self.swap_feeds
        logger.info(f"Swapping feeds: {self.swap_feeds}")

    def _stop_all_timers(self) -> None:
        """
        Stop all timers

        Returns:
            None
        """
        logger.info("Stopping all timers")
        for timer in self.timers.values():
            if timer is None:
                continue

            if timer.isActive():
                logger.debug(f"Stopping timer: {timer}")
                timer.stop()

    def close_app(self) -> None:
        """
        Stop the application and signal other threads to stop

        Returns:
            None
        """
        self._stop_all_timers()

        if not self.stop_event.is_set():
            logger.info("Stopping threads from GUI")
            self.stop_event.set()

        logger.info("Closing GUI")
        self.close()