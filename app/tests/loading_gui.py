import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QProgressBar, QVBoxLayout, QWidget
from PyQt6.QtGui import QPixmap, QResizeEvent
from PyQt6.QtCore import QTimer, Qt

from ..src.utils import file_handler


class LoadingScreen(QMainWindow):
    """
    Loading GUI
    """

    def __init__(self):
        super(LoadingScreen, self).__init__()

        self.setWindowTitle("Loading Screen")
        self.setGeometry(100, 100, 800, 600)

        self.__init_gui()
        self.__init_timers()

        self.show()

    def __init_gui(self) -> None:
        """
        Initialise GUI components
        """
        self.__init_bg_image()

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        self.__init_messages()
        self.__init_progress_bar()
        self.__init_layout()

    def __init_bg_image(self):
        """Initialize the background image."""
        self.background_label = QLabel(self)
        loading_img_path = file_handler.get_assets_folder() / "ai_developed_drone_image.webp"
        self.background_pixmap = QPixmap(loading_img_path.as_posix())
        self.background_label.setPixmap(self.background_pixmap)
        self.background_label.setScaledContents(True)
        self.background_label.setGeometry(0, 0, self.width(), self.height())

    def __init_messages(self):
        self.message_label = QLabel("Starting...", self.central_widget)
        self.message_label.setStyleSheet("color: black; font-size: 24px;")
        self.message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def __init_progress_bar(self):
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
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.addWidget(self.message_label)
        self.layout.addWidget(self.progress_bar)
        self.central_widget.setLayout(self.layout)
        self.central_widget.raise_()

    def __init_timers(self):
        self.begin_progress()

    def begin_progress(self):
        self.progress = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_progress)
        self.timer.start(500)  # delay for updating progress bar

    def update_progress(self):
        """Update progress bar and display different messages based on progress."""
        self.progress += 2
        self.progress_bar.setValue(self.progress)

        # Update messages based on progress
        if self.progress < 30:
            self.message_label.setText("Initializing...")
        elif self.progress < 60:
            self.message_label.setText("Loading assets...")
        elif self.progress < 90:
            self.message_label.setText("Finalizing setup...")
        else:
            self.message_label.setText("Almost done...")

        if self.progress >= 100:
            self.timer.stop()
            self.close()  # Close the loading screen when complete

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
    loading_screen = LoadingScreen()
    sys.exit(app.exec())
