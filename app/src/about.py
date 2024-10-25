"""
Defines the abouts window for the gui
"""

from PyQt6.QtCore import QMetaObject

from common.common_dialog import CommonDialog


class AboutDialog(CommonDialog):
    def __init__(self):
        super().__init__("About Drone Control", 300, 300)

        self.__init_ui()

    def __init_ui(self):
        self.setObjectName("About")
        self.resize(389, 300)

        self.ok_button = self._add_button("OK", self.accept)
        self.cancel_button = self._add_button("Cancel", self.reject)

        self.retranslateUi()
        QMetaObject.connectSlotsByName(self)
