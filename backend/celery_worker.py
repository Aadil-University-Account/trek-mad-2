import os
import sys

# make sure the backend folder is importable inside the worker (tasks import app.py)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from celery import Celery
from celery.schedules import crontab

# Redis is both the broker (queue) and the result backend
celery = Celery(
    "trekking_app",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0",
)

celery.conf.timezone = "Asia/Kolkata"
celery.conf.broker_connection_retry_on_startup = True

# Scheduled jobs (run by "celery beat")
celery.conf.beat_schedule = {
    "daily-trek-reminders": {
        "task": "tasks.reminder_tasks.daily_trek_reminder",
        "schedule": crontab(hour=9, minute=0),  # every day 9:00 AM
    },
    "monthly-activity-report": {
        "task": "tasks.reminder_tasks.monthly_activity_report",
        "schedule": crontab(day_of_month=1, hour=8, minute=0),  # 1st of every month, 8:00 AM
    },
}

# import the tasks so that the worker knows them (keep at the bottom)
import tasks.reminder_tasks  # noqa: E402,F401
import tasks.export_tasks  # noqa: E402,F401


