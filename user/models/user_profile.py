import uuid
from django.db import models
from .user import User


class UserProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")

    preferred_stack = models.JSONField(default=list)
    skill_level = models.CharField(max_length=50, blank=True)
    timezone = models.CharField(max_length=50, blank=True)

    ai_temperature = models.FloatField(default=0.7)

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Profile({self.user.email})"

    class Meta:
        db_table = "user_profile"
