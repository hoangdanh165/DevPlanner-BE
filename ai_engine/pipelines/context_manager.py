from planner.models import Project, Section, SectionVersion
from django.core.cache import cache
from typing import Union
from django.db import transaction


def load_context(project: Union[Project, dict]):
    """Combine all previous sections into one unified context string.

    If project is a dict (temporary), read cached sections; otherwise read from DB.
    """
    if isinstance(project, dict):
        key = f"temp_project_sections:{project.get('id')}"
        sections = cache.get(key) or []
        context = "\n\n".join(
            [
                f"[{s['title']}]\n{s['content']}"
                for s in sorted(sections, key=lambda x: x.get("order_index", 0))
                if s.get("content")
            ]
        )
        return context or "No prior context."

    sections = Section.objects.filter(project=project).order_by("order_index")
    context = "\n\n".join([f"[{s.title}]\n{s.content}" for s in sections if s.content])
    return context or "No prior context."


def bump_project_version(base_project: Project) -> str:
    current = base_project.version

    new = current + 1
    base_project.version = new
    base_project.save(update_fields=["version"])

    return new


@transaction.atomic
def save_section(
    project: Union[Project, dict], title: str, content: str, order: int
) -> str:
    """Create or update a section. Bump project version only when section is updated."""
    if isinstance(project, dict):
        base_project = Project.objects.get(id=project.get("id"))
    else:
        base_project = project

    section, created = Section.objects.select_for_update().get_or_create(
        project=base_project,
        title=title,
        defaults={
            "order_index": order,
            "content": content,
            "content_json": {},
            "generated_by_ai": True,
            "current_version": 1,
        },
    )

    if created:
        SectionVersion.objects.create(
            project=base_project,
            section=section,
            project_version=base_project.version,
            section_version=section.current_version,
            title=section.title,
            content=section.content,
            content_json=section.content_json,
            order_index=section.order_index,
            generated_by_ai=section.generated_by_ai,
        )
        return base_project.version

    new_project_version = bump_project_version(base_project)

    # Increase version of section
    section.current_version = (section.current_version or 1) + 1
    section.content = content
    section.order_index = order
    section.generated_by_ai = True
    section.save(
        update_fields=[
            "content",
            "order_index",
            "generated_by_ai",
            "current_version",
            "updated_at",
        ]
    )

    SectionVersion.objects.create(
        project=base_project,
        section=section,
        project_version=new_project_version,
        section_version=section.current_version,
        title=section.title,
        content=section.content,
        content_json=section.content_json,
        order_index=section.order_index,
        generated_by_ai=section.generated_by_ai,
    )

    return new_project_version
