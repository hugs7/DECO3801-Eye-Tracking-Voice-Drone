from ui_starter.main_app import MainApp
from PyQt6.QtWidgets import QApplication
import sys


class App():

    def __init__(self):
        app = QApplication(sys.argv)
        app.setStyle("Fusion")
        self.main_window = MainApp()
        self.main_window.show()
        sys.exit(app.exec())


if __name__ == "__main__":
    app = App()

