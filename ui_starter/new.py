from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(635, 523)
        self.centralwidget = QtWidgets.QWidget(parent=MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        # Create a layout for the central widget
        self.background_label = QtWidgets.QLabel(self)
        self.background_pixmap = QtWidgets.QPixmap("drone\\assets\\ai_developed_drone_image.webp")
        self.background_label.setPixmap(self.background_pixmap)
        self.background_label.setScaledContents(True)  # Make sure the image scales to fit the window
        self.background_label.setGeometry(0, 0, self.width(), self.height())  # Set the geometry

        self.layout = QtWidgets.QVBoxLayout(self.centralwidget)

        # Create a layout for the frame
        self.frame_layout = QtWidgets.QStackedLayout(self.frame)  # Use QStackedLayout to stack widgets

        # Create the drone feed label and add it to the frame layout
        self.droneFeed = QtWidgets.QLabel(parent=self.frame)
        self.droneFeed.setEnabled(True)
        self.droneFeed.setScaledContents(True)
        self.droneFeed.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.droneFeed.setObjectName("droneFeed")
        self.frame_layout.addWidget(self.droneFeed)

        # Create the command frame for recent commands
        self.command_frame = QtWidgets.QFrame(parent=self.frame)
        self.command_frame.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.command_frame.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.command_frame.setObjectName("command_frame")
        self.command_frame.setGeometry(QtCore.QRect(20, 20, 171, 101))  # Position of the command frame

        # Add the recentCommand label to the command_frame
        self.recentCommand = QtWidgets.QLabel(parent=self.command_frame)
        self.recentCommand.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.recentCommand.setObjectName("recentCommand")

        # Create the video frame for video feed
        self.video_frame = QtWidgets.QFrame(parent=self.frame)
        self.video_frame.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.video_frame.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.video_frame.setObjectName("video_frame")
        self.video_frame.setGeometry(QtCore.QRect(200, 350, 151, 91))  # Position of the video frame

        # Add the videoFeed label to the video_frame
        self.videoFeed = QtWidgets.QLabel(parent=self.video_frame)
        self.videoFeed.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.videoFeed.setObjectName("videoFeed")

        # Set the main frame layout
        self.layout.addWidget(self.frame)

        MainWindow.setCentralWidget(self.centralwidget)

        self.menubar = QtWidgets.QMenuBar(parent=MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 635, 18))
        self.menubar.setObjectName("menubar")
        self.menuile = QtWidgets.QMenu(parent=self.menubar)
        self.menuile.setObjectName("menuile")
        self.menuHelp = QtWidgets.QMenu(parent=self.menubar)
        self.menuHelp.setObjectName("menuHelp")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(parent=MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionHelp = QtGui.QAction(parent=MainWindow)
        self.actionHelp.setObjectName("actionHelp")
        self.actionQuit = QtGui.QAction(parent=MainWindow)
        self.actionQuit.setObjectName("actionQuit")
        self.actionAbout = QtGui.QAction(parent=MainWindow)
        self.actionAbout.setObjectName("actionAbout")
        self.menuile.addAction(self.actionHelp)
        self.menuile.addAction(self.actionQuit)
        self.menuHelp.addAction(self.actionAbout)
        self.menubar.addAction(self.menuile.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.droneFeed.setText(_translate("MainWindow", "Main drone feed"))
        self.recentCommand.setText(_translate("MainWindow", "Recent command"))
        self.videoFeed.setText(_translate("MainWindow", "Video feed"))
        self.menuile.setTitle(_translate("MainWindow", "File"))
        self.menuHelp.setTitle(_translate("MainWindow", "Help"))
        self.actionHelp.setText(_translate("MainWindow", "Options"))
        self.actionQuit.setText(_translate("MainWindow", "Quit"))
        self.actionAbout.setText(_translate("MainWindow", "About"))

