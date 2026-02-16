"""
Конфигурация URL-маршрутов проекта electronics_network.

API Root доступен по /api/ без авторизации.
Админ-панель доступна по /admin/.
"""

from django.contrib import admin
from django.urls import include, path
from django.views.generic.base import RedirectView

from network.views import api_root_view, obtain_token_view

urlpatterns: list = [
    path("", RedirectView.as_view(url="/api/", permanent=False), name="root-redirect"),
    path("admin/", admin.site.urls),
    path("api/", api_root_view, name="api-root"),
    path("api/token/", obtain_token_view, name="api-token"),
    path("api/", include("network.urls")),
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
]
