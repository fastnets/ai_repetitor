"""Render deterministic screenshots of all desktop pages without calling backend."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "desktop"))

from PySide6.QtWidgets import QApplication

from app.ui.main_window import MainWindow
from app.ui.styles.theme import APP_QSS


def no_network_restore(window):
    window.session_id = "screenshot-session"
    window.messages = []
    window.render_messages()
    window.apply_stats(
        {
            "lessons_started": 0,
            "completed_tasks": 0,
            "today_completed": 0,
            "user_messages": 0,
            "last_task": None,
            "recent_tasks": [],
            "topic_activity": [],
            "latest_lesson": None,
        }
    )


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(APP_QSS)
    original_restore = MainWindow.restore_session
    MainWindow.restore_session = lambda self: None
    try:
        window = MainWindow()
    finally:
        MainWindow.restore_session = original_restore
    no_network_restore(window)
    window.resize(1440, 900)
    window.show()
    output = ROOT / "screenshots"
    output.mkdir(exist_ok=True)
    for name in ("home", "lesson", "tasks", "progress", "parent"):
        window.show_page(name)
        app.processEvents()
        window.grab().save(str(output / f"{name}.png"))
    window.close()


if __name__ == "__main__":
    main()
