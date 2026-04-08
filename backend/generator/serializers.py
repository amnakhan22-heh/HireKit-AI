from rest_framework import serializers
from .models import InterviewKit

VALID_SECTIONS = [
    "job_description",
    "scorecard",
    "interview_questions",
    "skills_assessment_rubric",
]


class InterviewKitCreateSerializer(serializers.Serializer):
    """
    Validate input for the full kit generation endpoint.

    Enforces character length constraints on ``role_description`` and restricts
    optional context fields to their defined choice sets.
    """

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
    """
    Read serializer for the ``InterviewKit`` model.

    All fields are read-only. The ``created_by`` field exposes the owner's
    username rather than the internal user ID.
    """

    created_by = serializers.SerializerMethodField()

    def get_created_by(self, obj):
        """
        Return the username of the kit's creator, or None if unset.

        Args:
            obj (InterviewKit): The kit instance being serialized.

        Returns:
            str or None: The username string, or None if ``created_by`` is null.
        """
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
    """
    Validate the ``status`` field for the publish toggle endpoint.

    Accepts only ``draft`` or ``published``.
    """

    status = serializers.ChoiceField(choices=[('draft', 'Draft'), ('published', 'Published')])


class RegenerateSectionSerializer(serializers.Serializer):
    """
    Validate the ``section_name`` field for the regenerate section endpoint.

    Accepts only the four valid kit section names defined in ``VALID_SECTIONS``.
    """

    section_name = serializers.ChoiceField(choices=VALID_SECTIONS)
