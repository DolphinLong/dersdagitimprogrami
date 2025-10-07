from rest_framework import serializers
from .models import Teacher, Classroom, Course, TimeSlot, Constraint, Schedule, ScheduleItem

class TeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teacher
        fields = '__all__'

class ClassroomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Classroom
        fields = '__all__'

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = '__all__'

class TimeSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeSlot
        fields = '__all__'

class ConstraintSerializer(serializers.ModelSerializer):
    class Meta:
        model = Constraint
        fields = '__all__'

class ScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Schedule
        fields = '__all__'

class ScheduleItemSerializer(serializers.ModelSerializer):
    teacher = TeacherSerializer(read_only=True)
    classroom = ClassroomSerializer(read_only=True)
    course = CourseSerializer(read_only=True)
    time_slot = TimeSlotSerializer(read_only=True)
    
    class Meta:
        model = ScheduleItem
        fields = '__all__'

class ConflictSerializer(serializers.Serializer):
    type = serializers.CharField()
    message = serializers.CharField()
    # Diğer alanlar dinamik olarak eklenebilir