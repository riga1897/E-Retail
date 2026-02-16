"""
Тесты Token-аутентификации.

Проверяют получение токена и доступ к API с использованием токена.
"""

from __future__ import annotations

import pytest
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APIClient


@pytest.mark.django_db
class TestObtainToken:
    """Тесты получения токена авторизации."""

    def test_obtain_token_success(
        self, api_client: APIClient, active_user: User
    ) -> None:
        """Тест успешного получения токена."""
        response = api_client.post(
            "/api/token/",
            {"username": "testuser", "password": "testpass123"},
        )
        assert response.status_code == status.HTTP_200_OK
        assert "token" in response.data

    def test_obtain_token_wrong_password(
        self, api_client: APIClient, active_user: User
    ) -> None:
        """Тест получения токена с неверным паролем."""
        response = api_client.post(
            "/api/token/",
            {"username": "testuser", "password": "wrongpassword"},
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_obtain_token_nonexistent_user(
        self, api_client: APIClient
    ) -> None:
        """Тест получения токена для несуществующего пользователя."""
        response = api_client.post(
            "/api/token/",
            {"username": "nonexistent", "password": "testpass123"},
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_obtain_token_inactive_user(
        self, api_client: APIClient, inactive_user: User
    ) -> None:
        """Тест получения токена для неактивного пользователя."""
        response = api_client.post(
            "/api/token/",
            {"username": "inactiveuser", "password": "testpass123"},
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_obtain_token_missing_fields(
        self, api_client: APIClient
    ) -> None:
        """Тест получения токена без указания username/password."""
        response = api_client.post("/api/token/", {})
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_obtain_token_missing_password(
        self, api_client: APIClient
    ) -> None:
        """Тест получения токена без пароля."""
        response = api_client.post("/api/token/", {"username": "testuser"})
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_obtain_token_json_format(
        self, api_client: APIClient, active_user: User
    ) -> None:
        """Тест получения токена через JSON."""
        response = api_client.post(
            "/api/token/",
            {"username": "testuser", "password": "testpass123"},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        assert "token" in response.data


@pytest.mark.django_db
class TestTokenAuthentication:
    """Тесты доступа к API с использованием токена."""

    def test_access_api_with_token(
        self, api_client: APIClient, active_user: User
    ) -> None:
        """Тест доступа к API с токеном."""
        token_response = api_client.post(
            "/api/token/",
            {"username": "testuser", "password": "testpass123"},
        )
        token = token_response.data["token"]

        api_client.credentials(HTTP_AUTHORIZATION=f"Token {token}")
        response = api_client.get("/api/network-nodes/")
        assert response.status_code == status.HTTP_200_OK

    def test_access_api_with_invalid_token(
        self, api_client: APIClient
    ) -> None:
        """Тест доступа к API с невалидным токеном."""
        api_client.credentials(HTTP_AUTHORIZATION="Token invalidtoken123")
        response = api_client.get("/api/network-nodes/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_api_root_shows_token_url(
        self, api_client: APIClient
    ) -> None:
        """Тест: API Root содержит ссылку на токен (доступен без авторизации)."""
        response = api_client.get("/api/")
        assert response.status_code == status.HTTP_200_OK
        assert "auth" in response.data
        assert "obtain_token" in response.data["auth"]

    def test_api_root_shows_hint_for_anonymous(
        self, api_client: APIClient
    ) -> None:
        """Тест: API Root показывает подсказку для неавторизованных."""
        response = api_client.get("/api/")
        assert response.status_code == status.HTTP_200_OK
        assert "подсказка" in response.data

    def test_token_endpoint_get_returns_instructions(
        self, api_client: APIClient
    ) -> None:
        """Тест: GET /api/token/ возвращает инструкцию по использованию."""
        response = api_client.get("/api/token/")
        assert response.status_code == status.HTTP_200_OK
        assert "описание" in response.data
        assert "параметры" in response.data
        assert "username" in response.data["параметры"]
        assert "password" in response.data["параметры"]


@pytest.mark.django_db
class TestApiRootTokenAuth:
    """Тесты авторизации по токену через API Root."""

    def test_api_root_post_valid_token_json(
        self, api_client: APIClient, active_user: User
    ) -> None:
        """Тест: POST /api/ с валидным токеном (JSON) возвращает ресурсы и устанавливает сессию."""
        token_response = api_client.post(
            "/api/token/",
            {"username": "testuser", "password": "testpass123"},
        )
        token = token_response.data["token"]

        response = api_client.post("/api/", {"token": token}, format="json")
        assert response.status_code == status.HTTP_200_OK
        assert "message" in response.data
        assert "network-nodes" in response.data
        assert "products" in response.data

        get_response = api_client.get("/api/")
        assert "network-nodes" in get_response.data

    def test_api_root_post_valid_token_html_redirect(
        self, api_client: APIClient, active_user: User
    ) -> None:
        """Тест: POST /api/ с валидным токеном (HTML) редиректит на GET /api/."""
        token_response = api_client.post(
            "/api/token/",
            {"username": "testuser", "password": "testpass123"},
        )
        token = token_response.data["token"]

        response = api_client.post(
            "/api/", {"token": token}, HTTP_ACCEPT="text/html"
        )
        assert response.status_code == status.HTTP_302_FOUND
        assert "/api/" in response["Location"]

    def test_api_root_post_invalid_token(
        self, api_client: APIClient
    ) -> None:
        """Тест: POST /api/ с недействительным токеном."""
        response = api_client.post("/api/", {"token": "invalidtoken123"})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "error" in response.data

    def test_api_root_post_empty_token(
        self, api_client: APIClient
    ) -> None:
        """Тест: POST /api/ без токена."""
        response = api_client.post("/api/", {})
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_api_root_post_inactive_user_token(
        self, api_client: APIClient, inactive_user: User
    ) -> None:
        """Тест: POST /api/ с токеном неактивного пользователя."""
        from rest_framework.authtoken.models import Token

        token, _ = Token.objects.get_or_create(user=inactive_user)
        response = api_client.post("/api/", {"token": token.key})
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "error" in response.data

    def test_api_root_get_serializer(
        self, api_client: APIClient
    ) -> None:
        """Тест: ApiRootView.get_serializer() возвращает ApiRootTokenSerializer."""
        from network.views import ApiRootView

        view = ApiRootView()
        serializer = view.get_serializer()
        assert "token" in serializer.fields

    def test_obtain_token_get_serializer(
        self, api_client: APIClient
    ) -> None:
        """Тест: ObtainTokenView.get_serializer() возвращает TokenSerializer."""
        from network.views import ObtainTokenView

        view = ObtainTokenView()
        serializer = view.get_serializer()
        assert "username" in serializer.fields
        assert "password" in serializer.fields
