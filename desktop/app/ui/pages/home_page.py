from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QGridLayout, QHBoxLayout, QLabel, QPushButton, QVBoxLayout

from ...services.mock_data import HOME
from ..widgets import Card, Mascot, PageTitle, SectionTitle
from .base import ScrollPage


def info_card(title, value, tone="surface"):
    layout = QVBoxLayout()
    layout.setContentsMargins(20, 18, 20, 18)
    layout.setSpacing(7)
    card = Card(layout, tone)
    label = QLabel(title)
    label.setObjectName("muted")
    text = QLabel(value)
    text.setWordWrap(True)
    text.setStyleSheet("font-size:16px; font-weight:650")
    layout.addWidget(label)
    layout.addWidget(text)
    return card


class HomePage(ScrollPage):
    start_requested = Signal()
    continue_requested = Signal()

    def __init__(self):
        super().__init__()
        hero_layout = QHBoxLayout()
        hero_layout.setContentsMargins(28, 24, 28, 24)
        hero = Card(hero_layout, "lavender")
        copy = QVBoxLayout()
        copy.setSpacing(9)
        title = QLabel(f"Привет, {HOME['student']}!")
        title.setStyleSheet("font-size:30px; font-weight:800; color:#172033")
        subtitle = QLabel("Готов позаниматься математикой?")
        subtitle.setStyleSheet("font-size:17px; color:#59637A")
        start = QPushButton("Начать занятие")
        start.setObjectName("primary")
        start.setMinimumHeight(48)
        start.setMaximumWidth(210)
        start.clicked.connect(self.start_requested)
        copy.addWidget(title)
        copy.addWidget(subtitle)
        copy.addSpacing(8)
        copy.addWidget(start)
        hero_layout.addLayout(copy, 1)
        hero_layout.addWidget(Mascot(150), 0, Qt.AlignmentFlag.AlignRight)
        self.layout.addWidget(hero)

        stats = QHBoxLayout()
        stats.setSpacing(16)
        stats.addWidget(info_card("Сегодня решено", f"{HOME['today_solved']} задачи", "mint"), 1)
        stats.addWidget(info_card("Последняя тема", HOME["last_topic"]), 1)
        self.layout.addLayout(stats)

        self.layout.addWidget(SectionTitle("Твои занятия"))
        grid = QGridLayout()
        grid.setSpacing(16)
        recent = "\n".join(f"• {item}" for item in HOME["recent"])
        grid.addWidget(info_card("Последние задания", recent), 0, 0, 2, 1)
        grid.addWidget(info_card("У тебя хорошо получается", HOME["strong"], "mint"), 0, 1)
        grid.addWidget(info_card("Стоит повторить", HOME["repeat"]), 1, 1)
        self.layout.addLayout(grid)
        continue_button = QPushButton("Продолжить последнее занятие")
        continue_button.setObjectName("primary")
        continue_button.setMinimumHeight(48)
        continue_button.clicked.connect(self.continue_requested)
        self.layout.addWidget(continue_button)
        demo = QLabel("Данные карточек пока демонстрационные")
        demo.setObjectName("muted")
        demo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(demo)
        self.layout.addStretch()
