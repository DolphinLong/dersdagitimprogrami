"""
Helper functions for the Class Scheduling Program
"""

import logging

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtWidgets import QMessageBox


def setup_logging():
    """Configure logging.

    Prefer the project's centralized logging configuration in `logging_config.setup_logging`.
    Falls back to a simple error-only file handler if that module isn't available.
    """
    try:
        # Prefer central logging setup
        from logging_config import setup_logging as central_setup

        central_setup()
    except Exception:
        # Minimal fallback for tests / environments where logging_config can't run
        logging.basicConfig(
            level=logging.ERROR,
            format="%(asctime)s - %(levelname)s - %(message)s",
            filename="error.log",
            filemode="a",
        )


def generate_color_for_lesson(lesson_name):
    """Generate a beautiful, consistent color for a lesson based on its name"""
    # Enhanced color palette for different subjects
    color_palette = {
        # Ana dersler - güçlü renkler
        "Matematik": "#FF6B6B",  # Parlak kırmızı
        "Türkçe": "#4ECDC4",  # Turkuaz
        "Fen Bilimleri": "#45B7D1",  # Mavi
        "Sosyal Bilgiler": "#FFA07A",  # Açık somon
        "İngilizce": "#98D8C8",  # Açık yeşil
        "Din Kültürü": "#F7DC6F",  # Açık sarı
        "Görsel Sanatlar": "#BB8FCE",  # Açık mor
        "Beden Eğitimi": "#85C1E9",  # Açık mavi
        "Müzik": "#F8C471",  # Açık turuncu
        # Seçmeli dersler - pastel renkler
        "Almanca": "#D7DBDD",  # Açık gri
        "Fransızca": "#AED6F1",  # Çok açık mavi
        "Bilgisayar": "#A3E4D7",  # Açık nane
        "Rehberlik": "#F9E79F",  # Açık krem
        "T.C. İnkılap Tarihi": "#D5A6BD",  # Açık pembe
        # Diğer dersler için fallback renkler
        "default_colors": [
            "#FDEAA7",
            "#F8C471",
            "#85C1E9",
            "#82E0AA",
            "#F1948A",
            "#BB8FCE",
            "#85C1E9",
            "#D7DBDD",
        ],
    }

    # Önce tam eşleşme ara
    if lesson_name in color_palette:
        color_hex = color_palette[lesson_name]
        return QColor(color_hex)

    # Kısmi eşleşme ara (örneğin "Matematik" için "Mat" içeren)
    lesson_lower = lesson_name.lower()
    for lesson, color_hex in color_palette.items():
        if lesson != "default_colors" and lesson.lower() in lesson_lower:
            return QColor(color_hex)

    # Hiç eşleşme yoksa basit hash-based renk kullan
    hash_value = hash(lesson_name)
    default_colors = color_palette["default_colors"]
    color_index = hash_value % len(default_colors)
    return QColor(default_colors[color_index])


def create_styled_message_box(parent, title, text, icon=QMessageBox.Information):
    """Create a styled QMessageBox with consistent appearance"""
    msg = QMessageBox(parent)
    msg.setWindowTitle(title)
    msg.setText(text)
    msg.setIcon(icon)

    # Apply consistent styling
    msg.setStyleSheet(
        """
        QMessageBox {
            background-color: #ffffff;
            color: #212529;
            font-family: "Segoe UI", sans-serif;
        }
        QMessageBox QLabel {
            color: #212529;
            font-size: 14px;
        }
        QMessageBox QPushButton {
            background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                      stop: 0 #3498db, stop: 1 #2980b9);
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            font-weight: bold;
            min-width: 80px;
            font-size: 14px;
        }
        QMessageBox QPushButton:hover {
            background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                      stop: 0 #2980b9, stop: 1 #2573a7);
        }
        QMessageBox QPushButton:pressed {
            background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                      stop: 0 #2573a7, stop: 1 #1f618d);
        }
    """
    )

    return msg
