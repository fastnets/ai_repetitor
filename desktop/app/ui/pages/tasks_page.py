from PySide6.QtCore import Signal
from PySide6.QtWidgets import QGridLayout, QLabel, QPushButton, QVBoxLayout

from ..widgets import Card, PageTitle
from .base import ScrollPage


class TasksPage(ScrollPage):
    task_requested = Signal(str)

    TASKS = [
        ("Разминка", "Вычисли: 36 + 27", "5 минут"),
        ("Таблица умножения", "Сколько будет 9 × 7?", "5 минут"),
        ("Задача", "У прямоугольника стороны 6 см и 4 см. Найди периметр.", "10 минут"),
        ("Повторение", "Раздели 38 на 6 и найди остаток.", "10 минут"),
    ]

    def __init__(self):
        super().__init__()
        self.layout.addWidget(PageTitle("Задачи", "Выбери небольшую тренировку на сегодня"))
        grid = QGridLayout()
        grid.setSpacing(16)
        for index, (title, task, duration) in enumerate(self.TASKS):
            box = QVBoxLayout()
            box.setContentsMargins(20, 18, 20, 18)
            box.setSpacing(9)
            card = Card(box)
            heading = QLabel(title)
            heading.setStyleSheet("font-size:17px; font-weight:700")
            body = QLabel(task)
            body.setWordWrap(True)
            body.setMinimumHeight(45)
            timing = QLabel(duration)
            timing.setObjectName("muted")
            button = QPushButton("Решить")
            button.setObjectName("primary")
            button.clicked.connect(lambda _checked=False, text=task: self.task_requested.emit(text))
            box.addWidget(heading)
            box.addWidget(body)
            box.addWidget(timing)
            box.addWidget(button)
            grid.addWidget(card, index // 2, index % 2)
        self.layout.addLayout(grid)
        note = QLabel("Подборка задач пока демонстрационная; позже её сформирует backend по темам ученика.")
        note.setObjectName("muted")
        note.setWordWrap(True)
        self.layout.addWidget(note)
        self.layout.addStretch()
