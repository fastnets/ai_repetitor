import sys

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from .config import ASSETS_DIR
from .ui.main_window import MainWindow
from .ui.styles.theme import APP_QSS


def main():
    application = QApplication(sys.argv)
    application.setApplicationName("Умный друг")
    application.setOrganizationName("Smart Friend")
    application.setWindowIcon(QIcon(str(ASSETS_DIR / "app.ico")))
    application.setStyleSheet(APP_QSS)
    window = MainWindow()
    window.show()
    sys.exit(application.exec())


if __name__ == "__main__":
    main()
