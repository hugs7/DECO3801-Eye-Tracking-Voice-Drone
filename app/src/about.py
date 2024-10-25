"""
Defines the abouts window for the gui
"""

from PyQt6.QtWidgets import QDialogButtonBox, QVBoxLayout, QLabel,  QDialog
from PyQt6.QtCore import Qt, QMetaObject, QCoreApplication, QRect

from common.common_gui import CommonGUI


class AboutDialog(QDialog, CommonGUI):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("About Drone Control")
        self.setWindowModality(Qt.WindowModality.WindowModal)
        self.setFixedSize(300, 300)

        self.layout = QVBoxLayout()

        self.__init_ui()

    def __init_ui(self):
        self.setObjectName("About")
        self.resize(389, 300)

        self.ok_button = self._add_button("OK", self.accept)
        self.cancel_button = self._add_button("Cancel", self.reject)

        self.retranslateUi()
        QMetaObject.connectSlotsByName(self)

    def retranslateUi(self, ):
        _translate = QCoreApplication.translate
        self.setWindowTitle(_translate("Dialog", "Dialog"))
