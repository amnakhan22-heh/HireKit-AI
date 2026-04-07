import uuid
from django.db import models


class InterviewKit(models.Model):
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
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.role_title} ({self.id})"
