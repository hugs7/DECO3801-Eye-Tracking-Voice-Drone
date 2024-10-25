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
        self.window_layout: Optional[QLayout] = None

    def _add_button(self, label: str, callback: callable, layout: Optional[QLayout] = None) -> None:
        """
        Add a button to the main window.

        Args:
            label: The label for the button
            callback: The callback function to run when the button is clicked.
            layout: The layout to add the button to. If None, the window layout is used.

        Returns:
            None
        """
        self.__check_layout(layout)

        button = QPushButton(label)
        button.clicked.connect(callback)
        layout.addWidget(button)

    def _add_label(self, text: str, layout: Optional[QLayout] = None) -> None:
        """
        Add a label to the preferences dialog

        Args:
            text: Label text
            layout: The layout to add the label to. If None, the window layout is used.
        """
        use_layout = self.__check_layout(layout)

        label = QLabel(text)
        use_layout.addWidget(label)

    def _add_label_with_alignment(self, alignment: Qt.AlignmentFlag, layout: Optional[QLayout]) -> QLabel:
        """
        Add a label to the preferences dialog

        Args:
            text: Label text
            layout: The layout to add the label to. If None, the window layout is used.

        Returns:
            The label widget
        """
        use_layout = self.__check_layout(layout)

        label = QLabel(self)
        label.setAlignment(alignment)
        use_layout.addWidget(label)

        return label

    def __check_layout(self, layout: Optional[QLayout] = None) -> QLayout:
        """ 
        Check if a layout is set before adding a widget

        Args:
            layout: The layout to check

        Returns:
            The layout to check

        Raises:
            ValueError: If the layout is not set
        """
        if layout is None:
            layout_to_check = self.window_layout
        else:
            layout_to_check = layout

        if layout_to_check is None:
            raise ValueError("Layout must be set before adding a widget")

        return layout_to_check
