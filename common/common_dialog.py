"""
Defines common methods for dialogs
"""

from PyQt6.QtWidgets import QVBoxLayout, QDialog
from PyQt6.QtCore import Qt, QCoreApplication

from .logger_helper import init_logger

logger = init_logger()


class CommonDialog(QDialog):
    def __init__(self, title: str, width: int, height: int):
        super().__init__()
        logger.info("Initialising CommonDialog")

        self.setWindowTitle(title)
        self.setWindowModality(Qt.WindowModality.WindowModal)
        self.setFixedSize(width, height)

        self.layout = QVBoxLayout()

    def retranslateUi(self):
        """
        Retranslates the UI to the current language
        """
        _translate = QCoreApplication.translate
        self.setWindowTitle(_translate("Dialog", "Dialog"))
