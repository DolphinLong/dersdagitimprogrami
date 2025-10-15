"""
Login dialog for the Class Scheduling Program
"""

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QDialog,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from database import db_manager
from utils.helpers import create_styled_message_box


class LoginDialog(QDialog):
    """Login dialog window with modern design"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Ders Programı - Giriş")
        self.setFixedSize(500, 600)

        self.setup_ui()
        self.apply_styles()

    def setup_ui(self):
        """Set up the user interface with a clean, modern design."""
        # Main container widget with colored background
        container = QWidget(self)
        container.setObjectName("container")
        container.setGeometry(0, 0, 500, 600)

        layout = QVBoxLayout(container)
        layout.setContentsMargins(50, 50, 50, 50)
        layout.setSpacing(20)
        layout.setAlignment(Qt.AlignCenter)

        # Header
        icon_label = QLabel("📚")
        icon_label.setObjectName("iconLabel")
        icon_label.setAlignment(Qt.AlignCenter)

        title_label = QLabel("Ders Programı")
        title_label.setObjectName("titleLabel")
        title_label.setAlignment(Qt.AlignCenter)

        subtitle_label = QLabel("Sisteme Hoş Geldiniz")
        subtitle_label.setObjectName("subtitleLabel")
        subtitle_label.setAlignment(Qt.AlignCenter)

        # Form Layout
        form_layout = QVBoxLayout()
        form_layout.setSpacing(15)

        username_label = QLabel("Kullanıcı Adı")
        username_label.setObjectName("fieldLabel")

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Kullanıcı adınızı girin")
        self.username_input.setObjectName("usernameInput")

        password_label = QLabel("Şifre")
        password_label.setObjectName("fieldLabel")

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Şifrenizi girin")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setObjectName("passwordInput")

        form_layout.addWidget(username_label)
        form_layout.addWidget(self.username_input)
        form_layout.addWidget(password_label)
        form_layout.addWidget(self.password_input)

        # Button Layout
        self.login_button = QPushButton("Giriş Yap")
        self.login_button.setObjectName("loginButton")
        self.login_button.clicked.connect(self.login)

        # Add widgets to main layout
        layout.addWidget(icon_label)
        layout.addWidget(title_label)
        layout.addWidget(subtitle_label)
        layout.addSpacing(30)
        layout.addLayout(form_layout)
        layout.addSpacing(20)
        layout.addWidget(self.login_button)

        # Set focus and connections
        self.username_input.setFocus()
        self.username_input.returnPressed.connect(self.login)
        self.password_input.returnPressed.connect(self.login)

    def apply_styles(self):
        """Apply a clean and professional stylesheet."""
        self.setStyleSheet(
            """
            #container {
                background-color: #6366f1;
            }
            #iconLabel {
                font-size: 72px;
                margin-bottom: 10px;
            }
            #titleLabel {
                font-size: 32px;
                font-weight: bold;
                color: #ffffff;
                margin-bottom: 5px;
            }
            #subtitleLabel {
                font-size: 16px;
                color: rgba(255, 255, 255, 0.9);
                font-weight: 500;
            }
            #fieldLabel {
                font-size: 13px;
                color: #ffffff;
                font-weight: 600;
                margin-bottom: 5px;
            }
            QLineEdit {
                padding: 14px 16px;
                border: 2px solid rgba(255, 255, 255, 0.3);
                border-radius: 10px;
                background-color: rgba(255, 255, 255, 0.15);
                font-size: 14px;
                color: #ffffff;
                selection-background-color: rgba(255, 255, 255, 0.3);
            }
            QLineEdit::placeholder {
                color: rgba(255, 255, 255, 0.6);
            }
            QLineEdit:focus {
                border: 2px solid rgba(255, 255, 255, 0.6);
                background-color: rgba(255, 255, 255, 0.2);
            }
            #loginButton {
                padding: 16px;
                font-size: 16px;
                font-weight: bold;
                color: #6366f1;
                background-color: #ffffff;
                border: none;
                border-radius: 10px;
            }
            #loginButton:hover {
                background-color: #f0f0f0;
            }
            #loginButton:pressed {
                background-color: #e0e0e0;
            }
        """
        )
        self.setMessageBoxStyle()

    def setMessageBoxStyle(self):
        """Set the style for message boxes"""
        QMessageBox.setStyleSheet(
            self,
            """
            QMessageBox {
                background-color: #ffffff;
                color: #2c3e50;
                font-family: "Segoe UI", sans-serif;
            }
            QMessageBox QLabel {
                color: #2c3e50;
                font-size: 14px;
            }
            QMessageBox QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                          stop: 0 #667eea, stop: 1 #764ba2);
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 8px;
                font-weight: bold;
                min-width: 80px;
                font-size: 14px;
            }
            QMessageBox QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                          stop: 0 #5568d3, stop: 1 #6b3f8f);
            }
            QMessageBox QPushButton:pressed {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                          stop: 0 #4a5ac0, stop: 1 #5f367d);
            }
        """,
        )

    def login(self):
        """Handle login attempt"""
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        if not username or not password:
            msg = create_styled_message_box(
                self, "Giriş Başarısız", "Lütfen kullanıcı adı ve şifre girin.", QMessageBox.Warning
            )
            msg.exec_()
            return

        # Check credentials
        user = db_manager.get_user(username, password)
        if user:
            self.accept()
            # In a real application, you would pass the user object to the main window
        else:
            msg = create_styled_message_box(
                self, "Giriş Başarısız", "Geçersiz kullanıcı adı veya şifre.", QMessageBox.Warning
            )
            msg.exec_()
            self.password_input.clear()
            self.username_input.setFocus()
