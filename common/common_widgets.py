"""
Defines common methods for using widgets in PyQT6
"""

from typing import Optional

from PyQt6.QtWidgets import QPushButton, QLabel, QLayout
from PyQt6.QtCore import Qt

from .logger_helper import init_logger

logger = init_logger()


class CommonWidgets:
    """
    Defines common methods for using widgets in PyQT6
    """

    def __init__(self):
        self.layout: Optional[QLayout] = None

    def _add_button(self, label: str, callback) -> None:
        """
        Add a button to the main window

        Args:
            label: The label for the button
            callback: The callback function to run when the button is clicked

        Returns:
            None
        """
        self.__check_layout()

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

    def _add_label_with_alignment(self, alignment: Qt.AlignmentFlag) -> QLabel:
        """
        Add a label to the preferences dialog

        Args:
            text: Label text

        Returns:
            The label widget
        """
        self.__check_layout()

        label = QLabel(self)
        label.setAlignment(alignment)
        self.layout.addWidget(label)

        return label

    def __check_layout(self):
        if self.layout is None:
            raise ValueError("Layout must be set before adding a widget")
