"""
Class schedule dialog for the Class Scheduling Program - FIXED
"""

import logging

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtWidgets import (
    QComboBox,
    QDialog,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
)

from database import db_manager
from utils.helpers import generate_color_for_lesson


class ClassScheduleDialog(QDialog):
    """Dialog for viewing a specific class schedule"""

    SCHOOL_TIME_SLOTS = {
        "İlkokul": 6,
        "Ortaokul": 7,
        "Lise": 8,
        "Anadolu Lisesi": 8,
        "Fen Lisesi": 8,
        "Sosyal Bilimler Lisesi": 8,
    }

    def __init__(self, parent=None):
        super().__init__(parent)

        # 🎯 Force Fusion style
        from PyQt5.QtWidgets import QApplication

        QApplication.setStyle("Fusion")

        self.setWindowTitle("Sınıf Programı Görüntüle")
        self.setFixedSize(1000, 600)
        self.setup_ui()
        self.populate_classes()
        self.apply_styles()

    def setup_ui(self):
        """Set up the user interface"""
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        # Title
        title_label = QLabel("SINIF PROGRAMI")
        title_label.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        title_label.setFont(QFont("Segoe UI", 18, QFont.Bold))
        layout.addWidget(title_label)

        # Class selection
        class_layout = QHBoxLayout()
        class_label = QLabel("Sınıf:")
        self.class_combo = QComboBox()
        self.class_combo.currentIndexChanged.connect(self.load_class_schedule)

        class_layout.addWidget(class_label)
        class_layout.addWidget(self.class_combo, 1)
        layout.addLayout(class_layout)

        # HTML Schedule view
        self.schedule_html = QTextEdit()
        self.schedule_html.setReadOnly(True)
        self.schedule_html.setMinimumHeight(400)
        layout.addWidget(self.schedule_html)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.export_html_button = QPushButton("🌐 HTML Export")
        self.export_html_button.clicked.connect(self.export_to_html)

        self.open_html_button = QPushButton("🌐 Tarayıcıda Aç")
        self.open_html_button.clicked.connect(self.open_in_browser)

        self.close_button = QPushButton("Kapat")
        self.close_button.clicked.connect(self.accept)

        button_layout.addWidget(self.export_html_button)
        button_layout.addWidget(self.open_html_button)
        button_layout.addWidget(self.close_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def generate_html_schedule(self, class_entries):
        """Generate HTML schedule for the class"""
        # Group entries by day and time slot
        schedule_grid = {}
        for entry in class_entries:
            day = entry.day
            slot = entry.time_slot
            if day not in schedule_grid:
                schedule_grid[day] = {}
            schedule_grid[day][slot] = entry

        html = """
        <html>
        <head>
            <style>
                body { 
                    font-family: 'Segoe UI', Arial, sans-serif; 
                    margin: 20px; 
                    background: #f8f9fa; 
                }
                .schedule-container { 
                    background: white; 
                    padding: 20px; 
                    border-radius: 15px; 
                    box-shadow: 0 5px 15px rgba(0,0,0,0.1); 
                }
                h2 { 
                    color: #2c3e50; 
                    text-align: center; 
                    margin-bottom: 20px; 
                }
                table {
                    width: 100%;
                    border-collapse: collapse;
                    font-size: 14px;
                    margin: 0 auto;
                }
                th {
                    background: linear-gradient(135deg, #3498db, #2980b9);
                    color: white;
                    padding: 15px;
                    text-align: center;
                    font-weight: bold;
                    border: 1px solid #2980b9;
                }
                td {
                    padding: 15px;
                    text-align: center;
                    border: 1px solid #ddd;
                    vertical-align: middle;
                    height: 80px;
                }
                .time-header {
                    background: linear-gradient(135deg, #27ae60, #229954) !important;
                }
                .day-header {
                    background: linear-gradient(135deg, #9b59b6, #8e44ad) !important;
                }
        """

        # Add lesson-specific colors
        lessons = set()
        for entry in class_entries:
            lesson = db_manager.get_lesson_by_id(entry.lesson_id)
            if lesson:
                lessons.add(lesson.name)

        for lesson in lessons:
            color = generate_color_for_lesson(lesson)
            html += f"""
                .lesson-{hash(lesson) % 1000} {{
                    background: linear-gradient(135deg, {color.name()}, {self._darken_color(color.name())}) !important;
                    color: white !important;
                    font-weight: bold;
                }}
            """

        html += """
                .empty-slot {
                    background-color: #f8f9fa;
                    color: #6c757d;
                }
                .lesson-content {
                    font-size: 12px;
                    margin: 3px 0;
                }
                .teacher-name {
                    font-size: 11px;
                    opacity: 0.9;
                }
                .classroom-name {
                    font-size: 10px;
                    opacity: 0.8;
                }
            </style>
        </head>
        <body>
            <div class="schedule-container">
                <h2>📚 Sınıf Programı</h2>
                <table>
                    <thead>
                        <tr>
                            <th class="day-header">Gün</th>
                            <th class="time-header">1. Saat<br>08:00-09:00</th>
                            <th class="time-header">2. Saat<br>09:00-10:00</th>
                            <th class="time-header">3. Saat<br>10:00-11:00</th>
                            <th class="time-header">4. Saat<br>11:00-12:00</th>
                            <th class="time-header">5. Saat<br>12:00-13:00</th>
                            <th class="time-header">6. Saat<br>13:00-14:00</th>
                            <th class="time-header">7. Saat<br>14:00-15:00</th>
                            <th class="time-header">8. Saat<br>15:00-16:00</th>
                        </tr>
                    </thead>
                    <tbody>
        """

        days = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma"]
        for day in range(5):
            html += f"<tr><td style='background: linear-gradient(135deg, #9b59b6, #8e44ad); color: white; font-weight: bold;'>{days[day]}</td>"

            for slot in range(8):
                entry = schedule_grid.get(day, {}).get(slot)
                if entry:
                    lesson = db_manager.get_lesson_by_id(entry.lesson_id)
                    teacher = db_manager.get_teacher_by_id(entry.teacher_id)
                    classroom = db_manager.get_classroom_by_id(entry.classroom_id)

                    if lesson and teacher and classroom:
                        color_class = f"lesson-{hash(lesson.name) % 1000}"
                        html += f"""
                        <td class="{color_class}">
                            <div class="lesson-content">📚 {lesson.name}</div>
                            <div class="teacher-name">👨‍🏫 {teacher.name}</div>
                            <div class="classroom-name">🏫 {classroom.name}</div>
                        </td>
                        """
                    else:
                        html += "<td class='empty-slot'>-</td>"
                else:
                    html += "<td class='empty-slot'>-</td>"

            html += "</tr>"

        html += """
                    </tbody>
                </table>
                <div style="text-align: center; margin-top: 20px; color: #6c757d;">
                    <p>🎨 HTML ile oluşturulmuş renkli ders programı</p>
                </div>
            </div>
        </body>
        </html>
        """

        return html

    def _darken_color(self, hex_color: str) -> str:
        """Darken a hex color for gradient"""
        try:
            color = QColor(hex_color)
            darker = QColor(
                int(color.red() * 0.8), int(color.green() * 0.8), int(color.blue() * 0.8)
            )
            return darker.name()
        except (TypeError, ValueError) as e:
            logging.warning(f"Could not darken color {hex_color}: {e}")
            return hex_color

    def apply_styles(self):
        """Apply clean styles"""
        self.setStyleSheet(
            """
            QDialog {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                          stop: 0 #ffffff, stop: 1 #f8f9fa);
            }
            QLabel {
                color: #2c3e50;
                font-size: 14px;
                font-weight: bold;
            }
            QComboBox {
                padding: 10px;
                border: 2px solid #cccccc;
                border-radius: 8px;
                background: white;
                font-size: 14px;
                min-height: 20px;
            }
            QComboBox:hover {
                border: 2px solid #3498db;
            }
            QTextEdit {
                border: 2px solid #dee2e6;
                border-radius: 8px;
                background-color: white;
            }
            QPushButton {
                padding: 10px 20px;
                border: none;
                border-radius: 8px;
                font-weight: bold;
                color: white;
                font-size: 14px;
                min-width: 100px;
            }
            QPushButton:first-child {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                          stop: 0 #f39c12, stop: 1 #e67e22);
            }
            QPushButton:first-child:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                          stop: 0 #e67e22, stop: 1 #d35400);
            }
            QPushButton:nth-child(2) {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                          stop: 0 #27ae60, stop: 1 #229954);
            }
            QPushButton:nth-child(2):hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                          stop: 0 #229954, stop: 1 #1e8449);
            }
            QPushButton:last-child {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                          stop: 0 #e74c3c, stop: 1 #c0392b);
            }
            QPushButton:last-child:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                          stop: 0 #c0392b, stop: 1 #a93226);
            }
        """
        )

    def populate_classes(self):
        """Populate the class combo box"""
        self.class_combo.clear()
        classes = db_manager.get_all_classes()
        for class_obj in classes:
            self.class_combo.addItem(class_obj.name, class_obj.class_id)

    def load_class_schedule(self):
        """Load schedule for the selected class"""
        class_id = self.class_combo.currentData()
        if not class_id:
            return

        class_entries = db_manager.get_schedule_for_specific_class(class_id)
        html_content = self.generate_html_schedule(class_entries)
        self.schedule_html.setHtml(html_content)

    def export_to_html(self):
        """Export schedule to HTML file"""
        class_id = self.class_combo.currentData()
        if not class_id:
            QMessageBox.warning(self, "Uyarı", "Lütfen bir sınıf seçin.")
            return

        try:
            from reports.html_generator import HTMLScheduleGenerator

            generator = HTMLScheduleGenerator(db_manager)
            filename = generator.save_html_report(class_id)

            QMessageBox.information(
                self,
                "Başarılı!",
                f"📄 HTML programı oluşturuldu!\n\n"
                f"📁 Dosya: {filename}\n\n"
                f"🌐 Tarayıcıda açmak için dosyaya çift tıklayın.\n"
                f"🎨 Tamamen renkli ve güzel görünecek!",
            )

        except Exception as e:
            QMessageBox.critical(self, "Hata", f"HTML export hatası: {str(e)}")

    def open_in_browser(self):
        """Open HTML report in browser"""
        class_id = self.class_combo.currentData()
        if not class_id:
            QMessageBox.warning(self, "Uyarı", "Lütfen bir sınıf seçin.")
            return

        try:
            from reports.html_generator import HTMLScheduleGenerator

            generator = HTMLScheduleGenerator(db_manager)
            filename = generator.save_html_report(class_id)

            import os
            import webbrowser

            file_path = os.path.abspath(filename)
            webbrowser.open(f"file://{file_path}")

            QMessageBox.information(
                self,
                "Tarayıcıda Açılıyor!",
                f"🌐 HTML programı tarayıcıda açılıyor!\n\n"
                f"📁 Dosya: {filename}\n\n"
                f"🎨 Tarayıcıda %100 renkli ve güzel görünecek!\n"
                f"📱 Mobil cihazlarda da mükemmel çalışır!",
            )

        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Tarayıcı açma hatası: {str(e)}")
