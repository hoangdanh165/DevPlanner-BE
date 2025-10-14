import uuid
from django.db import models


class AICache(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    model_name = models.CharField(max_length=100)
    input_hash = models.CharField(max_length=64, unique=True)
    response_json = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cache({self.model_name})"
