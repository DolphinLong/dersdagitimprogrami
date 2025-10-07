from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import transaction

from .models import Teacher, Classroom, Course, TimeSlot, Constraint, Schedule, ScheduleItem
from .serializers import (
    TeacherSerializer, ClassroomSerializer, CourseSerializer, 
    TimeSlotSerializer, ConstraintSerializer, ScheduleSerializer, 
    ScheduleItemSerializer, ConflictSerializer
)
from .algorithms import SchedulingAlgorithm
from .conflict_matrix import ConflictMatrix, ConstraintAnalyzer

class TeacherViewSet(viewsets.ModelViewSet):
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer

class ClassroomViewSet(viewsets.ModelViewSet):
    queryset = Classroom.objects.all()
    serializer_class = ClassroomSerializer

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

class TimeSlotViewSet(viewsets.ModelViewSet):
    queryset = TimeSlot.objects.all()
    serializer_class = TimeSlotSerializer

class ConstraintViewSet(viewsets.ModelViewSet):
    queryset = Constraint.objects.all()
    serializer_class = ConstraintSerializer

class ScheduleViewSet(viewsets.ModelViewSet):
    queryset = Schedule.objects.all()
    serializer_class = ScheduleSerializer
    
    @action(detail=True, methods=['post'])
    def add_schedule_item(self, request, pk=None):
        """Çizelgeye yeni bir ders ekler"""
        schedule = self.get_object()
        algorithm = SchedulingAlgorithm(schedule)
        
        # Gerekli parametreleri al
        course_id = request.data.get('course_id')
        teacher_id = request.data.get('teacher_id')
        classroom_id = request.data.get('classroom_id')
        time_slot_id = request.data.get('time_slot_id')
        date = request.data.get('date')
        
        # Parametrelerin varlığını kontrol et
        if not all([course_id, teacher_id, classroom_id, time_slot_id, date]):
            return Response(
                {'error': 'Tüm alanlar zorunludur: course_id, teacher_id, classroom_id, time_slot_id, date'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Objeleri al
        try:
            course = Course.objects.get(id=course_id)
            teacher = Teacher.objects.get(id=teacher_id)
            classroom = Classroom.objects.get(id=classroom_id)
            time_slot = TimeSlot.objects.get(id=time_slot_id)
        except (Course.DoesNotExist, Teacher.DoesNotExist, Classroom.DoesNotExist, TimeSlot.DoesNotExist) as e:
            return Response(
                {'error': f'Nesne bulunamadı: {str(e)}'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Dersi oluştur
        success, schedule_item, errors = algorithm.create_schedule_item(
            course, teacher, classroom, time_slot, date
        )
        
        if success:
            serializer = ScheduleItemSerializer(schedule_item)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(
                {'errors': errors},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['get'])
    def conflicts(self, request, pk=None):
        """Çizelgedeki çakışmaları bulur"""
        schedule = self.get_object()
        algorithm = SchedulingAlgorithm(schedule)
        
        conflicts = algorithm.find_conflicts()
        serializer = ConflictSerializer(conflicts, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def conflict_matrix(self, request, pk=None):
        """Çizelgenin çakışma matrisini oluşturur"""
        schedule = self.get_object()
        conflict_matrix = ConflictMatrix(schedule)
        matrix = conflict_matrix.build_conflict_matrix()
        
        # Matrisi JSON uyumlu hale getir
        json_matrix = {}
        for key, value in matrix.items():
            json_matrix[str(key)] = {}
            for item_id, conflicts in value.items():
                json_matrix[str(key)][str(item_id)] = conflicts
        
        return Response({
            'matrix': json_matrix,
            'summary': conflict_matrix.get_conflicts_summary()
        })
    
    @action(detail=True, methods=['get'])
    def constraint_analysis(self, request, pk=None):
        """Kısıtlama analizi yapar"""
        constraint_analyzer = ConstraintAnalyzer()
        analysis = constraint_analyzer.analyze_constraints()
        design_doc = constraint_analyzer.generate_design_document()
        
        return Response({
            'analysis': analysis,
            'design_document': design_doc
        })

class ScheduleItemViewSet(viewsets.ModelViewSet):
    queryset = ScheduleItem.objects.all()
    serializer_class = ScheduleItemSerializer