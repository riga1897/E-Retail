"""
Тесты моделей приложения network.

Проверяют создание, валидацию, расчёт иерархии
и защиту от циклических зависимостей.
"""

from __future__ import annotations

from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError

from network.models import NetworkNode, Product
from network.tests.factories import (
    FactoryNodeFactory,
    IndividualEntrepreneurFactory,
    ProductFactory,
    RetailNetworkFactory,
)


@pytest.mark.django_db
class TestNetworkNodeModel:
    """Тесты модели NetworkNode."""

    def test_create_factory(self) -> None:
        """Тест создания завода."""
        factory_node = FactoryNodeFactory()
        assert factory_node.node_type == NetworkNode.NodeType.FACTORY  # type: ignore[attr-defined]
        assert factory_node.hierarchy_level == 0  # type: ignore[attr-defined]
        assert factory_node.supplier is None  # type: ignore[attr-defined]

    def test_create_retail_network(self) -> None:
        """Тест создания розничной сети."""
        retail = RetailNetworkFactory()
        assert retail.node_type == NetworkNode.NodeType.RETAIL_NETWORK  # type: ignore[attr-defined]
        assert retail.hierarchy_level == 1  # type: ignore[attr-defined]
        assert retail.supplier is not None  # type: ignore[attr-defined]

    def test_create_individual_entrepreneur(self) -> None:
        """Тест создания ИП."""
        ie = IndividualEntrepreneurFactory()
        assert ie.node_type == NetworkNode.NodeType.INDIVIDUAL_ENTREPRENEUR  # type: ignore[attr-defined]
        assert ie.hierarchy_level == 1  # type: ignore[attr-defined]
        assert ie.supplier is not None  # type: ignore[attr-defined]

    def test_hierarchy_level_calculation(self) -> None:
        """Тест автоматического расчёта уровня иерархии."""
        factory_node = FactoryNodeFactory()
        retail = RetailNetworkFactory(supplier=factory_node)
        ie = IndividualEntrepreneurFactory(supplier=retail)

        assert factory_node.hierarchy_level == 0  # type: ignore[attr-defined]
        assert retail.hierarchy_level == 1  # type: ignore[attr-defined]
        assert ie.hierarchy_level == 2  # type: ignore[attr-defined]

    def test_factory_cannot_have_supplier(self) -> None:
        """Тест: завод не может иметь поставщика."""
        other_factory = FactoryNodeFactory()
        with pytest.raises(ValidationError, match="Завод не может иметь поставщика"):
            FactoryNodeFactory(supplier=other_factory)

    def test_retail_must_have_supplier(self) -> None:
        """Тест: розничная сеть должна иметь поставщика."""
        with pytest.raises(ValidationError, match="должны иметь поставщика"):
            RetailNetworkFactory(supplier=None)

    def test_ie_must_have_supplier(self) -> None:
        """Тест: ИП должен иметь поставщика."""
        with pytest.raises(ValidationError, match="должны иметь поставщика"):
            IndividualEntrepreneurFactory(supplier=None)

    def test_circular_dependency_protection(self) -> None:
        """Тест защиты от циклических зависимостей."""
        factory_node = FactoryNodeFactory()
        retail_1 = RetailNetworkFactory(supplier=factory_node)
        retail_2 = RetailNetworkFactory(supplier=retail_1)

        with pytest.raises(ValidationError, match="циклическая зависимость"):
            retail_1.supplier = retail_2  # type: ignore[assignment]
            retail_1.save()  # type: ignore[attr-defined]

    def test_self_reference_protection(self) -> None:
        """Тест защиты от ссылки на самого себя."""
        factory_node = FactoryNodeFactory()
        retail = RetailNetworkFactory(supplier=factory_node)

        with pytest.raises(ValidationError, match="циклическая зависимость"):
            retail.supplier = retail  # type: ignore[assignment]
            retail.save()  # type: ignore[attr-defined]

    def test_str_representation(self) -> None:
        """Тест строкового представления модели."""
        factory_node = FactoryNodeFactory(name="Тестовый завод")
        assert "Тестовый завод" in str(factory_node)
        assert "Завод" in str(factory_node)

    def test_debt_default_value(self) -> None:
        """Тест значения задолженности по умолчанию."""
        factory_node = FactoryNodeFactory()
        assert factory_node.debt == Decimal("0.00")  # type: ignore[attr-defined]

    def test_debt_with_value(self) -> None:
        """Тест задолженности с указанным значением."""
        retail = RetailNetworkFactory(debt=Decimal("15000.50"))
        assert retail.debt == Decimal("15000.50")  # type: ignore[attr-defined]

    def test_ordering(self) -> None:
        """Тест сортировки по уровню иерархии и названию."""
        factory_node = FactoryNodeFactory(name="ААА Завод")
        RetailNetworkFactory(name="БББ Сеть", supplier=factory_node)

        nodes = list(NetworkNode.objects.all())
        assert nodes[0].hierarchy_level <= nodes[-1].hierarchy_level

    def test_deep_hierarchy(self) -> None:
        """Тест глубокой иерархии (3 уровня)."""
        factory_node = FactoryNodeFactory()
        retail_1 = RetailNetworkFactory(supplier=factory_node)
        retail_2 = RetailNetworkFactory(supplier=retail_1)
        ie = IndividualEntrepreneurFactory(supplier=retail_2)

        assert factory_node.hierarchy_level == 0  # type: ignore[attr-defined]
        assert retail_1.hierarchy_level == 1  # type: ignore[attr-defined]
        assert retail_2.hierarchy_level == 2  # type: ignore[attr-defined]
        assert ie.hierarchy_level == 3  # type: ignore[attr-defined]

    def test_hierarchy_level_circular_visited_protection(self) -> None:
        """Тест: calculate_hierarchy_level корректно обрабатывает циклическую ссылку через visited."""
        from unittest.mock import PropertyMock, patch

        from network.services.hierarchy import calculate_hierarchy_level

        factory_node = FactoryNodeFactory()
        retail = RetailNetworkFactory(supplier=factory_node)

        with patch.object(
            type(factory_node), "supplier", new_callable=PropertyMock
        ) as mock_supplier:
            mock_supplier.return_value = retail
            level = calculate_hierarchy_level(retail)  # type: ignore[arg-type]
            assert level >= 1


@pytest.mark.django_db
class TestProductModel:
    """Тесты модели Product."""

    def test_create_product(self) -> None:
        """Тест создания продукта."""
        product = ProductFactory()
        assert product.pk is not None  # type: ignore[attr-defined]
        assert product.name is not None  # type: ignore[attr-defined]
        assert product.network_node is not None  # type: ignore[attr-defined]

    def test_str_representation(self) -> None:
        """Тест строкового представления продукта."""
        product = ProductFactory(name="Смартфон", model="SM-100")
        assert str(product) == "Смартфон (SM-100)"

    def test_product_belongs_to_node(self) -> None:
        """Тест связи продукта с узлом сети."""
        factory_node = FactoryNodeFactory()
        product = ProductFactory(network_node=factory_node)
        assert product.network_node == factory_node
        assert product in factory_node.products.all()  # type: ignore[attr-defined]

    def test_product_cascade_delete(self) -> None:
        """Тест каскадного удаления продуктов при удалении узла."""
        factory_node = FactoryNodeFactory()
        ProductFactory(network_node=factory_node)
        ProductFactory(network_node=factory_node)

        node_pk = factory_node.pk  # type: ignore[attr-defined]
        assert Product.objects.filter(network_node_id=node_pk).count() == 2
        factory_node.delete()  # type: ignore[attr-defined]
        assert Product.objects.filter(network_node_id=node_pk).count() == 0
