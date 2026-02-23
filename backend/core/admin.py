from django.contrib import admin
from .models import Student, Attendance
from .models import AttendanceSession
from .models import Timetable
from .models import Task

# Register your models here.
admin.site.register(Student)
admin.site.register(Attendance)
admin.site.register(AttendanceSession)
admin.site.register(Timetable)
admin.site.register(Task)