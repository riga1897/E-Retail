"""
Конфигурация pytest для интеграционных тестов.

Содержит общие фикстуры для тестирования.
"""

from __future__ import annotations

import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient


@pytest.fixture
def api_client() -> APIClient:
    """Фикстура: API-клиент для тестирования."""
    return APIClient()


@pytest.fixture
def active_user(db: None) -> User:
    """Фикстура: активный пользователь."""
    return User.objects.create_user(
        username="testuser",
        password="testpass123",
        is_active=True,
        is_staff=True,
    )


@pytest.fixture
def inactive_user(db: None) -> User:
    """Фикстура: неактивный пользователь."""
    return User.objects.create_user(
        username="inactiveuser",
        password="testpass123",
        is_active=False,
    )


@pytest.fixture
def authenticated_client(
    api_client: APIClient, active_user: User
) -> APIClient:
    """Фикстура: аутентифицированный API-клиент."""
    api_client.force_authenticate(user=active_user)
    return api_client
