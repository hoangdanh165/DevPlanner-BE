import uuid
from django.db import models
from planner.models import Project


class Export(models.Model):
    EXPORT_TYPES = [
        ("markdown", "Markdown"),
        ("pdf", "PDF"),
        ("github", "GitHub Repo"),
        ("json", "JSON"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="exports"
    )
    export_type = models.CharField(max_length=50, choices=EXPORT_TYPES)
    file_url = models.URLField(blank=True, null=True)
    metadata = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Export({self.export_type}) of {self.project.name}"

    class Meta:
        db_table = "export"
