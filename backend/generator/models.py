import uuid
from django.db import models


class InterviewKit(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    role_title = models.CharField(max_length=255)
    role_description = models.TextField()
    generated_kit = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.role_title} ({self.id})"
