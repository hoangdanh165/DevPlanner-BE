import os
import requests
from django.shortcuts import render
from django.db.models import Exists, OuterRef, Max
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, renderers
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status
from django.conf import settings
from django.utils import timezone
from ..models import Project, SectionVersion
from ..serializers.project import (
    ProjectDetailSerializer,
    ProjectListSerializer,
    ProjectDetailMainSerializer,
)
from ..serializers.section_history import (
    SectionVersionSerializer,
    SectionVersionListSerializer,
)

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

    @staticmethod
    def _normalize_version_param(raw: str | None) -> tuple[bool, int | None]:
        """
        Returns (is_latest, version_int_or_None).
        - None / "" / "latest" / "current"  -> (True, None)   (caller will fetch latest)
        - "v3" / "3"                        -> (False, 3)
        Raises ValueError if invalid.
        """
        if raw is None or raw == "":
            return True, None

        raw_l = raw.strip().lower()
        if raw_l in {"latest", "current"}:
            return True, None

        if raw_l.startswith("v"):
            raw_l = raw_l[1:]

        # must be positive int
        v = int(raw_l)  # may raise ValueError
        if v <= 0:
            raise ValueError("Version must be a positive integer.")
        return False, v

    def _resolve_version_number(
        self, project, is_latest: bool, version_num: int | None
    ) -> int | None:
        """
        If latest → return the max version that exists for this project (or None if no rows).
        Else → return the requested version number.
        """
        if is_latest:
            agg = SectionVersion.objects.filter(project=project).aggregate(
                max_v=Max("version")
            )
            return agg["max_v"]
        return version_num

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
        detail=True,
        methods=["get"],
        url_path="version-history",
        permission_classes=[IsAuthenticated],
        renderer_classes=[renderers.JSONRenderer],
    )
    def get_version_history(self, request, pk=None):
        try:
            project = self.get_queryset().get(pk=pk)
        except Project.DoesNotExist:
            return error_response(
                errors=None,
                message="Project plan with this id not found",
                status=status.HTTP_404_NOT_FOUND,
            )
        except (ValueError, TypeError):
            return error_response(
                errors=None,
                message="Invalid project id",
                status=status.HTTP_400_BAD_REQUEST,
            )

        raw = request.query_params.get("version")
        try:
            is_latest, version_num = self._normalize_version_param(raw)
        except ValueError as e:
            return error_response(
                errors={"version": [str(e)]},
                message="Invalid version parameter.",
                status=status.HTTP_400_BAD_REQUEST,
            )

        resolved_version = self._resolve_version_number(project, is_latest, version_num)
        if resolved_version is None:
            return error_response(
                errors=None,
                message="No versions exist for this project.",
                status=status.HTTP_404_NOT_FOUND,
            )

        sections_qs = (
            SectionVersion.objects.filter(
                project=project, section_version=resolved_version
            )
            .select_related("section")
            .order_by("order_index")
        )

        if not sections_qs.exists():
            return error_response(
                errors=None,
                message=f"No section snapshots found for version {resolved_version}.",
                status=status.HTTP_404_NOT_FOUND,
            )

        list_serializer = SectionVersionListSerializer(child=SectionVersionSerializer())
        sections_data = list_serializer.to_representation(sections_qs)

        return success_response(
            data=sections_data,
            message="Project plan version retrieved successfully",
            status=status.HTTP_200_OK,
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
