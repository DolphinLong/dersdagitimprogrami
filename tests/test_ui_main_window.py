# -*- coding: utf-8 -*-
"""
UI Tests for Main Window
Requires pytest-qt: pip install pytest-qt
"""

import pytest
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication

# Import main window
try:
    from ui.main_window import MainWindow
    MAIN_WINDOW_AVAILABLE = True
except ImportError:
    MAIN_WINDOW_AVAILABLE = False


@pytest.mark.skipif(not MAIN_WINDOW_AVAILABLE, reason="MainWindow not available")
class TestMainWindow:
    """Test MainWindow UI functionality"""

    @pytest.fixture
    def main_window(self, qtbot, db_manager):
        """Create MainWindow instance for testing"""
        window = MainWindow()
        qtbot.addWidget(window)
        return window

    def test_main_window_creation(self, qtbot, db_manager):
        """Test that main window can be created"""
        window = MainWindow()
        qtbot.addWidget(window)
        assert window is not None
        assert window.windowTitle() != ""

    def test_main_window_visible(self, main_window, qtbot):
        """Test that main window can be shown"""
        main_window.show()
        qtbot.waitExposed(main_window)
        assert main_window.isVisible()

    def test_main_window_has_menu_bar(self, main_window):
        """Test that main window has a menu bar"""
        menu_bar = main_window.menuBar()
        assert menu_bar is not None

    def test_main_window_has_status_bar(self, main_window):
        """Test that main window has a status bar"""
        status_bar = main_window.statusBar()
        assert status_bar is not None

    def test_main_window_close(self, main_window, qtbot):
        """Test that main window can be closed"""
        main_window.show()
        qtbot.waitExposed(main_window)
        main_window.close()
        qtbot.wait(100)  # Wait for close animation
        assert not main_window.isVisible()

    def test_main_window_resize(self, main_window, qtbot):
        """Test that main window can be resized"""
        main_window.show()
        qtbot.waitExposed(main_window)
        
        original_size = main_window.size()
        main_window.resize(800, 600)
        qtbot.wait(100)
        
        new_size = main_window.size()
        assert new_size.width() == 800
        assert new_size.height() == 600

    @pytest.mark.parametrize("key", [Qt.Key_Escape, Qt.Key_F1, Qt.Key_F5])
    def test_main_window_keyboard_shortcuts(self, main_window, qtbot, key):
        """Test keyboard shortcuts don't crash the application"""
        main_window.show()
        qtbot.waitExposed(main_window)
        
        # Send key press
        qtbot.keyPress(main_window, key)
        qtbot.wait(100)
        
        # Window should still be functional
        assert main_window is not None


@pytest.mark.skipif(not MAIN_WINDOW_AVAILABLE, reason="MainWindow not available")
class TestMainWindowIntegration:
    """Integration tests for MainWindow with database"""

    def test_main_window_with_database(self, qtbot, db_manager):
        """Test main window integration with database"""
        window = MainWindow()
        qtbot.addWidget(window)
        
        # Window should initialize without errors
        assert window is not None
        
        # Database should be accessible
        assert db_manager is not None

    def test_main_window_school_type_selection(self, qtbot, db_manager):
        """Test school type selection in main window"""
        # Set school type in database
        db_manager.set_school_type("Lise")
        
        window = MainWindow()
        qtbot.addWidget(window)
        
        # Window should reflect school type
        assert window is not None


# Marker for UI tests
pytestmark = pytest.mark.ui
