from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtWidgets import QButtonGroup, QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout

from .assets import icon
from .widgets.mascot import Mascot


class SidebarButton(QPushButton):
    def __init__(self, text: str, icon_name: str):
        super().__init__(icon(icon_name), text)
        self.setCheckable(True)
        self.setIconSize(QSize(22, 22))
        self.setMinimumHeight(46)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet(
            "QPushButton {text-align:left; padding:10px 14px; border-radius:12px; color:#45506B; background:transparent;}"
            "QPushButton:hover {background:#F1F0FB;}"
            "QPushButton:checked {background:#ECEBFF; color:#4F46E5; font-weight:700;}"
        )


class Sidebar(QFrame):
    page_requested = Signal(str)
    new_lesson_requested = Signal()
    settings_requested = Signal()

    ITEMS = [
        ("home", "Главная", "home"),
        ("lesson", "Занятие", "lesson"),
        ("tasks", "Задачи", "tasks"),
        ("progress", "Мои успехи", "progress"),
        ("parent", "Для родителя", "parent"),
    ]

    def __init__(self):
        super().__init__()
        self.setFixedWidth(244)
        self.setStyleSheet("Sidebar {background:#FFFFFF; border-right:1px solid #E7E5E0;}")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 22, 18, 18)
        layout.setSpacing(8)
        brand = QHBoxLayout()
        brand.addWidget(Mascot(54))
        name_box = QVBoxLayout()
        name = QLabel("Умный друг")
        name.setStyleSheet("font-size:18px; font-weight:800; color:#172033")
        caption = QLabel("Рядом, когда сложно")
        caption.setStyleSheet("font-size:11px; color:#718096")
        name_box.addWidget(name)
        name_box.addWidget(caption)
        brand.addLayout(name_box)
        brand.addStretch()
        layout.addLayout(brand)
        layout.addSpacing(22)

        self.group = QButtonGroup(self)
        self.group.setExclusive(True)
        self.buttons = {}
        for key, label, icon_name in self.ITEMS:
            button = SidebarButton(label, icon_name)
            button.clicked.connect(lambda _checked=False, page=key: self.page_requested.emit(page))
            self.group.addButton(button)
            self.buttons[key] = button
            layout.addWidget(button)
        layout.addStretch()

        new_button = SidebarButton("Новое занятие", "new_lesson")
        new_button.setCheckable(False)
        new_button.setStyleSheet(
            "QPushButton {text-align:left; padding:10px 14px; border:1px solid #D9D7FA; border-radius:12px; color:#4F46E5; background:#F8F7FF; font-weight:700;}"
            "QPushButton:hover {background:#ECEBFF;}"
        )
        new_button.clicked.connect(self.new_lesson_requested)
        layout.addWidget(new_button)
        settings = SidebarButton("Настройки", "settings")
        settings.setCheckable(False)
        settings.clicked.connect(self.settings_requested)
        layout.addWidget(settings)

    def select(self, page: str):
        if page in self.buttons:
            self.buttons[page].setChecked(True)
