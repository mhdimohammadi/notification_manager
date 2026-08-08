from rest_framework import serializers

from channel.models import Channel


class ChannelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Channel

        fields = ["id", "name", "type", "is_active", "created_at", "updated_at", ]
        read_only_fields = ["id", "created_at", "updated_at", ]
