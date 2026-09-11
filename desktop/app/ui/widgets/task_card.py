from PySide6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout

from ..assets import icon
from .common import Card


class TaskCard(Card):
    def __init__(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 17, 20, 18)
        layout.setSpacing(7)
        super().__init__(layout, "surface")
        header = QHBoxLayout()
        marker = QLabel()
        marker.setPixmap(icon("textbook").pixmap(24, 24))
        title = QLabel("Текущая задача")
        title.setStyleSheet("font-weight:700; font-size:15px")
        self.source = QLabel("")
        self.source.setObjectName("muted")
        header.addWidget(marker)
        header.addWidget(title)
        header.addStretch()
        header.addWidget(self.source)
        self.text = QLabel("Напиши условие задачи — разберём его вместе.")
        self.text.setWordWrap(True)
        self.text.setStyleSheet("font-size:15px; color:#29304A")
        layout.addLayout(header)
        layout.addWidget(self.text)
        self.setVisible(False)

    def set_task(self, text: str, source: str = ""):
        self.setVisible(bool(text))
        if not text:
            return
        self.text.setText(text)
        self.source.setText(source)
        self.source.setVisible(bool(source))
