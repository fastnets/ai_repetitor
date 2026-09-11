from PySide6.QtWidgets import QGridLayout, QHBoxLayout, QLabel, QVBoxLayout

from ...services.mock_data import PROGRESS
from ..assets import icon
from ..widgets import Card, PageTitle, SectionTitle, StatCard, TopicProgress
from .base import ScrollPage


def text_card(title: str, text: str, tone="surface"):
    layout = QVBoxLayout()
    layout.setContentsMargins(20, 18, 20, 18)
    layout.setSpacing(8)
    card = Card(layout, tone)
    heading = QLabel(title)
    heading.setStyleSheet("font-size:16px; font-weight:700")
    body = QLabel(text)
    body.setWordWrap(True)
    body.setStyleSheet("color:#59637A")
    layout.addWidget(heading)
    layout.addWidget(body)
    return card


class ProgressPage(ScrollPage):
    def __init__(self):
        super().__init__()
        title_row = QHBoxLayout()
        title_row.addWidget(PageTitle("Мои успехи", "Твой прогресс по математике"))
        title_row.addStretch()
        demo = QLabel("Демо-данные")
        demo.setStyleSheet("background:#FFF1C7; color:#8A6200; border-radius:10px; padding:6px 10px")
        title_row.addWidget(demo)
        self.layout.addLayout(title_row)

        stats = QHBoxLayout()
        stats.setSpacing(15)
        stats.addWidget(StatCard(PROGRESS["solved"], "Решено задач"), 1)
        stats.addWidget(StatCard(PROGRESS["lessons"], "Занятий", "#24A879"), 1)
        stats.addWidget(StatCard(PROGRESS["independence"], "Средняя самостоятельность", "#D99A00"), 1)
        self.layout.addLayout(stats)

        progress_layout = QVBoxLayout()
        progress_layout.setContentsMargins(22, 20, 22, 20)
        progress_layout.setSpacing(7)
        progress_layout.addWidget(SectionTitle("Прогресс по темам"))
        for topic, value in PROGRESS["topics"]:
            progress_layout.addWidget(TopicProgress(topic, value))
        self.layout.addWidget(Card(progress_layout))

        insights = QHBoxLayout()
        insights.setSpacing(15)
        insights.addWidget(text_card("Получается хорошо", "Сложение столбиком и задачи на периметр — уверенно!", "mint"), 1)
        insights.addWidget(text_card("Стоит повторить", "Единицы времени и деление с остатком.", "lavender"), 1)
        self.layout.addLayout(insights)

        achievements = QHBoxLayout()
        achievements.setContentsMargins(20, 17, 20, 17)
        badge = QLabel()
        badge.setPixmap(icon("achievement").pixmap(38, 38))
        achievements.addWidget(badge)
        copy = QVBoxLayout()
        copy.addWidget(SectionTitle("Мои достижения"))
        detail = QLabel("7 дней занятий • 10 задач без подсказки • Знаток периметра")
        detail.setWordWrap(True)
        detail.setObjectName("muted")
        copy.addWidget(detail)
        achievements.addLayout(copy, 1)
        self.layout.addWidget(Card(achievements))
        self.layout.addStretch()
