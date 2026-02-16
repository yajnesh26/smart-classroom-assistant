from django.db import models

# Create your models here.
class Student(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    usn = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.name
    
class Attendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.student.name} - {self.status}"