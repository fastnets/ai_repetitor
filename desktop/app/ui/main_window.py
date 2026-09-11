import json
import os
from pathlib import Path

from PySide6.QtCore import QThreadPool
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QHBoxLayout, QMainWindow, QMessageBox, QStackedWidget, QWidget

from ..config import ASSETS_DIR, BACKEND_URL
from ..services.api import ApiWorker
from .pages import HomePage, LessonPage, ParentPage, ProgressPage, TasksPage
from .sidebar import Sidebar


WELCOME = "Привет! Пришли задачу по математике — разберём её вместе 🙂"


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.session_id = None
        self.pending_text = ""
        self.messages = []
        self.latest_session_id = None
        self.pool = QThreadPool.globalInstance()
        self.session_file = Path(os.getenv("LOCALAPPDATA", Path.home())) / "AI-Tutor" / "session.json"
        self.setWindowTitle("Умный друг — AI-репетитор")
        self.setWindowIcon(QIcon(str(ASSETS_DIR / "app.ico")))
        self.setMinimumSize(1100, 700)
        self.resize(1440, 900)
        self._build_ui()
        self.restore_session()

    def _build_ui(self):
        root = QWidget()
        root.setObjectName("appRoot")
        layout = QHBoxLayout(root)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.sidebar = Sidebar()
        self.stack = QStackedWidget()
        self.pages = {
            "home": HomePage(),
            "lesson": LessonPage(),
            "tasks": TasksPage(),
            "progress": ProgressPage(),
            "parent": ParentPage(),
        }
        for page in self.pages.values():
            self.stack.addWidget(page)
        layout.addWidget(self.sidebar)
        layout.addWidget(self.stack, 1)
        self.setCentralWidget(root)

        self.sidebar.page_requested.connect(self.show_page)
        self.sidebar.new_lesson_requested.connect(self.new_session)
        self.sidebar.settings_requested.connect(self.show_settings)
        self.pages["home"].start_requested.connect(self.new_session)
        self.pages["home"].continue_requested.connect(self.continue_latest_session)
        self.pages["lesson"].send_requested.connect(self.send_message)
        self.pages["lesson"].hint_requested.connect(self.send_hint)
        self.pages["lesson"].finish_requested.connect(self.finish_session)
        self.pages["tasks"].task_requested.connect(self.start_task)
        self.pages["parent"].lesson_requested.connect(self.continue_latest_session)
        self.pages["parent"].new_lesson_requested.connect(self.new_session)
        self.show_page("home")

    def show_page(self, name: str):
        page = self.pages.get(name)
        if page:
            self.stack.setCurrentWidget(page)
            self.sidebar.select(name)

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
            self.create_session_in_background()
            return
        self.set_busy(True)
        self.run_api("GET", f"/api/session/{self.session_id}/messages", None, self.on_history, self.on_restore_error)

    def create_session_in_background(self):
        self.set_busy(True)
        self.run_api("POST", "/api/session/new", {}, self.on_initial_session)

    def on_initial_session(self, data):
        self.session_id = data["session_id"]
        self.save_session()
        self.reset_lesson()
        self.set_busy(False)
        self.load_stats()

    def on_history(self, data):
        self.messages = list(data.get("messages", []))
        self.render_messages()
        self.set_busy(False)
        self.load_stats()

    def on_restore_error(self, _message):
        self.session_id = None
        self.create_session_in_background()

    def render_messages(self):
        lesson = self.pages["lesson"]
        lesson.clear_messages()
        if self.messages:
            for message in self.messages:
                lesson.add_message(message["role"], message["content"])
            first_task = next((item["content"] for item in self.messages if item["role"] == "user"), "")
            lesson.set_task(first_task)
        else:
            lesson.add_message("assistant", WELCOME)
            lesson.set_task()
        user_count = sum(item["role"] == "user" for item in self.messages)
        lesson.set_step(min(5, max(1, user_count + 1)))
        self.pages["parent"].set_dialogue(self.messages)

    def reset_lesson(self):
        self.messages = []
        self.render_messages()

    def set_busy(self, busy: bool):
        self.pages["lesson"].set_busy(busy)

    def new_session(self):
        self.show_page("lesson")
        self.set_busy(True)
        self.run_api("POST", "/api/session/new", {}, self.on_new_session)

    def on_new_session(self, data):
        self.session_id = data["session_id"]
        self.pending_text = ""
        self.save_session()
        self.reset_lesson()
        self.set_busy(False)
        self.pages["lesson"].input.setFocus()

    def start_task(self, text: str):
        self.new_session()
        self.pages["lesson"].input.setText(text)

    def send_message(self, text: str):
        if not text or not self.session_id:
            return
        lesson = self.pages["lesson"]
        lesson.take_input()
        self.pending_text = text
        if not any(item["role"] == "user" for item in self.messages):
            lesson.set_task(text)
        self.messages.append({"role": "user", "content": text})
        lesson.add_message("user", text)
        lesson.set_step(min(5, sum(item["role"] == "user" for item in self.messages) + 1))
        self.set_busy(True)
        self.run_api("POST", "/api/chat", {"session_id": self.session_id, "message": text}, self.on_chat)

    def send_hint(self):
        text = "Мне нужна небольшая подсказка."
        self.pages["lesson"].input.setText(text)
        self.send_message(text)

    def on_chat(self, data):
        self.pending_text = ""
        message = data["message"]
        self.messages.append({"role": "assistant", "content": message})
        self.pages["lesson"].add_message("assistant", message)
        self.pages["parent"].set_dialogue(self.messages)
        self.set_busy(False)
        self.pages["lesson"].input.setFocus()
        self.load_stats()

    def finish_session(self):
        if not self.session_id:
            return
        self.set_busy(True)
        self.run_api("POST", f"/api/session/{self.session_id}/finish", {}, self.on_finish)

    def on_finish(self, data):
        self.set_busy(False)
        self.load_stats()
        QMessageBox.information(self, "Итог занятия", data["summary"])

    def load_stats(self):
        self.run_api("GET", "/api/stats", None, self.apply_stats, lambda _message: None)

    def apply_stats(self, data: dict):
        latest = data.get("latest_lesson")
        self.latest_session_id = latest.get("session_id") if latest else None
        for name in ("home", "tasks", "progress", "parent"):
            self.pages[name].set_stats(data)

    def continue_latest_session(self):
        if not self.latest_session_id or self.latest_session_id == self.session_id:
            self.show_page("lesson")
            return
        self.session_id = self.latest_session_id
        self.save_session()
        self.show_page("lesson")
        self.set_busy(True)
        self.run_api(
            "GET",
            f"/api/session/{self.session_id}/messages",
            None,
            self.on_history,
            self.on_restore_error,
        )

    def on_error(self, message: str):
        self.set_busy(False)
        self.pages["lesson"].restore_input(self.pending_text)
        self.pages["lesson"].add_message("assistant", "Не получилось получить ответ. Твой текст остался в поле — попробуй ещё раз.")
        QMessageBox.warning(self, "Связь прервалась", message)

    def show_settings(self):
        QMessageBox.information(
            self,
            "Настройки",
            f"Сейчас приложение подключено к:\n{BACKEND_URL}\n\nВыбор ученика и предмета добавим на следующем этапе.",
        )
