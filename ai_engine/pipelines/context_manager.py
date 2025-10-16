from planner.models import Project, Section
from django.core.cache import cache
from typing import Union


def load_context(project: Union[Project, dict]):
    """Combine all previous sections into one unified context string.

    If project is a dict (temporary), read cached sections; otherwise read from DB.
    """
    if isinstance(project, dict) and project.get("temp"):
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


def save_section(project: Union[Project, dict], title: str, content: str, order: int):
    """Create or update a section. For temporary projects, store sections in cache."""
    if isinstance(project, dict) and project.get("temp"):
        key = f"temp_project_sections:{project.get('id')}"
        sections = cache.get(key) or []
        # replace if title exists
        existing = next((s for s in sections if s.get("title") == title), None)
        if existing:
            existing["content"] = content
            existing["order_index"] = order
        else:
            sections.append({"title": title, "content": content, "order_index": order})
        cache.set(key, sections, None)
        return

    Section.objects.update_or_create(
        project=project,
        title=title,
        defaults={
            "order_index": order,
            "content": content,
        },
    )
