from rest_framework import serializers
from .models import User


class UserCreationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ("email", "username", "phone_number", "password")
        extra_kwargs = {"email": {"error_messages": { "unique": "Email already exists"}},
                        "username": { "error_messages": { "unique": "Username already exists"}},
                        # "phone_number": {"error_messages": {"unique": "Phone number already exists"}},
        }

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)
