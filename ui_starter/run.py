from designer import QMainWindow
from PyQt6.QtWidgets import QApplication
import sys

app = QApplication(sys.argv)
app.setStyle("Fusion")
window = QMainWindow()
window.show()
sys.exit(app.exec())
