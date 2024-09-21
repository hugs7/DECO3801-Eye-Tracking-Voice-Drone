"""
Handles GUI for the application using PyQt6
"""

from typing import Dict, List, Union, Tuple, Optional
from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel, QLineEdit
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QImage, QPixmap, QKeyEvent
import cv2
import numpy as np
from threading import Event, Lock
from omegaconf import OmegaConf
from multiprocessing import Queue as MPQueue
from queue import Queue

from common.logger_helper import init_logger
from common.common_gui import CommonGUI

from options import PreferencesDialog
import constants as c
import utils.file_handler as file_handler


logger = init_logger("DEBUG")


class MainApp(QMainWindow, CommonGUI):
    def __init__(self, stop_event: Event, thread_data: Dict, data_lock: Lock, interprocess_data: Dict):
        super().__init__()
        self.stop_event = stop_event
        self.thread_data = thread_data
        self.data_lock = data_lock
        self.interprocess_data = interprocess_data

        self.config = self._init_config()
        self._init_gui()
        self._init_feed_labels()
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
        self.main_video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.main_video_label)

        # Side video feed display
        self.side_video_label = QLabel(self)
        self.side_video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.side_video_label)

        # Button to switch video feeds
        self.switch_button = QPushButton("Switch", self)
        self.switch_button.clicked.connect(self._switch_feeds)
        self.layout.addWidget(self.switch_button)
        self.switch_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        # Quit button
        self.quit_button = QPushButton("Quit", self)
        self.quit_button.clicked.connect(self.close_app)
        self.layout.addWidget(self.quit_button)
        self.quit_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)

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

    def _init_feed_labels(self) -> None:
        """
        Initialise the labels for the video feeds
        """
        self.drone_video_label = self.main_video_label
        self.webcam_video_label = self.side_video_label

    def _init_timers(self) -> Dict[str, QTimer]:
        """
        Initialise the timers for the gui

        Returns:
            Dict[str, QTimer]: The timers configuration in an OmegaConf object
        """
        timers_conf = {
            "webcam": {"callback": self.get_webcam_feed, "fps": self.config.timers.webcam},
            "drone_feed": {"callback": self.get_drone_feed, "fps": self.config.timers.drone_video},
            "voice_command": {"callback": self.get_next_voice_command, "fps": self.config.timers.voice_command},
        }

        return {name: self._configure_timer(name, **conf) for name, conf in timers_conf.items()}

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

        if key == Qt.Key.Key_Escape or key == Qt.Key.Key_Q:
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
        dialog.exec()

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

        frame_data = np.require(frame, np.uint8, 'C')
        height, width, channel = frame.shape
        bytes_per_line = channel * width
        try:
            return QImage(frame_data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
        except Exception as e:
            logger.error(f"Error converting frame to QImage: {e}")

    def get_video_feed(self, source: str, label: QLabel) -> Optional[cv2.typing.MatLike]:
        """
        Retrieves the video feed from the specified module and updates the corresponding label.

        Args:
            source (str): The key in thread_data to retrieve the video frame from.
            label (QLabel): The label to update with the video feed.

        Returns:
            Optional[cv2.typing.MatLike]: The decoded frame or None if decoding failed
        """
        try:
            data: Dict = self.thread_data[source]
            frame = data.get("video_frame", None)
            if frame is None:
                return None
            
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            self._set_pixmap(label, frame)
        except KeyboardInterrupt:
            logger.critical("Interrupted! Stopping all threads...")
            self.close_app()

    def get_webcam_feed(self) -> Optional[cv2.typing.MatLike]:
        """
        Retrieves the webcam feed from the shared data of the eye tracking module.

        Returns:
            Optional[cv2.typing.MatLike]: The decoded frame or None if decoding failed
        """
        return self.get_video_feed("eye_tracking", self.webcam_video_label)
    
    def get_drone_feed(self) -> Optional[cv2.typing.MatLike]:
        """
        Retrieves the drone feed from the shared data of the drone module.

        Returns:
            Optional[cv2.typing.MatLike]: The decoded frame or None if decoding failed
        """
        return self.get_video_feed("drone", self.drone_video_label)

    def get_next_voice_command(self) -> Optional[List[Dict[str, Union[str, Tuple[str, int]]]]]:
        """
        Gets the voice command from the IPC shared data of the voice control
        module.

        Returns:
            Optional[
                List[Dict[str, 
                          Union[str, 
                                Tuple[str, int]]]]]: A dictionary of the voice as 
                                                     text and parsed command The 
                                                     voice command.
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
            logger.info(f"Next voice command: {next_command["text"]}")

            return next_command

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
