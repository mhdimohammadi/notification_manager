from rest_framework import serializers


class NotificationLogSerializer(serializers.Serializer):
    event = serializers.CharField()
    notification_id = serializers.IntegerField()
    channel_id = serializers.IntegerField()
    channel_type = serializers.CharField(allow_null=True)
    status = serializers.CharField(allow_null=True)
    recipient = serializers.CharField(allow_null=True)
    created_at = serializers.DateTimeField()
    metadata = serializers.JSONField()