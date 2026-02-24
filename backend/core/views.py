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
from .models import Timetable
from .serializers import TimetableSerializer
from datetime import datetime
from .models import Task

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
    
class TimetableViewSet(viewsets.ModelViewSet):
    queryset = Timetable.objects.all()
    serializer_class = TimetableSerializer

@api_view(['GET'])
def current_class(request):
    now = datetime.now()
    day = now.strftime("%A")
    time_now = now.time()

    classes = Timetable.objects.filter(day_of_week=day)

    for c in classes:
        if c.start_time <= time_now <= c.end_time:
            return Response({
                "current_class": c.subject,
                "room": c.classroom
            })
        
    return Response({"message": "Free period"})

@api_view(['GET'])
def recommend_tasks(request, student_id):
    student = Student.objects.get(id=student_id)
    tasks = Task.objects.all()

    recommendations = []

    for task in tasks:
        score = 0

        if student.interests and task.category.lower() in student.interests.lower():
            score += 2

        if student.weak_subjects and task.category.lower() in student.weak_subjects.lower():
            score += 3

        if student.career_goal and task.category.lower() in student.career_goal.lower():
            score += 1

        if score > 0:
            recommendations.append((task.title, score))

    recommendations.sort(key=lambda x: x[1], reverse=True)

    return Response({
        "recommendations": [r[0] for r in recommendations]
    })

@api_view(['GET'])
def generate_daily_routine(request, student_id):
    day = request.GET.get('day')

    if day:
        today = day
    else:
        today = datetime.now().strftime("%A")

    student = Student.objects.get(id=student_id)

    classes = Timetable.objects.filter(day_of_week__iexact=today).order_by('start_time')
    tasks = Task.objects.all()

    routine = []

    def pick_task():
        interests = student.interests.lower().split(',')
        interests = [i.strip() for i in interests]

        weak = student.weak_subjects.lower().split(',') if student.weak_subjects else []
        weak = [w.strip() for w in weak]

        for task in tasks:
            category = task.category.lower().strip()

            if category in interests or category in weak:
                return task.title
            
        return "Self study"
    
    last_end = None

    for c in classes:
        if c.subject.lower() == "free":
            routine.append({
                "time": f"{c.start_time} - {c.end_time}",
                "activity": pick_task()
            })
        
        else:
            routine.append({
                "time": f"{c.start_time} - {c.end_time}",
                "activity": f"Class: {c.subject}"
            })

        last_end = c.end_time

    return Response({
        "day": today,
        "routine": routine
    })