"""
Вспомогательные функции для приложения network.

Содержит утилиты, не относящиеся к бизнес-логике.
"""

from __future__ import annotations

from typing import Any


def get_node_type_display_name(node_type: str) -> str:
    """
    Возвращает человекочитаемое название типа узла.

    Args:
        node_type: Код типа узла (FACTORY, RETAIL_NETWORK, INDIVIDUAL_ENTREPRENEUR).

    Returns:
        Строка с названием на русском языке.
    """
    type_names: dict[str, str] = {
        "FACTORY": "Завод",
        "RETAIL_NETWORK": "Розничная сеть",
        "INDIVIDUAL_ENTREPRENEUR": "Индивидуальный предприниматель",
    }
    return type_names.get(node_type, node_type)


def format_currency(amount: Any) -> str:
    """
    Форматирует денежную сумму для отображения.

    Args:
        amount: Сумма для форматирования.

    Returns:
        Строка с отформатированной суммой (например, '1 234.56 руб.').
    """
    try:
        value = float(amount)
        formatted = f"{value:,.2f}".replace(",", " ")
        return f"{formatted} руб."
    except (TypeError, ValueError):
        return "0.00 руб."
