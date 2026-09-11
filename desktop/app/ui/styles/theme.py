COLORS = {
    "bg": "#F8F7F3",
    "surface": "#FFFFFF",
    "primary": "#6366F1",
    "primary_dark": "#4F46E5",
    "mint": "#34D399",
    "mint_soft": "#DDF8ED",
    "yellow": "#FBBF24",
    "text": "#172033",
    "muted": "#718096",
    "line": "#E8E7E2",
    "lavender": "#EEF0FF",
}

APP_QSS = """
QWidget { color: #172033; font-family: 'Segoe UI'; font-size: 14px; }
QMainWindow, QWidget#appRoot, QStackedWidget { background: #F8F7F3; }
QLabel#pageTitle { font-size: 28px; font-weight: 700; }
QLabel#pageSubtitle { color: #718096; font-size: 15px; }
QLabel#sectionTitle { font-size: 17px; font-weight: 650; }
QLabel#muted { color: #718096; }
QFrame#card { background: #FFFFFF; border: 1px solid #E8E7E2; border-radius: 18px; }
QFrame#softCard { background: #EEF0FF; border: none; border-radius: 18px; }
QFrame#mintCard { background: #DDF8ED; border: none; border-radius: 18px; }
QScrollArea, QScrollArea QWidget#qt_scrollarea_viewport { background: transparent; }
QPushButton { border: none; border-radius: 11px; padding: 10px 16px; font-weight: 600; }
QPushButton#primary { background: #6366F1; color: white; }
QPushButton#primary:hover { background: #4F46E5; }
QPushButton#primary:disabled { background: #B8BAF4; }
QPushButton#secondary { background: #FFFFFF; color: #4F46E5; border: 1px solid #D9DAF8; }
QPushButton#secondary:hover { background: #F1F2FF; }
QPushButton#dangerSoft { background: #FFF7E6; color: #9A6700; border: 1px solid #F8D58A; }
QLineEdit { background: white; border: 1px solid #DDDDE5; border-radius: 13px; padding: 11px 14px; selection-background-color: #6366F1; }
QLineEdit:focus { border: 2px solid #8587F5; }
QScrollArea { border: none; background: transparent; }
QScrollBar:vertical { width: 9px; background: transparent; margin: 4px 0; }
QScrollBar::handle:vertical { background: #D4D5DF; border-radius: 4px; min-height: 32px; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QProgressBar { background: #ECECF2; border: none; border-radius: 5px; height: 10px; text-align: center; }
QProgressBar::chunk { background: #6366F1; border-radius: 5px; }
QToolTip { background: #172033; color: white; border: none; padding: 6px; }
"""
