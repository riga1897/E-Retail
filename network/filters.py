"""
Фильтры для API приложения network.

Определяет классы фильтрации для поиска
узлов сети по различным критериям.
"""

from __future__ import annotations

from django_filters import rest_framework as filters

from network.models import NetworkNode


class NetworkNodeFilter(filters.FilterSet):
    """
    Фильтр для модели NetworkNode.

    Позволяет фильтровать узлы сети по стране
    (регистронезависимое совпадение).
    """

    country = filters.CharFilter(
        field_name="country",
        lookup_expr="iexact",
        label="Страна",
    )

    class Meta:
        model = NetworkNode
        fields: list[str] = ["country"]
