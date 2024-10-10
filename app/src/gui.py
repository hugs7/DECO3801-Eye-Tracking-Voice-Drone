"""
Handles GUI for the application using PyQt6
"""

from typing import Dict, List, Union, Tuple, Optional
from threading import Event, Lock
from multiprocessing import Queue as MPQueue
from queue import Queue

import cv2
import numpy as np
from omegaconf import OmegaConf
from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel, QDialog
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QImage, QPixmap, QKeyEvent

from common.logger_helper import init_logger
from common.common_gui import CommonGUI
from common import constants as cc

from options import PreferencesDialog
from windows import Window
from gui_signals import GuiSignals
from main_gui import MainGui
import constants as c
import utils.file_handler as file_handler


logger = init_logger("DEBUG")


class MainApp(QMainWindow, CommonGUI, MainGui):
    def __init__(self, stop_event: Event, thread_data: Dict, data_lock: Lock, interprocess_data: Dict):
        super().__init__()
        self.stop_event = stop_event
        self.thread_data = thread_data
        self.data_lock = data_lock
        self.interprocess_data = interprocess_data

        self.config = self._init_config()
        self._init_gui()
        self._init_feed_labels()
        self._init_timers()
        self._init_keyboard_queue()

        self.actionAbout.triggered.connect(self.aboutWindow)
        self.actionOptions.triggered.connect(self.optionsWindow)

        self.signals = GuiSignals()
        self.signals.updateCommand.connect(self.updateRecentCommand)

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
            raise FileNotFoundError(
                f"GUI configuration file not found: {gui_config}")

        config = OmegaConf.load(gui_config)
        logger.info("Configuration initialised")

        return config

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

    def _init_timers(self) -> None:
        """
        Initialise the timers for the gui
        """
        timers_conf = {
            "webcam": {cc.THREAD_CALLBACK: self.get_webcam_feed, cc.THREAD_FPS: self.config.timers.webcam},
            "drone_feed": {cc.THREAD_CALLBACK: self.get_drone_feed, cc.THREAD_FPS: self.config.timers.drone_video},
            "voice_command": {cc.THREAD_CALLBACK: self.get_next_voice_command, cc.THREAD_FPS: self.config.timers.voice_command},
        }

        self._configure_timers(timers_conf)

    def _init_keyboard_queue(self) -> None:
        """
        Initialise the keyboard queue. Not assigned to any
        particular module since any thread can "subscribe" to this queue.
        """
        with self.data_lock:
            self.thread_data[cc.KEYBOARD_QUEUE] = Queue()

    def resizeEvent(self, event):
        """
        Handles the event where the window gets resized
        """
        # Resize the background image to fit the entire window
        self.droneFeed.setGeometry(0, 0, self.width(), self.height())
        self.droneFeed.setPixmap(self.background.scaled(self.width(), self.height(
        ), Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation))

        # Make sure that centralwidget stays on top of the background
        self.centralwidget.raise_()
        self.signals.resize.emit()

    def aboutWindow(self):
        """
        Handles the event in which 'about' in the file menu is pressed. 
        Currently, this method also triggers the 'updateCommand' event, just to show its usage
        Some references
        https://stackoverflow.com/questions/1807299/open-a-second-window-in-pyqt
        https://pythonpyqt.com/pyqt-events/#:~:text=You%20can%20use%20any%20key,event%20that%20quits%20the%20program.&text=In%20our%20example%2C%20we%20reimplement%20the%20keyPressEvent()%20event%20handler.&text=If%20we%20press%20the%20Esc,the%20keyboard%2C%20the%20application%20terminates.
        """
        dialog = QDialog()
        dialog.ui = Window()
        dialog.ui.setupUi(dialog, "About text")
        # Here is how to trigger the "updateCommand" event
        self.signals.updateCommand.emit("Hello")
        dialog.exec()

    def optionsWindow(self):
        """
        Handles the event in which 'options' in the file menu is pressed. 
        """
        dialog = QDialog()
        # Create a new pop-up dialog window
        dialog.ui = Window()
        # Edit options window to say some text
        dialog.ui.setupUi(dialog, "Options text")
        dialog.exec()

    def updateRecentCommand(self, newCommand):
        """
        Updates the recent command at the top, to some given new command

        Args:
            newCommand (string): the new command to be updated to
        """
        self.recentCommand.setText(newCommand)

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

        if key == Qt.Key.Key_Escape:
            self.close_app()

        # Any other key goes into the keyboard queue
        with self.data_lock:
            logger.debug(f"Adding key to queue: {key}")
            keyboard_queue: Queue = self.thread_data[cc.KEYBOARD_QUEUE]
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

        frame_data = np.require(frame, np.uint8, "C")
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
            frame = data.get(cc.VIDEO_FRAME, None)
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
        return self.get_video_feed(cc.EYE_TRACKING, self.webcam_video_label)

    def get_drone_feed(self) -> Optional[cv2.typing.MatLike]:
        """
        Retrieves the drone feed from the shared data of the drone module.

        Returns:
            Optional[cv2.typing.MatLike]: The decoded frame or None if decoding failed
        """
        return self.get_video_feed(cc.DRONE, self.drone_video_label)

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

        voice_data: Dict = self.interprocess_data[cc.VOICE_CONTROL]
        if not voice_data:
            return None

        command_queue: MPQueue = voice_data.get(cc.COMMAND_QUEUE, None)
        if command_queue is None:
            logger.error("Voice command queue not found")
            return None

        if not command_queue.empty():
            queue_size = command_queue.qsize()
            logger.info("Voice command queue size %d", queue_size)
            next_command = command_queue.get()
            command_text = next_command.get(cc.COMMAND_TEXT, None)
            logger.info("Next voice command %s", command_text)

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
            logger.info("Signalling all threads to stop")
            self.stop_event.set()

        logger.info("Closing GUI")
        self.close()
