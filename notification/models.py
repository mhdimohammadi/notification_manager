from django.db import models
from channel.models import Channel
from django.conf import settings



class Notification(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "pending"
        PROCESSING = "processing", "processing"
        SENT = "sent", "sent"
        FAILED = "failed", "failed"

    channel = models.ForeignKey(Channel, on_delete=models.PROTECT, related_name="notifications")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="notifications")
    recipient = models.EmailField(max_length=255)
    subject = models.CharField(max_length=255, blank=True)
    body = models.TextField()
    html_body = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    failure_reason = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"

    def __str__(self):
        return self.subject
