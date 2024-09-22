from PyQt6.QtWidgets import *
from designer import Ui_MainWindow

class MainApp (QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.window = QMainWindow()
        self.setupUi(self)
        self.show()