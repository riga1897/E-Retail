"""
Сервис для работы с иерархией сети.

Отвечает за расчёт уровня иерархии узла
на основе цепочки поставщиков.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from network.models import NetworkNode


def calculate_hierarchy_level(node: NetworkNode) -> int:
    """
    Рассчитывает уровень иерархии узла сети.

    Уровень определяется количеством звеньев
    в цепочке поставщиков до корневого узла (завода).

    Args:
        node: Узел сети, для которого рассчитывается уровень.

    Returns:
        Целое число — уровень иерархии (0 для завода).
    """
    level: int = 0
    current: NetworkNode | None = node.supplier
    visited: set[int] = set()

    while current is not None:
        if current.pk in visited:
            break
        visited.add(current.pk)
        level += 1
        current = current.supplier

    return level
