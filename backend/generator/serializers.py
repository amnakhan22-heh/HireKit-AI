from rest_framework import serializers
from .models import InterviewKit

VALID_SECTIONS = [
    "job_description",
    "scorecard",
    "interview_questions",
    "skills_assessment_rubric",
]


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
    role_level = serializers.ChoiceField(
        choices=InterviewKit.ROLE_LEVEL_CHOICES,
        required=False,
        allow_blank=True,
        default="",
    )
    industry = serializers.ChoiceField(
        choices=InterviewKit.INDUSTRY_CHOICES,
        required=False,
        allow_blank=True,
        default="",
    )
    company_size = serializers.ChoiceField(
        choices=InterviewKit.COMPANY_SIZE_CHOICES,
        required=False,
        allow_blank=True,
        default="",
    )
    remote_policy = serializers.ChoiceField(
        choices=InterviewKit.REMOTE_POLICY_CHOICES,
        required=False,
        allow_blank=True,
        default="",
    )


class InterviewKitSerializer(serializers.ModelSerializer):
    created_by = serializers.SerializerMethodField()

    def get_created_by(self, obj):
        if obj.created_by:
            return obj.created_by.username
        return None

    class Meta:
        model = InterviewKit
        fields = [
            "id",
            "role_title",
            "role_description",
            "role_level",
            "industry",
            "company_size",
            "remote_policy",
            "generated_kit",
            "status",
            "created_by",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "role_title",
            "role_level",
            "industry",
            "company_size",
            "remote_policy",
            "generated_kit",
            "status",
            "created_by",
            "created_at",
        ]


class PublishToggleSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=[('draft', 'Draft'), ('published', 'Published')])


class RegenerateSectionSerializer(serializers.Serializer):
    section_name = serializers.ChoiceField(choices=VALID_SECTIONS)
