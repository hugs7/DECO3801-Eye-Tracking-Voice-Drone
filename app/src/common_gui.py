"""
Defines common methods for the GUI
"""

from PyQt6.QtWidgets import QMenu, QAction, QPushButton, QLabel
from PyQt6.QtCore import Qt


class CommonGUI:
    def __init__(self):
        self.layout = None

    def __check_layout(self):
        if self.layout is None:
            raise ValueError("Layout must be set before adding a widget")

    def _add_menu_action(self, menu: QMenu, action_name: str, callback: callable) -> None:
        """
        Add an action to the menu

        Args:
            menu: The menu to add the action to
            action_name: The name of the action
            callback: The callback function to run when the action is triggered

        Returns:
            None
        """

        action = QAction(action_name, self)
        action.triggered.connect(callback)
        menu.addAction(action)

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

    def _add_label_with_alignment(self, alignment: Qt.Alignment | Qt.AlignmentFlag) -> QLabel:
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
