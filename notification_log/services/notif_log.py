from datetime import datetime, timedelta, timezone
from .mongodb import get_db


class NotificationLogService:

    COLLECTION_NAME = "notification_logs"

    @classmethod
    def create(cls,*,event,notification_id,channel_id=None,channel_type=None,status=None,recipient=None,metadata=None):

        document = {
            "event": event,
            "notification_id": notification_id,
            "channel_id": channel_id,
            "channel_type": channel_type,
            "status": status,
            "recipient": recipient,
            "created_at": datetime.now(timezone.utc),
            "metadata": metadata or {},
        }

        return get_db()[cls.COLLECTION_NAME].insert_one(document)



    @classmethod
    def get_log_for_notification(cls, notification_id):
        return get_db()[cls.COLLECTION_NAME].find({"notification_id": notification_id}).sort("created_at", 1)


    @classmethod
    def delete_expired_logs(cls):
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=90)
        return get_db()[cls.COLLECTION_NAME].delete_many({"created_at": {"$lt": cutoff_date}})