from celery import shared_task
from ai_engine.pipelines.planner_pipeline import run_project_pipeline
from django.core.cache import cache


@shared_task(bind=True, max_retries=3)
def run_pipeline_task(self, project):
    """
    Accept either a Project id (string) or a dict payload representing a temporary project.
    """
    from ai_engine.services.pubsub import get_default_publisher

    publisher = get_default_publisher()
    try:
        project_id = project.get("id")
        print("PROJ ID", project_id)
        if not project or not project_id:
            publisher.publish(str(project_id), "pipeline_failed", 0)
            return

        publisher.publish(str(project_id), "pipeline_started", 0)
        run_project_pipeline(project)

    except Exception as e:
        publisher.publish(str(project_id), "pipeline_failed", 0)
        raise self.retry(exc=e, countdown=10)
