from django.contrib import admin
from .models import Teacher, Classroom, Course, TimeSlot, Constraint, Schedule, ScheduleItem

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'max_daily_hours', 'max_weekly_hours')
    search_fields = ('first_name', 'last_name', 'email')
    list_filter = ('available_days', 'unavailable_slots')

@admin.register(Classroom)
class ClassroomAdmin(admin.ModelAdmin):
    list_display = ('name', 'capacity', 'location', 'has_projector', 'has_computer', 'has_smart_board', 'is_lab')
    search_fields = ('name', 'location')
    list_filter = ('has_projector', 'has_computer', 'has_smart_board', 'is_lab')

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'duration_hours', 'requires_projector', 'requires_computer', 'requires_smart_board', 'is_lab_course')
    search_fields = ('code', 'name')
    list_filter = ('requires_projector', 'requires_computer', 'requires_smart_board', 'is_lab_course')
    filter_horizontal = ('eligible_teachers',)

@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ('get_day_display', 'start_time', 'end_time')
    list_filter = ('day',)

@admin.register(Constraint)
class ConstraintAdmin(admin.ModelAdmin):
    list_display = ('name', 'constraint_type', 'is_active', 'priority')
    search_fields = ('name', 'description')
    list_filter = ('constraint_type', 'is_active', 'priority', 'teachers', 'classrooms', 'courses')
    filter_horizontal = ('teachers', 'classrooms', 'courses', 'time_slots')

@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date', 'is_active', 'is_published')
    search_fields = ('name', 'description')
    list_filter = ('is_active', 'is_published')

@admin.register(ScheduleItem)
class ScheduleItemAdmin(admin.ModelAdmin):
    list_display = ('schedule', 'course', 'teacher', 'classroom', 'time_slot', 'date')
    search_fields = ('schedule__name', 'course__name', 'teacher__first_name', 'teacher__last_name', 'classroom__name')
    list_filter = ('schedule', 'date', 'time_slot')