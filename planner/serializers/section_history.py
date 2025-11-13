from rest_framework import serializers
from ..models.section_history import SectionVersion


class SectionVersionListSerializer(serializers.ListSerializer):
    """
    response data format:
    {
      "sections": {
        "overview": "...",
        "features": {...},
        "techstack": {...},
        "tasks": {...},
        "docs": "...",
        "diagrams": [
          { "type": "diagrams_gantt", "code": "..." },
          { "type": "diagrams_er", "code": "..." },
          ...
        ]
      }
    }
    """

    def to_representation(self, data):
        sections_data = {}
        diagrams = []

        iterable = data.all() if hasattr(data, "all") else data
        iterable = sorted(iterable, key=lambda o: o.order_index)

        for obj in iterable:
            section_title = (obj.section.title or "").strip()
            value = obj.content

            if section_title.startswith("diagrams_"):
                diagram_type = section_title
                code = value

                diagrams.append(
                    {
                        "type": diagram_type,
                        "code": code,
                    }
                )
            else:
                sections_data[section_title] = value

        if diagrams:
            sections_data["diagrams"] = diagrams

        return {"sections": sections_data}


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

        list_serializer_class = SectionVersionListSerializer
