"""
Run basic gui
"""
# from mainApp import MainApp
# from PyQt6.QtWidgets import QApplication
# import sys

# app = QApplication(sys.argv)
# app.setStyle('Fusion')
# window = MainApp()
# sys.exit(app.exec())


# from mainApp import MainApp
# from PyQt6.QtWidgets import QApplication, QMainWindow
# import sys
# from main import Ui_MainWindow
from mainApp import MainApp
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

