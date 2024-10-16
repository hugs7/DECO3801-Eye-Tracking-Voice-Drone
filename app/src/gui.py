"""
Handles GUI for the application using PyQt6
"""

from typing import Dict, List, Union, Tuple, Optional, Any
from threading import Event, Lock
from multiprocessing import Queue as MPQueue

import cv2
import numpy as np
from omegaconf import OmegaConf
from PyQt6.QtWidgets import QMainWindow, QLabel, QVBoxLayout, QWidget
from PyQt6.QtCore import Qt, QRect, QCoreApplication
from PyQt6.QtGui import QImage, QPixmap, QKeyEvent

from common.logger_helper import init_logger
from common.common_gui import CommonGUI
from common import image
from common import constants as cc
from common.PeekableQueue import PeekableQueue
from common import omegaconf_helper as oh

from options import PreferencesDialog
from about import AboutDialog
import constants as c

import utils.file_handler as file_handler


logger = init_logger("DEBUG")


class MainApp(QMainWindow, CommonGUI):
    def __init__(self, stop_event: Event, thread_data: Dict, data_lock: Lock, interprocess_data: Dict):
        self.stop_event = stop_event
        self.thread_data = thread_data
        self.data_lock = data_lock
        self.interprocess_data = interprocess_data

        super().__init__()

        self.config = self._init_config()
        self._init_gui()
        self._init_qpixmaps()
        self._init_timers()
        self._init_queues()

    def _init_gui(self):
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

        self.batteryLabel = QLabel("Battery: 100%", self)
        self.batteryLabel.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.batteryLabel.setStyleSheet("color: green; font-size: 14px;")
        self.batteryLabel.move(self.width() - 120, 10)

    def _init_qpixmaps(self) -> None:
        """
        Initialises qpixmaps for the video feeds.
        """

        self.webcam_pixmap: Optional[QPixmap] = None
        self.drone_pixmap: Optional[QPixmap] = None

    def _init_config(self) -> OmegaConf:
        """
        Initialise the configuration object

        Returns:
            OmegaConf: The configuration object
        """

        logger.info("Initialising configuration")
        configs_folder = file_handler.get_configs_folder()
        gui_config_path = configs_folder / "gui.yaml"

        config = oh.load_or_create_config(
            gui_config_path, c.DEFAULT_GUI_CONFIG)
        logger.info("Configuration initialised")
        return config

    def _init_menu(self) -> None:
        """
        Initialises the menu bar
        """

        logger.info("Initialising menu bar")

        menu_bar = self.menuBar()
        menu_bar.setGeometry(QRect(0, 0, 626, 18))
        self.file_menu = menu_bar.addMenu("File")

        self._add_menu_action(self.file_menu, "Options", self._open_options)
        self.file_menu.addSeparator()
        self._add_menu_action(self.file_menu, "Quit", self.close_app)

        self.help_menu = menu_bar.addMenu("Help")
        self._add_menu_action(self.help_menu, "About", self._open_about)

        self.retranslateUi(self)
        logger.info("Menu bar initialised")

    def _init_timers(self) -> None:
        """
        Initialise the timers for the gui
        """
        self.timers_fps = self.config.timers
        self.callback_delays = self.config.callback_delays
        self.timers = dict()

        timers_conf = {
            "webcam": {cc.THREAD_CALLBACK: self.get_webcam_feed, cc.THREAD_FPS: self.timers_fps.webcam},
            "drone_feed": {cc.THREAD_CALLBACK: self.get_drone_feed, cc.THREAD_FPS: self.timers_fps.drone_video},
            "voice_command": {cc.THREAD_CALLBACK: self.get_next_voice_command, cc.THREAD_FPS: self.timers_fps.voice_command},
            "battery": {cc.THREAD_CALLBACK: self.update_battery, cc.THREAD_FPS: self.timers_fps.battery},
        }

        self._configure_timers(timers_conf)

    def _init_queues(self) -> None:
        """
        Initialise the keyboard queue. Not assigned to any
        particular module since any thread can "subscribe" to this queue.
        """
        with self.data_lock:
            self.thread_data[cc.KEYBOARD_QUEUE] = PeekableQueue()
            self.thread_data[cc.DRONE][cc.COMMAND_QUEUE] = PeekableQueue()

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

    def _position_battery_label(self):
        """
        Position the battery label at the top right of the window
        """
        self.batteryLabel.move(self.width() - 120, 10)

    def resizeEvent(self, event):
        """
        Handles the event where the window gets resized
        """

        self.__resize_drone_frame()
        self._resize_and_position_webcam_label()
        self._position_battery_label()

        return super().resizeEvent(event)

    def retranslateUi(self):
        _translate = QCoreApplication.translate
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
            keyboard_queue: PeekableQueue = self.thread_data[cc.KEYBOARD_QUEUE]
            keyboard_queue.put(key)

        keyboard_mp_queue: MPQueue = self.interprocess_data[cc.KEYBOARD_QUEUE]
        keyboard_mp_queue.put(key)

        logger.info(f"Key {key} added to keyboard queue")

    def _open_options(self) -> None:
        """
        Open the options window
        """
        logger.info("Opening options window")
        options_dialog = PreferencesDialog()
        options_dialog.exec()

    def _open_about(self) -> None:
        """
        Opens the about window
        """
        logger.info("Opening about window")
        about_dialog = AboutDialog()
        about_dialog.exec()

    def _set_pixmap(self, label: QLabel, frame: np.ndarray, retain_label_size: bool = True) -> QPixmap:
        """
        Set the pixmap of the label to the frame

        Args:
            label: The QLabel to update
            frame: The frame to display
            retain_label_size: If true, updated frame will scale to size of label.

        Returns:
            [QPixmap]: Converted qpix map from frame
        """
        q_img = self._convert_frame_to_qimage(frame)
        pixmap = QPixmap.fromImage(q_img)
        if retain_label_size:
            if not label.hasScaledContents():
                logger.warning(
                    "Label %s does not have scaled contents. Setting true", label.objectName())
                label.setScaledContents(True)
            pixmap = pixmap.scaled(label.size(
            ), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)

        label.setPixmap(pixmap)
        return pixmap

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

    def get_video_feed(self, source: str, frame_key: str = cc.VIDEO_FRAME, flip_colours: bool = True) -> Optional[cv2.typing.MatLike]:
        """
        Retrieves the video feed from the specified module.

        Args:
            source (str): The key in thread_data to retrieve the video frame from.
            frame_key (str): The key in the thread data to retrieve the video frame from.
                             Defaults to cc.VIDEO_FRAME.
            flip_colours (bool): Whether to flip the colours of the frame. Defaults to True.

        Returns:
            frame_qpixmap Optional[QPixmap]: Converted qpix map from frame or None
            if it fails to convert.
        """
        try:
            data: Dict = self.thread_data[source]
            frame = data.get(frame_key, None)
            if frame is None:
                return None

            if flip_colours:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        except KeyboardInterrupt:
            logger.critical("Interrupted! Stopping all threads...")
            self.close_app()

        return frame

    def get_webcam_feed(self) -> Optional[cv2.typing.MatLike]:
        """
        Retrieves the webcam feed from the shared data of the eye tracking module.
        """
        webcam_frame = self.get_video_feed(cc.EYE_TRACKING)
        if webcam_frame is None:
            return None

        self._set_pixmap(self.webcam_video_label, webcam_frame)

    def get_drone_feed(self) -> None:
        """
        Retrieves the drone feed from the shared data of the drone module.
        """
        drone_frame = self.get_video_feed(cc.DRONE, flip_colours=False)
        if drone_frame is None:
            return None

        gaze_overlay_frame = self.get_video_feed(
            cc.EYE_TRACKING, cc.GAZE_OVERLAY)
        if gaze_overlay_frame is None:
            out_frame = drone_frame
        else:
            gaze_overlay_frame = image.rescale_frame(
                gaze_overlay_frame, drone_frame.shape)
            out_frame = image.blend_frame(drone_frame, gaze_overlay_frame, 0.5)

        self._set_pixmap(self.drone_video_label, out_frame)

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
            next_command: Dict[str, Any] = command_queue.get()
            command_text = next_command.get(cc.COMMAND_TEXT, None)
            parsed_command: Optional[List[Tuple[str, int]]
                                     ] = next_command.get(cc.PARSED_COMMAND, None)
            logger.info("Next voice command %s with parsed command %s",
                        command_text, parsed_command)

            self._send_voice_command_to_drone(parsed_command)
            self._display_voice_command(command_text)

    def update_battery(self) -> None:
        """
        Updates the battery level of the drone
        """

        logger.debug("Updating battery level")
        drone_data: Dict = self.thread_data[cc.DRONE]
        if cc.FLIGHT_STATISTICS not in drone_data.keys():
            logger.debug("Flight statistics not found")
            return

        flight_statistics: Dict = drone_data[cc.FLIGHT_STATISTICS]
        battery_level = flight_statistics.get(cc.BATTERY, None)
        if battery_level is None:
            logger.debug("Battery level not found")
            return

        battery_text = f"Battery: {battery_level}%"
        logger.info(battery_text)
        self.batteryLabel.setText(battery_text)

    def _send_voice_command_to_drone(self, parsed_command: Optional[List[Tuple[str, int]]]) -> None:
        """
        Sends the voice command to the drone module.

        Args:
            parsed_command (Optional[List[Tuple[str, int]]]): The parsed command to send to the drone.

        Returns:
            None
        """
        if parsed_command is None:
            return

        with self.data_lock:
            drone_cmd_queue: Optional[PeekableQueue] = self.thread_data[cc.DRONE][cc.COMMAND_QUEUE]
            if drone_cmd_queue is None:
                logger.error("Drone command queue not found")
                return

            logger.debug("Adding parsed command to drone command queue")
            drone_cmd_queue.put(parsed_command)

    def _display_voice_command(self, command_text: str) -> None:
        """
        Displays the voice command on the GUI

        Args:
            command_text (str): The voice command text
        """

        # Check for existing timers

        self.recentCommand.setText(command_text)
        delay_ms = self.callback_delays.voice_command
        if delay_ms is None:
            logger.error("Voice command delay not found")
            return

        if delay_ms <= 0:
            logger.warning("Voice command delay is 0 or negative")
            return

        singleshot = self._delayed_callback("clear_voice_command",
                                            self._clear_voice_command, delay_ms)

    def _clear_voice_command(self) -> None:
        """
        Clears the voice command text
        """
        self.recentCommand.setText("")
        logger.debug("Cleared voice command")

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

    def closeEvent(self, event: any) -> None:
        """
        Override close event handler
        """
        self.close_app()

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
