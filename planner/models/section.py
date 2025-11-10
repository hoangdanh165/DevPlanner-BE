import uuid
from django.db import models
from .project import Project


class Section(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="sections"
    )
    title = models.CharField(max_length=255)
    content = models.TextField(blank=True)
    content_json = models.JSONField(default=dict)
    order_index = models.IntegerField(default=0)
    generated_by_ai = models.BooleanField(default=True)

    current_version = models.PositiveIntegerField(default=1)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.project.name} - {self.title}"

    class Meta:
        db_table = "section"
        ordering = ["order_index"]
