from django.urls import path, include
from rest_framework import routers
from .views.ai import AIViewSet

router = routers.DefaultRouter()
router.register(r"ai", AIViewSet, basename="ai")

app_name = "ai"
urlpatterns = [
    path("api/v1/", include(router.urls)),
]
