from celery import shared_task
from planner.models import Project
from ai_engine.pipelines.planner_pipeline import run_project_pipeline
from django.core.cache import cache


@shared_task(bind=True, max_retries=3)
def run_pipeline_task(self, project_payload):
    """
    Accept either a Project id (string) or a dict payload representing a temporary project.
    """
    from ai_engine.services.pubsub import get_default_publisher

    publisher = get_default_publisher()
    try:
        project = None
        project_id = None

        # If a dict was passed (temp payload), use it directly
        if isinstance(project_payload, dict):
            project = project_payload
            project_id = project.get("id")
        else:
            # otherwise assume it's an id string and try to fetch from DB
            try:
                project = Project.objects.get(id=project_payload)
                project_id = project.id
            except Project.DoesNotExist:
                # try cache for temporary project
                temp = cache.get(f"temp_project:{project_payload}")
                if temp:
                    project = temp
                    project_id = temp.get("id")

        if not project or not project_id:
            publisher.publish(str(project_payload), "pipeline_failed", 0)
            return

        run_project_pipeline(project)
    except Exception as e:
        publisher.publish(str(project_payload), "pipeline_failed", 0)
        raise self.retry(exc=e, countdown=10)
