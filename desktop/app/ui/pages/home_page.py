from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QVBoxLayout

from ..widgets import Card, Mascot, SectionTitle
from .base import ScrollPage


def info_card(title, tone="surface"):
    layout = QVBoxLayout()
    layout.setContentsMargins(20, 18, 20, 18)
    layout.setSpacing(7)
    card = Card(layout, tone)
    label = QLabel(title)
    label.setObjectName("muted")
    value = QLabel("0")
    value.setWordWrap(True)
    value.setStyleSheet("font-size:16px; font-weight:650")
    layout.addWidget(label)
    layout.addWidget(value)
    return card, value


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
        title = QLabel("Привет, Артём!")
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
        today_card, self.today_value = info_card("Сегодня завершено", "mint")
        last_card, self.last_value = info_card("Последняя задача")
        self.last_value.setText("Пока нет данных")
        stats.addWidget(today_card, 1)
        stats.addWidget(last_card, 1)
        self.layout.addLayout(stats)

        self.layout.addWidget(SectionTitle("Последние задания"))
        recent_layout = QVBoxLayout()
        recent_layout.setContentsMargins(20, 18, 20, 18)
        self.recent_value = QLabel("Пока нет сохранённых заданий")
        self.recent_value.setWordWrap(True)
        self.recent_value.setStyleSheet("color:#59637A; line-height:1.5")
        recent_layout.addWidget(self.recent_value)
        self.layout.addWidget(Card(recent_layout))

        self.continue_button = QPushButton("Продолжить последнее занятие")
        self.continue_button.setObjectName("primary")
        self.continue_button.setMinimumHeight(48)
        self.continue_button.setEnabled(False)
        self.continue_button.clicked.connect(self.continue_requested)
        self.layout.addWidget(self.continue_button)
        self.layout.addStretch()

    def set_stats(self, data: dict):
        self.today_value.setText(str(data.get("today_completed", 0)))
        last_task = data.get("last_task")
        self.last_value.setText(last_task or "Пока нет данных")
        recent = data.get("recent_tasks") or []
        self.recent_value.setText("\n\n".join(f"• {task}" for task in recent) if recent else "Пока нет сохранённых заданий")
        self.continue_button.setEnabled(bool(last_task))
