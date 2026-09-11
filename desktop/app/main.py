import html
import json
import os
import sys
from pathlib import Path

import httpx
from PySide6.QtCore import QObject, QRunnable, Qt, QThreadPool, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from .config import BACKEND_URL


class WorkerSignals(QObject):
    result = Signal(object)
    error = Signal(str)


class ApiWorker(QRunnable):
    def __init__(self, method, path, payload=None):
        super().__init__()
        self.method, self.path, self.payload = method, path, payload
        self.signals = WorkerSignals()

    def run(self):
        try:
            response = httpx.request(self.method, BACKEND_URL + self.path, json=self.payload, timeout=120)
            response.raise_for_status()
            self.signals.result.emit(response.json())
        except httpx.TimeoutException:
            self.signals.error.emit("Репетитор отвечает дольше обычного. Попробуй отправить сообщение ещё раз.")
        except httpx.RemoteProtocolError:
            self.signals.error.emit("Связь с сервером прервалась. Сообщение сохранено в поле — попробуй отправить его ещё раз.")
        except Exception as exc:
            self.signals.error.emit(f"Не удалось связаться с сервером: {exc}")


class MessageBubble(QLabel):
    def __init__(self, role: str, content: str):
        title = "Ты" if role == "user" else "Репетитор"
        safe_content = html.escape(content).replace("**", "").replace("\n", "<br>")
        super().__init__(f"<b>{title}</b><br>{safe_content}")
        self.setWordWrap(True)
        self.setTextFormat(Qt.TextFormat.RichText)
        self.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        color = "#DCFCE7" if role == "user" else "#EEF2FF"
        self.setStyleSheet(
            f"background:{color}; color:#172033; border-radius:14px; padding:12px; margin:4px 0;"
        )


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.session_id = None
        self.pending_text = ""
        self.session_file = Path(os.getenv("LOCALAPPDATA", Path.home())) / "AI-Tutor" / "session.json"
        self.pool = QThreadPool.globalInstance()
        self.setWindowTitle("AI-репетитор")
        self.resize(780, 650)
        self._build_ui()
        self.restore_session()

    def _build_ui(self):
        root = QWidget()
        layout = QVBoxLayout(root)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(12)
        heading = QLabel("AI-репетитор")
        heading.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        subtitle = QLabel("Математика  •  3 класс")
        subtitle.setStyleSheet("color:#64748B; font-size:15px")
        layout.addWidget(heading)
        layout.addWidget(subtitle)

        self.message_host = QWidget()
        self.message_layout = QVBoxLayout(self.message_host)
        self.message_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(self.message_host)
        self.scroll.setStyleSheet("QScrollArea {border:1px solid #E2E8F0; border-radius:10px; background:white}")
        layout.addWidget(self.scroll, 1)

        self.thinking = QLabel("")
        self.thinking.setStyleSheet("color:#64748B; font-style:italic")
        layout.addWidget(self.thinking)
        input_row = QHBoxLayout()
        self.input = QLineEdit()
        self.input.setPlaceholderText("Напиши задачу или свой ответ…")
        self.input.setMinimumHeight(44)
        self.input.returnPressed.connect(self.send_message)
        self.send_button = QPushButton("Отправить")
        self.send_button.setMinimumHeight(44)
        self.send_button.clicked.connect(self.send_message)
        input_row.addWidget(self.input, 1)
        input_row.addWidget(self.send_button)
        layout.addLayout(input_row)

        actions = QHBoxLayout()
        new_button = QPushButton("Новое занятие")
        new_button.clicked.connect(self.new_session)
        finish_button = QPushButton("Закончить занятие")
        finish_button.clicked.connect(self.finish_session)
        actions.addWidget(new_button)
        actions.addWidget(finish_button)
        actions.addStretch()
        layout.addLayout(actions)
        root.setStyleSheet("QWidget {font-family:'Segoe UI'; font-size:14px} QPushButton {padding:8px 14px}")
        self.setCentralWidget(root)

    def run_api(self, method, path, payload, on_success, on_error=None):
        worker = ApiWorker(method, path, payload)
        worker.signals.result.connect(on_success)
        worker.signals.error.connect(on_error or self.on_error)
        self.pool.start(worker)

    def save_session(self):
        self.session_file.parent.mkdir(parents=True, exist_ok=True)
        self.session_file.write_text(json.dumps({"session_id": self.session_id}), encoding="utf-8")

    def restore_session(self):
        try:
            data = json.loads(self.session_file.read_text(encoding="utf-8"))
            self.session_id = data.get("session_id")
        except (OSError, ValueError, TypeError):
            self.session_id = None
        if not self.session_id:
            self.new_session()
            return
        self.set_busy(True)
        self.run_api(
            "GET",
            f"/api/session/{self.session_id}/messages",
            None,
            self.on_history,
            self.on_restore_error,
        )

    def on_history(self, data):
        self.clear_messages()
        if data["messages"]:
            for message in data["messages"]:
                self.add_message(message["role"], message["content"])
        else:
            self.add_message("assistant", "Привет! Пришли задачу по математике — разберём её вместе 🙂")
        self.set_busy(False)
        self.input.setFocus()

    def on_restore_error(self, _message):
        self.session_id = None
        self.new_session()

    def set_busy(self, busy):
        self.input.setEnabled(not busy)
        self.send_button.setEnabled(not busy)
        self.thinking.setText("Репетитор думает…" if busy else "")

    def clear_messages(self):
        while self.message_layout.count():
            item = self.message_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def add_message(self, role, content):
        self.message_layout.addWidget(MessageBubble(role, content))
        QApplication.processEvents()
        self.scroll.verticalScrollBar().setValue(self.scroll.verticalScrollBar().maximum())

    def new_session(self):
        self.set_busy(True)
        self.run_api("POST", "/api/session/new", {}, self.on_new_session)

    def on_new_session(self, data):
        self.session_id = data["session_id"]
        self.save_session()
        self.clear_messages()
        self.add_message("assistant", "Привет! Пришли задачу по математике — разберём её вместе 🙂")
        self.set_busy(False)
        self.input.setFocus()

    def send_message(self):
        text = self.input.text().strip()
        if not text or not self.session_id:
            return
        self.input.clear()
        self.pending_text = text
        self.add_message("user", text)
        self.set_busy(True)
        self.run_api("POST", "/api/chat", {"session_id": self.session_id, "message": text}, self.on_chat)

    def on_chat(self, data):
        self.pending_text = ""
        self.add_message("assistant", data["message"])
        self.set_busy(False)
        self.input.setFocus()

    def finish_session(self):
        if not self.session_id:
            return
        self.set_busy(True)
        self.run_api("POST", f"/api/session/{self.session_id}/finish", {}, self.on_finish)

    def on_finish(self, data):
        self.set_busy(False)
        QMessageBox.information(self, "Итог занятия", data["summary"])

    def on_error(self, message):
        self.set_busy(False)
        if self.pending_text and not self.input.text():
            self.input.setText(self.pending_text)
        self.add_message("assistant", "Не получилось получить ответ. Твой текст остался в поле — попробуй отправить ещё раз.")
        QMessageBox.warning(self, "Связь прервалась", message)


def main():
    application = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(application.exec())


if __name__ == "__main__":
    main()
