"""MarkPad application bootstrap."""
import sys
from PyQt6.QtWidgets import QApplication
from markpad.ui.main_window import MarkPad


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("MarkPad")
    app.setStyle("Fusion")
    window = MarkPad()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
