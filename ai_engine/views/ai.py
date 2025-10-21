import os
import requests
from django.shortcuts import render
from django.contrib.auth import authenticate
from django.db.models import Exists, OuterRef

from django.shortcuts import get_object_or_404
from rest_framework import viewsets, renderers
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import action
from rest_framework import status
from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from django.core.cache import cache

from django.db.models.functions import TruncMonth, TruncDate
from django.utils.timezone import now
from django.db.models import Count, Q
from core.utils.response import success_response, error_response
from ..tasks.generate_plan import run_pipeline_task
from planner.models import Project

CLIENT_ID = os.environ.get("CLIENT_ID")


class AIViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all().order_by("id")

    permission_classes = [IsAuthenticated]
    # serializer_class = UserSerializer

    @action(
        detail=False,
        url_path="generate-plan",
        methods=["post"],
        permission_classes=[IsAuthenticated],
        renderer_classes=[renderers.JSONRenderer],
    )
    def generate_plan(self, request):
        try:
            # Accept project data from frontend and store temporarily in cache.
            data = request.data or {}
            project_id = data.get("project_id")
            project_name = data.get("project_name") or data.get("name")
            description = data.get("description") or data.get("desc") or ""

            if not project_id or not project_name:
                return error_response(
                    errors=None,
                    message="project_id and project_name are required in the request",
                    status=400,
                )

            # Save straight to database

            # temp_key = f"temp_project:{project_id}"
            # project_payload = {
            #     "id": str(project_id),
            #     "name": project_name,
            #     "description": description,
            #     "temp": True,
            # }
            # # store without expiry (TTL: 24h)
            # cache.set(temp_key, project_payload, timeout=24 * 60 * 60)

            Project.objects.get_or_create(
                id=project_id,
                user=request.user,
                name=project_name,
                description=description,
            )

            project_payload = {
                "id": str(project_id),
                "name": project_name,
                "description": description,
                "temp": True,
            }

            # enqueue the pipeline task with the payload
            run_pipeline_task.delay(project_payload)

            return success_response(
                data=None, message="AI generation started", status=202
            )
        except Project.DoesNotExist:
            return error_response(errors=None, message="Project not found", status=404)
