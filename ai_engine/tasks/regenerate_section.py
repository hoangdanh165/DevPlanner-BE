from celery import shared_task
from ai_engine.pipelines.planner_pipeline import (
    run_section_regeneration,
)
from ai_engine.services.pubsub import get_default_publisher


publisher = get_default_publisher()


@shared_task(bind=True, max_retries=3)
def run_regenerate_section_task(self, project, section):
    """
    Accept either a Project id (string) or a dict payload representing a temporary project.
    """
    try:
        project_id = project.get("id")
        if not project or not project_id:
            publisher.publish(str(project_id), "pipeline_failed", None)
            return

        publisher.publish(str(project_id), "pipeline_started", None)
        run_section_regeneration(project, section)

    except Exception as e:
        publisher.publish(str(project_id), "pipeline_failed", None)
        raise self.retry(exc=e, countdown=10)
