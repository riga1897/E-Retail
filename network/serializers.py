"""
Сериализаторы для API приложения network.

Содержит сериализаторы для моделей NetworkNode и Product.
Поле debt (задолженность) доступно только для чтения через API.
"""

from __future__ import annotations

from rest_framework import serializers

from network.models import NetworkNode, Product


class ProductSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Product.

    Обеспечивает сериализацию/десериализацию данных продукта.
    """

    class Meta:  # pyright: ignore[reportIncompatibleVariableOverride]
        model = Product
        fields = [
            "id",
            "name",
            "model",
            "release_date",
            "network_node",
        ]


class NetworkNodeSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели NetworkNode.

    Поле debt (задолженность перед поставщиком) доступно
    только для чтения — обновление через API запрещено.
    """

    products = ProductSerializer(many=True, read_only=True)
    supplier_name = serializers.SerializerMethodField()

    class Meta:  # pyright: ignore[reportIncompatibleVariableOverride]
        model = NetworkNode
        fields = [
            "id",
            "name",
            "node_type",
            "hierarchy_level",
            "supplier",
            "supplier_name",
            "debt",
            "email",
            "country",
            "city",
            "street",
            "house_number",
            "products",
            "created_at",
        ]
        read_only_fields = [
            "debt",
            "hierarchy_level",
            "created_at",
        ]

    def get_supplier_name(self, obj: NetworkNode) -> str | None:
        """
        Возвращает название поставщика.

        Args:
            obj: Экземпляр NetworkNode.

        Returns:
            Название поставщика или None.
        """
        if obj.supplier:
            return str(obj.supplier.name)
        return None


class NetworkNodeCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания и обновления NetworkNode.

    Запрещает обновление поля debt через API.
    """

    class Meta:  # pyright: ignore[reportIncompatibleVariableOverride]
        model = NetworkNode
        fields = [
            "id",
            "name",
            "node_type",
            "hierarchy_level",
            "supplier",
            "debt",
            "email",
            "country",
            "city",
            "street",
            "house_number",
            "created_at",
        ]
        read_only_fields = [
            "debt",
            "hierarchy_level",
            "created_at",
        ]
