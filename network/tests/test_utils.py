"""
Тесты утилит приложения network.

Проверяют вспомогательные функции.
"""

from __future__ import annotations

from decimal import Decimal

from network.utils.helpers import format_currency, get_node_type_display_name


class TestGetNodeTypeDisplayName:
    """Тесты функции get_node_type_display_name."""

    def test_factory_type(self) -> None:
        """Тест отображения типа 'Завод'."""
        assert get_node_type_display_name("FACTORY") == "Завод"

    def test_retail_network_type(self) -> None:
        """Тест отображения типа 'Розничная сеть'."""
        assert get_node_type_display_name("RETAIL_NETWORK") == "Розничная сеть"

    def test_individual_entrepreneur_type(self) -> None:
        """Тест отображения типа 'ИП'."""
        result = get_node_type_display_name("INDIVIDUAL_ENTREPRENEUR")
        assert result == "Индивидуальный предприниматель"

    def test_unknown_type(self) -> None:
        """Тест отображения неизвестного типа."""
        assert get_node_type_display_name("UNKNOWN") == "UNKNOWN"


class TestFormatCurrency:
    """Тесты функции format_currency."""

    def test_format_integer(self) -> None:
        """Тест форматирования целого числа."""
        assert format_currency(1000) == "1 000.00 руб."

    def test_format_decimal(self) -> None:
        """Тест форматирования десятичного числа."""
        assert format_currency(Decimal("1234.56")) == "1 234.56 руб."

    def test_format_zero(self) -> None:
        """Тест форматирования нуля."""
        assert format_currency(0) == "0.00 руб."

    def test_format_none(self) -> None:
        """Тест форматирования None."""
        assert format_currency(None) == "0.00 руб."

    def test_format_string(self) -> None:
        """Тест форматирования строки."""
        assert format_currency("invalid") == "0.00 руб."
