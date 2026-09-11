from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel

from ..assets import mascot


class Mascot(QLabel):
    def __init__(self, size=72):
        super().__init__()
        self.setPixmap(mascot(size))
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setFixedSize(size, size)
