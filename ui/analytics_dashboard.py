#!/usr/bin/env python3
"""
Analytics Dashboard for Schedule Management System
Advanced analytics with interactive visualizations
"""

import io
import sys

if sys.platform.startswith("win"):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    else:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

from PyQt5.QtCore import (
    QDateTime,
    Qt,
    QTimer,
    QThread,
    QUrl,
    pyqtSignal,
    QPropertyAnimation,
    QEasingCurve,
    QSize,
)
from PyQt5.QtGui import QFont, QColor, QPalette, QPainter, QPen, QBrush, QLinearGradient
from PyQt5.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
    QScrollArea,
    QGridLayout,
    QProgressBar,
    QGraphicsDropShadowEffect,
    QSplitter,
    QComboBox,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QTextEdit,
    QPushButton,
    QMessageBox,
)

from database import db_manager
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import seaborn as sns

# Configure matplotlib for high DPI displays
plt.rcParams['figure.dpi'] = 100
plt.rcParams['savefig.dpi'] = 150
sns.set_palette("husl")


class AnalyticsCard(QFrame):
    """Advanced analytics card with animations"""

    def __init__(
        self,
        title: str,
        value: Any,
        subtitle: str = "",
        trend: Optional[float] = None,
        color: str = "#3498db",
        icon: str = "📊",
        parent=None,
    ):
        super().__init__(parent)
        self.color = color
        self.target_value = value
        self.current_value = 0
        self.setup_ui(title, value, subtitle, trend, icon)
        self.animate_value()

    def setup_ui(self, title, value, subtitle, trend, icon):
        """Setup the card UI"""
        self.setObjectName("analyticsCard")
        self.setMinimumHeight(150)

        # Shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setOffset(0, 8)
        shadow.setColor(QColor(0, 0, 0, 50))
        self.setGraphicsEffect(shadow)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(25, 20, 25, 20)
        layout.setSpacing(15)

        # Icon section
        icon_widget = QWidget()
        icon_widget.setFixedWidth(70)
        icon_layout = QVBoxLayout(icon_widget)
        icon_layout.setContentsMargins(0, 0, 0, 0)

        icon_label = QLabel(icon)
        icon_label.setFont(QFont("Segoe UI Emoji", 36))
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet(f"color: {self.color};")
        icon_layout.addWidget(icon_label)

        layout.addWidget(icon_widget, 0)

        # Content section
        content_layout = QVBoxLayout()
        content_layout.setSpacing(8)

        # Title
        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 14, QFont.Bold))
        title_label.setStyleSheet("color: #2c3e50;")
        content_layout.addWidget(title_label)

        # Value
        self.value_label = QLabel(str(value))
        self.value_label.setFont(QFont("Segoe UI", 32, QFont.Bold))
        self.value_label.setStyleSheet(f"color: {self.color};")
        content_layout.addWidget(self.value_label)

        # Subtitle and trend
        bottom_layout = QHBoxLayout()

        subtitle_label = QLabel(subtitle)
        subtitle_label.setFont(QFont("Segoe UI", 10))
        subtitle_label.setStyleSheet("color: #7f8c8d;")
        bottom_layout.addWidget(subtitle_label)

        bottom_layout.addStretch()

        if trend is not None:
            trend_color = "#27ae60" if trend >= 0 else "#e74c3c"
            trend_icon = "↗️" if trend >= 0 else "↘️"
            trend_label = QLabel(f"{trend_icon} {abs(trend):.1f}%")
            trend_label.setFont(QFont("Segoe UI", 10, QFont.Bold))
            trend_label.setStyleSheet(f"color: {trend_color};")
            bottom_layout.addWidget(trend_label)

        content_layout.addLayout(bottom_layout)
        layout.addLayout(content_layout, 1)

        # Styling
        self.setStyleSheet(
            f"""
            QFrame#analyticsCard {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #ffffff, stop:1 #f8f9fa);
                border-radius: 15px;
                border: 2px solid #e9ecef;
            }}
            QFrame#analyticsCard:hover {{
                border: 2px solid {self.color};
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #ffffff, stop:1 #f0f9ff);
            }}
        """
        )

    def animate_value(self):
        """Animate the value display"""
        if isinstance(self.target_value, (int, float)):
            self.animation = QPropertyAnimation(self, b"animated_value")
            self.animation.setStartValue(0)
            self.animation.setEndValue(self.target_value)
            self.animation.setDuration(1000)
            self.animation.setEasingCurve(QEasingCurve.OutCubic)
            self.animation.start()

    def set_animated_value(self, value):
        """Set animated value"""
        if isinstance(value, float):
            self.value_label.setText(f"{value:.1f}")
        else:
            self.value_label.setText(str(value))

    def get_animated_value(self):
        """Get current animated value"""
        return self.current_value

    animated_value = property(get_animated_value, set_animated_value)


class DataLoaderThread(QThread):
    """Background data loading thread"""

    progress = pyqtSignal(str)
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)

    def run(self):
        try:
            self.progress.emit("🔍 Analiz verileri hazırlanıyor...")

            # Load comprehensive analytics data
            analytics_data = {
                'summary': self._load_summary_stats(),
                'schedule_analysis': self._load_schedule_analysis(),
                'teacher_workload': self._load_teacher_workload(),
                'class_utilization': self._load_class_utilization(),
                'time_distribution': self._load_time_distribution(),
                'performance_metrics': self._load_performance_metrics(),
            }

            self.progress.emit("📊 Görselleştirmeler hazırlanıyor...")
            # Generate charts data
            analytics_data['charts'] = self._generate_charts_data(analytics_data)

            self.progress.emit("✅ Analiz tamamlandı!")
            self.finished.emit(analytics_data)

        except Exception as e:
            self.logger.error(f"Analytics loading error: {e}")
            self.error.emit(f"Analiz verisi yüklenirken hata: {str(e)}")

    def _load_summary_stats(self) -> Dict:
        """Load summary statistics"""
        classes = db_manager.get_all_classes()
        teachers = db_manager.get_all_teachers()
        lessons = db_manager.get_all_lessons()
        schedule_entries = db_manager.get_schedule_program_by_school_type()

        return {
            'total_classes': len(classes),
            'total_teachers': len(teachers),
            'total_lessons': len(lessons),
            'total_schedule_entries': len(schedule_entries),
            'school_type': db_manager.get_school_type() or "Lise",
        }

    def _load_schedule_analysis(self) -> Dict:
        """Load detailed schedule analysis"""
        schedule = db_manager.get_schedule_program_by_school_type()
        assignments = db_manager.get_schedule_by_school_type()

        # Calculate coverage
        total_slots = len(db_manager.get_all_classes()) * 5 * 8  # Rough estimate
        coverage_rate = (len(schedule) / total_slots * 100) if total_slots > 0 else 0

        # Conflict analysis
        conflicts = self._analyze_conflicts(schedule)

        # Day distribution
        day_distribution = {}
        for entry in schedule:
            day_name = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"][entry.day]
            day_distribution[day_name] = day_distribution.get(day_name, 0) + 1

        return {
            'total_entries': len(schedule),
            'coverage_rate': coverage_rate,
            'conflicts': conflicts,
            'day_distribution': day_distribution,
            'assigned_lessons': len(assignments),
            'scheduled_lessons': len(schedule),
        }

    def _load_teacher_workload(self) -> Dict:
        """Analyze teacher workload distribution"""
        teachers = db_manager.get_all_teachers()
        schedule = db_manager.get_schedule_program_by_school_type()

        workload = {}
        for teacher in teachers:
            workload[teacher.name] = 0

        for entry in schedule:
            teacher = db_manager.get_teacher_by_id(entry.teacher_id)
            if teacher:
                workload[teacher.name] = workload.get(teacher.name, 0) + 1

        # Calculate statistics
        if workload:
            hours_list = list(workload.values())
            avg_workload = sum(hours_list) / len(hours_list)
            max_workload = max(hours_list)
            min_workload = min(hours_list)

            # Find most/least busy teachers
            most_busy = max(workload.items(), key=lambda x: x[1])
            least_busy = min(workload.items(), key=lambda x: x[1])
        else:
            avg_workload = max_workload = min_workload = 0
            most_busy = least_busy = ("N/A", 0)

        return {
            'workload_distribution': workload,
            'avg_workload': avg_workload,
            'max_workload': max_workload,
            'min_workload': min_workload,
            'most_busy_teacher': most_busy[0],
            'most_busy_hours': most_busy[1],
            'least_busy_teacher': least_busy[0],
            'least_busy_hours': least_busy[1],
        }

    def _load_class_utilization(self) -> Dict:
        """Analyze class utilization"""
        classes = db_manager.get_all_classes()
        schedule = db_manager.get_schedule_program_by_school_type()

        utilization = {}
        for cls in classes:
            utilization[cls.name] = 0

        for entry in schedule:
            cls = db_manager.get_class_by_id(entry.class_id)
            if cls:
                utilization[cls.name] = utilization.get(cls.name, 0) + 1

        return {
            'utilization_by_class': utilization,
            'total_classes': len(classes),
            'scheduled_classes': len([c for c in utilization.values() if c > 0]),
        }

    def _load_time_distribution(self) -> Dict:
        """Analyze time slot distribution"""
        schedule = db_manager.get_schedule_program_by_school_type()

        time_slots = {}
        for i in range(8):  # Assume 8 time slots
            time_slots[f"Period {i+1}"] = 0

        for entry in schedule:
            slot_name = f"Period {entry.time_slot + 1}"
            time_slots[slot_name] = time_slots.get(slot_name, 0) + 1

        return time_slots

    def _load_performance_metrics(self) -> Dict:
        """Load performance metrics (mock data for now)"""
        # In a real system, this would load from performance logs
        return {
            'avg_algorithm_runtime': 2.5,  # seconds
            'total_generations': 1,
            'success_rate': 95.0,  # percentage
            'last_generation_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

    def _analyze_conflicts(self, schedule) -> int:
        """Analyze scheduling conflicts"""
        conflicts = 0

        # Check teacher conflicts
        teacher_slots = set()
        for entry in schedule:
            key = (entry.teacher_id, entry.day, entry.time_slot)
            if key in teacher_slots:
                conflicts += 1
            teacher_slots.add(key)

        # Check class conflicts
        class_slots = set()
        for entry in schedule:
            key = (entry.class_id, entry.day, entry.time_slot)
            if key in class_slots:
                conflicts += 1
            class_slots.add(key)

        return conflicts

    def _generate_charts_data(self, analytics_data: Dict) -> Dict:
        """Generate chart data for visualization"""
        return {
            'workload_chart': analytics_data['teacher_workload']['workload_distribution'],
            'day_distribution_chart': analytics_data['schedule_analysis']['day_distribution'],
            'time_distribution_chart': analytics_data['time_distribution'],
            'utilization_chart': analytics_data['class_utilization']['utilization_by_class'],
        }


class MatplotlibCanvas(FigureCanvas):
    """Matplotlib canvas for embedding plots"""

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig, self.axes = plt.subplots(figsize=(width, height), dpi=dpi)
        super().__init__(self.fig)
        self.setParent(parent)

    def plot_workload_distribution(self, data: Dict[str, int]):
        """Plot teacher workload distribution"""
        self.axes.clear()
        if data:
            names = list(data.keys())[:10]  # Show top 10
            values = [data[name] for name in names]

            bars = self.axes.bar(names, values, color='#3498db', alpha=0.7)
            self.axes.set_title('Öğretmen Ders Dağılımı', fontsize=12, pad=20)
            self.axes.set_xlabel('Öğretmenler', fontsize=10)
            self.axes.set_ylabel('Ders Saati', fontsize=10)
            self.axes.tick_params(axis='x', rotation=45)
            self.axes.grid(True, alpha=0.3)

            # Add value labels on bars
            for bar in bars:
                height = bar.get_height()
                self.axes.text(bar.get_x() + bar.get_width()/2., height,
                             f'{int(height)}', ha='center', va='bottom', fontsize=9)

        self.axes.figure.tight_layout()
        self.draw()

    def plot_day_distribution(self, data: Dict[str, int]):
        """Plot day distribution"""
        self.axes.clear()
        if data:
            days = list(data.keys())
            values = list(data.values())

            self.axes.pie(values, labels=days, autopct='%1.1f%%', startangle=90)
            self.axes.set_title('Günlük Ders Dağılımı', fontsize=12, pad=20)

        self.axes.figure.tight_layout()
        self.draw()

    def plot_time_distribution(self, data: Dict[str, int]):
        """Plot time slot distribution"""
        self.axes.clear()
        if data:
            slots = list(data.keys())
            values = list(data.values())

            colors = ['#3498db', '#2ecc71', '#e74c3c', '#f39c12', '#9b59b6', '#1abc9c', '#34495e', '#e67e22']
            bars = self.axes.bar(slots, values, color=colors[:len(slots)], alpha=0.7)
            self.axes.set_title('Zaman Dilimi Dağılımı', fontsize=12, pad=20)
            self.axes.set_xlabel('Ders Saati', fontsize=10)
            self.axes.set_ylabel('Ders Sayısı', fontsize=10)
            self.axes.grid(True, alpha=0.3)

            # Add value labels
            for bar in bars:
                height = bar.get_height()
                self.axes.text(bar.get_x() + bar.get_width()/2., height,
                             f'{int(height)}', ha='center', va='bottom', fontsize=9)

        self.axes.figure.tight_layout()
        self.draw()


class AnalyticsDashboard(QWidget):
    """Advanced Analytics Dashboard with Real-time Monitoring"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.analytics_data = {}
        self.loader_thread = None
        self.charts = {}
        self.setup_ui()
        self.load_analytics_data()

    def setup_ui(self):
        """Setup the analytics dashboard UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(25)

        # Header
        header = self.create_header_section()
        main_layout.addWidget(header)

        # Cards section
        self.cards_section = self.create_cards_section()
        main_layout.addWidget(self.cards_section)

        # Content splitter
        self.content_splitter = QSplitter(Qt.Horizontal)
        self.content_splitter.setSizes([400, 600])

        # Statistics panel
        stats_panel = self.create_statistics_panel()
        self.content_splitter.addWidget(stats_panel)

        # Charts panel
        charts_panel = self.create_charts_panel()
        self.content_splitter.addWidget(charts_panel)

        main_layout.addWidget(self.content_splitter)

        # Loading overlay (hidden by default)
        self.loading_overlay = self.create_loading_overlay()
        self.loading_overlay.setVisible(False)
        main_layout.addWidget(self.loading_overlay)

        # Apply styling
        self.apply_global_styles()

        # Resize splitter appropriately
        self.content_splitter.setSizes([350, 650])

    def create_header_section(self):
        """Create dashboard header"""
        header = QFrame()
        header.setObjectName("dashboardHeader")

        layout = QVBoxLayout(header)
        layout.setContentsMargins(0, 0, 0, 20)

        # Title
        title_layout = QHBoxLayout()

        icon = QLabel("📊")
        icon.setFont(QFont("Segoe UI Emoji", 36))
        title_layout.addWidget(icon)

        title = QLabel("ANALİTİK DASHBOARD")
        title.setFont(QFont("Segoe UI", 28, QFont.Bold))
        title.setStyleSheet("color: white; letter-spacing: 2px;")
        title_layout.addWidget(title)

        title_layout.addStretch()
        layout.addLayout(title_layout)

        # Subtitle
        subtitle = QLabel("Gerçek zamanlı performans analizi ve istatistikler")
        subtitle.setFont(QFont("Segoe UI", 12))
        subtitle.setStyleSheet("color: rgba(255, 255, 255, 0.9);")
        layout.addWidget(subtitle)

        # Controls
        controls = QHBoxLayout()
        controls.addStretch()

        refresh_btn = QPushButton("🔄 Yenile")
        refresh_btn.setFont(QFont("Segoe UI", 10, QFont.Bold))
        refresh_btn.clicked.connect(self.refresh_data)
        refresh_btn.setStyleSheet(
            """
            QPushButton {
                padding: 8px 16px;
                border: 2px solid white;
                border-radius: 8px;
                color: white;
                background: rgba(255, 255, 255, 0.2);
                font-weight: bold;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.3);
                border: 2px solid #3498db;
            }
        """
        )
        controls.addWidget(refresh_btn)

        export_btn = QPushButton("💾 Raporu Dışa Aktar")
        export_btn.setFont(QFont("Segoe UI", 10, QFont.Bold))
        export_btn.clicked.connect(self.export_report)
        export_btn.setStyleSheet(
            """
            QPushButton {
                padding: 8px 16px;
                border: 2px solid white;
                border-radius: 8px;
                color: white;
                background: rgba(255, 255, 255, 0.2);
                font-weight: bold;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.3);
                border: 2px solid #27ae60;
            }
        """
        )
        controls.addWidget(export_btn)

        layout.addLayout(controls)

        header.setStyleSheet(
            """
            QFrame#dashboardHeader {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #667eea, stop:0.5 #764ba2, stop:1 #f093fb);
                border-radius: 15px;
                padding: 20px;
                color: white;
            }
        """
        )

        return header

    def create_cards_section(self):
        """Create analytics cards section"""
        container = QFrame()
        container.setObjectName("cardsContainer")

        # Initially empty, will be populated when data loads
        self.cards_layout = QHBoxLayout(container)
        self.cards_layout.setSpacing(15)
        self.cards_layout.setContentsMargins(0, 0, 0, 0)

        # Placeholder cards
        self.create_placeholder_cards()

        return container

    def create_placeholder_cards(self):
        """Create placeholder cards while data loads"""
        placeholders = [
            ("📚 Toplam Ders", "0", "Yükleniyor...", "#3498db", "🏫"),
            ("👨‍🏫 Toplam Öğretmen", "0", "Yükleniyor...", "#27ae60", "👨‍🏫"),
            ("🎯 Kapsama Oranı", "0%", "Yükleniyor...", "#f39c12", "🎯"),
            ("⚠️ Çakışmalar", "0", "Yükleniyor...", "#e74c3c", "⚠️"),
        ]

        for title, value, subtitle, color, icon in placeholders:
            card = AnalyticsCard(title, value, subtitle, color=color, icon=icon)
            self.cards_layout.addWidget(card)

    def create_statistics_panel(self):
        """Create detailed statistics panel"""
        panel = QFrame()
        panel.setObjectName("statsPanel")

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Panel title
        panel_title = QLabel("Detaylı İstatistikler")
        panel_title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        panel_title.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        layout.addWidget(panel_title)

        # Statistics display
        self.stats_display = QTextEdit()
        self.stats_display.setReadOnly(True)
        self.stats_display.setFont(QFont("Consolas", 10))
        self.stats_display.setStyleSheet(
            """
            QTextEdit {
                background: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 10px;
            }
        """
        )
        layout.addWidget(self.stats_display)

        # Insights section
        insights_title = QLabel("💡 Öneriler ve İçgörüler")
        insights_title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        insights_title.setStyleSheet("color: #2c3e50; margin-top: 15px;")
        layout.addWidget(insights_title)

        self.insights_display = QTextEdit()
        self.insights_display.setReadOnly(True)
        self.insights_display.setFont(QFont("Segoe UI", 10))
        self.insights_display.setStyleSheet(
            """
            QTextEdit {
                background: #fff3cd;
                border: 1px solid #ffeaa7;
                border-radius: 8px;
                padding: 10px;
            }
        """
        )
        self.insights_display.setPlainText("📊 Analiz verisi yükleniyor...")
        layout.addWidget(self.insights_display)

        return panel

    def create_charts_panel(self):
        """Create charts visualization panel"""
        panel = QFrame()
        panel.setObjectName("chartsPanel")

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Panel title
        panel_title = QLabel("Grafiksel Analizler")
        panel_title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        panel_title.setStyleSheet("color: #2c3e50;")
        layout.addWidget(panel_title)

        # Chart selector
        selector_layout = QHBoxLayout()
        selector_layout.addWidget(QLabel("Grafik:"))

        self.chart_selector = QComboBox()
        self.chart_selector.addItems([
            "Öğretmen İş Yükü Dağılımı",
            "Günlük Ders Dağılımı",
            "Saat Dağılımı",
            "Sınıf Kullanım Oranı"
        ])
        self.chart_selector.currentTextChanged.connect(self.update_chart_display)
        selector_layout.addWidget(self.chart_selector)

        selector_layout.addStretch()
        layout.addLayout(selector_layout)

        # Chart container
        self.chart_container = QFrame()
        self.chart_container.setMinimumHeight(400)
        self.chart_container.setStyleSheet(
            """
            QFrame {
                background: white;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 10px;
            }
        """
        )

        chart_layout = QVBoxLayout(self.chart_container)

        # Placeholder for chart
        placeholder = QLabel("📊 Grafik yükleniyor...")
        placeholder.setAlignment(Qt.AlignCenter)
        placeholder.setFont(QFont("Segoe UI", 14))
        placeholder.setStyleSheet("color: #6c757d;")
        chart_layout.addWidget(placeholder)

        layout.addWidget(self.chart_container)

        return panel

    def create_loading_overlay(self):
        """Create loading overlay"""
        overlay = QFrame()
        overlay.setObjectName("loadingOverlay")

        layout = QVBoxLayout(overlay)
        layout.setAlignment(Qt.AlignCenter)

        loading_label = QLabel("🔄 Analitik Veriler Yükleniyor...")
        loading_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        loading_label.setStyleSheet("color: #3498db;")
        layout.addWidget(loading_label)

        self.loading_progress = QProgressBar()
        self.loading_progress.setMaximumWidth(300)
        self.loading_progress.setRange(0, 0)  # Indeterminate progress
        layout.addWidget(self.loading_progress)

        overlay.setStyleSheet(
            """
            QFrame#loadingOverlay {
                background: rgba(255, 255, 255, 0.9);
                border-radius: 15px;
                margin: 20px;
            }
        """
        )

        return overlay

    def apply_global_styles(self):
        """Apply global styling"""
        self.setStyleSheet(
            """
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f5f7fa, stop:1 #e3e8ef);
                font-family: "Segoe UI", Arial, sans-serif;
            }
        """
        )

    def load_analytics_data(self):
        """Load analytics data in background thread"""
        self.loading_overlay.setVisible(True)
        self.loader_thread = DataLoaderThread()

        self.loader_thread.progress.connect(self.update_loading_progress)
        self.loader_thread.finished.connect(self.on_data_loaded)
        self.loader_thread.error.connect(self.on_data_error)

        self.loader_thread.start()

    def update_loading_progress(self, message: str):
        """Update loading progress"""
        # Find loading label and update text
        loading_label = self.loading_overlay.findChild(QLabel)
        if loading_label:
            loading_label.setText(message)

    def on_data_loaded(self, analytics_data: Dict):
        """Handle loaded analytics data"""
        self.loading_overlay.setVisible(False)
        self.analytics_data = analytics_data

        # Update UI with data
        self.update_cards()
        self.update_statistics_display()
        self.update_insights_display()
        self.initialize_charts()

    def on_data_error(self, error_msg: str):
        """Handle data loading error"""
        self.loading_overlay.setVisible(False)

        QMessageBox.critical(self, "Hata", f"Analitik veri yüklenirken hata:\n\n{error_msg}")

    def update_cards(self):
        """Update analytics cards with real data"""
        # Clear existing cards
        while self.cards_layout.count():
            item = self.cards_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.setParent(None)

        summary = self.analytics_data.get('summary', {})
        schedule = self.analytics_data.get('schedule_analysis', {})
        teacher = self.analytics_data.get('teacher_workload', {})

        cards_data = [
            (
                f"📚 Toplam Ders",
                summary.get('total_schedule_entries', 0),
                f"{summary.get('total_lessons', 0)} tür ders",
                None,
                "#3498db",
                "📚"
            ),
            (
                f"👨‍🏫 Toplam Öğretmen",
                summary.get('total_teachers', 0),
                ".1f",
                None,
                "#27ae60",
                "👨‍🏫"
            ),
            (
                f"🏫 Kapsama Oranı",
                ".1f",
                f"{schedule.get('total_entries', 0)} ders yerleştirildi",
                None,
                "#f39c12",
                "🏫"
            ),
            (
                f"⚠️ Çakışmalar",
                schedule.get('conflicts', 0),
                "Algoritma çakışması" if schedule.get('conflicts', 0) == 0 else "Gözden geçirin",
                None,
                "#27ae60" if schedule.get('conflicts', 0) == 0 else "#e74c3c",
                "⚠️"
            ),
        ]

        for title, value, subtitle, trend, color, icon in cards_data:
            card = AnalyticsCard(title, value, subtitle, trend, color, icon)
            self.cards_layout.addWidget(card)

    def update_statistics_display(self):
        """Update detailed statistics display"""
        summary = self.analytics_data.get('summary', {})
        schedule = self.analytics_data.get('schedule_analysis', {})
        teacher = self.analytics_data.get('teacher_workload', {})
        utilization = self.analytics_data.get('class_utilization', {})

        stats_text = f"""
📊 DERS DAĞITIM SİSTEMİ ANALİZİ
{'='*50}

🗓️  OKUL TİPİ: {summary.get('school_type', 'Bilinmiyor')}

🏫 TEMEL İSTATİSTİKLER:
   • Toplam Sınıf: {summary.get('total_classes', 0)}
   • Toplam Öğretmen: {summary.get('total_teachers', 0)}
   • Toplam Ders Türü: {summary.get('total_lessons', 0)}
   • Planlanan Ders: {schedule.get('assigned_lessons', 0)}
   • Yerleştirilen Ders: {schedule.get('total_entries', 0)}

📈 PROGRAM ANALİZİ:
   • Kapsama Oranı: {schedule.get('coverage_rate', 0):.1f}%
   • Toplam Çakışma: {schedule.get('conflicts', 0)}
   • Kullanılan Sınıf: {utilization.get('scheduled_classes', 0)}/{utilization.get('total_classes', 0)}

👨‍🏫 ÖĞRETMEN ANALİZİ:
   • Ortalama İş Yükü: {teacher.get('avg_workload', 0):.1f} saat
   • Max İş Yükü: {teacher.get('max_workload', 0)} saat ({teacher.get('most_busy_teacher', 'N/A')})
   • Min İş Yükü: {teacher.get('min_workload', 0)} saat ({teacher.get('least_busy_teacher', 'N/A')})

📅 GÜNLÜK DAĞILIM:
"""

        day_dist = schedule.get('day_distribution', {})
        for day, count in day_dist.items():
            stats_text += f"   • {day}: {count} ders\n"

        stats_text += f"""

🕐 SAAT DAĞILIM ANALİZİ:
"""
        time_dist = self.analytics_data.get('time_distribution', {})
        for slot, count in time_dist.items():
            if count > 0:
                stats_text += f"   • {slot}: {count} ders\n"

        self.stats_display.setPlainText(stats_text.strip())

    def update_insights_display(self):
        """Update insights and recommendations"""
        insights = []

        schedule = self.analytics_data.get('schedule_analysis', {})
        teacher = self.analytics_data.get('teacher_workload', {})
        utilization = self.analytics_data.get('class_utilization', {})

        # Coverage insights
        coverage = schedule.get('coverage_rate', 0)
        if coverage < 70:
            insights.append("⚠️ Düşük kapsama oranı - daha güçlü algoritma kullanın")
        elif coverage > 95:
            insights.append("✅ Mükemmel kapsama oranı!")

        # Conflict insights
        conflicts = schedule.get('conflicts', 0)
        if conflicts > 0:
            insights.append(f"🔧 {conflicts} çakışma tespit edildi - manuel düzeltme gerekli")
        else:
            insights.append("✨ Çakışma yok - mükemmel programlama!")

        # Workload insights
        workload_diff = teacher.get('max_workload', 0) - teacher.get('min_workload', 0)
        if workload_diff > 5:
            insights.append(f"⚖️ İş yükü dengesizlik ({workload_diff} saat fark) - yük dengeleme gerekli")
        else:
            insights.append("⚖️ Dengeli iş yükü dağılımı")

        # Utilization insights
        scheduled_classes = utilization.get('scheduled_classes', 0)
        total_classes = utilization.get('total_classes', 0)
        if scheduled_classes < total_classes * 0.8:
            insights.append("📚 Bazı sınıflar az kullanıldı - kaynak optimizasyonu yapılabilir")

        # Performance insights
        if coverage > 90 and conflicts == 0:
            insights.append("🚀 Sistem mükemmel performans gösteriyor!")
        elif coverage > 80:
            insights.append("👍 İyi performans - küçük iyileştirmeler yeterli")
        else:
            insights.append("🔄 Performans iyileştirilebilir - algoritma inceleme gerekli")

        insights_text = "\n".join(f"• {insight}" for insight in insights)
        self.insights_display.setPlainText(insights_text)

    def initialize_charts(self):
        """Initialize chart displays"""
        # Remove placeholder
        old_widget = self.chart_container.layout().itemAt(0).widget()
        if old_widget:
            old_widget.setParent(None)

        # Initialize chart canvases
        self.charts = {
            'workload': MatplotlibCanvas(width=8, height=5),
            'day_distribution': MatplotlibCanvas(width=6, height=5),
            'time_distribution': MatplotlibCanvas(width=8, height=5),
            'utilization': MatplotlibCanvas(width=8, height=5),
        }

        # Plot initial charts
        self.update_chart_display()

    def update_chart_display(self):
        """Update displayed chart based on selector"""
        chart_type = self.chart_selector.currentText()
        chart_key = ""

        if "Öğretmen İş Yükü" in chart_type:
            chart_key = 'workload'
            self.charts[chart_key].plot_workload_distribution(
                self.analytics_data.get('charts', {}).get('workload_chart', {})
            )
        elif "Günlük Ders" in chart_type:
            chart_key = 'day_distribution'
            self.charts[chart_key].plot_day_distribution(
                self.analytics_data.get('charts', {}).get('day_distribution_chart', {})
            )
        elif "Saat" in chart_type:
            chart_key = 'time_distribution'
            self.charts[chart_key].plot_time_distribution(
                self.analytics_data.get('charts', {}).get('time_distribution_chart', {})
            )
        elif "Sınıf Kullanım" in chart_type:
            chart_key = 'utilization'
            # For utilization, show bar chart of class usage
            self.charts[chart_key].plot_workload_distribution(
                self.analytics_data.get('charts', {}).get('utilization_chart', {})
            )

        # Update container layout
        layout = self.chart_container.layout()
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.setParent(None)

        if chart_key and chart_key in self.charts:
            layout.addWidget(self.charts[chart_key])

    def refresh_data(self):
        """Refresh analytics data"""
        self.load_analytics_data()

    def export_report(self):
        """Export analytics report"""
        if not self.analytics_data:
            QMessageBox.warning(self, "Uyarı", "Dışa aktarılacak veri bulunmuyor!")
            return

        try:
            # Create report content
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"analytics_report_{timestamp}.txt"

            with open(filename, 'w', encoding='utf-8') as f:
                f.write("DERS DAĞITIM SİSTEMİ ANALİZ RAPORU\n")
                f.write("=" * 50 + "\n\n")
                f.write(f"Oluşturulma Tarihi: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n\n")

                # Write statistics
                f.write("TEMEL İSTATİSTİKLER:\n")
                f.write("-" * 30 + "\n")

                summary = self.analytics_data.get('summary', {})
                schedule = self.analytics_data.get('schedule_analysis', {})
                teacher = self.analytics_data.get('teacher_workload', {})

                f.write(f"Okul Türü: {summary.get('school_type', 'N/A')}\n")
                f.write(f"Toplam Sınıf: {summary.get('total_classes', 0)}\n")
                f.write(f"Toplam Öğretmen: {summary.get('total_teachers', 0)}\n")
                f.write(f"Toplam Ders Türü: {summary.get('total_lessons', 0)}\n")
                f.write(f"Kapsama Oranı: {schedule.get('coverage_rate', 0):.1f}%\n")
                f.write(f"Toplam Çakışma: {schedule.get('conflicts', 0)}\n")
                f.write(f"Ortalama Öğretmen İş Yükü: {teacher.get('avg_workload', 0):.1f} saat\n\n")

                # Write insights
                f.write("ÖNERİLER VE İÇGÜRÜLER:\n")
                f.write("-" * 30 + "\n")

                insights_text = self.insights_display.toPlainText()
                f.write(insights_text)
                f.write("\n")

                f.write("\nRapor başarıyla oluşturuldu!")

            QMessageBox.information(
                self, "Başarılı",
                f"Analiz raporu başarıyla oluşturuldu:\n\n{filename}"
            )

        except Exception as e:
            QMessageBox.critical(
                self, "Hata",
                f"Rapor oluşturulurken hata oluştu:\n\n{str(e)}"
            )


# Standalone execution for testing
if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    dashboard = AnalyticsDashboard()
    dashboard.show()
    sys.exit(app.exec_())
