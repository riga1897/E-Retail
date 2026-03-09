"""
Тесты админ-панели приложения network.

Проверяют кастомные admin actions, фильтры и отображение.
"""

from __future__ import annotations

from decimal import Decimal

import pytest
from django.contrib.admin.sites import AdminSite
from django.test import RequestFactory

from network.admin import NetworkNodeAdmin
from network.models import NetworkNode
from network.tests.factories import (
    FactoryNodeFactory,
    RetailNetworkFactory,
    UserFactory,
)


@pytest.mark.django_db
class TestNetworkNodeAdmin:
    """Тесты настроек админ-панели NetworkNode."""

    def setup_method(self) -> None:
        """Инициализация объектов для тестов."""
        self.site = AdminSite()
        self.admin = NetworkNodeAdmin(NetworkNode, self.site)
        self.factory = RequestFactory()

    def test_clear_debt_action(self) -> None:
        """Тест admin action: очистка задолженности."""
        retail_1 = RetailNetworkFactory(debt=Decimal("10000.00"))
        retail_2 = RetailNetworkFactory(debt=Decimal("20000.00"))

        queryset = NetworkNode.objects.filter(
            pk__in=[retail_1.pk, retail_2.pk]  # type: ignore[attr-defined]
        )

        from django.contrib.messages.storage.fallback import FallbackStorage

        user = UserFactory(is_staff=True, is_active=True)
        request = self.factory.post("/admin/")
        request.user = user  # type: ignore[assignment]
        request.session = "session"  # type: ignore[assignment]
        messages = FallbackStorage(request)
        request._messages = messages  # type: ignore[attr-defined]

        self.admin.clear_debt(request, queryset)

        retail_1.refresh_from_db()  # type: ignore[attr-defined]
        retail_2.refresh_from_db()  # type: ignore[attr-defined]
        assert retail_1.debt == Decimal("0.00")  # type: ignore[attr-defined]
        assert retail_2.debt == Decimal("0.00")  # type: ignore[attr-defined]

    def test_link_to_supplier_with_supplier(self) -> None:
        """Тест ссылки на поставщика (есть поставщик)."""
        factory_node = FactoryNodeFactory(name="Поставщик")
        retail = RetailNetworkFactory(supplier=factory_node)

        link = self.admin.link_to_supplier(retail)  # type: ignore[arg-type]
        assert "Поставщик" in link
        assert f"/admin/network/networknode/{factory_node.pk}/change/" in link  # type: ignore[attr-defined]

    def test_link_to_supplier_without_supplier(self) -> None:
        """Тест ссылки на поставщика (нет поставщика)."""
        factory_node = FactoryNodeFactory()
        link = self.admin.link_to_supplier(factory_node)  # type: ignore[arg-type]
        assert link == "-"

    def test_list_display_fields(self) -> None:
        """Тест наличия полей в list_display."""
        expected_fields = [
            "name",
            "node_type",
            "hierarchy_level",
            "link_to_supplier",
            "debt",
            "city",
        ]
        for field in expected_fields:
            assert field in self.admin.list_display

    def test_list_filter_includes_city(self) -> None:
        """Тест: фильтр по городу включён в list_filter."""
        assert "city" in self.admin.list_filter

    def test_clear_debt_action_registered(self) -> None:
        """Тест: admin action очистки задолженности зарегистрирован."""
        assert "clear_debt" in self.admin.actions
