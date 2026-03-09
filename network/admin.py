"""
Настройки админ-панели для приложения network.

Кастомизированное отображение узлов сети с:
- ссылкой на поставщика,
- фильтром по городу,
- admin action для очистки задолженности.
"""

from __future__ import annotations

from decimal import Decimal

from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest
from django.utils.html import format_html

from network.models import NetworkNode, Product


class ProductInline(admin.TabularInline):  # type: ignore[type-arg]
    """Инлайн-отображение продуктов в админке узла сети."""

    model = Product
    extra = 1
    fields = ["name", "model", "release_date"]


@admin.register(NetworkNode)
class NetworkNodeAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    """
    Настройки админ-панели для модели NetworkNode.

    Включает:
    - отображение ключевых полей в списке,
    - ссылку на поставщика,
    - фильтр по городу,
    - admin action для обнуления задолженности.
    """

    list_display = [
        "name",
        "node_type",
        "hierarchy_level",
        "link_to_supplier",
        "debt",
        "city",
        "country",
        "created_at",
    ]
    list_filter = ["city", "node_type", "hierarchy_level"]
    search_fields = ["name", "city", "country"]
    list_select_related = ["supplier"]
    readonly_fields = ["hierarchy_level", "created_at"]
    inlines = [ProductInline]
    actions = ["clear_debt"]

    fieldsets = [
        (
            None,
            {
                "fields": (
                    "name",
                    "node_type",
                    "hierarchy_level",
                ),
            },
        ),
        (
            "Поставщик и задолженность",
            {
                "fields": (
                    "supplier",
                    "debt",
                ),
            },
        ),
        (
            "Контактные данные",
            {
                "fields": (
                    "email",
                    "country",
                    "city",
                    "street",
                    "house_number",
                ),
            },
        ),
        (
            "Системные поля",
            {
                "fields": ("created_at",),
                "classes": ("collapse",),
            },
        ),
    ]

    class Media:
        css: dict[str, tuple[str]] = {
            "all": ("admin/css/custom_admin.css",),
        }

    @admin.display(description="Поставщик")
    def link_to_supplier(self, obj: NetworkNode) -> str:
        """
        Формирует HTML-ссылку на страницу поставщика в админке.

        Args:
            obj: Экземпляр NetworkNode.

        Returns:
            HTML-ссылка на поставщика или прочерк.
        """
        if obj.supplier:
            url = f"/admin/network/networknode/{obj.supplier.pk}/change/"
            return format_html(
                '<a href="{}">{}</a>',
                url,
                obj.supplier.name,
            )
        return "-"

    @admin.action(description="Очистить задолженность перед поставщиком")
    def clear_debt(
        self,
        request: HttpRequest,
        queryset: QuerySet[NetworkNode],
    ) -> None:
        """
        Admin action: обнуляет задолженность у выбранных узлов.

        Args:
            request: HTTP-запрос.
            queryset: Набор выбранных узлов сети.
        """
        updated: int = queryset.update(debt=Decimal("0.00"))
        self.message_user(
            request,
            f"Задолженность очищена у {updated} объектов.",
        )


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    """Настройки админ-панели для модели Product."""

    list_display = ["name", "model", "release_date", "network_node"]
    list_filter = ["release_date"]
    search_fields = ["name", "model"]
    list_select_related = ["network_node"]
