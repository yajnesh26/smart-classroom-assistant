from rest_framework.routers import DefaultRouter
from .views import StudentViewSet, AttendanceViewSet

router = DefaultRouter()
router.register(r'students', StudentViewSet)
router.register(r'attendance', AttendanceViewSet)

urlpatterns = router.urls
