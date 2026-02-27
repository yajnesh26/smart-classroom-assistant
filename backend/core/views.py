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
import cv2
import face_recognition
import numpy as np
import os
from django.conf import settings

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

def run_face_recognition():
    video = cv2.VideoCapture(0)

    known_encodings = []
    known_ids = []

    faces_dir = os.path.join(settings.BASE_DIR.parent, "faces")

    for file in os.listdir(faces_dir):
        img_path = os.path.join(faces_dir, file)
        img = face_recognition.load_image_file(img_path)

        face_enc = face_recognition.face_encodings(img)

        if len(face_enc) == 0:
            print(f"No face detected in {file}")
            continue

        student_id = int(file.split("_")[1].split(".")[0])

        known_encodings.append(face_enc[0])
        known_ids.append(student_id)

    if len(known_encodings) == 0:
        return Response({"error": "No valid faces found in faces folder"})
    
    marked = False
    detected_name = ""

    while True:
        ret, frame = video.read()
        if not ret:
            break

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb)
        encodings = face_recognition.face_encodings(rgb, face_locations)

        for (top, right, bottom, left), encoding in zip(face_locations, encodings):
            matches = face_recognition.compare_faces(known_encodings, encoding)

            if True in matches:
                index = matches.index(True)
                student_id = known_ids[index]
                student = Student.objects.get(id=student_id)

                detected_name = student.name

                # Draw face box
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)

                # Show name above face
                cv2.putText(frame, detected_name, (left, top-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

                if not marked:
                    Attendance.objects.create(
                    student = student,
                    status = "Present"
                )
                marked = True

                # Show confirmation text
                cv2.putText(frame, f"{student.name} Attendance marked", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)
            
        cv2.imshow("Face Attendance", frame)

        if marked:
            cv2.waitKey(2000)
            break

        # Press Q to close window
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    video.release()
    cv2.destroyAllWindows()

    if marked:
        return Response({"message": f"{detected_name} marked present"})
    else:
        return Response({"message": "No face recognised"})

@api_view(['GET'])
def face_attendance(request):
    import threading

    threading.Thread(target=run_face_recognition).start()

    return Response({"message": "Face Attendance Started"})