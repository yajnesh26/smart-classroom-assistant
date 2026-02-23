from rest_framework.routers import DefaultRouter
from .views import StudentViewSet, AttendanceViewSet
from django.urls import path
from .views import generate_qr, scan_qr
from .views import TimetableViewSet
from .views import current_class
from .views import recommend_tasks

router = DefaultRouter()
router.register(r'students', StudentViewSet)
router.register(r'attendance', AttendanceViewSet)
router.register(r'timetable', TimetableViewSet)

urlpatterns = router.urls
urlpatterns += [
    path('generate_qr/', generate_qr),
    path('scan/', scan_qr),
    path('current-class/', current_class),
    path('recommend/<int:student_id>/', recommend_tasks),
]