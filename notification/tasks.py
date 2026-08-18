from time import sleep

from celery import shared_task
from .models import Notification
from channel.tasks import send_email
from .task_base import NotificationTask
from notification_log.services.notif_log import NotificationLogService




@shared_task(base=NotificationTask)
def dispatch_notification(*,notification_id):
    notification = Notification.objects.select_related("channel").get(pk=notification_id)
    notification.status = Notification.Status.PROCESSING
    notification.save(update_fields=["status", "updated_at"])
    channel = notification.channel

    NotificationLogService.create(
        event="notification.processing",
        notification_id=notification.id,
        channel_id=notification.channel.id,
        channel_type=notification.channel.type,
        status=notification.status,
        recipient=notification.recipient)

    if not channel.is_active:
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
        raise NotImplementedError("SMS channel is not implemented yet.")

    elif channel.type == channel.ChannelType.TELEGRAM:
        raise NotImplementedError("Telegram channel is not implemented yet.")
