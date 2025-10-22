"""
Real-time Schedule Preview Widget
Provides live preview of schedule changes during generation
"""
import sys
from typing import List, Dict, Any, Optional
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QLabel, QHeaderView, QSplitter, QGroupBox, QPushButton, QFrame
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QColor, QFont
from database.models import Class, Teacher, Lesson


class RealTimeSchedulePreviewWidget(QTableWidget):
    """
    Real-time schedule preview widget that shows schedule as it's being generated
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.schedule_data = {}  # {class_id: {day: {time_slot: entry}}}
        self.classes = []
        self.teachers = {}
        self.lessons = {}
        
    def setup_ui(self):
        """Setup the UI for the schedule preview"""
        self.setColumnCount(9)  # 8 time slots + 1 for day names
        self.setRowCount(6)  # 5 days + 1 header
        
        # Set headers
        day_headers = ["", "Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma"]
        time_headers = ["", "1", "2", "3", "4", "5", "6", "7", "8"]
        
        # Set horizontal headers (time slots)
        self.setHorizontalHeaderLabels(time_headers)
        
        # Set vertical headers (days) 
        self.setVerticalHeaderLabels(day_headers)
        
        # Configure table properties
        self.setEditTriggers(self.NoEditTriggers)
        self.setSelectionBehavior(self.SelectItems)
        self.setSelectionMode(self.NoSelection)
        self.setAlternatingRowColors(True)
        
        # Set header properties
        h_header = self.horizontalHeader()
        h_header.setSectionResizeMode(QHeaderView.Stretch)
        v_header = self.verticalHeader()
        v_header.setSectionResizeMode(QHeaderView.Stretch)
        
        # Set table properties
        self.setShowGrid(True)
        self.setGridStyle(Qt.SolidLine)
        
    def update_schedule_preview(self, schedule_entries: List[Dict[str, Any]], 
                              classes: List[Class], 
                              teachers: List[Teacher], 
                              lessons: List[Lesson]):
        """
        Update the schedule preview with new entries
        
        Args:
            schedule_entries: List of schedule entries
            classes: List of classes
            teachers: List of teachers
            lessons: List of lessons
        """
        # Store references to class, teacher, and lesson data
        self.classes = classes
        self.teachers = {t.teacher_id: t for t in teachers}
        self.lessons = {l.lesson_id: l for l in lessons}
        
        # Clear existing data
        for i in range(self.rowCount()):
            for j in range(self.columnCount()):
                item = self.item(i, j)
                if item:
                    item.setText("")
                    item.setBackground(QColor(255, 255, 255))
        
        # Populate schedule data
        self.schedule_data = {}
        for entry in schedule_entries:
            class_id = entry.get("class_id")
            day = entry.get("day", 0) + 1  # +1 to match table indexing (days start from 1)
            time_slot = entry.get("time_slot", 0) + 1  # +1 to match table indexing (slots start from 1)
            
            if class_id not in self.schedule_data:
                self.schedule_data[class_id] = {}
            if day not in self.schedule_data[class_id]:
                self.schedule_data[class_id][day] = {}
            
            self.schedule_data[class_id][day][time_slot] = entry
            
            # Find the class name
            class_name = "Unknown"
            for cls in classes:
                if cls.class_id == class_id:
                    class_name = cls.name
                    break
            
            # Get teacher and lesson info
            teacher = self.teachers.get(entry.get("teacher_id", -1))
            lesson = self.lessons.get(entry.get("lesson_id", -1))
            
            teacher_name = teacher.name if teacher else "Unknown"
            lesson_name = lesson.name if lesson else "Unknown"
            
            # Set the item text and style
            item = QTableWidgetItem(f"{lesson_name}\n{teacher_name}")
            item.setTextAlignment(Qt.AlignCenter)
            
            # Color coding based on lesson type
            if "Matematik" in lesson_name or "Fizik" in lesson_name or "Kimya" in lesson_name:
                # Science subjects in blue
                item.setBackground(QColor(173, 216, 230))
            elif "Beden" in lesson_name or "Müzik" in lesson_name or "Sanat" in lesson_name:
                # PE and arts in green
                item.setBackground(QColor(144, 238, 144))
            else:
                # Other subjects in light yellow
                item.setBackground(QColor(255, 255, 224))
            
            self.setItem(class_id % (self.rowCount()-1) + 1, time_slot, item)
        
        self.update()
    
    def set_class_selection(self, class_id: int):
        """Highlight a specific class in the preview"""
        # This would highlight the row for the selected class
        pass


class SchedulePreviewDialog(QWidget):
    """
    Dialog that shows real-time schedule preview during generation
    """
    
    def __init__(self, parent=None, db_manager=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.setWindowTitle("Real-time Schedule Preview")
        self.setGeometry(200, 200, 1200, 800)
        
        self.preview_widget = RealTimeSchedulePreviewWidget()
        self.setup_ui()
        
        # Timer for updating the preview (in a real implementation)
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_preview)
        self.update_timer.setInterval(1000)  # Update every second
        
        # Store original schedule data for comparison
        self.original_entries = []
        
    def setup_ui(self):
        """Setup the main UI"""
        layout = QVBoxLayout()
        
        # Title
        title_label = QLabel("Real-time Schedule Preview")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        layout.addWidget(title_label)
        
        # Info panel
        info_layout = QHBoxLayout()
        
        # Stats group
        stats_group = QGroupBox("Schedule Statistics")
        stats_layout = QHBoxLayout()
        
        self.coverage_label = QLabel("Coverage: 0%")
        self.conflicts_label = QLabel("Conflicts: 0")
        self.entries_label = QLabel("Entries: 0")
        
        stats_layout.addWidget(self.coverage_label)
        stats_layout.addWidget(self.conflicts_label) 
        stats_layout.addWidget(self.entries_label)
        
        stats_group.setLayout(stats_layout)
        info_layout.addWidget(stats_group)
        
        # Controls
        controls_layout = QHBoxLayout()
        self.pause_button = QPushButton("Pause Updates")
        self.pause_button.clicked.connect(self.toggle_updates)
        self.reset_button = QPushButton("Reset Preview")
        self.reset_button.clicked.connect(self.reset_preview)
        
        controls_layout.addWidget(self.pause_button)
        controls_layout.addWidget(self.reset_button)
        controls_layout.addStretch()
        
        info_layout.addLayout(controls_layout)
        layout.addLayout(info_layout)
        
        # Preview widget
        layout.addWidget(self.preview_widget)
        
        # Status bar
        self.status_label = QLabel("Ready to show schedule preview...")
        layout.addWidget(self.status_label)
        
        self.setLayout(layout)
        
        # Set initial state
        self.updates_paused = False
        self.update_button_text()
        
    def update_preview(self):
        """Update the preview with latest schedule data"""
        if self.updates_paused or not self.db_manager:
            return
            
        try:
            # Get current schedule data
            classes = self.db_manager.get_all_classes() or []
            teachers = self.db_manager.get_all_teachers() or []
            lessons = self.db_manager.get_all_lessons() or []
            current_entries = self.db_manager.get_schedule_program_by_school_type() or []
            
            # Update the preview widget
            self.preview_widget.update_schedule_preview(current_entries, classes, teachers, lessons)
            
            # Update statistics
            total_slots = len(classes) * 5 * 8  # 5 days, max 8 slots per day
            scheduled_count = len(current_entries)
            coverage = (scheduled_count / total_slots * 100) if total_slots > 0 else 0
            
            # Count conflicts (simplified - in a real app you'd check the actual conflicts)
            # For demo purposes, we'll just count entries
            conflicts = 0  # This would actually check for conflicts
            
            self.coverage_label.setText(f"Coverage: {coverage:.1f}% ({scheduled_count}/{total_slots})")
            self.conflicts_label.setText(f"Conflicts: {conflicts}")
            self.entries_label.setText(f"Entries: {scheduled_count}")
            
            # Update status
            self.status_label.setText(f"Updated preview at {time.strftime('%H:%M:%S')}. {scheduled_count} entries shown.")
            
        except Exception as e:
            self.status_label.setText(f"Error updating preview: {str(e)}")
    
    def toggle_updates(self):
        """Toggle between pause and resume updates"""
        self.updates_paused = not self.updates_paused
        if self.updates_paused:
            self.update_timer.stop()
            self.status_label.setText("Updates paused. Click 'Resume Updates' to continue.")
        else:
            self.update_timer.start()
            self.status_label.setText("Updates resumed. Preview updates every second.")
        
        self.update_button_text()
    
    def update_button_text(self):
        """Update the pause/resume button text"""
        if self.updates_paused:
            self.pause_button.setText("Resume Updates")
        else:
            self.pause_button.setText("Pause Updates")
    
    def reset_preview(self):
        """Reset the preview to empty state"""
        self.preview_widget.clear()
        self.coverage_label.setText("Coverage: 0% (0/0)")
        self.conflicts_label.setText("Conflicts: 0")
        self.entries_label.setText("Entries: 0")
        self.status_label.setText("Preview reset. Ready to show new schedule data.")
    
    def start_updates(self):
        """Start the preview updates"""
        if not self.update_timer.isActive():
            self.update_timer.start()
    
    def stop_updates(self):
        """Stop the preview updates"""
        if self.update_timer.isActive():
            self.update_timer.stop()


if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    import time
    
    app = QApplication(sys.argv)
    
    # Create a demo dialog
    dialog = SchedulePreviewDialog()
    dialog.show()
    
    sys.exit(app.exec_())