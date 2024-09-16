"""
Defines common methods for the GUI
"""

from PyQt5.QtWidgets import QMenu, QAction, QPushButton, QLabel


class CommonGUI:
    def __init__(self):
        self.layout = None

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
        if self.layout is None:
            raise ValueError("Layout must be set before adding a button")

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
