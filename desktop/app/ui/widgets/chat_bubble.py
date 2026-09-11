import html

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QSizePolicy, QVBoxLayout, QWidget

from .mascot import Mascot


class ChatBubble(QWidget):
    def __init__(self, role: str, content: str):
        super().__init__()
        outer = QHBoxLayout(self)
        outer.setContentsMargins(0, 4, 0, 4)
        outer.setSpacing(9)
        bubble = QFrame()
        bubble.setMaximumWidth(720)
        bubble.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)
        bubble.setStyleSheet(
            "QFrame {background:%s; border-radius:17px;}" % ("#DDF8ED" if role == "user" else "#EEF2FF")
        )
        body = QVBoxLayout(bubble)
        body.setContentsMargins(16, 12, 16, 13)
        body.setSpacing(5)
        title = QLabel("Ты" if role == "user" else "Умный друг")
        title.setStyleSheet("font-weight:700; color:#29304A")
        text = QLabel(html.escape(content).replace("**", "").replace("\n", "<br>"))
        text.setTextFormat(Qt.TextFormat.RichText)
        text.setWordWrap(True)
        text.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        text.setStyleSheet("font-size:14px; line-height:1.35; color:#172033")
        body.addWidget(title)
        body.addWidget(text)
        if role == "user":
            outer.addStretch(1)
            outer.addWidget(bubble, 0, Qt.AlignmentFlag.AlignRight)
        else:
            outer.addWidget(Mascot(38), 0, Qt.AlignmentFlag.AlignTop)
            outer.addWidget(bubble, 0, Qt.AlignmentFlag.AlignLeft)
            outer.addStretch(1)
