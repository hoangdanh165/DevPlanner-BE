from django.urls import path, include
from rest_framework import routers
from .views.project import ProjectViewSet

router = routers.DefaultRouter()
router.register(r"projects", ProjectViewSet, basename="projects")

app_name = "planner"
urlpatterns = [
    path("api/v1/", include(router.urls)),
]
