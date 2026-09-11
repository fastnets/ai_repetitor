from PySide6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget

from ..widgets import Card, PageTitle, SectionTitle, StatCard
from .base import ScrollPage


class ProgressPage(ScrollPage):
    def __init__(self):
        super().__init__()
        self.layout.addWidget(PageTitle("Мои успехи", "Только данные из твоих занятий"))

        stats = QHBoxLayout()
        stats.setSpacing(15)
        self.completed = StatCard("0", "Завершено задач")
        self.lessons = StatCard("0", "Начато занятий", "#24A879")
        self.messages = StatCard("0", "Сообщений ученика", "#D99A00")
        stats.addWidget(self.completed, 1)
        stats.addWidget(self.lessons, 1)
        stats.addWidget(self.messages, 1)
        self.layout.addLayout(stats)

        topic_layout = QVBoxLayout()
        topic_layout.setContentsMargins(22, 20, 22, 20)
        topic_layout.setSpacing(12)
        topic_layout.addWidget(SectionTitle("Темы занятий"))
        self.topic_host = QWidget()
        self.topic_rows = QVBoxLayout(self.topic_host)
        self.topic_rows.setContentsMargins(0, 0, 0, 0)
        self.topic_rows.setSpacing(9)
        topic_layout.addWidget(self.topic_host)
        self.layout.addWidget(Card(topic_layout))

        note_layout = QVBoxLayout()
        note_layout.setContentsMargins(20, 18, 20, 18)
        note_layout.addWidget(SectionTitle("Оценка навыков"))
        note = QLabel(
            "Пока репетитор не сохраняет проверенную оценку знаний, поэтому проценты, "
            "сильные стороны и рекомендации не показываются."
        )
        note.setWordWrap(True)
        note.setObjectName("muted")
        note_layout.addWidget(note)
        self.layout.addWidget(Card(note_layout, "lavender"))
        self.set_stats({})
        self.layout.addStretch()

    @staticmethod
    def _set_stat(card: StatCard, value):
        card.value_label.setText(str(value))

    def set_stats(self, data: dict):
        self._set_stat(self.completed, data.get("completed_tasks", 0))
        self._set_stat(self.lessons, data.get("lessons_started", 0))
        self._set_stat(self.messages, data.get("user_messages", 0))
        while self.topic_rows.count():
            item = self.topic_rows.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        topics = data.get("topic_activity") or []
        if not topics:
            empty = QLabel("Пока нет данных по темам")
            empty.setObjectName("muted")
            self.topic_rows.addWidget(empty)
            return
        for topic in topics:
            row = QHBoxLayout()
            name = QLabel(topic["name"])
            name.setStyleSheet("font-size:15px; font-weight:650")
            count = QLabel(f"{topic['lessons']} занятие" if topic["lessons"] == 1 else f"{topic['lessons']} занятий")
            count.setObjectName("muted")
            row.addWidget(name)
            row.addStretch()
            row.addWidget(count)
            wrapper = QWidget()
            wrapper.setLayout(row)
            self.topic_rows.addWidget(wrapper)
