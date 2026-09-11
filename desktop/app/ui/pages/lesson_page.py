from PySide6.QtCore import QTimer, Qt, Signal
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from ..assets import icon
from ..widgets import ChatBubble, TaskCard


class LessonPage(QWidget):
    send_requested = Signal(str)
    hint_requested = Signal()
    finish_requested = Signal()

    def __init__(self):
        super().__init__()
        root = QVBoxLayout(self)
        root.setContentsMargins(34, 25, 34, 24)
        root.setSpacing(15)

        header = QHBoxLayout()
        title_box = QVBoxLayout()
        title = QLabel("Математика • 3 класс")
        title.setObjectName("pageTitle")
        subtitle = QLabel("Разбираем задачу вместе, шаг за шагом")
        subtitle.setObjectName("muted")
        title_box.addWidget(title)
        title_box.addWidget(subtitle)
        header.addLayout(title_box)
        header.addStretch()
        progress_box = QVBoxLayout()
        self.step_label = QLabel("Шаг 1 из 5")
        self.step_label.setStyleSheet("font-weight:700; color:#4F46E5")
        self.step_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        segments = QHBoxLayout()
        segments.setSpacing(5)
        self.segments = []
        for _ in range(5):
            segment = QFrame()
            segment.setFixedSize(32, 6)
            self.segments.append(segment)
            segments.addWidget(segment)
        progress_box.addWidget(self.step_label)
        progress_box.addLayout(segments)
        header.addLayout(progress_box)
        root.addLayout(header)

        self.task_card = TaskCard()
        root.addWidget(self.task_card)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll.setStyleSheet("QScrollArea, QScrollArea > QWidget > QWidget {background:#F8F7F3; border:none;}")
        self.message_host = QWidget()
        self.message_layout = QVBoxLayout(self.message_host)
        self.message_layout.setContentsMargins(2, 3, 6, 3)
        self.message_layout.setSpacing(4)
        self.message_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll.setWidget(self.message_host)
        root.addWidget(self.scroll, 1)

        self.thinking = QLabel("")
        self.thinking.setStyleSheet("color:#6366F1; font-style:italic; padding-left:48px")
        root.addWidget(self.thinking)

        panel = QFrame()
        panel.setObjectName("card")
        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(12, 11, 12, 11)
        panel_layout.setSpacing(9)
        input_row = QHBoxLayout()
        self.input = QLineEdit()
        self.input.setPlaceholderText("Напиши свой ответ…")
        self.input.setMinimumHeight(46)
        self.input.returnPressed.connect(self.emit_message)
        self.send_button = QPushButton(icon("send"), "Отправить")
        self.send_button.setObjectName("primary")
        self.send_button.setMinimumHeight(46)
        self.send_button.clicked.connect(self.emit_message)
        input_row.addWidget(self.input, 1)
        input_row.addWidget(self.send_button)
        action_row = QHBoxLayout()
        self.hint_button = QPushButton(icon("hint"), "Нужна подсказка")
        self.hint_button.setObjectName("secondary")
        self.hint_button.clicked.connect(self.hint_requested)
        finish = QPushButton(icon("finish"), "Закончить занятие")
        finish.setObjectName("finishButton")
        finish.setStyleSheet("QPushButton {color:#9A6700; background:#FFF7DB; border-radius:11px; padding:8px 13px;} QPushButton:hover {background:#FCECB7;}")
        finish.clicked.connect(self.finish_requested)
        action_row.addWidget(self.hint_button)
        action_row.addStretch()
        action_row.addWidget(finish)
        panel_layout.addLayout(input_row)
        panel_layout.addLayout(action_row)
        root.addWidget(panel)
        self.set_step(1)

    def emit_message(self):
        text = self.input.text().strip()
        if text:
            self.send_requested.emit(text)

    def take_input(self) -> str:
        text = self.input.text().strip()
        self.input.clear()
        return text

    def restore_input(self, text: str):
        if text and not self.input.text():
            self.input.setText(text)

    def set_busy(self, busy: bool):
        self.input.setEnabled(not busy)
        self.send_button.setEnabled(not busy)
        self.hint_button.setEnabled(not busy)
        self.thinking.setText("Сова думает над ответом…" if busy else "")

    def clear_messages(self):
        while self.message_layout.count():
            item = self.message_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def add_message(self, role: str, content: str):
        self.message_layout.addWidget(ChatBubble(role, content))
        QApplication.processEvents()
        QTimer.singleShot(0, lambda: self.scroll.verticalScrollBar().setValue(self.scroll.verticalScrollBar().maximum()))

    def set_task(self, text: str = "", source: str = ""):
        self.task_card.set_task(text, source)

    def set_step(self, value: int):
        value = max(1, min(value, 5))
        self.step_label.setText(f"Шаг {value} из 5")
        for index, segment in enumerate(self.segments, start=1):
            segment.setStyleSheet(
                "background:%s; border-radius:3px;" % ("#6366F1" if index <= value else "#DEDDE7")
            )
