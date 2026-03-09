"""
Интеграционные тесты проекта.

Проверяют полные сценарии работы с API:
создание иерархии, фильтрацию, права доступа.
"""

from __future__ import annotations

from decimal import Decimal

import pytest
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APIClient

from network.models import NetworkNode


@pytest.mark.django_db
class TestFullHierarchyScenario:
    """Интеграционный тест: полный сценарий создания иерархии."""

    def test_create_full_hierarchy_via_api(
        self, authenticated_client: APIClient
    ) -> None:
        """Тест создания полной иерархии через API."""
        # Создание завода
        factory_data = {
            "name": "Интеграционный Завод",
            "node_type": "FACTORY",
            "email": "factory@integration.com",
            "country": "Россия",
            "city": "Москва",
            "street": "Тестовая",
            "house_number": "1",
        }
        response = authenticated_client.post("/api/network-nodes/", factory_data)
        assert response.status_code == status.HTTP_201_CREATED
        factory_id = response.data["id"]
        assert response.data["hierarchy_level"] == 0

        # Создание розничной сети (уровень 1)
        retail_data = {
            "name": "Интеграционная Сеть",
            "node_type": "RETAIL_NETWORK",
            "email": "retail@integration.com",
            "country": "Россия",
            "city": "Санкт-Петербург",
            "street": "Невский",
            "house_number": "10",
            "supplier": factory_id,
        }
        response = authenticated_client.post("/api/network-nodes/", retail_data)
        assert response.status_code == status.HTTP_201_CREATED
        retail_id = response.data["id"]
        assert response.data["hierarchy_level"] == 1

        # Создание ИП (уровень 2)
        ie_data = {
            "name": "Интеграционный ИП",
            "node_type": "INDIVIDUAL_ENTREPRENEUR",
            "email": "ie@integration.com",
            "country": "Россия",
            "city": "Казань",
            "street": "Баумана",
            "house_number": "5",
            "supplier": retail_id,
        }
        response = authenticated_client.post("/api/network-nodes/", ie_data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["hierarchy_level"] == 2

        # Проверка списка
        response = authenticated_client.get("/api/network-nodes/")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 3


@pytest.mark.django_db
class TestFilteringScenario:
    """Интеграционный тест: фильтрация по стране."""

    def test_filter_nodes_by_country(
        self, authenticated_client: APIClient
    ) -> None:
        """Тест фильтрации узлов по стране через API."""
        # Создание узлов в разных странах
        countries = [
            ("Завод РФ", "Россия", "zavodrf"),
            ("Завод КЗ", "Казахстан", "zavodkz"),
            ("Завод БР", "Беларусь", "zavodbr"),
        ]
        for name, country, email_prefix in countries:
            data = {
                "name": name,
                "node_type": "FACTORY",
                "email": f"{email_prefix}@test.com",
                "country": country,
                "city": "Город",
                "street": "Улица",
                "house_number": "1",
            }
            response = authenticated_client.post("/api/network-nodes/", data)
            assert response.status_code == status.HTTP_201_CREATED, response.data

        # Фильтрация по России
        response = authenticated_client.get("/api/network-nodes/?country=Россия")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["country"] == "Россия"

        # Фильтрация по Казахстану
        response = authenticated_client.get("/api/network-nodes/?country=Казахстан")
        assert len(response.data) == 1


@pytest.mark.django_db
class TestAccessControlScenario:
    """Интеграционный тест: контроль доступа."""

    def test_inactive_user_cannot_access_api(
        self, api_client: APIClient, inactive_user: User
    ) -> None:
        """Тест: неактивный пользователь не имеет доступа к API."""
        api_client.force_authenticate(user=inactive_user)
        response = api_client.get("/api/network-nodes/")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_anonymous_user_cannot_access_api(
        self, api_client: APIClient
    ) -> None:
        """Тест: анонимный пользователь не имеет доступа к API."""
        response = api_client.get("/api/network-nodes/")
        assert response.status_code in (
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_403_FORBIDDEN,
        )

    def test_active_user_can_crud(
        self, authenticated_client: APIClient
    ) -> None:
        """Тест: активный пользователь может выполнять CRUD операции."""
        # Create
        data = {
            "name": "Тестовый завод",
            "node_type": "FACTORY",
            "email": "crud@test.com",
            "country": "Россия",
            "city": "Москва",
            "street": "Ленина",
            "house_number": "1",
        }
        response = authenticated_client.post("/api/network-nodes/", data)
        assert response.status_code == status.HTTP_201_CREATED
        node_id = response.data["id"]

        # Read
        response = authenticated_client.get(f"/api/network-nodes/{node_id}/")
        assert response.status_code == status.HTTP_200_OK

        # Update
        response = authenticated_client.patch(
            f"/api/network-nodes/{node_id}/",
            {"name": "Обновлённый завод"},
        )
        assert response.status_code == status.HTTP_200_OK

        # Delete
        response = authenticated_client.delete(f"/api/network-nodes/{node_id}/")
        assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.django_db
class TestDebtProtectionScenario:
    """Интеграционный тест: защита поля задолженности."""

    def test_debt_cannot_be_changed_via_api(
        self, authenticated_client: APIClient
    ) -> None:
        """Тест: задолженность не меняется через API."""
        # Создание завода
        data = {
            "name": "Завод",
            "node_type": "FACTORY",
            "email": "debt@test.com",
            "country": "Россия",
            "city": "Москва",
            "street": "Ленина",
            "house_number": "1",
        }
        response = authenticated_client.post("/api/network-nodes/", data)
        node_id = response.data["id"]

        # Попытка изменить debt
        response = authenticated_client.patch(
            f"/api/network-nodes/{node_id}/",
            {"debt": "99999.99"},
        )
        assert response.status_code == status.HTTP_200_OK

        # Проверяем, что debt не изменилась
        node = NetworkNode.objects.get(pk=node_id)
        assert node.debt == Decimal("0.00")


@pytest.mark.django_db
class TestProductScenario:
    """Интеграционный тест: работа с продуктами."""

    def test_create_and_list_products(
        self, authenticated_client: APIClient
    ) -> None:
        """Тест создания и получения списка продуктов."""
        # Создание завода
        factory_data = {
            "name": "Завод продуктов",
            "node_type": "FACTORY",
            "email": "products@test.com",
            "country": "Россия",
            "city": "Москва",
            "street": "Ленина",
            "house_number": "1",
        }
        response = authenticated_client.post("/api/network-nodes/", factory_data)
        factory_id = response.data["id"]

        # Создание продукта
        product_data = {
            "name": "Тестовый смартфон",
            "model": "TS-100",
            "release_date": "2024-06-01",
            "network_node": factory_id,
        }
        response = authenticated_client.post("/api/products/", product_data)
        assert response.status_code == status.HTTP_201_CREATED

        # Проверка списка продуктов
        response = authenticated_client.get("/api/products/")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["name"] == "Тестовый смартфон"
