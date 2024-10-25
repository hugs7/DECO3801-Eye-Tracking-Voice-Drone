"""
Defines the abouts window for the gui
"""

from PyQt6.QtCore import QMetaObject
from PyQt6.QtWidgets import QHBoxLayout, QSpacerItem, QSizePolicy

from common.common_dialog import CommonDialog


class AboutDialog(CommonDialog):
    def __init__(self):
        super().__init__("About Drone Control", 500, 350)

        self.__init_ui()

    def __init_ui(self):
        if self.window_layout is None:
            return

        self.setObjectName("About")

        button_layout = QHBoxLayout()
        spacer = QSpacerItem(
            40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        button_layout.addItem(spacer)

        self.ok_button = self._add_button("OK", self.accept, button_layout)
        self.cancel_button = self._add_button(
            "Cancel", self.reject, button_layout)

        self.window_layout.addChildLayout(button_layout)

        self.retranslateUi()
        QMetaObject.connectSlotsByName(self)
