from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name','phone','created_at','updated_at','last_login',
                  'date_joined']
        read_only_fields = ['id', 'created_at', 'updated_at', 'last_login', 'date_joined']
        extra_kwargs = {
            'password': {'write_only': True,},
            'email': {'required': True,},
            'username': {'required': True,},
            'phone': {'required': True,},
        }

    def validate_phone(self, value):
        if User.objects.filter(phone=value).exists():
            raise serializers.ValidationError("phone already exist!")
        if not value.isdigit():
            raise serializers.ValidationError('phone must be a number')
        if not value.startswith('09'):
            raise serializers.ValidationError('phone must starts with 09 digit')
        if len(value) != 11:
            raise serializers.ValidationError('phone must be 11 digits')
        return value