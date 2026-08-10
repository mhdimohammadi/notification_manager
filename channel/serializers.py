from rest_framework import serializers

from channel.models import Channel, EmailConfiguration


class ChannelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Channel

        fields = ["id", "name", "type", "is_active", "created_at", "updated_at", ]
        read_only_fields = ["id", "created_at", "updated_at", ]


class EmailSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, allow_blank=False, required=False)
    confirm_password = serializers.CharField(write_only=True, allow_blank=False, required=False)

    class Meta:
        model = EmailConfiguration
        fields = ["id", "channel", "host", "port", "username", "password", "confirm_password"
            , "from_email", "display_name", "use_tls", "use_ssl", "timeout"]

        read_only_fields = ["id"]

    def validate(self, attrs):
        password = attrs.get("password")
        confirm_password = attrs.get("confirm_password")

        if self.instance is None:
            if password is None:
                raise serializers.ValidationError({"password": "This field is required."})

            if confirm_password is None:
                raise serializers.ValidationError({"confirm_password": "This field is required."})


        else:
            if password is None and confirm_password is None:
                return attrs


            if password is None:
                raise serializers.ValidationError({
                    "password": "This field is required when changing the password."
                })

            if confirm_password is None:
                raise serializers.ValidationError({
                    "confirm_password": "This field is required when changing the password."
                })

        if password != confirm_password:
            raise serializers.ValidationError({
                "confirm_password": "Passwords do not match."
            })

        attrs.pop("confirm_password")

        return attrs
