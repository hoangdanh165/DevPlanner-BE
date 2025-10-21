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
from ..serializers.project import ProjectDetailSerializer, ProjectListSerializer
from django.db.models.functions import TruncMonth, TruncDate
from django.utils.timezone import now
from django.db.models import Count, Q
from core.utils.response import success_response, error_response

from core.permissions import IsUser
from core.utils.custom_pagination import CustomPaginationProject


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all().order_by("id")

    permission_classes = [IsAuthenticated]
    serializer_class = ProjectListSerializer
    pagination_class = CustomPaginationProject

    @action(
        detail=False,
        methods=["get"],
        url_path="all",
        permission_classes=[IsAuthenticated],
        renderer_classes=[renderers.JSONRenderer],
    )
    def get_all(self, request):
        user = request.user
        queryset = Project.objects.filter(user=user).order_by("-created_at")

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request)
        serializer = self.get_serializer(page, many=True)

        meta = {
            "count": paginator.page.paginator.count,
            "total_pages": paginator.page.paginator.num_pages,
            "page": paginator.page.number,
            "page_size": paginator.page.paginator.per_page,
        }

        return success_response(
            data=serializer.data,
            meta=meta,
            message="Projects retrieved successfully",
            status=200,
        )
