"""
URL-маршруты приложения network.

Определяет маршруты для API.
"""

from __future__ import annotations

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from network.views import NetworkNodeViewSet, ProductViewSet

router = DefaultRouter()
router.register(r"network-nodes", NetworkNodeViewSet, basename="networknode")
router.register(r"products", ProductViewSet, basename="product")

urlpatterns: list = [
    path("", include(router.urls)),
]
