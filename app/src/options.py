"""
Defines the options window for the gui
"""


from PyQt6.QtWidgets import QDialogButtonBox, QVBoxLayout, QLabel,  QDialog
from PyQt6.QtCore import Qt, QMetaObject, QCoreApplication, QRect

from common.common_dialog import CommonDialog


class PreferencesDialog(CommonDialog):
    def __init__(self):
        super().__init__("Drone Control Preferences", 300, 300)

        self.__init_ui()

    def __init_ui(self):
        self.setObjectName("Options")
        self.resize(389, 300)

        self.ok_button = self._add_button("OK", self.accept)
        self.cancel_button = self._add_button("Cancel", self.reject)

        self.retranslateUi()
        QMetaObject.connectSlotsByName(self)
