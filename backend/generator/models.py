import uuid
from django.conf import settings
from django.db import models


class InterviewKit(models.Model):
    """
    Persist a generated interview kit alongside its input context.

    Stores the hiring manager's original role description, the contextual
    metadata used to tailor the kit (role level, industry, company size, remote
    policy), the full JSON output from the AI generation pipeline, and the
    kit's publication status.

    Attributes:
        id (UUID): Auto-generated UUID primary key.
        role_title (str): Role title extracted from the generated job description.
        role_description (str): Original plain-language description from the hiring manager.
        role_level (str): Seniority level choice (e.g. ``Senior``).
        industry (str): Industry context choice (e.g. ``Tech``).
        company_size (str): Company size choice (e.g. ``Startup``).
        remote_policy (str): Work arrangement choice (e.g. ``Remote``).
        generated_kit (dict): Full kit JSON with all four sections.
        status (str): ``draft`` (default) or ``published``.
        created_by (User): ForeignKey to the Django user who created the kit.
        created_at (datetime): Auto-set timestamp on creation, in UTC.
    """

    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
    ]
    ROLE_LEVEL_CHOICES = [
        ("Junior", "Junior"),
        ("Mid-level", "Mid-level"),
        ("Senior", "Senior"),
        ("Lead", "Lead"),
    ]
    INDUSTRY_CHOICES = [
        ("Tech", "Tech"),
        ("Finance", "Finance"),
        ("Healthcare", "Healthcare"),
        ("Marketing", "Marketing"),
        ("Operations", "Operations"),
        ("Other", "Other"),
    ]
    COMPANY_SIZE_CHOICES = [
        ("Startup", "Startup"),
        ("Mid-size", "Mid-size"),
        ("Enterprise", "Enterprise"),
    ]
    REMOTE_POLICY_CHOICES = [
        ("Remote", "Remote"),
        ("Hybrid", "Hybrid"),
        ("On-site", "On-site"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    role_title = models.CharField(max_length=255)
    role_description = models.TextField()
    role_level = models.CharField(max_length=50, choices=ROLE_LEVEL_CHOICES, blank=True)
    industry = models.CharField(max_length=50, choices=INDUSTRY_CHOICES, blank=True)
    company_size = models.CharField(max_length=50, choices=COMPANY_SIZE_CHOICES, blank=True)
    remote_policy = models.CharField(max_length=50, choices=REMOTE_POLICY_CHOICES, blank=True)
    generated_kit = models.JSONField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='kits',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        """
        Return a human-readable representation of the kit.

        Returns:
            str: The role title followed by the UUID in parentheses.
        """
        return f"{self.role_title} ({self.id})"
