"""
Report generation for the Class Scheduling Program
"""

from reports.excel_generator import ExcelGenerator
from reports.pdf_generator import PDFGenerator


class ReportGenerator:
    """Handles report generation"""

    SCHOOL_TIME_SLOTS = {
        "İlkokul": 6,
        "Ortaokul": 7,
        "Lise": 8,
        "Anadolu Lisesi": 8,
        "Fen Lisesi": 8,
        "Sosyal Bilimler Lisesi": 8,
    }

    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.pdf_generator = PDFGenerator(db_manager)
        self.excel_generator = ExcelGenerator(db_manager)

    def generate_class_schedule_report(self, class_id):
        """
        Generate a schedule report for a specific class.
        Returns a tuple of (headers, data).
        """
        class_obj = self.db_manager.get_class_by_id(class_id)
        if not class_obj:
            return [], []

        schedule_entries = self.db_manager.get_schedule_for_specific_class(class_id)
        teachers = {t.teacher_id: t for t in self.db_manager.get_all_teachers()}
        lessons = {l.lesson_id: l for l in self.db_manager.get_all_lessons()}

        school_type = self.db_manager.get_school_type() or "Lise"
        time_slots_count = self.SCHOOL_TIME_SLOTS.get(school_type, 8)

        headers = ["Saat", "Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma"]
        data = []

        schedule_matrix = {}
        for entry in schedule_entries:
            schedule_matrix[(entry.day, entry.time_slot)] = entry

        for i in range(time_slots_count):
            start_hour = 8 + i
            time_slot_label = f"{start_hour:02d}:00 - {start_hour+1:02d}:00"
            row_data = [time_slot_label]
            for day in range(5):
                entry = schedule_matrix.get((day, i))
                if entry:
                    lesson = lessons.get(entry.lesson_id)
                    teacher = teachers.get(entry.teacher_id)
                    if lesson and teacher:
                        row_data.append(f"{lesson.name}\n({teacher.name})")
                    else:
                        row_data.append("Hata")
                else:
                    row_data.append("")
            data.append(row_data)

        return headers, data

    def generate_teacher_schedule_report(self, teacher_id):
        """
        Generate a schedule report for a specific teacher.
        Returns a tuple of (headers, data).
        """
        teacher = self.db_manager.get_teacher_by_id(teacher_id)
        if not teacher:
            return [], []

        schedule_entries = self.db_manager.get_schedule_for_specific_teacher(teacher_id)
        classes = {c.class_id: c for c in self.db_manager.get_all_classes()}
        lessons = {l.lesson_id: l for l in self.db_manager.get_all_lessons()}

        school_type = self.db_manager.get_school_type() or "Lise"
        time_slots_count = self.SCHOOL_TIME_SLOTS.get(school_type, 8)

        headers = ["Saat", "Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma"]
        data = []

        schedule_matrix = {}
        for entry in schedule_entries:
            schedule_matrix[(entry.day, entry.time_slot)] = entry

        for i in range(time_slots_count):
            start_hour = 8 + i
            time_slot_label = f"{start_hour:02d}:00 - {start_hour+1:02d}:00"
            row_data = [time_slot_label]
            for day in range(5):
                entry = schedule_matrix.get((day, i))
                if entry:
                    lesson = lessons.get(entry.lesson_id)
                    class_obj = classes.get(entry.class_id)
                    if lesson and class_obj:
                        row_data.append(f"{lesson.name}\n({class_obj.name})")
                    else:
                        row_data.append("Hata")
                else:
                    row_data.append("")
            data.append(row_data)

        return headers, data

    def generate_classroom_usage_report(self):
        """
        Generate a classroom usage report.
        For simplicity, this will now return data for the first classroom.
        A more advanced implementation would allow selecting a classroom.
        Returns a tuple of (headers, data).
        """
        classrooms = self.db_manager.get_all_classrooms()
        if not classrooms:
            return ["Hata"], [["Derslik bulunamadı."]]

        # For this example, we'll just report on the first classroom
        classroom = classrooms[0]

        schedule_entries = self.db_manager.get_schedule_by_school_type()

        school_type = self.db_manager.get_school_type() or "Lise"
        time_slots_count = self.SCHOOL_TIME_SLOTS.get(school_type, 8)

        headers = ["Saat", "Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma"]
        data = []

        schedule_matrix = {}
        for entry in schedule_entries:
            if entry.classroom_id == classroom.classroom_id:
                schedule_matrix[(entry.day, entry.time_slot)] = entry

        all_classes = {c.class_id: c for c in self.db_manager.get_all_classes()}
        all_lessons = {l.lesson_id: l for l in self.db_manager.get_all_lessons()}

        for i in range(time_slots_count):
            start_hour = 8 + i
            time_slot_label = f"{start_hour:02d}:00 - {start_hour+1:02d}:00"
            row_data = [time_slot_label]
            for day in range(5):
                entry = schedule_matrix.get((day, i))
                if entry:
                    lesson = all_lessons.get(entry.lesson_id)
                    class_obj = all_classes.get(entry.class_id)
                    if lesson and class_obj:
                        row_data.append(f"{class_obj.name}\n({lesson.name})")
                    else:
                        row_data.append("Hata")
                else:
                    row_data.append("")
            data.append(row_data)

        # Prepend classroom name to headers for context
        headers[0] = f"Derslik: {classroom.name}"
        return headers, data

    def export_to_pdf(self, report_type, identifier=None, filename=None):
        """
        Export report to PDF
        """
        if report_type == "class_schedule":
            filename = filename or f"class_{identifier}_schedule.pdf"
            return self.pdf_generator.generate_class_schedule_pdf(identifier, filename)
        elif report_type == "teacher_schedule":
            filename = filename or f"teacher_{identifier}_schedule.pdf"
            return self.pdf_generator.generate_teacher_schedule_pdf(identifier, filename)
        elif report_type == "classroom_usage":
            filename = filename or "classroom_usage.pdf"
            return self.pdf_generator.generate_classroom_usage_pdf(filename)
        else:
            return "Geçersiz rapor türü"

    def export_to_excel(self, report_type, identifier=None, filename=None):
        """
        Export report to Excel
        """
        if report_type == "class_schedule":
            filename = filename or f"class_{identifier}_schedule.xlsx"
            return self.excel_generator.generate_class_schedule_excel(identifier, filename)
        elif report_type == "teacher_schedule":
            filename = filename or f"teacher_{identifier}_schedule.xlsx"
            return self.excel_generator.generate_teacher_schedule_excel(identifier, filename)
        elif report_type == "classroom_usage":
            filename = filename or "classroom_usage.xlsx"
            return self.excel_generator.generate_classroom_usage_excel(identifier, filename)
        else:
            return "Geçersiz rapor türü"
