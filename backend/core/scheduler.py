from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from .models import Timetable
from .views import run_face_recognition
import threading

def check_and_mark_attendance():
    now = datetime.now()
    day = now.strftime("%A")
    current_time = now.time()

    classes = Timetable.objects.filter(day_of_week__iexact=day)

    for c in classes:
        if c.start_time <= current_time <= c.end_time:
            print(f"Class running: {c.subject}")
            threading.Thread(target=run_face_recognition).start()
            break

def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(check_and_mark_attendance, 'interval', minutes=1)
    scheduler.start()