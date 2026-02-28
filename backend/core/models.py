from django.db import models
import uuid

# Create your models here.
class Student(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    usn = models.CharField(max_length=20, unique=True)

    interests = models.TextField(blank=True)
    weak_subjects = models.TextField(blank=True)
    career_goal = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return self.name
    
class Attendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100, null=True, blank=True)
    date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.student.name} - {self.status}"
    
class AttendanceSession(models.Model):
    session_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def __str__(self):
        return str(self.session_id)

class Timetable(models.Model):
    subject = models.CharField(max_length=100)
    day_of_week = models.CharField(max_length=10)
    start_time = models.TimeField()
    end_time = models.TimeField()
    classroom = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.subject} ({self.day_of_week})"

class Task(models.Model):
    title = models.CharField(max_length=200)
    category = models.CharField(max_length=100)
    estimated_minutes = models.IntegerField()

    def __str__(self):
        return self.title