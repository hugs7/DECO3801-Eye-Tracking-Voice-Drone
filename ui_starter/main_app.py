from PyQt6.QtWidgets import *
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtGui import QFontMetrics
from app.src.windows import Window
from main import Ui_MainWindow
from app.src.signals import Signals
from PyQt6 import QtCore, QtGui, QtWidgets
from app.src.signals import Signals
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QProgressBar, QVBoxLayout, QWidget
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QProgressBar, QVBoxLayout, QWidget
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import QTimer, Qt

class MainApp (QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.window = QMainWindow()
        self.setupUi(self)

        self.actionAbout.triggered.connect(self.aboutWindow)
        self.actionOptions.triggered.connect(self.optionsWindow)

        # Event handling from anywhere/anytime
        self.signals = Signals()

        # updateRecentCommand method of this class is called when "updateCommand" event triggered
        self.signals.updateCommand.connect(self.updateRecentCommand)

    
    def resizeEvent(self, event):
        """
        Handles the event where the window gets resized
        """
        # Resize the background image to fit the entire window
        self.droneFeed.setGeometry(0, 0, self.width(), self.height())
        self.droneFeed.setPixmap(self.background.scaled(self.width(), self.height(), Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation))

        # Make sure that centralwidget stays on top of the background
        self.centralwidget.raise_()
        self.signals.resize.emit()

    def aboutWindow(self):
        """
        Handles the event in which 'about' in the file menu is pressed. 
        Currently, this method also triggers the 'updateCommand' event, just to show its usage
        Some references
        https://stackoverflow.com/questions/1807299/open-a-second-window-in-pyqt
        https://pythonpyqt.com/pyqt-events/#:~:text=You%20can%20use%20any%20key,event%20that%20quits%20the%20program.&text=In%20our%20example%2C%20we%20reimplement%20the%20keyPressEvent()%20event%20handler.&text=If%20we%20press%20the%20Esc,the%20keyboard%2C%20the%20application%20terminates.
        """
        dialog = QtWidgets.QDialog()
        dialog.ui = Window()
        dialog.ui.setupUi(dialog, "About text")
        self.signals.updateCommand.emit("Hello")  #Here is how to trigger the "updateCommand" event
        dialog.exec()

    def optionsWindow(self):        
        """
        Handles the event in which 'options' in the file menu is pressed. 
        """
        dialog = QtWidgets.QDialog()
        #Create a new pop-up dialog window
        dialog.ui = Window()
        #Edit options window to say some text
        dialog.ui.setupUi(dialog, "Options text")
        dialog.exec()

    def updateRecentCommand(self, newCommand):
        """
        Updates the recent command at the top, to some given new command

        Args:
            newCommand (string): the new command to be updated to
        """
        self.recentCommand.setText(newCommand)
 