from PySide6.QtCore import Signal
from PySide6.QtWidgets import QGridLayout, QHBoxLayout, QLabel, QPushButton, QVBoxLayout

from ...services.mock_data import PARENT
from ..widgets import Card, PageTitle, SectionTitle, StatCard
from .base import ScrollPage


def report_card(title: str, body: str, tone="surface"):
    layout = QVBoxLayout()
    layout.setContentsMargins(20, 17, 20, 18)
    layout.setSpacing(8)
    card = Card(layout, tone)
    heading = QLabel(title)
    heading.setStyleSheet("font-size:16px; font-weight:700")
    text = QLabel(body)
    text.setWordWrap(True)
    text.setStyleSheet("color:#59637A")
    layout.addWidget(heading)
    layout.addWidget(text)
    return card


class ParentPage(ScrollPage):
    lesson_requested = Signal()
    new_lesson_requested = Signal()

    def __init__(self):
        super().__init__()
        title = QHBoxLayout()
        title.addWidget(PageTitle("Отчёт для родителя", "Итоги занятия за сегодня"))
        title.addStretch()
        profile = QLabel("Артём • 3 класс")
        profile.setStyleSheet("background:#ECEBFF; color:#4F46E5; border-radius:12px; padding:9px 14px; font-weight:700")
        title.addWidget(profile)
        self.layout.addLayout(title)

        stats = QHBoxLayout()
        stats.setSpacing(15)
        stats.addWidget(StatCard(PARENT["duration"], "Время занятия"), 1)
        stats.addWidget(StatCard(PARENT["solved"], "Решено задач", "#24A879"), 1)
        stats.addWidget(StatCard(PARENT["independence"], "Самостоятельность", "#D99A00"), 1)
        self.layout.addLayout(stats)

        grid = QGridLayout()
        grid.setSpacing(15)
        grid.addWidget(report_card("Что делали на занятии", PARENT["did"]), 0, 0)
        grid.addWidget(report_card("Где возникли трудности", PARENT["difficulty"], "lavender"), 0, 1)
        grid.addWidget(report_card("Что получилось хорошо", PARENT["success"], "mint"), 1, 0)
        grid.addWidget(report_card("На что обратить внимание", PARENT["attention"]), 1, 1)
        self.layout.addLayout(grid)

        dialogue_layout = QVBoxLayout()
        dialogue_layout.setContentsMargins(20, 17, 20, 18)
        dialogue_layout.addWidget(SectionTitle("Фрагмент диалога"))
        self.dialogue = QLabel("Умный друг: Какое действие поможет узнать число групп?\nАртём: Нужно разделить.")
        self.dialogue.setWordWrap(True)
        self.dialogue.setStyleSheet("color:#59637A; padding-top:5px")
        dialogue_layout.addWidget(self.dialogue)
        self.layout.addWidget(Card(dialogue_layout))

        buttons = QHBoxLayout()
        view = QPushButton("Посмотреть занятие")
        view.setObjectName("secondary")
        view.clicked.connect(self.lesson_requested)
        new = QPushButton("Начать новое занятие")
        new.setObjectName("primary")
        new.clicked.connect(self.new_lesson_requested)
        buttons.addStretch()
        buttons.addWidget(view)
        buttons.addWidget(new)
        self.layout.addLayout(buttons)
        note = QLabel("Статистика и рекомендации пока демонстрационные; итог завершённого занятия показывается отдельно.")
        note.setObjectName("muted")
        note.setWordWrap(True)
        self.layout.addWidget(note)
        self.layout.addStretch()

    def set_dialogue(self, messages):
        if not messages:
            return
        excerpt = messages[-2:]
        lines = [("Артём" if item["role"] == "user" else "Умный друг") + ": " + item["content"] for item in excerpt]
        self.dialogue.setText("\n".join(lines))
