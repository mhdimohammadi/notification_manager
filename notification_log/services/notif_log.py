from datetime import datetime, timezone

from .mongodb import db


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

        return db[cls.COLLECTION_NAME].insert_one(document)


