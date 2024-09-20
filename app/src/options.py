"""
Defines the options window for the gui
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QComboBox, QPushButton, QCheckBox, QDialog
from PyQt6.QtCore import Qt

from common.common_gui import CommonGUI


class PreferencesDialog(QDialog, CommonGUI):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Drone Control Preferences")
        self.setWindowModality(Qt.ApplicationModal)
        self.setFixedSize(300, 300)

        self.layout = QVBoxLayout()

        self.__init_ui()

    def __init_ui(self) -> None:
        """
        Initialise the UI elements for the preferences dialog
        """

        # === Title ===
        title = QLabel("Preferences")
        title.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(title)

        self.setLayout(self.layout)

        # === Options ===

        # === Gaze Tracking ===

        self._add_label("Gaze Tracking")

        # === Voice Control ===

        self._add_label("Voice Control")

        # === Drone Control ===

        self._add_label("Drone Control")

        # === OK Button ===
        self.ok_button = self._add_button("OK", self.accept)

        # === Cancel Button ===
        self.cancel_button = self._add_button("Cancel", self.reject)
