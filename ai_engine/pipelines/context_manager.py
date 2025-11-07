from planner.models import Project, Section
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
    current = (base_project.version or "").strip()

    if not current.lower().startswith("v"):
        num = 1
    else:
        try:
            num = int(current[1:])
        except ValueError:
            num = 1

    new = f"v{num + 1 }"
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

    _, created = Section.objects.update_or_create(
        project=base_project,
        title=title,
        defaults={
            "order_index": order,
            "content": content,
        },
    )

    if not created:
        new = bump_project_version(base_project)
        return new

    return base_project.version
