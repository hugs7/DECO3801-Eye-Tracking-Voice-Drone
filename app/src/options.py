"""
Defines the options window for the gui
"""

from PyQt6.QtWidgets import QVBoxLayout
from PyQt6.QtCore import QMetaObject

from common.common_dialog import CommonDialog


class PreferencesDialog(CommonDialog):
    def __init__(self):
        super().__init__("Drone Control Preferences", 500, 350)

        self.__init_ui()

    def __init_ui(self):
        # Set window properties
        self.setObjectName("Options")

        # Create layout
        self.layout = QVBoxLayout(self)

        # Create and add buttons to layout
        self.ok_button = self._add_button("OK", self.accept)
        self.cancel_button = self._add_button("Cancel", self.reject)

        self.retranslateUi()
        QMetaObject.connectSlotsByName(self)
