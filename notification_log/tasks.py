from celery import shared_task
from notification_log.services.notif_log import NotificationLogService




@shared_task
def cleanup_notification_logs():
    result = NotificationLogService.delete_expired_logs()
    return {"deleted_count": result.deleted_count}