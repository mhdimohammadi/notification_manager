from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id',
                  'username',
                  'password',
                  'email',
                  'first_name',
                  'last_name',
                  'phone',
                  'created_at',
                  'updated_at',
                  'last_login',
                  'date_joined',
                  'is_active',
                  'is_staff',
                  'is_superuser',
                  ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'last_login', 'date_joined', 'last_login']
        extra_kwargs = {
            'password': {'write_only': True, 'required': True},
            'email': {'required': True},
            'username': {'required': True},
            'phone': {'required': True}
        }

    def validate_phone(self, value):
        if not value.isdigit():
            raise serializers.ValidationError('phone must be a number')

        if not value.startswith('09'):
            raise serializers.ValidationError('phone must starts with 09 digit')

        if len(value) != 11:
            raise serializers.ValidationError('phone must be 11 digits')

        queryset = User.objects.filter(phone=value)
        if self.instance is not None:
            queryset = queryset.exclude(pk=self.instance.pk)

        if queryset.exists():
            raise serializers.ValidationError("Phone number already exists.")

        return value


    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)

        instance.save()
        return instance










class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "password",
            "first_name",
            "last_name",
            "phone",
        ]

        extra_kwargs = {
            "password": {"write_only": True,"required": True},
            "username": {"required": True},
            "email": {"required": True},
            "phone": {"required": True}
        }

    def validate_phone(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("Phone must contain only numbers.")

        if len(value) != 11:
            raise serializers.ValidationError("Phone must be 11 digits.")

        if not value.startswith("09"):
            raise serializers.ValidationError("Phone must start with 09.")

        if User.objects.filter(phone=value).exists():
            raise serializers.ValidationError("Phone number already exists.")

        return value

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user