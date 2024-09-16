"""
Defines the options window for the gui
"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QComboBox, QPushButton, QCheckBox, QDialog
from PyQt5.QtCore import Qt


class PreferencesDialog(QDialog):
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

    def _add_button(self, label: str, callback) -> None:
        """
        Add a button to the preferences dialog

        Args:
            label: Button label
            callback: Button callback
        """
        button = QPushButton(label)
        button.clicked.connect(callback)
        self.layout.addWidget(button)

    def _add_label(self, text: str) -> None:
        """
        Add a label to the preferences dialog

        Args:
            text: Label text
        """
        label = QLabel(text)
        self.layout.addWidget(label)
