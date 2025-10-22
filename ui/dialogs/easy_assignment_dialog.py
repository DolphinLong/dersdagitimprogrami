# -*- coding: utf-8 -*-
"""
Kolay Ders Atama Dialog - Basit ve hızlı atama/silme işlemleri
"""

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from database import db_manager


class EasyAssignmentDialog(QDialog):
    """Kolay ders atama ve silme dialog'u"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Ders Atama Yönetimi")
        self.resize(1200, 700)
        self.setup_ui()
        self.load_data()
        self.refresh_assignments()

    def setup_ui(self):
        """Ana arayüzü kur"""
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)

        # Sol panel - Filtreler ve toplu işlemler
        left_panel = self.create_left_panel()

        # Orta panel - Atama listesi
        center_panel = self.create_center_panel()

        # Sağ panel - Hızlı atama
        right_panel = self.create_right_panel()

        # Splitter ile panelleri ayır
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(center_panel)
        splitter.addWidget(right_panel)
        splitter.setStretchFactor(0, 1)  # Sol panel
        splitter.setStretchFactor(1, 3)  # Orta panel (en geniş)
        splitter.setStretchFactor(2, 1)  # Sağ panel

        main_layout.addWidget(splitter)

        self.apply_styles()

    def create_left_panel(self):
        """Sol panel - Filtreler ve toplu silme"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setSpacing(15)

        # Başlık
        title = QLabel("Filtreler ve İşlemler")
        title.setFont(QFont("Segoe UI", 11, QFont.Bold))
        title.setStyleSheet("color: #2c3e50; padding: 5px;")
        layout.addWidget(title)

        # Filtreler grubu
        filter_group = QGroupBox("Filtrele")
        filter_layout = QVBoxLayout()
        filter_layout.setSpacing(10)

        # Sınıf filtresi
        filter_layout.addWidget(QLabel("Sınıf:"))
        self.filter_class_combo = QComboBox()
        self.filter_class_combo.addItem("Tümü", None)
        self.filter_class_combo.currentIndexChanged.connect(self.refresh_assignments)
        filter_layout.addWidget(self.filter_class_combo)

        # Öğretmen filtresi
        filter_layout.addWidget(QLabel("Öğretmen:"))
        self.filter_teacher_combo = QComboBox()
        self.filter_teacher_combo.addItem("Tümü", None)
        self.filter_teacher_combo.currentIndexChanged.connect(self.refresh_assignments)
        filter_layout.addWidget(self.filter_teacher_combo)

        # Ders filtresi
        filter_layout.addWidget(QLabel("Ders:"))
        self.filter_lesson_combo = QComboBox()
        self.filter_lesson_combo.addItem("Tümü", None)
        self.filter_lesson_combo.currentIndexChanged.connect(self.refresh_assignments)
        filter_layout.addWidget(self.filter_lesson_combo)

        # Filtreleri temizle
        clear_filter_btn = QPushButton("Filtreleri Temizle")
        clear_filter_btn.clicked.connect(self.clear_filters)
        filter_layout.addWidget(clear_filter_btn)

        filter_group.setLayout(filter_layout)
        layout.addWidget(filter_group)

        # Otomatik doldurma grubu
        auto_group = QGroupBox("Otomatik İşlemler")
        auto_layout = QVBoxLayout()
        auto_layout.setSpacing(10)

        # Eksikleri otomatik doldur butonu
        self.auto_fill_btn = QPushButton("⚡ Eksikleri\nOtomatik Doldur")
        self.auto_fill_btn.setStyleSheet(
            "background-color: #27ae60; color: white; font-weight: bold; font-size: 11px;"
        )
        self.auto_fill_btn.clicked.connect(self.auto_fill_missing_assignments)
        auto_layout.addWidget(self.auto_fill_btn)

        # Bilgi metni
        info_text = QLabel("Müfredatta tanımlı ancak\natanmamış dersleri\notomatik olarak atar.")
        info_text.setStyleSheet("color: #7f8c8d; font-size: 10px; font-weight: normal;")
        info_text.setWordWrap(True)
        auto_layout.addWidget(info_text)

        auto_group.setLayout(auto_layout)
        layout.addWidget(auto_group)

        # Toplu silme grubu
        bulk_group = QGroupBox("Toplu Silme")
        bulk_layout = QVBoxLayout()
        bulk_layout.setSpacing(10)

        # Seçili öğretmenin tüm atamalarını sil
        self.delete_teacher_btn = QPushButton("Öğretmenin Tüm\nAtamaları")
        self.delete_teacher_btn.setStyleSheet(
            "background-color: #e74c3c; color: white; font-size: 11px;"
        )
        self.delete_teacher_btn.clicked.connect(self.delete_teacher_assignments)
        bulk_layout.addWidget(self.delete_teacher_btn)

        # Seçili sınıfın tüm atamalarını sil
        self.delete_class_btn = QPushButton("Sınıfın Tüm\nAtamaları")
        self.delete_class_btn.setStyleSheet(
            "background-color: #e74c3c; color: white; font-size: 11px;"
        )
        self.delete_class_btn.clicked.connect(self.delete_class_assignments)
        bulk_layout.addWidget(self.delete_class_btn)

        # Tüm atamaları sil
        self.delete_all_btn = QPushButton("TÜM ATAMALARI\nSİL")
        self.delete_all_btn.setStyleSheet(
            "background-color: #c0392b; color: white; font-weight: bold; font-size: 11px;"
        )
        self.delete_all_btn.clicked.connect(self.delete_all_assignments)
        bulk_layout.addWidget(self.delete_all_btn)

        bulk_group.setLayout(bulk_layout)
        layout.addWidget(bulk_group)

        layout.addStretch()

        return panel

    def create_center_panel(self):
        """Orta panel - Mevcut atamalar listesi"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setSpacing(10)

        # Başlık ve istatistikler
        header_layout = QHBoxLayout()
        title = QLabel("Mevcut Atamalar")
        title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        title.setStyleSheet("color: #2c3e50;")
        header_layout.addWidget(title)

        self.count_label = QLabel("Toplam: 0")
        self.count_label.setStyleSheet("color: #7f8c8d; font-size: 12px;")
        header_layout.addStretch()
        header_layout.addWidget(self.count_label)

        layout.addLayout(header_layout)

        # Arama
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Ara:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Sınıf, öğretmen veya ders adı...")
        self.search_input.textChanged.connect(self.search_assignments)
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)

        # Tablo
        self.assignments_table = QTableWidget()
        self.assignments_table.setColumnCount(5)
        self.assignments_table.setHorizontalHeaderLabels(
            ["Sınıf", "Ders", "Öğretmen", "Haftalık Saat", "İşlem"]
        )

        # Tablo ayarları
        header = self.assignments_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.Fixed)
        self.assignments_table.setColumnWidth(4, 100)

        self.assignments_table.setAlternatingRowColors(True)
        self.assignments_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.assignments_table.setSelectionMode(QTableWidget.SingleSelection)
        self.assignments_table.verticalHeader().setVisible(False)
        self.assignments_table.verticalHeader().setDefaultSectionSize(45)

        layout.addWidget(self.assignments_table)

        return panel

    def create_right_panel(self):
        """Sağ panel - Toplu atama formu"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setSpacing(15)

        # Başlık ve mod seçici
        header_layout = QHBoxLayout()
        title = QLabel("Toplu Atama")
        title.setFont(QFont("Segoe UI", 11, QFont.Bold))
        title.setStyleSheet("color: #2c3e50; padding: 5px;")
        header_layout.addWidget(title)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        # Öğretmen seçimi (önce öğretmen)
        teacher_group = QGroupBox("1️⃣ Öğretmen Seç")
        teacher_layout = QVBoxLayout()
        teacher_layout.setSpacing(8)

        self.new_teacher_combo = QComboBox()
        self.new_teacher_combo.currentIndexChanged.connect(self.on_teacher_selected)
        teacher_layout.addWidget(self.new_teacher_combo)

        # Öğretmen yük göstergesi
        self.teacher_load_label = QLabel("Mevcut Yük: -")
        self.teacher_load_label.setStyleSheet("color: #7f8c8d; font-size: 10px; padding: 5px;")
        teacher_layout.addWidget(self.teacher_load_label)

        teacher_group.setLayout(teacher_layout)
        layout.addWidget(teacher_group)

        # Ders seçimi (branşa göre filtrelenmiş)
        lesson_group = QGroupBox("2️⃣ Ders Seç")
        lesson_layout = QVBoxLayout()
        lesson_layout.setSpacing(8)

        self.new_lesson_combo = QComboBox()
        self.new_lesson_combo.currentIndexChanged.connect(self.on_lesson_selected)
        lesson_layout.addWidget(self.new_lesson_combo)

        # Ders bilgisi
        self.lesson_info_label = QLabel("")
        self.lesson_info_label.setStyleSheet("color: #7f8c8d; font-size: 10px; padding: 5px;")
        self.lesson_info_label.setWordWrap(True)
        lesson_layout.addWidget(self.lesson_info_label)

        lesson_group.setLayout(lesson_layout)
        layout.addWidget(lesson_group)

        # Sınıf seçimi (çoklu)
        class_group = QGroupBox("3️⃣ Sınıfları Seç (Çoklu)")
        class_layout = QVBoxLayout()
        class_layout.setSpacing(5)

        # Hızlı seçim butonları
        quick_select_layout = QHBoxLayout()
        select_all_btn = QPushButton("Tümünü Seç")
        select_all_btn.clicked.connect(self.select_all_classes)
        select_all_btn.setMaximumHeight(30)
        quick_select_layout.addWidget(select_all_btn)

        deselect_all_btn = QPushButton("Hiçbiri")
        deselect_all_btn.clicked.connect(self.deselect_all_classes)
        deselect_all_btn.setMaximumHeight(30)
        quick_select_layout.addWidget(deselect_all_btn)
        class_layout.addLayout(quick_select_layout)

        # Sınıf checkboxları için scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setMaximumHeight(200)

        scroll_widget = QWidget()
        self.class_checkboxes_layout = QVBoxLayout(scroll_widget)
        self.class_checkboxes_layout.setSpacing(5)
        self.class_checkboxes = []

        scroll.setWidget(scroll_widget)
        class_layout.addWidget(scroll)

        class_group.setLayout(class_layout)
        layout.addWidget(class_group)

        # Toplu atama butonu
        self.bulk_assign_btn = QPushButton("✓ TOPLU ATAMA YAP")
        self.bulk_assign_btn.setMinimumHeight(50)
        self.bulk_assign_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #27ae60;
                color: white;
                font-weight: bold;
                font-size: 14px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
            }
        """
        )
        self.bulk_assign_btn.clicked.connect(self.bulk_assign)
        self.bulk_assign_btn.setEnabled(False)
        layout.addWidget(self.bulk_assign_btn)

        # Bilgi kutusu
        info_label = QLabel(
            "<b>💡 Nasıl Kullanılır:</b><br><br>"
            "1. Önce öğretmen seçin<br>"
            "2. Atanacak dersi seçin<br>"
            "3. Birden fazla sınıf seçin<br>"
            "4. Toplu atama yapın<br><br>"
            "<b>Avantajlar:</b><br>"
            "• Tek seferde çok atama<br>"
            "• Tüm dersler görünür<br>"
            "• Öğretmen yükü görünür"
        )
        info_label.setStyleSheet(
            """
            QLabel {
                background-color: #e3f2fd;
                border-left: 4px solid #2196f3;
                padding: 12px;
                border-radius: 5px;
                color: #2c3e50;
                font-size: 10px;
            }
        """
        )
        info_label.setWordWrap(True)
        layout.addWidget(info_label)

        layout.addStretch()

        return panel

    def load_data(self):
        """Verileri yükle"""
        # Sınıfları yükle
        classes = db_manager.get_all_classes()
        
        # Filtre combo'ya ekle
        for cls in classes:
            self.filter_class_combo.addItem(f"{cls.name} (Seviye {cls.grade})", cls.class_id)
        
        # Checkbox'lar oluştur
        for cls in classes:
            checkbox = QCheckBox(f"{cls.name} (Seviye {cls.grade})")
            checkbox.setProperty("class_id", cls.class_id)
            checkbox.stateChanged.connect(self.update_bulk_assign_button)
            self.class_checkboxes.append(checkbox)
            self.class_checkboxes_layout.addWidget(checkbox)

        # Öğretmenleri yükle
        teachers = db_manager.get_all_teachers()
        for combo in [self.filter_teacher_combo, self.new_teacher_combo]:
            for teacher in teachers:
                combo.addItem(f"{teacher.name} ({teacher.subject})", teacher.teacher_id)

        # Dersleri yükle (başlangıçta boş - öğretmen seçilince dolacak)
        lessons = db_manager.get_all_lessons()
        for combo in [self.filter_lesson_combo]:
            for lesson in lessons:
                combo.addItem(lesson.name, lesson.lesson_id)
        
        # ComboBox'ların dropdown arka planını beyaz yap
        self._fix_combobox_backgrounds()

    def refresh_assignments(self):
        """Atama listesini yenile"""
        # Filtreleri al
        class_id = self.filter_class_combo.currentData()
        teacher_id = self.filter_teacher_combo.currentData()
        lesson_id = self.filter_lesson_combo.currentData()

        # Tüm atamaları al
        all_assignments = db_manager.get_schedule_by_school_type()

        # Filtreleme
        filtered = []
        for assignment in all_assignments:
            if class_id and assignment.class_id != class_id:
                continue
            if teacher_id and assignment.teacher_id != teacher_id:
                continue
            if lesson_id and assignment.lesson_id != lesson_id:
                continue
            filtered.append(assignment)

        # Tabloyu doldur
        self.assignments_table.setRowCount(0)

        for assignment in filtered:
            # Bilgileri al
            cls = db_manager.get_class_by_id(assignment.class_id)
            lesson = db_manager.get_lesson_by_id(assignment.lesson_id)
            teacher = db_manager.get_teacher_by_id(assignment.teacher_id)

            if not (cls and lesson and teacher):
                continue

            # Haftalık saat bilgisi
            weekly_hours = db_manager.get_weekly_hours_for_lesson(lesson.lesson_id, cls.grade)

            # Satır ekle
            row = self.assignments_table.rowCount()
            self.assignments_table.insertRow(row)

            # Hücreler
            self.assignments_table.setItem(row, 0, QTableWidgetItem(cls.name))
            self.assignments_table.setItem(row, 1, QTableWidgetItem(lesson.name))
            self.assignments_table.setItem(row, 2, QTableWidgetItem(teacher.name))
            self.assignments_table.setItem(row, 3, QTableWidgetItem(str(weekly_hours or 0)))

            # Sil butonu - container ile merkezlenmiş
            delete_btn = QPushButton("Sil")
            delete_btn.setStyleSheet(
                """
                QPushButton {
                    background-color: #e74c3c; 
                    color: white; 
                    border: none; 
                    border-radius: 4px;
                    padding: 6px 20px;
                    font-size: 11px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #c0392b;
                }
            """
            )
            delete_btn.setFixedWidth(70)
            delete_btn.clicked.connect(
                lambda checked, entry_id=assignment.entry_id: self.delete_single_assignment(
                    entry_id
                )
            )

            # Butonu merkezlemek için container widget
            container = QWidget()
            container_layout = QHBoxLayout(container)
            container_layout.addWidget(delete_btn)
            container_layout.setAlignment(Qt.AlignCenter)
            container_layout.setContentsMargins(5, 2, 5, 2)

            self.assignments_table.setCellWidget(row, 4, container)

        # Sayacı güncelle
        self.count_label.setText(f"Toplam: {len(filtered)}")

    def search_assignments(self, text):
        """Tabloda arama yap"""
        for row in range(self.assignments_table.rowCount()):
            match = False
            for col in range(3):  # İlk 3 sütunda ara
                item = self.assignments_table.item(row, col)
                if item and text.lower() in item.text().lower():
                    match = True
                    break
            self.assignments_table.setRowHidden(row, not match)

    def clear_filters(self):
        """Filtreleri temizle"""
        self.filter_class_combo.setCurrentIndex(0)
        self.filter_teacher_combo.setCurrentIndex(0)
        self.filter_lesson_combo.setCurrentIndex(0)
    
    def _fix_combobox_backgrounds(self):
        """Tüm ComboBox'ların dropdown arka planını beyaz yap"""
        comboboxes = [
            self.filter_class_combo,
            self.filter_teacher_combo, 
            self.filter_lesson_combo,
            self.new_teacher_combo,
            self.new_lesson_combo
        ]
        
        for combo in comboboxes:
            # View'ı al ve stil ayarla
            view = combo.view()
            view.setStyleSheet("""
                QListView {
                    background-color: white;
                    color: #2c3e50;
                    selection-background-color: #3498db;
                    selection-color: white;
                    border: 1px solid #dcdde1;
                    outline: none;
                }
                QListView::item {
                    background-color: white;
                    color: #2c3e50;
                    padding: 8px;
                    min-height: 30px;
                }
                QListView::item:hover {
                    background-color: #ecf0f1;
                }
                QListView::item:selected {
                    background-color: #3498db;
                    color: white;
                }
            """)

    def on_teacher_selected(self):
        """Öğretmen seçildiğinde yük bilgisini göster ve tüm dersleri listele"""
        teacher_id = self.new_teacher_combo.currentData()
        if not teacher_id:
            self.new_lesson_combo.clear()
            self.teacher_load_label.setText("Mevcut Yük: -")
            return
        
        teacher = db_manager.get_teacher_by_id(teacher_id)
        if not teacher:
            return
        
        # Öğretmenin mevcut yükünü hesapla
        assignments = db_manager.get_schedule_by_school_type()
        teacher_assignments = [a for a in assignments if a.teacher_id == teacher_id]
        total_hours = 0
        for assignment in teacher_assignments:
            lesson = db_manager.get_lesson_by_id(assignment.lesson_id)
            cls = db_manager.get_class_by_id(assignment.class_id)
            if lesson and cls:
                hours = db_manager.get_weekly_hours_for_lesson(lesson.lesson_id, cls.grade)
                total_hours += hours or 0
        
        self.teacher_load_label.setText(f"Mevcut Yük: {total_hours} saat/hafta | Branş: {teacher.subject}")
        
        # Tüm dersleri göster (filtreleme yok)
        self.new_lesson_combo.clear()
        all_lessons = db_manager.get_all_lessons()
        
        for lesson in all_lessons:
            self.new_lesson_combo.addItem(lesson.name, lesson.lesson_id)
        
        self.lesson_info_label.setText(f"Toplam {len(all_lessons)} ders")
        
        # Ders combobox'ının arka planını düzelt
        view = self.new_lesson_combo.view()
        view.setStyleSheet("""
            QListView {
                background-color: white;
                color: #2c3e50;
                selection-background-color: #3498db;
                selection-color: white;
                border: 1px solid #dcdde1;
                outline: none;
            }
            QListView::item {
                background-color: white;
                color: #2c3e50;
                padding: 8px;
                min-height: 30px;
            }
            QListView::item:hover {
                background-color: #ecf0f1;
            }
            QListView::item:selected {
                background-color: #3498db;
                color: white;
            }
        """)
        
        self.update_bulk_assign_button()
    
    def on_lesson_selected(self):
        """Ders seçildiğinde bilgi göster"""
        lesson_id = self.new_lesson_combo.currentData()
        if not lesson_id:
            return
        
        lesson = db_manager.get_lesson_by_id(lesson_id)
        if lesson:
            # Kaç sınıfta bu ders var
            classes = db_manager.get_all_classes()
            applicable_count = 0
            for cls in classes:
                hours = db_manager.get_weekly_hours_for_lesson(lesson_id, cls.grade)
                if hours and hours > 0:
                    applicable_count += 1
            
            self.lesson_info_label.setText(f"Bu ders {applicable_count} sınıfta mevcut")
        
        self.update_bulk_assign_button()
    
    def select_all_classes(self):
        """Tüm sınıfları seç"""
        for checkbox in self.class_checkboxes:
            checkbox.setChecked(True)
    
    def deselect_all_classes(self):
        """Tüm sınıf seçimlerini kaldır"""
        for checkbox in self.class_checkboxes:
            checkbox.setChecked(False)
    
    def update_bulk_assign_button(self):
        """Toplu atama butonunu aktif/pasif yap"""
        teacher_id = self.new_teacher_combo.currentData()
        lesson_id = self.new_lesson_combo.currentData()
        selected_classes = [cb for cb in self.class_checkboxes if cb.isChecked()]
        
        if teacher_id and lesson_id and len(selected_classes) > 0:
            self.bulk_assign_btn.setEnabled(True)
            self.bulk_assign_btn.setText(f"✓ {len(selected_classes)} SINIFA ATAMA YAP")
        else:
            self.bulk_assign_btn.setEnabled(False)
            self.bulk_assign_btn.setText("✓ TOPLU ATAMA YAP")
    
    def bulk_assign(self):
        """Toplu atama yap"""
        teacher_id = self.new_teacher_combo.currentData()
        lesson_id = self.new_lesson_combo.currentData()
        selected_classes = [cb for cb in self.class_checkboxes if cb.isChecked()]
        
        if not all([teacher_id, lesson_id]) or len(selected_classes) == 0:
            QMessageBox.warning(self, "Uyarı", "Lütfen öğretmen, ders ve en az bir sınıf seçin!")
            return
        
        teacher = db_manager.get_teacher_by_id(teacher_id)
        lesson = db_manager.get_lesson_by_id(lesson_id)
        
        # Onay iste
        class_names = [cb.text() for cb in selected_classes]
        reply = QMessageBox.question(
            self,
            "Toplu Atama Onayı",
            f"Öğretmen: {teacher.name}\n"
            f"Ders: {lesson.name}\n"
            f"Sınıf Sayısı: {len(selected_classes)}\n\n"
            f"Sınıflar:\n" + "\n".join([f"  • {name}" for name in class_names[:5]]) +
            (f"\n  ... ve {len(class_names) - 5} sınıf daha" if len(class_names) > 5 else "") +
            "\n\nBu atamaları yapmak istiyor musunuz?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply != QMessageBox.Yes:
            return
        
        # Atamaları yap
        success_count = 0
        overwrite_count = 0
        error_count = 0
        
        for checkbox in selected_classes:
            class_id = checkbox.property("class_id")
            
            # Mevcut atama var mı kontrol et
            assignments = db_manager.get_schedule_by_school_type()
            existing = None
            for assignment in assignments:
                if assignment.class_id == class_id and assignment.lesson_id == lesson_id:
                    existing = assignment
                    break
            
            # Mevcut atamayı sil
            if existing:
                db_manager.delete_schedule_entry(existing.entry_id)
                overwrite_count += 1
            
            # Yeni atama yap
            if db_manager.add_schedule_entry(class_id, teacher_id, lesson_id, 1, -1, -1):
                success_count += 1
            else:
                error_count += 1
        
        # Sonuç mesajı
        result_msg = f"✓ Başarılı: {success_count} atama\n"
        if overwrite_count > 0:
            result_msg += f"↻ Üzerine yazılan: {overwrite_count} atama\n"
        if error_count > 0:
            result_msg += f"✗ Hata: {error_count} atama\n"
        
        QMessageBox.information(self, "Toplu Atama Tamamlandı", result_msg)
        
        # Seçimleri temizle
        self.deselect_all_classes()
        
        # Listeyi yenile
        self.refresh_assignments()
    
    def quick_assign(self):
        """Hızlı atama yap (eski tek atama - artık kullanılmıyor)"""
        # Toplu atama kullanılıyor, bu fonksiyon artık gerekli değil
        pass

    def delete_single_assignment(self, entry_id):
        """Tek bir atamayı sil"""
        reply = QMessageBox.question(
            self,
            "Onay",
            "Bu atamayı silmek istediğinize emin misiniz?",
            QMessageBox.Yes | QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            if db_manager.delete_schedule_entry(entry_id):
                QMessageBox.information(self, "Başarılı", "Atama silindi!")
                self.refresh_assignments()
            else:
                QMessageBox.critical(self, "Hata", "Atama silinemedi!")

    def delete_teacher_assignments(self):
        """Seçili öğretmenin tüm atamalarını sil"""
        teacher_id = self.filter_teacher_combo.currentData()
        if not teacher_id:
            QMessageBox.warning(self, "Uyarı", "Lütfen bir öğretmen seçin!")
            return

        teacher = db_manager.get_teacher_by_id(teacher_id)
        reply = QMessageBox.question(
            self,
            "Onay",
            f"{teacher.name} öğretmeninin TÜM atamaları silinecek!\n\nEmin misiniz?",
            QMessageBox.Yes | QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            count = 0
            assignments = db_manager.get_schedule_by_school_type()
            for assignment in assignments:
                if assignment.teacher_id == teacher_id:
                    if db_manager.delete_schedule_entry(assignment.entry_id):
                        count += 1

            QMessageBox.information(self, "Başarılı", f"{count} atama silindi!")
            self.refresh_assignments()

    def delete_class_assignments(self):
        """Seçili sınıfın tüm atamalarını sil"""
        class_id = self.filter_class_combo.currentData()
        if not class_id:
            QMessageBox.warning(self, "Uyarı", "Lütfen bir sınıf seçin!")
            return

        cls = db_manager.get_class_by_id(class_id)
        reply = QMessageBox.question(
            self,
            "Onay",
            f"{cls.name} sınıfının TÜM atamaları silinecek!\n\nEmin misiniz?",
            QMessageBox.Yes | QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            count = 0
            assignments = db_manager.get_schedule_by_school_type()
            for assignment in assignments:
                if assignment.class_id == class_id:
                    if db_manager.delete_schedule_entry(assignment.entry_id):
                        count += 1

            QMessageBox.information(self, "Başarılı", f"{count} atama silindi!")
            self.refresh_assignments()

    def delete_all_assignments(self):
        """Tüm atamaları sil"""
        reply = QMessageBox.critical(
            self,
            "DİKKAT",
            "TÜM ATAMALAR SİLİNECEK!\n\nBu işlem geri alınamaz!\n\nDevam etmek istiyor musunuz?",
            QMessageBox.Yes | QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            # İkinci onay
            reply2 = QMessageBox.question(
                self,
                "Son Onay",
                "Gerçekten TÜM atamaları silmek istiyor musunuz?",
                QMessageBox.Yes | QMessageBox.No,
            )

            if reply2 == QMessageBox.Yes:
                count = 0
                assignments = db_manager.get_schedule_by_school_type()
                for assignment in assignments:
                    if db_manager.delete_schedule_entry(assignment.entry_id):
                        count += 1

                QMessageBox.information(self, "Başarılı", f"{count} atama silindi!")
                self.refresh_assignments()

    def auto_fill_missing_assignments(self):
        """Eksik atamaları otomatik doldur"""
        # Önce eksik atamaları kontrol et
        missing_data = db_manager.find_missing_assignments()

        if not missing_data:
            QMessageBox.information(
                self, "Bilgi", "Tüm dersler zaten atanmış!\n\nEksik atama bulunmuyor."
            )
            return

        # Eksik atama sayısını hesapla
        total_missing = sum(len(data["missing_lessons"]) for data in missing_data.values())

        # Onay iste
        reply = QMessageBox.question(
            self,
            "Otomatik Doldurma",
            f"{len(missing_data)} sınıfta toplam {total_missing} eksik ders bulundu.\n\n"
            "Bu dersler otomatik olarak uygun öğretmenlere atanacak.\n\n"
            "Devam etmek istiyor musunuz?",
            QMessageBox.Yes | QMessageBox.No,
        )

        if reply != QMessageBox.Yes:
            return

        # Progress dialog göster (basit message box ile)
        QMessageBox.information(
            self, "İşlem Başladı", "Otomatik atama yapılıyor...\n\nLütfen bekleyin."
        )

        # Otomatik doldurma işlemini yap
        result = db_manager.auto_fill_assignments()

        # Sonuçları göster
        success_count = len(result["success"])
        failed_count = len(result["failed"])

        # Detaylı rapor oluştur
        report = "📊 OTOMATIK ATAMA SONUÇLARI\n"
        report += "=" * 50 + "\n\n"

        if success_count > 0:
            report += f"✅ BAŞARILI: {success_count} atama yapıldı\n\n"
            for class_name, lesson_name, teacher_name in result["success"][:10]:  # İlk 10'u göster
                report += f"  • {class_name}: {lesson_name} → {teacher_name}\n"
            if success_count > 10:
                report += f"  ... ve {success_count - 10} atama daha\n"
            report += "\n"

        if failed_count > 0:
            report += f"❌ BAŞARISIZ: {failed_count} atama yapılamadı\n\n"
            for class_name, lesson_name, reason in result["failed"][:10]:  # İlk 10'u göster
                report += f"  • {class_name}: {lesson_name}\n    → {reason}\n"
            if failed_count > 10:
                report += f"  ... ve {failed_count - 10} hata daha\n"

        # Sonuç mesajını göster
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Otomatik Atama Tamamlandı")
        msg_box.setText(report)

        if failed_count > 0:
            msg_box.setIcon(QMessageBox.Warning)
            msg_box.setInformativeText(
                "Bazı dersler atanamadı. Bunları manuel olarak atamanız gerekebilir."
            )
        else:
            msg_box.setIcon(QMessageBox.Information)
            msg_box.setInformativeText("Tüm eksik atamalar başarıyla tamamlandı!")

        msg_box.exec_()

        # Tabloyu yenile
        self.refresh_assignments()

    def apply_styles(self):
        """Stilleri uygula"""
        self.setStyleSheet(
            """
            QDialog {
                background-color: #f5f6fa;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #dcdde1;
                border-radius: 8px;
                margin-top: 10px;
                padding: 15px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QComboBox, QLineEdit {
                padding: 8px;
                border: 2px solid #dcdde1;
                border-radius: 5px;
                background-color: white;
                min-height: 25px;
            }
            QComboBox:focus, QLineEdit:focus {
                border: 2px solid #3498db;
            }
            QComboBox::drop-down {
                border: none;
                border-radius: 5px;
                padding-right: 5px;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                color: #2c3e50;
                selection-background-color: #3498db;
                selection-color: white;
                border: 1px solid #dcdde1;
                outline: 0px;
                padding: 5px;
            }
            QComboBox QAbstractItemView::item {
                background-color: white;
                color: #2c3e50;
                padding: 8px;
                min-height: 30px;
                border: none;
            }
            QComboBox QAbstractItemView::item:hover {
                background-color: #ecf0f1;
                color: #2c3e50;
            }
            QComboBox QAbstractItemView::item:selected {
                background-color: #3498db;
                color: white;
            }
            QComboBox QListView {
                background-color: white;
                color: #2c3e50;
            }
            QComboBox::item {
                background-color: white;
                color: #2c3e50;
            }
            QPushButton {
                padding: 10px 15px;
                border: none;
                border-radius: 5px;
                background-color: #3498db;
                color: white;
                font-weight: bold;
                min-height: 40px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
            QTableWidget {
                background-color: white;
                alternate-background-color: #f8f9fa;
                border: 2px solid #dcdde1;
                border-radius: 5px;
                gridline-color: #ecf0f1;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QTableWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
            QHeaderView::section {
                background-color: #34495e;
                color: white;
                padding: 10px;
                border: none;
                font-weight: bold;
            }
        """
        )
