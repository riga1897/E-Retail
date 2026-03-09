"""
Классы прав доступа для API приложения network.

Определяет кастомные permission-классы
для ограничения доступа к API.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from rest_framework.permissions import BasePermission

if TYPE_CHECKING:
    from rest_framework.request import Request


class IsActiveEmployee(BasePermission):
    """
    Разрешает доступ только активным сотрудникам.

    Проверяет, что пользователь аутентифицирован и активен (is_active=True).
    """

    message: str = "Доступ разрешён только активным сотрудникам."

    def has_permission(self, request: Request, view: Any) -> bool:
        """
        Проверяет права доступа пользователя.

        Args:
            request: HTTP-запрос.
            view: Представление, к которому осуществляется доступ.

        Returns:
            True, если пользователь аутентифицирован и активен.
        """
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.is_active
        )
