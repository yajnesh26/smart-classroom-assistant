from rest_framework import serializers
from .models import Student, Attendance, AttendanceSession
from .models import Timetable

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = '__all__'

class AttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = '__all__'

class AttendanceSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttendanceSession
        fields = '__all__'

class TimetableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Timetable 
        fields = '__all__'