from .steps import (
    generate_overview,
    generate_tech_stack,
    generate_features,
    generate_tasks,
    generate_docs,
)
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


def run_project_pipeline(project):
    """Run each step sequentially with context carry-over.

    project can be a Django Project instance or a dict (temporary payload).
    """
    pid = _get_project_id_for_publish(project)

    pubisher.publish(pid, "overview_start", None)
    overview_text = generate_overview(project)

    pubisher.publish(pid, "features_start", None)
    features_text = generate_features(project)

    pubisher.publish(pid, "techstack_start", None)
    techstack_text = generate_tech_stack(project)

    pubisher.publish(pid, "tasks_start", None)
    tasks_tech = generate_tasks(project)
    print(tasks_tech)

    pubisher.publish(pid, "docs_start", None)
    techstack_text = generate_docs(project)

    pubisher.publish(pid, "pipeline_complete", None)
