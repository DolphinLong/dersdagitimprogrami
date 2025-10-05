"""
Notification system for the Class Scheduling Program
"""

from PyQt5.QtWidgets import QMessageBox, QSystemTrayIcon, QMenu, QAction, qApp, QWidget, QStatusBar
from PyQt5.QtGui import QIcon, QPixmap, QColor
from PyQt5.QtCore import QObject, pyqtSignal, Qt

class NotificationManager(QObject):
    """Manages notifications for the application"""
    
    # Signal for sending notifications
    notification_sent = pyqtSignal(str, str)  # title, message
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._parent = parent
        self.setup_system_tray()
    
    def setup_system_tray(self):
        """Set up system tray icon"""
        try:
            # Check if system tray is available
            if QSystemTrayIcon.isSystemTrayAvailable():
                self.tray_icon = QSystemTrayIcon(self._parent)
                
                # Create a simple pixmap icon as fallback
                pixmap = QPixmap(32, 32)
                pixmap.fill(QColor(0, 0, 0, 0))  # Transparent color
                self.tray_icon.setIcon(QIcon(pixmap))
                
                # Create context menu
                self.tray_menu = QMenu()
                quit_action = QAction("Çıkış", self.tray_menu)
                quit_action.triggered.connect(qApp.quit)
                self.tray_menu.addAction(quit_action)
                
                self.tray_icon.setContextMenu(self.tray_menu)
                self.tray_icon.show()
            else:
                self.tray_icon = None
        except Exception as e:
            print(f"System tray setup error: {e}")
            self.tray_icon = None
    
    def get_status_bar(self):
        """Get the main window's status bar by navigating up the parent hierarchy"""
        # Navigate up to the main window to get the status bar
        parent = self._parent
        while parent and not hasattr(parent, 'statusBar'):
            parent = getattr(parent, 'parent', lambda: None)()
            if parent is None:
                break
        if parent and hasattr(parent, 'statusBar'):
            # Type checking workaround for basedpyright
            status_bar_method = getattr(parent, 'statusBar')
            if callable(status_bar_method):
                return status_bar_method()
        return None
    
    def show_message(self, title, message, level="info"):
        """
        Show a notification message
        level: info, warning, error, success
        """
        # Show in status bar if available
        status_bar = self.get_status_bar()
        if status_bar and isinstance(status_bar, QStatusBar):
            status_bar.showMessage(f"{title}: {message}", 5000)  # 5 seconds
        
        # Show system tray notification
        if self.tray_icon:
            # Use Qt constants for icon types - with type checking workaround
            icon = QSystemTrayIcon.MessageIcon(QSystemTrayIcon.Information)  # type: ignore
            if level == "warning":
                icon = QSystemTrayIcon.MessageIcon(QSystemTrayIcon.Warning)  # type: ignore
            elif level == "error":
                icon = QSystemTrayIcon.MessageIcon(QSystemTrayIcon.Critical)  # type: ignore
            elif level == "success":
                icon = QSystemTrayIcon.MessageIcon(QSystemTrayIcon.Information)  # type: ignore
            
            self.tray_icon.showMessage(title, message, icon, 3000)  # 3 seconds
        
        # Emit signal
        self.notification_sent.emit(title, message)
        
        # For now, also show a message box (in a real app, this would be configurable)
        msg_box = QMessageBox(self._parent) if self._parent and isinstance(self._parent, QWidget) else QMessageBox()
        msg_box.setWindowTitle(title)
        
        if level == "warning":
            msg_box.setIcon(QMessageBox.Warning)
        elif level == "error":
            msg_box.setIcon(QMessageBox.Critical)
        else:
            msg_box.setIcon(QMessageBox.Information)
        
        msg_box.setText(message)
        
        # Apply consistent styling
        msg_box.setStyleSheet("""
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
        """)
        
        msg_box.exec_()
    
    def notify_schedule_change(self, class_name, change_type="updated"):
        """Notify about schedule changes"""
        if change_type == "updated":
            title = "Program Güncellendi"
            message = f"{class_name} sınıfının ders programı güncellendi."
        elif change_type == "created":
            title = "Yeni Program"
            message = f"{class_name} sınıfı için yeni ders programı oluşturuldu."
        elif change_type == "deleted":
            title = "Program Silindi"
            message = f"{class_name} sınıfının ders programı silindi."
        else:
            title = "Program Değişikliği"
            message = f"{class_name} sınıfının ders programında değişiklik yapıldı."
        
        self.show_message(title, message, "info")
    
    def notify_conflict(self, conflict_type, details):
        """Notify about schedule conflicts"""
        title = "Çakışma Uyarısı"
        
        if conflict_type == "teacher":
            message = f"Öğretmen çakışması: {details}"
        elif conflict_type == "class":
            message = f"Sınıf çakışması: {details}"
        elif conflict_type == "classroom":
            message = f"Derslik çakışması: {details}"
        else:
            message = f"Çakışma tespit edildi: {details}"
        
        self.show_message(title, message, "warning")
    
    def notify_export_complete(self, export_type, filename):
        """Notify about export completion"""
        title = "Dışa Aktarma Tamamlandı"
        message = f"{export_type} raporu başarıyla dışa aktarıldı: {filename}"
        self.show_message(title, message, "success")

# Global notification manager instance
notification_manager = None

def get_notification_manager(parent=None):
    """Get or create the global notification manager"""
    global notification_manager
    if notification_manager is None:
        notification_manager = NotificationManager(parent)
    return notification_manager