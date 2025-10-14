import uuid
from django.db import models
from planner.models import Project, Section


class AIHistory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="ai_history"
    )
    section = models.ForeignKey(
        Section,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="ai_history",
    )
    model_name = models.CharField(max_length=100)
    prompt = models.TextField()
    response = models.TextField()
    token_usage = models.JSONField(default=dict)
    cost_estimate = models.DecimalField(
        max_digits=10, decimal_places=4, null=True, blank=True
    )
    duration_ms = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"AI call ({self.model_name}) on {self.project.name}"
