from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QIcon, QPixmap

from ..config import ASSETS_DIR


def icon(name: str, size: int = 22) -> QIcon:
    result = QIcon(str(ASSETS_DIR / "icons" / f"{name}.svg"))
    result.addFile(str(ASSETS_DIR / "icons" / f"{name}.svg"), QSize(size, size))
    return result


def mascot(size: int) -> QPixmap:
    pixmap = QPixmap(str(ASSETS_DIR / "mascot" / "mascot.png"))
    return pixmap.scaled(
        size,
        size,
        Qt.AspectRatioMode.KeepAspectRatio,
        Qt.TransformationMode.SmoothTransformation,
    )
