import sys
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtCore import pyqtSignal, QObject
 

class Signals(QObject):
    updateCommand = pyqtSignal(str)
    resize = pyqtSignal()
    