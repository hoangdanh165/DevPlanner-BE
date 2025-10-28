from rest_framework import serializers
from ..models import Project
from .section import SectionSerializer


class ProjectListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = [
            "id",
            "name",
            "version",
            "description",
            "created_at",
            "updated_at",
        ]


class ProjectDetailSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source="user.email", read_only=True)
    sections = SectionSerializer(many=True, read_only=True)

    class Meta:
        model = Project
        fields = [
            "id",
            "user",
            "user_email",
            "sections",
            "name",
            "description",
            "version",
            "status",
            "tags",
            "visibility",
            "created_at",
            "updated_at",
            "deleted_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "deleted_at"]
