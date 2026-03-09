"""
Тесты сериализаторов приложения network.

Проверяют корректность сериализации/десериализации
и блокировку поля debt.
"""

from __future__ import annotations

import pytest

from network.models import NetworkNode
from network.serializers import (
    NetworkNodeCreateUpdateSerializer,
    NetworkNodeSerializer,
    ProductSerializer,
)
from network.tests.factories import (
    FactoryNodeFactory,
    ProductFactory,
    RetailNetworkFactory,
)


@pytest.mark.django_db
class TestNetworkNodeSerializer:
    """Тесты сериализатора NetworkNodeSerializer."""

    def test_serialization(self) -> None:
        """Тест сериализации узла сети."""
        factory_node = FactoryNodeFactory(name="Тестовый завод")
        serializer = NetworkNodeSerializer(factory_node)
        data = serializer.data

        assert data["name"] == "Тестовый завод"
        assert data["node_type"] == NetworkNode.NodeType.FACTORY
        assert data["hierarchy_level"] == 0
        assert data["supplier"] is None

    def test_debt_is_read_only(self) -> None:
        """Тест: поле debt доступно только для чтения."""
        serializer = NetworkNodeCreateUpdateSerializer()
        assert "debt" in serializer.Meta.read_only_fields

    def test_hierarchy_level_is_read_only(self) -> None:
        """Тест: поле hierarchy_level доступно только для чтения."""
        serializer = NetworkNodeCreateUpdateSerializer()
        assert "hierarchy_level" in serializer.Meta.read_only_fields

    def test_supplier_name_field(self) -> None:
        """Тест отображения имени поставщика."""
        factory_node = FactoryNodeFactory(name="Поставщик")
        retail = RetailNetworkFactory(supplier=factory_node)
        serializer = NetworkNodeSerializer(retail)

        assert serializer.data["supplier_name"] == "Поставщик"

    def test_supplier_name_none_for_factory(self) -> None:
        """Тест: supplier_name = None для завода."""
        factory_node = FactoryNodeFactory()
        serializer = NetworkNodeSerializer(factory_node)

        assert serializer.data["supplier_name"] is None

    def test_products_included(self) -> None:
        """Тест: продукты включены в сериализацию."""
        factory_node = FactoryNodeFactory()
        ProductFactory(network_node=factory_node, name="Тест-продукт")
        serializer = NetworkNodeSerializer(factory_node)

        assert len(serializer.data["products"]) == 1
        assert serializer.data["products"][0]["name"] == "Тест-продукт"


@pytest.mark.django_db
class TestNetworkNodeCreateUpdateSerializer:
    """Тесты сериализатора для создания/обновления."""

    def test_valid_factory_data(self) -> None:
        """Тест валидных данных для создания завода."""
        data = {
            "name": "Новый завод",
            "node_type": NetworkNode.NodeType.FACTORY,
            "email": "new@factory.com",
            "country": "Россия",
            "city": "Москва",
            "street": "Ленина",
            "house_number": "1",
        }
        serializer = NetworkNodeCreateUpdateSerializer(data=data)
        assert serializer.is_valid(), serializer.errors

    def test_valid_retail_data(self) -> None:
        """Тест валидных данных для создания розничной сети."""
        factory_node = FactoryNodeFactory()
        data = {
            "name": "Новая сеть",
            "node_type": NetworkNode.NodeType.RETAIL_NETWORK,
            "email": "new@retail.com",
            "country": "Россия",
            "city": "Москва",
            "street": "Ленина",
            "house_number": "2",
            "supplier": factory_node.pk,  # type: ignore[attr-defined]
        }
        serializer = NetworkNodeCreateUpdateSerializer(data=data)
        assert serializer.is_valid(), serializer.errors

    def test_debt_cannot_be_set_via_serializer(self) -> None:
        """Тест: debt нельзя установить через сериализатор."""
        data = {
            "name": "Завод",
            "node_type": NetworkNode.NodeType.FACTORY,
            "email": "test@test.com",
            "country": "Россия",
            "city": "Москва",
            "street": "Ленина",
            "house_number": "1",
            "debt": "99999.99",
        }
        serializer = NetworkNodeCreateUpdateSerializer(data=data)
        assert serializer.is_valid()
        assert "debt" not in serializer.validated_data


@pytest.mark.django_db
class TestProductSerializer:
    """Тесты сериализатора ProductSerializer."""

    def test_serialization(self) -> None:
        """Тест сериализации продукта."""
        product = ProductFactory(name="Тестовый продукт", model="TP-1")
        serializer = ProductSerializer(product)
        data = serializer.data

        assert data["name"] == "Тестовый продукт"
        assert data["model"] == "TP-1"

    def test_valid_product_data(self) -> None:
        """Тест валидных данных для создания продукта."""
        factory_node = FactoryNodeFactory()
        data = {
            "name": "Новый продукт",
            "model": "NP-100",
            "release_date": "2024-01-15",
            "network_node": factory_node.pk,  # type: ignore[attr-defined]
        }
        serializer = ProductSerializer(data=data)
        assert serializer.is_valid(), serializer.errors
