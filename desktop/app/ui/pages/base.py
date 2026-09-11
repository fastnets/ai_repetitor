from PySide6.QtCore import Qt
from PySide6.QtWidgets import QScrollArea, QVBoxLayout, QWidget


class ScrollPage(QScrollArea):
    def __init__(self):
        super().__init__()
        self.setWidgetResizable(True)
        self.setFrameShape(QScrollArea.Shape.NoFrame)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.content = QWidget()
        self.layout = QVBoxLayout(self.content)
        self.layout.setContentsMargins(34, 28, 34, 32)
        self.layout.setSpacing(20)
        self.setWidget(self.content)
