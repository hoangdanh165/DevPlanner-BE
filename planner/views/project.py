import os
import requests
from django.shortcuts import render
from django.db.models import Exists, OuterRef
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, renderers
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status
from django.conf import settings
from django.utils import timezone
from ..models import Project
from ..serializers.project import (
    ProjectDetailSerializer,
    ProjectListSerializer,
    ProjectDetailMainSerializer,
)
from django.db.models.functions import TruncMonth, TruncDate
from django.utils.timezone import now
from django.db.models import Count, Q
from core.utils.response import success_response, error_response

from core.permissions import IsUser
from core.utils.custom_pagination import CustomPaginationProject


class ProjectViewSet(viewsets.ModelViewSet):
    # queryset = Project.objects.all().order_by("id")

    permission_classes = [IsAuthenticated]
    serializer_class = ProjectDetailSerializer
    pagination_class = CustomPaginationProject

    def get_queryset(self):
        user = self.request.user
        return Project.objects.filter(user=user, deleted_at__isnull=True).order_by(
            "-updated_at"
        )

    @action(
        detail=False,
        methods=["get"],
        url_path="all",
        permission_classes=[IsAuthenticated],
        renderer_classes=[renderers.JSONRenderer],
    )
    def get_all(self, request):
        queryset = self.get_queryset()

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request)
        serializer = ProjectListSerializer(page, many=True)

        meta = {
            "count": paginator.page.paginator.count,
            "total_pages": paginator.page.paginator.num_pages,
            "page": paginator.page.number,
            "page_size": paginator.page.paginator.per_page,
        }

        return success_response(
            data=serializer.data,
            meta=meta,
            message="Project plans retrieved successfully",
            status=200,
        )

    @action(
        detail=True,
        methods=["get"],
        url_path="detail",
        permission_classes=[IsAuthenticated],
        renderer_classes=[renderers.JSONRenderer],
    )
    def get_detail(self, request, pk):
        try:
            project = Project.objects.get(pk=pk, user=request.user)
        except Project.DoesNotExist:
            return error_response(
                errors=None,
                message="Project plan with this id not found",
                status=404,
            )

        except (ValueError, TypeError):
            return error_response(
                errors=None,
                message="Invalid project id",
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = ProjectDetailSerializer(project)

        return success_response(
            data=serializer.data,
            message="Project plan details retrieved successfully",
            status=200,
        )

    @action(
        detail=True,
        methods=["get"],
        url_path="detail-main",
        permission_classes=[IsAuthenticated],
        renderer_classes=[renderers.JSONRenderer],
    )
    def get_detail_main(self, request, pk):
        try:
            project = self.get_queryset().get(pk=pk)
        except Project.DoesNotExist:
            return error_response(
                errors=None,
                message="Project plan with this id not found",
                status=404,
            )

        except (ValueError, TypeError):
            return error_response(
                errors=None,
                message="Invalid project id",
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = ProjectDetailMainSerializer(project)

        return success_response(
            data=serializer.data,
            message="Project plan details retrieved successfully",
            status=200,
        )

    @action(
        methods=["post"],
        detail=False,
        url_path="delete-multiple",
        permission_classes=[IsUser],
    )
    def delete_multiple(self, request):
        project_ids = request.data.get("ids", [])

        if not project_ids:
            return error_response(
                errors=None,
                message="No ID(s) provided!",
                status=400,
            )

        projects = Project.objects.filter(id__in=project_ids)

        if not projects.exists():
            return Response(
                {"error": "Can not found project(s) with provided ID(s)!"},
                status=status.HTTP_404_NOT_FOUND,
            )

        print(projects)
        deleted_count, _ = projects.delete()
        return success_response(
            message=f"Deleted {deleted_count} projects(s) successfully!",
            status=200,
        )
