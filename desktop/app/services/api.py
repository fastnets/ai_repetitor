import httpx
from PySide6.QtCore import QObject, QRunnable, Signal

from ..config import BACKEND_URL


class WorkerSignals(QObject):
    result = Signal(object)
    error = Signal(str)


class ApiWorker(QRunnable):
    """Execute one backend request away from the UI thread."""

    def __init__(self, method: str, path: str, payload=None):
        super().__init__()
        self.method, self.path, self.payload = method, path, payload
        self.signals = WorkerSignals()

    def run(self):
        try:
            response = httpx.request(
                self.method,
                BACKEND_URL + self.path,
                json=self.payload,
                timeout=120,
            )
            response.raise_for_status()
            self.signals.result.emit(response.json())
        except httpx.TimeoutException:
            self.signals.error.emit("Репетитор отвечает дольше обычного. Попробуй ещё раз.")
        except httpx.RemoteProtocolError:
            self.signals.error.emit("Связь с сервером прервалась. Твой ответ сохранён в поле.")
        except Exception as exc:
            self.signals.error.emit(f"Не удалось связаться с сервером: {exc}")
