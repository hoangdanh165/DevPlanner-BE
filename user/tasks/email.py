from celery import shared_task
from ai_engine.pipelines.planner_pipeline import run_project_pipeline
from django.core.cache import cache
from ..services.user import (
    send_verification_email,
    send_password_reset_email,
)
from ..models.user import User


@shared_task(bind=True, max_retries=3)
def run_send_password_reset_email(self, user_id):
    try:
        user = User.objects.get(id=user_id)
        send_password_reset_email(user)
    except Exception as e:
        raise self.retry(exc=e, countdown=10)


@shared_task(bind=True, max_retries=3)
def run_send_verification_email(self, user_id):
    try:
        user = User.objects.get(id=user_id)
        send_verification_email(user)
    except Exception as e:
        raise self.retry(exc=e, countdown=10)
