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
            "status",
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


class ProjectDetailMainSerializer(serializers.ModelSerializer):
    updatedAt = serializers.DateTimeField(source="updated_at", read_only=True)
    currentVersion = serializers.IntegerField(source="version", read_only=True)
    availableVersions = serializers.SerializerMethodField()
    sections = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            "id",
            "name",
            "description",
            "status",
            "visibility",
            "tags",
            "updatedAt",
            "currentVersion",
            "availableVersions",
            "sections",
        ]
        read_only_fields = ["id"]

    def get_availableVersions(self, obj: Project):
        if not obj.version:
            return []

        return list(range(1, obj.version + 1))

    def get_sections(self, obj):
        result = {}
        sections = obj.sections.all().order_by("order_index", "title")
        diagrams = []
        for section in sections:
            if "diagram" in section.title:
                diagrams.append({"type": section.title, "code": section.content})

                continue

            key = section.title
            content = section.content

            result[key] = content

        if diagrams:
            result["diagrams"] = diagrams

        return result
