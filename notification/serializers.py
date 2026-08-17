from rest_framework import serializers
from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ("id","channel","recipient","subject","body","html_body","status","failure_reason","created_at","updated_at")
        read_only_fields = ("id","status","failure_reason","created_at","updated_at")
