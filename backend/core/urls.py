from rest_framework.routers import DefaultRouter
from .views import StudentViewSet, AttendanceViewSet
from django.urls import path
from .views import generate_qr, scan_qr
from .views import TimetableViewSet

router = DefaultRouter()
router.register(r'students', StudentViewSet)
router.register(r'attendance', AttendanceViewSet)
router.register(r'timetable', TimetableViewSet)

urlpatterns = router.urls
urlpatterns += [
    path('generate_qr/', generate_qr),
    path('scan/', scan_qr),
]