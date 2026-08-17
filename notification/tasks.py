from celery import shared_task
from .models import Notification
from channel.tasks import send_email
from .task_base import NotificationTask





@shared_task(base=NotificationTask)
def dispatch_notification(*,notification_id):
    notification = Notification.objects.select_related("channel").get(pk=notification_id)
    notification.status = Notification.Status.PROCESSING
    notification.save(update_fields=["status", "updated_at"])
    channel = notification.channel


    if not channel.is_active:
        notification.status = Notification.Status.FAILED
        notification.save(update_fields=["status", "updated_at"])
        raise ValueError("Channel is inactive.")

    if channel.type == channel.ChannelType.EMAIL:
        configuration = channel.email_configuration

        send_email.delay(
            configuration_id=configuration.id,
            notification_id=notification.id,
            to=notification.recipient,
            subject=notification.subject,
            body=notification.body,
            html_body=notification.html_body)

    elif channel.type == channel.ChannelType.SMS:
        notification.status = Notification.Status.FAILED
        notification.save(update_fields=["status", "updated_at"])
        raise NotImplementedError("SMS channel is not implemented yet.")

    elif channel.type == channel.ChannelType.TELEGRAM:
        notification.status = Notification.Status.FAILED
        notification.save(update_fields=["status", "updated_at"])
        raise NotImplementedError("Telegram channel is not implemented yet.")
