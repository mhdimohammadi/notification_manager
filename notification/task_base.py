from celery import Task
from django.utils import timezone
from .models import Notification
from notification_log.services.notif_log import NotificationLogService

class NotificationTask(Task):
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        notification_id = kwargs.get("notification_id")

        if notification_id is not None:
            notification = Notification.objects.select_related("channel").filter(pk=notification_id).first()

            if notification is not None:
                notification.status = Notification.Status.FAILED
                notification.failure_reason = str(exc)
                notification.updated_at = timezone.now()
                notification.save(update_fields=["status","failure_reason","updated_at"])
                NotificationLogService.create(
                    event="notification.failed",
                    notification_id=notification.id,
                    channel_id=notification.channel.id,
                    channel_type=notification.channel.type,
                    status=notification.status,
                    recipient=notification.recipient,
                    metadata={
                        "failure_reason": str(exc),
                        "exception_type": type(exc).__name__,
                        "task_id": task_id}
                )

        super().on_failure(exc, task_id, args, kwargs, einfo)
