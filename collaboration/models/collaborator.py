import uuid
from django.db import models
from user.models import User
from planner.models import Project


class Collaborator(models.Model):
    ROLE_CHOICES = [
        ("viewer", "Viewer"),
        ("editor", "Editor"),
        ("owner", "Owner"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="collaborators"
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="collaborations"
    )
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default="viewer")
    invited_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("project", "user")

    def __str__(self):
        return f"{self.user.email} - {self.role} of {self.project.name}"
