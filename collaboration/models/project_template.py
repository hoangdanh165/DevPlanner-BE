import uuid
from django.db import models


class ProjectTemplate(models.Model):
    CATEGORY_CHOICES = [
        ("webapp", "Web Application"),
        ("mobile", "Mobile App"),
        ("ai", "AI Project"),
        ("data", "Data Project"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    description = models.TextField()
    default_sections = models.JSONField(default=dict)  # prefilled overview/features
    default_diagrams = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Template: {self.name}"
