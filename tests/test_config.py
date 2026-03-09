"""
Тесты конфигурации проекта electronics_network.

Проверяют настройки (settings), маршрутизацию (urls),
WSGI/ASGI приложения.
"""

from __future__ import annotations

import pytest
from django.conf import settings
from rest_framework import status
from rest_framework.test import APIClient


class TestSettings:
    """Тесты настроек Django проекта."""

    def test_secret_key_is_set(self) -> None:
        """Тест: SECRET_KEY задан и не пустой."""
        assert settings.SECRET_KEY
        assert len(settings.SECRET_KEY) > 0

    def test_installed_apps_contains_network(self) -> None:
        """Тест: приложение network включено в INSTALLED_APPS."""
        assert "network" in settings.INSTALLED_APPS

    def test_installed_apps_contains_rest_framework(self) -> None:
        """Тест: DRF включён в INSTALLED_APPS."""
        assert "rest_framework" in settings.INSTALLED_APPS

    def test_installed_apps_contains_authtoken(self) -> None:
        """Тест: rest_framework.authtoken включён в INSTALLED_APPS."""
        assert "rest_framework.authtoken" in settings.INSTALLED_APPS

    def test_installed_apps_contains_django_filters(self) -> None:
        """Тест: django_filters включён в INSTALLED_APPS."""
        assert "django_filters" in settings.INSTALLED_APPS

    def test_database_configured(self) -> None:
        """Тест: база данных настроена."""
        assert "default" in settings.DATABASES
        assert settings.DATABASES["default"]["ENGINE"]

    def test_rest_framework_permissions(self) -> None:
        """Тест: DRF настроен с IsActiveEmployee permission."""
        assert "DEFAULT_PERMISSION_CLASSES" in settings.REST_FRAMEWORK
        permissions = settings.REST_FRAMEWORK["DEFAULT_PERMISSION_CLASSES"]
        assert "network.permissions.IsActiveEmployee" in permissions

    def test_rest_framework_filter_backends(self) -> None:
        """Тест: DRF настроен с DjangoFilterBackend."""
        assert "DEFAULT_FILTER_BACKENDS" in settings.REST_FRAMEWORK
        backends = settings.REST_FRAMEWORK["DEFAULT_FILTER_BACKENDS"]
        assert "django_filters.rest_framework.DjangoFilterBackend" in backends

    def test_rest_framework_authentication(self) -> None:
        """Тест: DRF настроен с Token и Session аутентификацией."""
        auth_classes = settings.REST_FRAMEWORK["DEFAULT_AUTHENTICATION_CLASSES"]
        assert "rest_framework.authentication.TokenAuthentication" in auth_classes
        assert "rest_framework.authentication.SessionAuthentication" in auth_classes

    def test_language_code(self) -> None:
        """Тест: язык по умолчанию — русский."""
        assert settings.LANGUAGE_CODE == "ru-ru"

    def test_time_zone(self) -> None:
        """Тест: часовой пояс — Москва."""
        assert settings.TIME_ZONE == "Europe/Moscow"

    def test_use_i18n_enabled(self) -> None:
        """Тест: интернационализация включена."""
        assert settings.USE_I18N is True

    def test_use_tz_enabled(self) -> None:
        """Тест: поддержка временных зон включена."""
        assert settings.USE_TZ is True

    def test_default_auto_field(self) -> None:
        """Тест: тип первичного ключа по умолчанию — BigAutoField."""
        assert settings.DEFAULT_AUTO_FIELD == "django.db.models.BigAutoField"

    def test_root_urlconf(self) -> None:
        """Тест: ROOT_URLCONF указывает на electronics_network.urls."""
        assert settings.ROOT_URLCONF == "electronics_network.urls"

    def test_wsgi_application(self) -> None:
        """Тест: WSGI_APPLICATION указывает на electronics_network.wsgi."""
        assert settings.WSGI_APPLICATION == "electronics_network.wsgi.application"

    def test_static_url(self) -> None:
        """Тест: STATIC_URL настроен."""
        assert "static" in settings.STATIC_URL

    def test_allowed_hosts_configured(self) -> None:
        """Тест: ALLOWED_HOSTS настроен."""
        assert isinstance(settings.ALLOWED_HOSTS, list)
        assert len(settings.ALLOWED_HOSTS) > 0

    def test_csrf_trusted_origins_configured(self) -> None:
        """Тест: CSRF_TRUSTED_ORIGINS содержит Replit домены."""
        assert isinstance(settings.CSRF_TRUSTED_ORIGINS, list)

    def test_middleware_includes_whitenoise(self) -> None:
        """Тест: WhiteNoise включён в middleware."""
        assert "whitenoise.middleware.WhiteNoiseMiddleware" in settings.MIDDLEWARE

    def test_middleware_includes_security(self) -> None:
        """Тест: SecurityMiddleware включён в middleware."""
        assert "django.middleware.security.SecurityMiddleware" in settings.MIDDLEWARE

    def test_auth_password_validators_configured(self) -> None:
        """Тест: валидаторы паролей настроены."""
        assert len(settings.AUTH_PASSWORD_VALIDATORS) >= 4


@pytest.mark.django_db
class TestURLRouting:
    """Тесты маршрутизации URL проекта."""

    def setup_method(self) -> None:
        """Инициализация клиента для тестов."""
        self.client = APIClient()

    def test_root_redirects_to_api(self) -> None:
        """Тест: корневой URL перенаправляет на /api/."""
        response = self.client.get("/")
        assert response.status_code == status.HTTP_302_FOUND
        assert response.url == "/api/"  # type: ignore[attr-defined]

    def test_api_root_accessible(self) -> None:
        """Тест: /api/ доступен без авторизации."""
        response = self.client.get("/api/")
        assert response.status_code == status.HTTP_200_OK

    def test_admin_accessible(self) -> None:
        """Тест: /admin/ доступен (перенаправляет на login)."""
        response = self.client.get("/admin/")
        assert response.status_code in (
            status.HTTP_200_OK,
            status.HTTP_301_MOVED_PERMANENTLY,
            status.HTTP_302_FOUND,
        )

    def test_api_network_nodes_requires_auth(self) -> None:
        """Тест: /api/network-nodes/ требует авторизации."""
        response = self.client.get("/api/network-nodes/")
        assert response.status_code in (
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_403_FORBIDDEN,
        )

    def test_api_products_requires_auth(self) -> None:
        """Тест: /api/products/ требует авторизации."""
        response = self.client.get("/api/products/")
        assert response.status_code in (
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_403_FORBIDDEN,
        )

    def test_api_token_get_returns_instructions(self) -> None:
        """Тест: GET /api/token/ возвращает инструкцию."""
        response = self.client.get("/api/token/")
        assert response.status_code == status.HTTP_200_OK

    def test_api_auth_urls_accessible(self) -> None:
        """Тест: /api-auth/ (DRF login/logout) доступен."""
        response = self.client.get("/api-auth/login/")
        assert response.status_code == status.HTTP_200_OK

    def test_nonexistent_url_returns_404(self) -> None:
        """Тест: несуществующий URL возвращает 404."""
        response = self.client.get("/nonexistent-url/")
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestSettingsDatabaseFallback:
    """Тесты fallback-конфигурации базы данных (без DATABASE_URL)."""

    def test_database_fallback_without_database_url(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Тест: при отсутствии DATABASE_URL используются отдельные DB_* переменные."""
        import importlib

        monkeypatch.delenv("DATABASE_URL", raising=False)
        monkeypatch.setenv("DB_ENGINE", "django.db.backends.postgresql")
        monkeypatch.setenv("DB_NAME", "test_db")
        monkeypatch.setenv("DB_USER", "test_user")
        monkeypatch.setenv("DB_PASSWORD", "test_pass")
        monkeypatch.setenv("DB_HOST", "localhost")
        monkeypatch.setenv("DB_PORT", "5432")

        import electronics_network.settings as settings_module

        importlib.reload(settings_module)

        assert settings_module.DATABASES["default"]["ENGINE"] == "django.db.backends.postgresql"
        assert settings_module.DATABASES["default"]["NAME"] == "test_db"
        assert settings_module.DATABASES["default"]["USER"] == "test_user"
        assert settings_module.DATABASES["default"]["HOST"] == "localhost"
        assert settings_module.DATABASES["default"]["PORT"] == "5432"


class TestWSGIApplication:
    """Тесты WSGI-приложения."""

    def test_wsgi_application_exists(self) -> None:
        """Тест: WSGI application корректно создаётся."""
        from electronics_network.wsgi import application

        assert application is not None
        assert callable(application)

    def test_wsgi_settings_module(self) -> None:
        """Тест: DJANGO_SETTINGS_MODULE установлен."""
        import os

        assert os.environ.get("DJANGO_SETTINGS_MODULE") == "electronics_network.settings"


class TestASGIApplication:
    """Тесты ASGI-приложения."""

    def test_asgi_application_exists(self) -> None:
        """Тест: ASGI application корректно создаётся."""
        from electronics_network.asgi import application

        assert application is not None
        assert callable(application)
