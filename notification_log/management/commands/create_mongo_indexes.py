from django.core.management.base import BaseCommand

from notification_log.services.mongodb import get_db


class Command(BaseCommand):
    help = "Create MongoDB indexes for notification logs."

    def handle(self, *args, **options):
        db = get_db()

        db["notification_logs"].create_index([("created_at", 1)])
        db["notification_logs"].create_index([("notification_id", 1),("created_at", 1)])

        self.stdout.write(self.style.SUCCESS("MongoDB indexes created successfully."))