from rest_framework import serializers
from ..models.section import Section


class SectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Section
        fields = [
            "id",
            "title",
            "content",
            "content_json",
            "order_index",
            "generated_by_ai",
            "updated_at",
        ]
        read_only_fields = ["id", "updated_at"]
