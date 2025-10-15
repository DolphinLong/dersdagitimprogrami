"""
Backup and Restore dialog for the Class Scheduling Program
"""

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtWidgets import (
    QDialog,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)

from database import db_manager
from utils.file_manager import FileManager
from utils.helpers import create_styled_message_box


class BackupRestoreDialog(QDialog):
    """Dialog for backup and restore operations"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.file_manager = FileManager(db_manager)
        self.setWindowTitle("Yedekle ve Geri Yükle")
        self.setMinimumSize(600, 400)
        self.setup_ui()
        self.apply_styles()

    def setup_ui(self):
        """Set up the user interface with a modern card-based design."""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Header
        header_layout = QHBoxLayout()
        icon_label = QLabel("💾")
        icon_label.setObjectName("headerIcon")
        title_label = QLabel("Yedekle ve Geri Yükle")
        title_label.setObjectName("headerTitle")
        header_layout.addWidget(icon_label)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        main_layout.addLayout(header_layout)

        # Cards Layout
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(20)

        backup_card = self._create_action_card(
            "📥",
            "Veri Tabanı Yedekle",
            "Mevcut programın ve tüm verilerin tam bir yedeğini oluşturun.",
            self.create_backup,
            "#27ae60",
        )

        restore_card = self._create_action_card(
            "📤",
            "Yedekten Geri Yükle",
            "Önceki bir yedekten programı geri yükleyin. DİKKAT: Mevcut tüm veriler silinecektir!",
            self.restore_backup,
            "#f39c12",
        )

        cards_layout.addWidget(backup_card)
        cards_layout.addWidget(restore_card)
        main_layout.addLayout(cards_layout)

        main_layout.addStretch()

        # Close Button
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        self.close_button = QPushButton("Kapat")
        self.close_button.setObjectName("closeButton")
        self.close_button.clicked.connect(self.accept)
        button_layout.addWidget(self.close_button)
        main_layout.addLayout(button_layout)

    def _create_action_card(self, icon, title, description, callback, color):
        """Helper function to create a styled action card."""
        card = QFrame()
        card.setObjectName("actionCard")
        layout = QVBoxLayout(card)
        layout.setSpacing(15)
        layout.setContentsMargins(25, 25, 25, 25)

        icon_label = QLabel(icon)
        icon_label.setObjectName("cardIcon")
        icon_label.setAlignment(Qt.AlignCenter)

        title_label = QLabel(title)
        title_label.setObjectName("cardTitle")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setWordWrap(True)

        desc_label = QLabel(description)
        desc_label.setObjectName("cardDescription")
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setWordWrap(True)

        layout.addStretch(1)
        layout.addWidget(icon_label)
        layout.addWidget(title_label)
        layout.addWidget(desc_label)
        layout.addStretch(2)

        button = QPushButton(title)
        button.clicked.connect(callback)
        button.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                padding: 12px;
                border-radius: 8px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {self._lighten_color(color)};
            }}
        """
        )
        layout.addWidget(button)

        return card

    def _lighten_color(self, color_str):
        color = QColor(color_str)
        color.setHsl(color.hslHue(), color.hslSaturation(), min(255, color.lightness() + 25))
        return color.name()

    def apply_styles(self):
        """Apply modern styles to the new card-based layout."""
        self.setStyleSheet(
            """
            QDialog {
                background-color: #f0f4f8;
            }
            #headerIcon {
                font-size: 28px;
            }
            #headerTitle {
                font-size: 22px;
                font-weight: bold;
                color: #2c3e50;
            }
            #actionCard {
                background-color: white;
                border-radius: 15px;
                border: 1px solid #e0e0e0;
            }
            #cardIcon {
                font-size: 48px;
                color: #34495e;
            }
            #cardTitle {
                font-size: 16px;
                font-weight: bold;
                color: #2c3e50;
            }
            #cardDescription {
                font-size: 13px;
                color: #7f8c8d;
                min-height: 60px;
            }
            #closeButton {
                background-color: #95a5a6;
                color: white;
                padding: 10px 20px;
                border-radius: 8px;
                font-weight: bold;
            }
            #closeButton:hover {
                background-color: #7f8c8d;
            }
        """
        )

    def create_backup(self):
        """Create a backup of the database"""
        try:
            # Ask user for backup location
            filename, _ = QFileDialog.getSaveFileName(
                self,
                "Yedek Dosyasını Kaydet",
                "schedule_backup.db",
                "Database Files (*.db);;All Files (*)",
            )

            if filename:
                # Create backup
                result = self.file_manager.backup_database(filename)

                # Show result
                if "başarıyla" in result and "oluşturuldu" in result:
                    msg = create_styled_message_box(self, "Başarılı", result)
                    msg.exec_()
                else:
                    msg = create_styled_message_box(self, "Hata", result, QMessageBox.Critical)
                    msg.exec_()
        except Exception as e:
            msg = create_styled_message_box(
                self, "Hata", f"Yedekleme hatası: {str(e)}", QMessageBox.Critical
            )
            msg.exec_()

    def restore_backup(self):
        """Restore database from backup"""
        try:
            # Confirm with user
            confirm = QMessageBox.question(
                self,
                "Onay",
                "Veri tabanını geri yüklemek istediğinizden emin misiniz? Mevcut veriler silinecektir.",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )

            if confirm == QMessageBox.Yes:
                # Ask user for backup file
                filename, _ = QFileDialog.getOpenFileName(
                    self, "Yedek Dosyasını Seç", "", "Database Files (*.db);;All Files (*)"
                )

                if filename:
                    # Restore backup
                    result = self.file_manager.restore_database(filename)

                    # Show result
                    if "başarıyla" in result and "geri yüklendi" in result:
                        msg = create_styled_message_box(
                            self, "Başarılı", result + "\n\nUygulama yeniden başlatılacak."
                        )
                        msg.exec_()
                        # Close the application to restart with new database
                        self.done(1)  # Use done() instead of close()
                    else:
                        msg = create_styled_message_box(self, "Hata", result, QMessageBox.Critical)
                        msg.exec_()
        except Exception as e:
            msg = create_styled_message_box(
                self, "Hata", f"Geri yükleme hatası: {str(e)}", QMessageBox.Critical
            )
            msg.exec_()
