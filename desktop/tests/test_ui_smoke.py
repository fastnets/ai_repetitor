import os
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

DESKTOP = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(DESKTOP))

from PySide6.QtWidgets import QApplication, QMessageBox

from app.ui.main_window import MainWindow


def test_navigation_and_lesson_flow(monkeypatch):
    app = QApplication.instance() or QApplication([])
    monkeypatch.setattr(MainWindow, "restore_session", lambda self: None)
    window = MainWindow()

    def fake_api(method, path, payload, success, error=None):
        if path == "/api/session/new":
            success({"session_id": "test-session"})
        elif path == "/api/chat":
            success({"message": "Верно рассуждаешь! Какой будет следующий шаг?"})
        elif path.endswith("/finish"):
            success({"summary": "Тестовое занятие завершено."})

    window.run_api = fake_api
    monkeypatch.setattr(QMessageBox, "information", lambda *args: QMessageBox.StandardButton.Ok)

    for page in ("home", "lesson", "tasks", "progress", "parent"):
        window.show_page(page)
        assert window.stack.currentWidget() is window.pages[page]

    window.new_session()
    assert window.session_id == "test-session"
    window.pages["lesson"].input.setText("Сколько будет 7 умножить на 8?")
    window.pages["lesson"].emit_message()
    assert [item["role"] for item in window.messages] == ["user", "assistant"]
    assert not window.pages["lesson"].thinking.text()
    window.finish_session()

    for width, height in ((1100, 700), (1440, 900), (1920, 1080)):
        window.resize(width, height)
        app.processEvents()
        assert window.width() >= width and window.height() >= height
    window.close()
