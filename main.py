from ui.main_window import ContactManagerApp
import sys
from PyQt6.QtWidgets import QApplication

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ContactManagerApp()
    window.show()
    sys.exit(app.exec())
    