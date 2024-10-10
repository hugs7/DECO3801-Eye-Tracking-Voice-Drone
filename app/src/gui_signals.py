import sys
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtCore import pyqtSignal, QObject
 

class GuiSignals(QObject):
    updateCommand = pyqtSignal(str)
    resize = pyqtSignal()
    