from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'teachers', views.TeacherViewSet)
router.register(r'classrooms', views.ClassroomViewSet)
router.register(r'courses', views.CourseViewSet)
router.register(r'time-slots', views.TimeSlotViewSet)
router.register(r'constraints', views.ConstraintViewSet)
router.register(r'schedules', views.ScheduleViewSet)
router.register(r'schedule-items', views.ScheduleItemViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
]