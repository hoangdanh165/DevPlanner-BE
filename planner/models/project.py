import uuid
from django.db import models
from user.models import User


class Project(models.Model):
    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("active", "Active"),
        ("archived", "Archived"),
    ]

    VISIBILITY_CHOICES = [
        ("private", "Private"),
        ("public", "Public"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="projects")
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default="draft")
    tags = models.JSONField(default=list)
    sections_json = models.JSONField(default=dict)
    visibility = models.CharField(
        max_length=50, choices=VISIBILITY_CHOICES, default="private"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.user.email})"
