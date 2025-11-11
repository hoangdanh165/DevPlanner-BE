from rest_framework import serializers
from ..models import Section, Project


class SectionSerializer(serializers.ModelSerializer):
    currentVersion = serializers.IntegerField(source="current_version", read_only=True)

    class Meta:
        model = Section
        fields = [
            "id",
            "title",
            "content",
            "content_json",
            "currentVersion",
            "order_index",
            "generated_by_ai",
            "updated_at",
        ]
        read_only_fields = ["id", "updated_at"]
