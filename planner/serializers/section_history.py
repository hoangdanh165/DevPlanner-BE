from rest_framework import serializers
from ..models.section_history import SectionVersion


class SectionVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SectionVersion
        fields = (
            "id",
            "project_version",
            "section_version",
            "title",
            "content",
            "content_json",
            "order_index",
            "generated_by_ai",
            "created_at",
            "created_by",
        )
