"""
Тесты представлений (views) API приложения network.

Проверяют CRUD операции, фильтрацию и права доступа.
"""

from __future__ import annotations

from decimal import Decimal

import pytest
from rest_framework import status
from rest_framework.test import APIClient

from network.models import NetworkNode
from network.tests.factories import (
    FactoryNodeFactory,
    ProductFactory,
    RetailNetworkFactory,
    UserFactory,
)


@pytest.mark.django_db
class TestNetworkNodeViewSet:
    """Тесты ViewSet для NetworkNode."""

    def setup_method(self) -> None:
        """Инициализация клиента и пользователя."""
        self.client = APIClient()
        self.user = UserFactory(is_active=True)
        self.client.force_authenticate(user=self.user)  # type: ignore[arg-type]

    def test_list_nodes(self) -> None:
        """Тест получения списка узлов сети."""
        FactoryNodeFactory()
        RetailNetworkFactory()

        response = self.client.get("/api/network-nodes/")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 3

    def test_retrieve_node(self) -> None:
        """Тест получения одного узла сети."""
        factory_node = FactoryNodeFactory(name="Тестовый завод")

        response = self.client.get(f"/api/network-nodes/{factory_node.pk}/")  # type: ignore[attr-defined]
        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == "Тестовый завод"

    def test_create_factory_node(self) -> None:
        """Тест создания завода через API."""
        data = {
            "name": "Новый завод",
            "node_type": "FACTORY",
            "email": "new@factory.com",
            "country": "Россия",
            "city": "Москва",
            "street": "Ленина",
            "house_number": "1",
        }
        response = self.client.post("/api/network-nodes/", data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["hierarchy_level"] == 0

    def test_create_retail_node(self) -> None:
        """Тест создания розничной сети через API."""
        factory_node = FactoryNodeFactory()
        data = {
            "name": "Новая сеть",
            "node_type": "RETAIL_NETWORK",
            "email": "new@retail.com",
            "country": "Россия",
            "city": "Москва",
            "street": "Ленина",
            "house_number": "2",
            "supplier": factory_node.pk,  # type: ignore[attr-defined]
        }
        response = self.client.post("/api/network-nodes/", data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["hierarchy_level"] == 1

    def test_update_node(self) -> None:
        """Тест обновления узла сети."""
        factory_node = FactoryNodeFactory()
        data = {
            "name": "Обновлённый завод",
            "node_type": "FACTORY",
            "email": "updated@factory.com",
            "country": "Россия",
            "city": "Москва",
            "street": "Ленина",
            "house_number": "1",
        }
        response = self.client.put(
            f"/api/network-nodes/{factory_node.pk}/", data  # type: ignore[attr-defined]
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == "Обновлённый завод"

    def test_partial_update_node(self) -> None:
        """Тест частичного обновления узла сети."""
        factory_node = FactoryNodeFactory()
        response = self.client.patch(
            f"/api/network-nodes/{factory_node.pk}/",  # type: ignore[attr-defined]
            {"name": "Частично обновлённый"},
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == "Частично обновлённый"

    def test_delete_node(self) -> None:
        """Тест удаления узла сети."""
        factory_node = FactoryNodeFactory()
        response = self.client.delete(f"/api/network-nodes/{factory_node.pk}/")  # type: ignore[attr-defined]
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not NetworkNode.objects.filter(pk=factory_node.pk).exists()  # type: ignore[attr-defined]

    def test_debt_cannot_be_updated_via_api(self) -> None:
        """Тест: задолженность нельзя обновить через API."""
        factory_node = FactoryNodeFactory()
        response = self.client.patch(
            f"/api/network-nodes/{factory_node.pk}/",  # type: ignore[attr-defined]
            {"debt": "99999.99"},
        )
        assert response.status_code == status.HTTP_200_OK
        factory_node.refresh_from_db()  # type: ignore[attr-defined]
        assert factory_node.debt == Decimal("0.00")

    def test_filter_by_country(self) -> None:
        """Тест фильтрации по стране."""
        FactoryNodeFactory(country="Россия")
        FactoryNodeFactory(country="Казахстан")

        response = self.client.get("/api/network-nodes/?country=Россия")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["country"] == "Россия"

    def test_filter_by_country_case_insensitive(self) -> None:
        """Тест регистронезависимой фильтрации по стране."""
        FactoryNodeFactory(country="Россия")

        response = self.client.get("/api/network-nodes/?country=россия")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1

    def test_unauthenticated_access_denied(self) -> None:
        """Тест: неаутентифицированный пользователь не имеет доступа."""
        self.client.logout()
        response = self.client.get("/api/network-nodes/")
        assert response.status_code in (
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_403_FORBIDDEN,
        )

    def test_inactive_user_access_denied(self) -> None:
        """Тест: неактивный пользователь не имеет доступа."""
        inactive_user = UserFactory(is_active=False)
        self.client.force_authenticate(user=inactive_user)  # type: ignore[arg-type]
        response = self.client.get("/api/network-nodes/")
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestProductViewSet:
    """Тесты ViewSet для Product."""

    def setup_method(self) -> None:
        """Инициализация клиента и пользователя."""
        self.client = APIClient()
        self.user = UserFactory(is_active=True)
        self.client.force_authenticate(user=self.user)  # type: ignore[arg-type]

    def test_list_products(self) -> None:
        """Тест получения списка продуктов."""
        ProductFactory()
        response = self.client.get("/api/products/")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1

    def test_create_product(self) -> None:
        """Тест создания продукта через API."""
        factory_node = FactoryNodeFactory()
        data = {
            "name": "Новый продукт",
            "model": "NP-1",
            "release_date": "2024-06-01",
            "network_node": factory_node.pk,  # type: ignore[attr-defined]
        }
        response = self.client.post("/api/products/", data)
        assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
class TestApiRoot:
    """Тесты корневого эндпоинта API."""

    def setup_method(self) -> None:
        """Инициализация клиента и пользователя."""
        self.client = APIClient()
        self.user = UserFactory(is_active=True)
        self.client.force_authenticate(user=self.user)  # type: ignore[arg-type]

    def test_api_root_returns_links_for_authenticated(self) -> None:
        """Тест: API Root возвращает все ссылки для авторизованного пользователя."""
        response = self.client.get("/api/")
        assert response.status_code == status.HTTP_200_OK
        assert "network-nodes" in response.data
        assert "products" in response.data
        assert "auth" in response.data
        assert "obtain_token" in response.data["auth"]

    def test_api_root_hides_resources_for_unauthenticated(self) -> None:
        """Тест: API Root скрывает ресурсы для неавторизованных пользователей."""
        self.client.logout()
        response = self.client.get("/api/")
        assert response.status_code == status.HTTP_200_OK
        assert "auth" in response.data
        assert "network-nodes" not in response.data
        assert "products" not in response.data

    def test_root_redirects_to_api(self) -> None:
        """Тест: корневой URL перенаправляет на /api/."""
        response = self.client.get("/")
        assert response.status_code == status.HTTP_302_FOUND
        assert response.url == "/api/"  # type: ignore[attr-defined]
