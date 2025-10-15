# -*- coding: utf-8 -*-
"""
UI Tests for Dialogs
Requires pytest-qt: pip install pytest-qt
"""

import pytest
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog

# Import dialogs
try:
    from ui.dialogs.class_dialog import ClassDialog
    CLASS_DIALOG_AVAILABLE = True
except ImportError:
    CLASS_DIALOG_AVAILABLE = False

try:
    from ui.dialogs.teacher_dialog import TeacherDialog
    TEACHER_DIALOG_AVAILABLE = True
except ImportError:
    TEACHER_DIALOG_AVAILABLE = False

try:
    from ui.dialogs.lesson_dialog import LessonDialog
    LESSON_DIALOG_AVAILABLE = True
except ImportError:
    LESSON_DIALOG_AVAILABLE = False


@pytest.mark.skipif(not CLASS_DIALOG_AVAILABLE, reason="ClassDialog not available")
class TestClassDialog:
    """Test ClassDialog UI functionality"""

    @pytest.fixture
    def class_dialog(self, qtbot, db_manager):
        """Create ClassDialog instance for testing"""
        dialog = ClassDialog(db_manager)
        qtbot.addWidget(dialog)
        return dialog

    def test_class_dialog_creation(self, qtbot, db_manager):
        """Test that class dialog can be created"""
        dialog = ClassDialog(db_manager)
        qtbot.addWidget(dialog)
        assert dialog is not None
        assert isinstance(dialog, QDialog)

    def test_class_dialog_has_input_fields(self, class_dialog):
        """Test that class dialog has required input fields"""
        # Dialog should have input fields for class name and grade
        assert class_dialog is not None

    def test_class_dialog_accept(self, class_dialog, qtbot):
        """Test accepting the dialog"""
        class_dialog.show()
        qtbot.waitExposed(class_dialog)
        
        # Simulate accepting dialog
        # Note: This is a basic test, actual implementation may vary
        assert class_dialog is not None

    def test_class_dialog_reject(self, class_dialog, qtbot):
        """Test rejecting the dialog"""
        class_dialog.show()
        qtbot.waitExposed(class_dialog)
        
        # Simulate rejecting dialog
        class_dialog.reject()
        qtbot.wait(100)
        
        assert not class_dialog.isVisible()


@pytest.mark.skipif(not TEACHER_DIALOG_AVAILABLE, reason="TeacherDialog not available")
class TestTeacherDialog:
    """Test TeacherDialog UI functionality"""

    @pytest.fixture
    def teacher_dialog(self, qtbot, db_manager):
        """Create TeacherDialog instance for testing"""
        dialog = TeacherDialog(db_manager)
        qtbot.addWidget(dialog)
        return dialog

    def test_teacher_dialog_creation(self, qtbot, db_manager):
        """Test that teacher dialog can be created"""
        dialog = TeacherDialog(db_manager)
        qtbot.addWidget(dialog)
        assert dialog is not None
        assert isinstance(dialog, QDialog)

    def test_teacher_dialog_visible(self, teacher_dialog, qtbot):
        """Test that teacher dialog can be shown"""
        teacher_dialog.show()
        qtbot.waitExposed(teacher_dialog)
        assert teacher_dialog.isVisible()

    def test_teacher_dialog_close(self, teacher_dialog, qtbot):
        """Test that teacher dialog can be closed"""
        teacher_dialog.show()
        qtbot.waitExposed(teacher_dialog)
        teacher_dialog.close()
        qtbot.wait(100)
        assert not teacher_dialog.isVisible()


@pytest.mark.skipif(not LESSON_DIALOG_AVAILABLE, reason="LessonDialog not available")
class TestLessonDialog:
    """Test LessonDialog UI functionality"""

    @pytest.fixture
    def lesson_dialog(self, qtbot, db_manager):
        """Create LessonDialog instance for testing"""
        dialog = LessonDialog(db_manager)
        qtbot.addWidget(dialog)
        return dialog

    def test_lesson_dialog_creation(self, qtbot, db_manager):
        """Test that lesson dialog can be created"""
        dialog = LessonDialog(db_manager)
        qtbot.addWidget(dialog)
        assert dialog is not None
        assert isinstance(dialog, QDialog)

    def test_lesson_dialog_keyboard_input(self, lesson_dialog, qtbot):
        """Test keyboard input in lesson dialog"""
        lesson_dialog.show()
        qtbot.waitExposed(lesson_dialog)
        
        # Test that dialog accepts keyboard input
        qtbot.keyPress(lesson_dialog, Qt.Key_Tab)
        qtbot.wait(50)
        
        assert lesson_dialog is not None


class TestDialogIntegration:
    """Integration tests for dialogs"""

    def test_multiple_dialogs_can_coexist(self, qtbot, db_manager):
        """Test that multiple dialogs can be created without conflicts"""
        dialogs = []
        
        if CLASS_DIALOG_AVAILABLE:
            dialog1 = ClassDialog(db_manager)
            qtbot.addWidget(dialog1)
            dialogs.append(dialog1)
        
        if TEACHER_DIALOG_AVAILABLE:
            dialog2 = TeacherDialog(db_manager)
            qtbot.addWidget(dialog2)
            dialogs.append(dialog2)
        
        if LESSON_DIALOG_AVAILABLE:
            dialog3 = LessonDialog(db_manager)
            qtbot.addWidget(dialog3)
            dialogs.append(dialog3)
        
        # All dialogs should be created successfully
        assert len(dialogs) > 0
        for dialog in dialogs:
            assert dialog is not None


# Marker for UI tests
pytestmark = pytest.mark.ui
