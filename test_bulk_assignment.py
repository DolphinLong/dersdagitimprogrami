#!/usr/bin/env python3
"""
Toplu Atama Dialog Test
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication
from ui.dialogs.easy_assignment_dialog import EasyAssignmentDialog

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Dialog'u aç
    dialog = EasyAssignmentDialog()
    dialog.show()
    
    sys.exit(app.exec_())
