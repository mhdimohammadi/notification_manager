from notification.task_base import NotificationTask
from celery import shared_task
from notification.models import Notification
from notification_log.services.notif_log import NotificationLogService
from .models import EmailConfiguration
from .services.email_sender import EmailSender
from channel.services.email_configuration_cache import EmailConfigurationCache
from .services.exceptions import EmailConnectionError, EmailAuthenticationError, EmailTimeoutError





@shared_task(bind=True, base=NotificationTask, max_retries=3)
def send_email(self, configuration_id, *, notification_id, to, subject, body, html_body=None, cc=None, bcc=None, ):
    notification = Notification.objects.select_related("channel").get(pk=notification_id)
    configuration = EmailConfigurationCache.get(configuration_id)

    if configuration is None:
        configuration = EmailConfiguration.objects.get(pk=configuration_id)
        configuration = EmailConfigurationCache.set(configuration)

    sender = EmailSender(configuration)
    try:
        result = sender.send(to=to, subject=subject, body=body, html_body=html_body, cc=cc, bcc=bcc, )
        notification.status = Notification.Status.SENT
        notification.save(update_fields=["status", "updated_at"])
        NotificationLogService.create(
            event="notification.sent",
            notification_id=notification.id,
            channel_id=notification.channel.id,
            channel_type=notification.channel.type,
            status=notification.status,
            recipient=notification.recipient,
        )

        return result

    except EmailAuthenticationError:
        raise

    except (EmailTimeoutError, EmailConnectionError) as exc:
        countdown = 10 * (2 ** self.request.retries)
        raise self.retry(exc=exc, countdown=countdown)
