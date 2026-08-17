from celery import Task
from django.utils import timezone
from .models import Notification


class NotificationTask(Task):
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        notification_id = kwargs.get("notification_id")

        if notification_id is not None:
            (Notification.objects.filter(pk=notification_id)
             .update(status=Notification.Status.FAILED, failure_reason=str(exc), updated_at=timezone.now()))

        super().on_failure(exc, task_id, args, kwargs, einfo)
