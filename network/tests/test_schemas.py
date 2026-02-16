"""
Тесты Pydantic схем приложения network.

Проверяют валидацию входных данных через Pydantic.
"""

from __future__ import annotations

from decimal import Decimal

import pytest
from pydantic import ValidationError

from network.schemas.network_node import NetworkNodeCreateSchema, ProductCreateSchema


class TestNetworkNodeCreateSchema:
    """Тесты схемы NetworkNodeCreateSchema."""

    def test_valid_factory_data(self) -> None:
        """Тест валидных данных для завода."""
        schema = NetworkNodeCreateSchema(
            name="Тестовый завод",
            node_type="FACTORY",
            email="test@factory.com",
            country="Россия",
            city="Москва",
            street="Ленина",
            house_number="1",
        )
        assert schema.name == "Тестовый завод"
        assert schema.node_type == "FACTORY"

    def test_valid_retail_data(self) -> None:
        """Тест валидных данных для розничной сети."""
        schema = NetworkNodeCreateSchema(
            name="Тестовая сеть",
            node_type="RETAIL_NETWORK",
            email="test@retail.com",
            country="Россия",
            city="Москва",
            street="Ленина",
            house_number="2",
            supplier_id=1,
        )
        assert schema.supplier_id == 1

    def test_invalid_node_type(self) -> None:
        """Тест невалидного типа узла."""
        with pytest.raises(ValidationError):
            NetworkNodeCreateSchema(
                name="Тест",
                node_type="INVALID_TYPE",
                email="test@test.com",
                country="Россия",
                city="Москва",
                street="Ленина",
                house_number="1",
            )

    def test_factory_with_supplier_raises_error(self) -> None:
        """Тест: завод с поставщиком вызывает ошибку."""
        with pytest.raises(ValidationError):
            NetworkNodeCreateSchema(
                name="Завод",
                node_type="FACTORY",
                email="test@test.com",
                country="Россия",
                city="Москва",
                street="Ленина",
                house_number="1",
                supplier_id=1,
            )

    def test_short_name_raises_error(self) -> None:
        """Тест: слишком короткое имя вызывает ошибку."""
        with pytest.raises(ValidationError):
            NetworkNodeCreateSchema(
                name="A",
                node_type="FACTORY",
                email="test@test.com",
                country="Россия",
                city="Москва",
                street="Ленина",
                house_number="1",
            )

    def test_invalid_email_raises_error(self) -> None:
        """Тест: невалидный email вызывает ошибку."""
        with pytest.raises(ValidationError):
            NetworkNodeCreateSchema(
                name="Тест",
                node_type="FACTORY",
                email="not-an-email",
                country="Россия",
                city="Москва",
                street="Ленина",
                house_number="1",
            )

    def test_negative_debt_raises_error(self) -> None:
        """Тест: отрицательная задолженность вызывает ошибку."""
        with pytest.raises(ValidationError):
            NetworkNodeCreateSchema(
                name="Тест",
                node_type="FACTORY",
                email="test@test.com",
                country="Россия",
                city="Москва",
                street="Ленина",
                house_number="1",
                debt=Decimal("-100"),
            )

    def test_default_debt_is_zero(self) -> None:
        """Тест: задолженность по умолчанию = 0."""
        schema = NetworkNodeCreateSchema(
            name="Тест",
            node_type="FACTORY",
            email="test@test.com",
            country="Россия",
            city="Москва",
            street="Ленина",
            house_number="1",
        )
        assert schema.debt == Decimal("0.00")


class TestProductCreateSchema:
    """Тесты схемы ProductCreateSchema."""

    def test_valid_product_data(self) -> None:
        """Тест валидных данных продукта."""
        schema = ProductCreateSchema(
            name="Смартфон",
            model="SM-100",
            release_date="2024-01-15",
            network_node_id=1,
        )
        assert schema.name == "Смартфон"

    def test_short_name_raises_error(self) -> None:
        """Тест: слишком короткое имя продукта."""
        with pytest.raises(ValidationError):
            ProductCreateSchema(
                name="A",
                model="SM",
                release_date="2024-01-15",
                network_node_id=1,
            )
