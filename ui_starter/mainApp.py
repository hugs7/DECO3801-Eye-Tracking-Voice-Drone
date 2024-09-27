from PyQt6.QtWidgets import *
from PyQt6 import QtCore, QtGui, QtWidgets
from windows import Window
from main import Ui_MainWindow
from signals import Signals

class MainApp (QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.window = QMainWindow()
        self.setupUi(self)
        # self.show()

        self.actionAbout.triggered.connect(self.aboutWindow)
        self.actionOptions.triggered.connect(self.optionsWindow)

        # Event handling from anywhere/anytime
        self.signals = Signals()
        # updateRecentCommand of this class is called when updateCommand event triggered
        self.signals.updateCommand.connect(self.updateRecentCommand)
    
    def aboutWindow(self):
        """
        Some references
        https://stackoverflow.com/questions/1807299/open-a-second-window-in-pyqt
        https://pythonpyqt.com/pyqt-events/#:~:text=You%20can%20use%20any%20key,event%20that%20quits%20the%20program.&text=In%20our%20example%2C%20we%20reimplement%20the%20keyPressEvent()%20event%20handler.&text=If%20we%20press%20the%20Esc,the%20keyboard%2C%20the%20application%20terminates.
        """
        dialog = QtWidgets.QDialog()
        dialog.ui = Window()
        dialog.ui.setupUi(dialog, "About text")

        self.signals.updateCommand.emit("Hello")  # updateCommand event is triggered

        dialog.exec()

    def optionsWindow(self):
        dialog = QtWidgets.QDialog()
        dialog.ui = Window()
        dialog.ui.setupUi(dialog, "Options text")
        dialog.exec()

    def updateRecentCommand(self, newCommand):
        self.recentCommand.setText(newCommand)
 