import os
import sys

# Add the project root to the path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
print("Project root: ", project_root)
sys.path.insert(0, project_root)

from typing import Dict, Union
from threading import Lock, Event

from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QProgressBar, QVBoxLayout, QWidget
from PyQt6.QtGui import QPixmap, QResizeEvent
from PyQt6.QtCore import QTimer, Qt, pyqtSignal

from app.src.utils import file_handler

from common.common_gui import CommonGUI
from common.logger_helper import init_logger


logger = init_logger()


class LoadingGUI(QMainWindow, CommonGUI):
    """
    Loading GUI
    """

    progress_update_signal = pyqtSignal(str, str)

    def __init__(self, loading_shared_data: Dict = None, loading_data_lock: Lock = None, loading_stop_event: Event = None):
        """
        Initialise the loading screen.

        Args (optional):
            loading_shared_data: Shared data between loading screen and main app
            loading_data_lock: Lock for shared data
            loading_stop_event: Stop event for loading screen
        """

        logger.info(">>> LoadingGUI Begin Init")

        super(LoadingGUI, self).__init__()

        required_args = [loading_shared_data, loading_data_lock, loading_stop_event]
        self.running_in_thread = all(required_args)
        if self.running_in_thread:
            if not all(required_args):
                raise ValueError("All or none of the optional arguments must be provided.")

            self.loading_shared_data = loading_shared_data
            self.loading_data_lock = loading_data_lock
            self.loading_stop_event = loading_stop_event

        self.setWindowTitle("Loading Screen")
        self.setGeometry(100, 100, 800, 600)

        self.__init_gui()
        self.timers = self.__init_timers()
        self.progress_update_signal.connect(self.accept_signal)

        logger.info("<<< LoadingGUI End Init")

    def __init_gui(self) -> None:
        """
        Initialise GUI components
        """
        logger.info(">>> LoadingGUI Begin Init GUI")
        self.__init_bg_image()

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        self.__init_messages()
        self.__init_progress_bar()
        self.__init_layout()

        logger.info("<<< LoadingGUI End Init GUI")

    def __init_bg_image(self):
        """Initialise the background image."""
        self.background_label = QLabel(self)
        loading_img_path = file_handler.get_assets_folder() / "ai_developed_drone_image.webp"
        self.background_pixmap = QPixmap(loading_img_path.as_posix())
        self.background_label.setPixmap(self.background_pixmap)
        self.background_label.setScaledContents(True)
        self.background_label.setGeometry(0, 0, self.width(), self.height())

    def __init_messages(self):
        self.title_label = QLabel("Starting...", self.central_widget)
        self.title_label.setStyleSheet("color: black; font-size: 24px;")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.task_label = QLabel("", self.central_widget)
        self.task_label.setStyleSheet("color: black; font-size: 18px;")
        self.task_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def __init_progress_bar(self):
        """Initialise the progress bar."""
        self.progress = 0
        self.progress_bar = QProgressBar(self.central_widget)
        self.progress_bar.setStyleSheet(
            """
            QProgressBar {
                background-color: transparent;
                color: black;
            }
        """
        )
        self.progress_bar.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def __init_layout(self):
        """
        Initialise layout for the loading screen.
        """
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.addWidget(self.title_label)
        self.layout.addWidget(self.task_label)
        self.layout.addWidget(self.progress_bar)
        self.central_widget.setLayout(self.layout)
        self.central_widget.raise_()

    def __init_timers(self) -> Dict[str, QTimer]:
        """
        Initialise timers loading GUI.

        Returns:
            Dict[str, QTimer]: Timers for the loading GUI
        """

        logger.info("Initialising timers")

        timers_conf = dict()

        if self.running_in_thread:
            thread_check = {"callback": self.thread_check, "fps": 30}
            timers_conf["thread_check"] = thread_check

        timers = self._configure_timers(timers_conf)
        logger.info("Timers initialised")
        return timers

    def accept_signal(self, key: str, value: Union[str, int]):
        """
        Event handler for progress update signal.

        Args:
            key: Key to update
            value: Value to update
        """
        match key:
            case "stage":
                self.set_stage(value)
                pass
            case "task":
                self.set_task(value)
                pass
            case "progress":
                progress = int(value)
                self.set_progress(progress)

    def set_stage(self, stage: str) -> None:
        """
        Set the stage of the loading screen.

        Args:
            stage: The stage value
        """
        self.current_stage_name = stage
        self.title_label.setText(stage)

    def set_task(self, task: str) -> None:
        """
        Set the task of the loading screen.

        Args:
            task: The task value
        """
        self.current_task_name = task
        self.task_label.setText(task)

    def set_progress(self, progress: int) -> None:
        """
        Set the progress of the loading screen.

        Args:
            progress: The progress value
        """
        self.progress = progress
        self.progress_bar.setValue(progress)

        logger.info(f"Progress: {self.progress}")
        if self.progress >= 100:
            self.close()

    def thread_check(self):
        """
        Check if the main thread is still alive. Exits the loading
        screen if the main thread is not alive.

        Raises:
            ValueError: If the main thread is not alive
        """
        if not self.running_in_thread:
            raise ValueError("This function should only be called when running in a thread.")

        if self.loading_stop_event.is_set():
            self.close()

    def resizeEvent(self, event: QResizeEvent) -> None:
        """
        Handle resize of the window

        Args:
            event: Resize event
        """
        self.background_label.setGeometry(0, 0, self.width(), self.height())
        self.background_label.setPixmap(
            self.background_pixmap.scaled(
                self.width(), self.height(), Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation
            )
        )

        self.central_widget.raise_()

        return super().resizeEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    loading_screen = LoadingGUI()
    sys.exit(app.exec())
