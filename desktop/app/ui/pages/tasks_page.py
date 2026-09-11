from PySide6.QtCore import Signal
from PySide6.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget

from ..widgets import Card, PageTitle
from .base import ScrollPage


class TasksPage(ScrollPage):
    task_requested = Signal(str)

    def __init__(self):
        super().__init__()
        self.layout.addWidget(PageTitle("Задачи", "Задания из реальных занятий"))
        self.host = QWidget()
        self.tasks_layout = QVBoxLayout(self.host)
        self.tasks_layout.setContentsMargins(0, 0, 0, 0)
        self.tasks_layout.setSpacing(14)
        self.layout.addWidget(self.host)
        self.set_stats({})
        self.layout.addStretch()

    def set_stats(self, data: dict):
        while self.tasks_layout.count():
            item = self.tasks_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        tasks = data.get("recent_tasks") or []
        if not tasks:
            empty_layout = QVBoxLayout()
            empty_layout.setContentsMargins(22, 24, 22, 24)
            title = QLabel("Пока нет сохранённых задач")
            title.setStyleSheet("font-size:17px; font-weight:700")
            caption = QLabel("Начни занятие и отправь условие — оно появится здесь автоматически.")
            caption.setWordWrap(True)
            caption.setObjectName("muted")
            empty_layout.addWidget(title)
            empty_layout.addWidget(caption)
            self.tasks_layout.addWidget(Card(empty_layout, "lavender"))
            return
        for index, task in enumerate(tasks, start=1):
            box = QVBoxLayout()
            box.setContentsMargins(20, 18, 20, 18)
            box.setSpacing(9)
            heading = QLabel(f"Задача {index}")
            heading.setStyleSheet("font-size:16px; font-weight:700")
            body = QLabel(task)
            body.setWordWrap(True)
            button = QPushButton("Разобрать ещё раз")
            button.setObjectName("secondary")
            button.clicked.connect(lambda _checked=False, text=task: self.task_requested.emit(text))
            box.addWidget(heading)
            box.addWidget(body)
            box.addWidget(button)
            self.tasks_layout.addWidget(Card(box))
