from PySide6.QtCore import Signal
from PySide6.QtWidgets import QGridLayout, QHBoxLayout, QLabel, QPushButton, QVBoxLayout

from ..widgets import Card, PageTitle, SectionTitle, StatCard
from .base import ScrollPage


def report_card(title: str, empty_text: str, tone="surface"):
    layout = QVBoxLayout()
    layout.setContentsMargins(20, 17, 20, 18)
    layout.setSpacing(8)
    card = Card(layout, tone)
    heading = QLabel(title)
    heading.setStyleSheet("font-size:16px; font-weight:700")
    value = QLabel(empty_text)
    value.setWordWrap(True)
    value.setStyleSheet("color:#59637A")
    layout.addWidget(heading)
    layout.addWidget(value)
    return card, value


class ParentPage(ScrollPage):
    lesson_requested = Signal()
    new_lesson_requested = Signal()

    def __init__(self):
        super().__init__()
        title = QHBoxLayout()
        title.addWidget(PageTitle("Отчёт для родителя", "Последнее реальное занятие"))
        title.addStretch()
        profile = QLabel("Артём • 3 класс")
        profile.setStyleSheet("background:#ECEBFF; color:#4F46E5; border-radius:12px; padding:9px 14px; font-weight:700")
        title.addWidget(profile)
        self.layout.addLayout(title)

        stats = QHBoxLayout()
        stats.setSpacing(15)
        self.duration = StatCard("—", "Время занятия")
        self.status = StatCard("Нет", "Занятие завершено", "#24A879")
        self.responses = StatCard("0", "Сообщений ученика", "#D99A00")
        stats.addWidget(self.duration, 1)
        stats.addWidget(self.status, 1)
        stats.addWidget(self.responses, 1)
        self.layout.addLayout(stats)

        grid = QGridLayout()
        grid.setSpacing(15)
        task_card, self.task = report_card("Что делали на занятии", "Пока нет данных")
        result_card, self.result = report_card("Результат", "Пока нет данных", "mint")
        difficulty_card, _ = report_card("Где возникли трудности", "Пока репетитор не сохраняет подтверждённую оценку трудностей.", "lavender")
        success_card, _ = report_card("Что получилось хорошо", "Пока репетитор не сохраняет подтверждённую оценку навыков.")
        grid.addWidget(task_card, 0, 0)
        grid.addWidget(result_card, 0, 1)
        grid.addWidget(difficulty_card, 1, 0)
        grid.addWidget(success_card, 1, 1)
        self.layout.addLayout(grid)

        dialogue_layout = QVBoxLayout()
        dialogue_layout.setContentsMargins(20, 17, 20, 18)
        dialogue_layout.addWidget(SectionTitle("Фрагмент диалога"))
        self.dialogue = QLabel("Пока нет сообщений")
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
        self.layout.addStretch()

    def set_stats(self, data: dict):
        latest = data.get("latest_lesson")
        if not latest:
            self.duration.value_label.setText("—")
            self.status.value_label.setText("Нет")
            self.responses.value_label.setText("0")
            self.task.setText("Пока нет данных")
            self.result.setText("Пока нет данных")
            self.dialogue.setText("Пока нет сообщений")
            return
        minutes = latest.get("duration_minutes")
        self.duration.value_label.setText("—" if minutes is None else ("<1 мин" if minutes == 0 else f"{minutes} мин"))
        finished = latest.get("status") == "finished"
        self.status.value_label.setText("Да" if finished else "Нет")
        self.responses.value_label.setText(str(latest.get("user_messages", 0)))
        self.task.setText(latest.get("task") or "Пока нет данных")
        self.result.setText("Занятие завершено" if finished else "Занятие ещё продолжается")
        dialogue = latest.get("dialogue") or []
        lines = [
            ("Артём" if item["role"] == "user" else "Умный друг") + ": " + item["content"]
            for item in dialogue
        ]
        self.dialogue.setText("\n\n".join(lines) if lines else "Пока нет сообщений")

    def set_dialogue(self, messages):
        if not messages:
            return
        lines = [
            ("Артём" if item["role"] == "user" else "Умный друг") + ": " + item["content"]
            for item in messages[-4:]
        ]
        self.dialogue.setText("\n\n".join(lines))
