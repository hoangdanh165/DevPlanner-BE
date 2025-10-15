import uuid
from django.db import models


class AIAgent(models.Model):
    ROLE_CHOICES = [
        ("planner", "Planner"),
        ("critic", "Critic"),
        ("diagrammer", "Diagrammer"),
        ("docwriter", "Doc Writer"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=50, choices=ROLE_CHOICES)
    description = models.TextField(blank=True)
    config = models.JSONField(default=dict)  # temperature, model, etc.
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.role})"

    class Meta:
        db_table = "ai_agents"