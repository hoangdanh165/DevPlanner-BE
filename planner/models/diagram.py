import uuid
from django.db import models
from .project import Project
from .section import Section


class Diagram(models.Model):
    DIAGRAM_TYPES = [
        ("mermaid", "Mermaid"),
        ("plantuml", "PlantUML"),
        ("d2", "D2"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="diagrams"
    )
    section = models.ForeignKey(
        Section,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="diagrams",
    )
    name = models.CharField(max_length=100)
    diagram_type = models.CharField(max_length=50, choices=DIAGRAM_TYPES)
    source_code = models.TextField()
    rendered_svg = models.TextField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.diagram_type})"
