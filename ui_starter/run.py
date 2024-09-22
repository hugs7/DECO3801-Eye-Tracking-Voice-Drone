from design_main import MainApp
from PyQt6.QtWidgets import QApplication
import sys

app = QApplication(sys.argv)
app.setStyle('Fusion')
window = MainApp()
sys.exit(app.exec())