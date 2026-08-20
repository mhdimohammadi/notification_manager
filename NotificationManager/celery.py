import os
from celery import Celery
from celery.schedules import crontab



os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'NotificationManager.settings')
app = Celery('NotificationManager')
app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()


app.conf.beat_schedule = {
    "cleanup_notification_logs_monthly": {
        "task": "notification_log.tasks.cleanup_notification_logs",
        "schedule": crontab(minute=0,hour=0,day_of_month=1)}
}