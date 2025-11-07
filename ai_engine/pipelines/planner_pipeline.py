from .steps import generate
from .context_manager import load_context
from ..services.pubsub import get_default_publisher

pubisher = get_default_publisher()


def _get_project_id_for_publish(project):
    # support both ORM project and temp dict
    if hasattr(project, "id"):
        return str(project.id)
    if isinstance(project, dict):
        return str(project.get("id"))
    return "unknown"


order_map = {
    "overview": 1,
    "features": 2,
    "techstack": 3,
    "tasks": 4,
    "diagrams_gantt": 5,
    "diagrams_er": 6,
    "diagrams_architecture": 7,
    "diagrams_sequence": 8,
    "docs": 9,
}


def _get_order_index(section: str) -> int:
    return order_map.get(section, 999)


def run_project_pipeline(project):
    """
    Run each step sequentially with context carry-over.
    project can be a Django Project instance or a dict (temporary payload).
    """
    pid = _get_project_id_for_publish(project)

    for section in order_map:
        order_index = _get_order_index(section)
        progress_message = section + "_start"
        pubisher.publish(pid, progress_message, None)
        generate(project, section=section, order_index=order_index)

    pubisher.publish(pid, "pipeline_complete", {"version": "v1"})


def run_section_regeneration(project, section):
    """
    Regenerate a specific section of project plan
    """
    pid = _get_project_id_for_publish(project)
    order_index = _get_order_index(section)

    progress_message = section + "_start"
    pubisher.publish(pid, progress_message, None)

    new_version = generate(project, section=section, order_index=order_index)

    pubisher.publish(pid, "pipeline_complete", {"version": new_version})
