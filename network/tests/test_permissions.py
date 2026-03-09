"""
Тесты прав доступа приложения network.

Проверяют работу кастомного permission-класса IsActiveEmployee.
"""

from __future__ import annotations

import pytest
from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory

from network.permissions import IsActiveEmployee
from network.tests.factories import UserFactory


@pytest.mark.django_db
class TestIsActiveEmployee:
    """Тесты permission-класса IsActiveEmployee."""

    def setup_method(self) -> None:
        """Инициализация объектов для тестов."""
        self.permission = IsActiveEmployee()
        self.factory = RequestFactory()

    def test_active_user_has_access(self) -> None:
        """Тест: активный пользователь имеет доступ."""
        user = UserFactory(is_active=True)
        request = self.factory.get("/")
        request.user = user  # type: ignore[assignment]

        assert self.permission.has_permission(request, None) is True  # type: ignore[arg-type]

    def test_inactive_user_denied(self) -> None:
        """Тест: неактивный пользователь не имеет доступа."""
        user = UserFactory(is_active=False)
        request = self.factory.get("/")
        request.user = user  # type: ignore[assignment]

        assert self.permission.has_permission(request, None) is False  # type: ignore[arg-type]

    def test_anonymous_user_denied(self) -> None:
        """Тест: анонимный пользователь не имеет доступа."""
        request = self.factory.get("/")
        request.user = AnonymousUser()

        assert self.permission.has_permission(request, None) is False  # type: ignore[arg-type]

    def test_permission_message(self) -> None:
        """Тест сообщения об ошибке доступа."""
        assert "активным сотрудникам" in self.permission.message
