#!/usr/bin/env python3
"""Test login dialog"""
import sys
from PyQt5.QtWidgets import QApplication
from ui.login_dialog import LoginDialog

app = QApplication(sys.argv)
dialog = LoginDialog()
dialog.show()
sys.exit(app.exec_())
