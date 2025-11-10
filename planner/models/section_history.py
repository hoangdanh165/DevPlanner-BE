from django.db import models
from ..models.project import Project
from ..models.section import Section
import uuid


class SectionVersion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="section_versions"
    )
    section = models.ForeignKey(
        Section, on_delete=models.CASCADE, related_name="versions"
    )

    # version của project tại thời điểm snapshot này
    project_version = models.PositiveIntegerField()

    # version của riêng section này
    section_version = models.PositiveIntegerField()

    title = models.CharField(max_length=255)
    content = models.TextField(blank=True)
    content_json = models.JSONField(default=dict)
    order_index = models.IntegerField(default=0)
    generated_by_ai = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        "user.User", null=True, blank=True, on_delete=models.SET_NULL
    )

    class Meta:
        db_table = "section_version"
        ordering = ["-created_at"]
        unique_together = ("section", "section_version")
        indexes = [
            models.Index(fields=["project", "project_version"]),
            models.Index(fields=["section"]),
        ]

    def __str__(self):
        return f"{self.project.name} - {self.section.title} v{self.section_version}"
