"""
Сервис валидации данных для узлов сети.

Содержит бизнес-правила валидации:
- Завод не может иметь поставщика.
- Нельзя создать циклическую зависимость.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from django.core.exceptions import ValidationError

if TYPE_CHECKING:
    from network.models import NetworkNode


def validate_factory_has_no_supplier(node: NetworkNode) -> None:
    """
    Проверяет, что завод не имеет поставщика.

    Args:
        node: Узел сети для валидации.

    Raises:
        ValidationError: Если завод имеет поставщика.
    """
    from network.models import NetworkNode

    if node.node_type == NetworkNode.NodeType.FACTORY and node.supplier is not None:
        raise ValidationError("Завод не может иметь поставщика.")


def validate_no_circular_dependency(node: NetworkNode) -> None:
    """
    Проверяет отсутствие циклических зависимостей в цепочке поставщиков.

    Проходит по цепочке поставщиков и проверяет, что узел
    не ссылается сам на себя (прямо или косвенно).

    Args:
        node: Узел сети для валидации.

    Raises:
        ValidationError: Если обнаружена циклическая зависимость.
    """
    if node.supplier is None:
        return

    visited: set[int] = set()
    if node.pk:
        visited.add(node.pk)

    current: NetworkNode | None = node.supplier
    while current is not None:
        if current.pk in visited:
            raise ValidationError(
                "Обнаружена циклическая зависимость в цепочке поставщиков."
            )
        visited.add(current.pk)
        current = current.supplier


def validate_non_factory_has_supplier(node: NetworkNode) -> None:
    """
    Проверяет, что не-завод имеет поставщика.

    Args:
        node: Узел сети для валидации.

    Raises:
        ValidationError: Если розничная сеть или ИП не имеет поставщика.
    """
    from network.models import NetworkNode

    if node.node_type != NetworkNode.NodeType.FACTORY and node.supplier is None:
        raise ValidationError(
            "Розничная сеть и индивидуальный предприниматель должны иметь поставщика."
        )
