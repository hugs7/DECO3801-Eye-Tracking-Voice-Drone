"""
Run basic gui
"""

from PyQt6.QtWidgets import QApplication, QMainWindow
import sys


from designer import Ui_MainWindow


class App(QApplication, Ui_MainWindow):

    def __init__(self):
        app = QApplication(sys.argv)
        app.setStyle("Fusion")
        self.main_window = QMainWindow()


if __name__ == "__main__":
    app = App()
    app.main_window.show()
    sys.exit(app.exec())
