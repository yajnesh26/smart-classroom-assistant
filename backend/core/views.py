from rest_framework import viewsets
from .models import Student, Attendance
from .serializers import StudentSerializer, AttendanceSerializer
import qrcode
from io import BytesIO
from django.http import HttpResponse
from django.utils import timezone
from datetime import timedelta
from .models import AttendanceSession
from rest_framework.decorators import api_view
from rest_framework.response import Response

# Create your views here.
class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer

class AttendanceViewSet(viewsets.ModelViewSet):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer

def generate_qr(request):
    session = AttendanceSession.objects.create(
        expires_at=timezone.now() + timedelta(minutes=5)
    )

    qr_data = str(session.session_id)

    img = qrcode.make(qr_data)

    buffer = BytesIO()
    img.save(buffer, format="PNG")

    return HttpResponse(buffer.getvalue(), content_type="image/png")

@api_view(['POST'])
def scan_qr(request):
    session_id = request.data.get('session_id')
    student_id = request.data.get('student_id')

    try:
        session = AttendanceSession.objects.get(session_id=session_id)

        if session.expires_at < timezone.now():
            return Response({"error": "Session expired"}, status=400)
        
        student = Student.objects.get(id=student_id)

        Attendance.objects.create(
            student=student,
            status="Present"
        )

        return Response({"message": "Attendance marked"})
    
    except AttendanceSession.DoesNotExist:
        return Response({"error": "Invalid session"}, status=400)