from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QProgressBar, QVBoxLayout, QWidget


class Card(QFrame):
    def __init__(self, layout=None, tone="surface", parent=None):
        super().__init__(parent)
        self.setObjectName({"surface": "card", "mint": "mintCard", "lavender": "softCard"}[tone])
        if layout:
            self.setLayout(layout)


class PageTitle(QFrame):
    def __init__(self, title: str, subtitle: str = ""):
        super().__init__()
        self.setFrameShape(QFrame.Shape.NoFrame)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        heading = QLabel(title)
        heading.setObjectName("pageTitle")
        layout.addWidget(heading)
        if subtitle:
            caption = QLabel(subtitle)
            caption.setObjectName("muted")
            layout.addWidget(caption)


class SectionTitle(QLabel):
    def __init__(self, text: str):
        super().__init__(text)
        self.setObjectName("sectionTitle")


class StatCard(Card):
    def __init__(self, value: str, label: str, accent="#6366F1"):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(5)
        super().__init__(layout)
        self.value_label = QLabel(str(value))
        self.value_label.setStyleSheet(f"font-size:28px; font-weight:700; color:{accent}")
        caption = QLabel(label)
        caption.setObjectName("muted")
        layout.addWidget(self.value_label)
        layout.addWidget(caption)


class TopicProgress(QWidget):
    def __init__(self, title: str, value: int):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 5, 0, 5)
        layout.setSpacing(7)
        row = QHBoxLayout()
        row.addWidget(QLabel(title))
        row.addStretch()
        value_label = QLabel(f"{value}%")
        value_label.setStyleSheet("font-weight:600; color:#4F46E5")
        row.addWidget(value_label)
        bar = QProgressBar()
        bar.setRange(0, 100)
        bar.setValue(value)
        bar.setTextVisible(False)
        bar.setFixedHeight(9)
        layout.addLayout(row)
        layout.addWidget(bar)
