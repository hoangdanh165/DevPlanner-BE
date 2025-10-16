from .steps import generate_overview, generate_tech_stack, generate_features
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
    pubisher.publish(pid, "overview_start", 10)
    overview_text = generate_overview(project)
    print(overview_text)

    pubisher.publish(pid, "techstack_start", 40)
    techstack_text = generate_tech_stack(project)

    pubisher.publish(pid, "features_start", 70)
    features_text = generate_features(project)

    pubisher.publish(pid, "pipeline_complete", 100)
