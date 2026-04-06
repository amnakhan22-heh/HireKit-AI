from rest_framework import serializers
from .models import InterviewKit


class InterviewKitCreateSerializer(serializers.Serializer):
    role_description = serializers.CharField(
        min_length=20,
        max_length=5000,
        error_messages={
            "min_length": "Role description must be at least 20 characters.",
            "max_length": "Role description must not exceed 5000 characters.",
            "blank": "Role description cannot be blank.",
        },
    )


class InterviewKitSerializer(serializers.ModelSerializer):
    class Meta:
        model = InterviewKit
        fields = ["id", "role_title", "role_description", "generated_kit", "created_at"]
        read_only_fields = ["id", "role_title", "generated_kit", "created_at"]
