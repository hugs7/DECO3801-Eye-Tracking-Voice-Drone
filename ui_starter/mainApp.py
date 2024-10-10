from PyQt6.QtWidgets import *
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtGui import QFontMetrics
from windows import Window
from main import Ui_MainWindow
from signals import Signals
from PyQt6 import QtCore, QtGui, QtWidgets
from signals import Signals
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

        # self.central_widget = QWidget(self)
        # self.setCentralWidget(self.central_widget)
        # layout = QVBoxLayout()
        # layout.addWidget(self.recentCommand)
  


        # sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Preferred)
        # layoutGrid = QGridLayout()
        # self.setLayout(layoutGrid)
        # self.droneFeed.setSizePolicy(sizePolicy)
        # self.lay.addWidget(self.droneFeed)
        # self.show()

        self.actionAbout.triggered.connect(self.aboutWindow)
        self.actionOptions.triggered.connect(self.optionsWindow)

        # Event handling from anywhere/anytime
        self.signals = Signals()
        # updateRecentCommand of this class is called when updateCommand event triggered
        self.signals.updateCommand.connect(self.updateRecentCommand)
        self.signals.resize.connect(self.AH)

    
    def resizeEvent(self, event):
               # Resize the background image to fit the entire window
        self.droneFeed.setGeometry(0, 0, self.width(), self.height())
        self.droneFeed.setPixmap(self.background.scaled(self.width(), self.height(), Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation))

        # Make sure that central_widget stays on top of the background
        self.centralwidget.raise_()
        self.signals.resize.emit()

    def AH(self):
        print ("AH")

    
    # def resizeEvent(self, event):
    #     self.signals.resize.emit()
    #     # print("Window has been resized")
    #     # QtWidgets.QMainWindow.resizeEvent(self, event)
    
    # def AH(self):
    #     print (self.contentsRect())
    #     print ("Window has been resized")
    #     coords = self.contentsRect().getCoords()
    #     new_height = coords[3] - self.original_height
    #     new_centre_recent_command = (coords[2] // 2) - (self.recentCommand.geometry().width() // 2)
    #     new_centre_drone = (coords[2] // 2) - (self.droneFeed.geometry().width() // 2)
    #     new_centre_video = (coords[2] // 2) - (self.videoFeed.geometry().width() // 2)
    #     new_centre_progress_bar = (coords[2] // 2) - (self.progressBar.geometry().width() // 2)

    

    #     # self.recentCommand.setGeometry(QtCore.QRect(new_centre_recent_command, 10, 261, 31))
    #     self.recentCommand.setGeometry(new_centre_recent_command, self.recentCommand.geometry().top(), self.recentCommand.geometry().width(), self.recentCommand.geometry().height())
    #     self.droneFeed.setGeometry(new_centre_drone, self.droneFeed.geometry().top(), self.droneFeed.geometry().width(), self.droneFeed.geometry().height())
    #     self.videoFeed.setGeometry(new_centre_video, self.videoFeed.geometry().top(), self.videoFeed.geometry().width(), self.videoFeed.geometry().height())
    #     self.progressBar.setGeometry(new_centre_progress_bar, self.progressBar.geometry().top(), self.progressBar.geometry().width(), self.progressBar.geometry().height())

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
 