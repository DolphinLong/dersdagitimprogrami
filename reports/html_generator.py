"""
HTML Report Generator for Class Scheduling Program
Creates beautiful, colorful web-based schedule tables
"""

import os
from typing import List, Dict
from database import db_manager
from utils.helpers import generate_color_for_lesson

class HTMLScheduleGenerator:
    """Generate beautiful HTML schedule reports"""

    def __init__(self, db_manager):
        self.db_manager = db_manager

    def generate_class_schedule_html(self, class_id: int) -> str:
        """Generate HTML schedule for a specific class"""
        class_obj = self.db_manager.get_class_by_id(class_id)
        if not class_obj:
            return "<h1>Sınıf bulunamadı!</h1>"

        # Get schedule entries
        schedule_entries = self.db_manager.get_schedule_for_specific_class(class_id)

        # Group by day and time slot
        schedule_grid = {}
        for entry in schedule_entries:
            day = entry.day
            slot = entry.time_slot
            if day not in schedule_grid:
                schedule_grid[day] = {}
            schedule_grid[day][slot] = entry

        # HTML generation
        html = f"""
        <!DOCTYPE html>
        <html lang="tr">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{class_obj.name} - Ders Programı</title>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    margin: 0;
                    padding: 20px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                }}
                .container {{
                    max-width: 1200px;
                    margin: 0 auto;
                    background: white;
                    border-radius: 20px;
                    padding: 30px;
                    box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                }}
                h1 {{
                    color: #2c3e50;
                    text-align: center;
                    margin-bottom: 30px;
                    font-size: 2.5em;
                }}
                .schedule-table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin-top: 20px;
                    font-size: 16px;
                }}
                .schedule-table th {{
                    background: linear-gradient(135deg, #3498db, #2980b9);
                    color: white;
                    padding: 15px;
                    text-align: center;
                    font-weight: bold;
                    border: 1px solid #2980b9;
                }}
                .schedule-table td {{
                    padding: 15px;
                    text-align: center;
                    border: 1px solid #ddd;
                    vertical-align: middle;
                }}
                .time-slot {{
                    background: linear-gradient(135deg, #27ae60, #229954);
                    color: white;
                    font-weight: bold;
                }}
                .day-header {{
                    background: linear-gradient(135deg, #9b59b6, #8e44ad);
                    color: white;
                    font-weight: bold;
                }}
        """

        # Add lesson-specific colors
        lessons = set()
        for entry in schedule_entries:
            lesson = self.db_manager.get_lesson_by_id(entry.lesson_id)
            if lesson:
                lessons.add(lesson.name)

        for lesson in lessons:
            color = generate_color_for_lesson(lesson)
            html += f"""
                .lesson-{hash(lesson) % 1000} {{
                    background: linear-gradient(135deg, {color.name()}, {self._darken_color(color.name())});
                    color: white;
                    font-weight: bold;
                }}
            """

        html += """
                .empty-slot {
                    background-color: #f8f9fa;
                    color: #6c757d;
                }
                .lesson-info {
                    font-size: 14px;
                    margin: 5px 0;
                }
                .teacher-name {
                    font-size: 12px;
                    opacity: 0.9;
                }
                .classroom-name {
                    font-size: 11px;
                    opacity: 0.8;
                }
                @media print {
                    body { background: white; }
                    .container { box-shadow: none; }
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>📚 {class_obj.name} - Ders Programı</h1>

                <table class="schedule-table">
                    <thead>
                        <tr>
                            <th class="day-header">Gün</th>
                            <th class="time-slot">1. Saat<br>08:00-09:00</th>
                            <th class="time-slot">2. Saat<br>09:00-10:00</th>
                            <th class="time-slot">3. Saat<br>10:00-11:00</th>
                            <th class="time-slot">4. Saat<br>11:00-12:00</th>
                            <th class="time-slot">5. Saat<br>12:00-13:00</th>
                            <th class="time-slot">6. Saat<br>13:00-14:00</th>
                            <th class="time-slot">7. Saat<br>14:00-15:00</th>
                            <th class="time-slot">8. Saat<br>15:00-16:00</th>
                        </tr>
                    </thead>
                    <tbody>
        """

        days = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma"]
        for day in range(5):
            html += f"<tr><td class='day-header'>{days[day]}</td>"

            for slot in range(8):  # Max 8 time slots
                entry = schedule_grid.get(day, {}).get(slot)
                if entry:
                    lesson = self.db_manager.get_lesson_by_id(entry.lesson_id)
                    teacher = self.db_manager.get_teacher_by_id(entry.teacher_id)
                    classroom = self.db_manager.get_classroom_by_id(entry.classroom_id)

                    if lesson and teacher and classroom:
                        color_class = f"lesson-{hash(lesson.name) % 1000}"
                        html += f"""
                        <td class="{color_class}">
                            <div class="lesson-info">📚 {lesson.name}</div>
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

                <div style="text-align: center; margin-top: 30px; color: #6c757d;">
                    <p>🎨 Renkli ders programı oluşturuldu</p>
                </div>
            </div>
        </body>
        </html>
        """

        return html

    def _darken_color(self, hex_color: str) -> str:
        """Darken a hex color for gradient"""
        try:
            from PyQt5.QtGui import QColor
            color = QColor(hex_color)
            # Make it darker
            darker = QColor(int(color.red() * 0.8), int(color.green() * 0.8), int(color.blue() * 0.8))
            return darker.name()
        except:
            return hex_color

    def save_html_report(self, class_id: int, filename: str = None) -> str:
        """Save HTML report to file"""
        if not filename:
            class_obj = self.db_manager.get_class_by_id(class_id)
            class_name = class_obj.name if class_obj else f"class_{class_id}"
            filename = f"{class_name}_programi.html"

        html_content = self.generate_class_schedule_html(class_id)

        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)

        return filename

    def open_in_browser(self, class_id: int):
        """Open HTML report in default browser"""
        filename = self.save_html_report(class_id)
        import webbrowser
        import os

        file_path = os.path.abspath(filename)
        webbrowser.open(f'file://{file_path}')

        return filename