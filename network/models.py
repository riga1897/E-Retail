"""
Модели данных для приложения network.

Содержит модели:
- TimestampedModel: абстрактная модель с полем времени создания.
- ContactInfoModel: абстрактная модель с контактными данными.
- NetworkNode: узел сети по продаже электроники.
- Product: продукт, связанный с узлом сети.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from django.core.validators import MinValueValidator
from django.db import models

from network.services.hierarchy import calculate_hierarchy_level
from network.services.validation import (
    validate_factory_has_no_supplier,
    validate_no_circular_dependency,
    validate_non_factory_has_supplier,
)


class TimestampedModel(models.Model):
    """
    Абстрактная модель с автоматическим полем времени создания.

    Используется как базовый класс для моделей,
    требующих отслеживания даты создания.
    """

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Время создания",
    )

    class Meta:
        abstract = True


class ContactInfoModel(models.Model):
    """
    Абстрактная модель с контактными данными.

    Содержит поля для хранения адреса и email.
    """

    email = models.EmailField(
        verbose_name="Email",
    )
    country = models.CharField(
        max_length=100,
        verbose_name="Страна",
    )
    city = models.CharField(
        max_length=100,
        verbose_name="Город",
    )
    street = models.CharField(
        max_length=200,
        verbose_name="Улица",
    )
    house_number = models.CharField(
        max_length=20,
        verbose_name="Номер дома",
    )

    class Meta:
        abstract = True


class NetworkNode(TimestampedModel, ContactInfoModel):
    """
    Модель узла сети по продаже электроники.

    Представляет звено иерархической структуры сети.
    Типы узлов: завод, розничная сеть, индивидуальный предприниматель.
    """

    class NodeType(models.TextChoices):
        """Типы узлов сети."""

        FACTORY = "FACTORY", "Завод"
        RETAIL_NETWORK = "RETAIL_NETWORK", "Розничная сеть"
        INDIVIDUAL_ENTREPRENEUR = "INDIVIDUAL_ENTREPRENEUR", "Индивидуальный предприниматель"

    name = models.CharField(
        max_length=255,
        verbose_name="Название",
    )
    node_type = models.CharField(
        max_length=30,
        choices=NodeType.choices,
        verbose_name="Тип узла",
    )
    hierarchy_level = models.IntegerField(
        default=0,
        editable=False,
        verbose_name="Уровень иерархии",
    )
    supplier = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="clients",
        verbose_name="Поставщик",
    )
    debt = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
        verbose_name="Задолженность перед поставщиком",
    )

    class Meta(TimestampedModel.Meta, ContactInfoModel.Meta):
        verbose_name = "Звено сети"
        verbose_name_plural = "Звенья сети"
        ordering = ["hierarchy_level", "name"]

    def __str__(self) -> str:
        """Строковое представление узла сети."""
        return f"{self.get_node_type_display()} - {self.name}"  # type: ignore[attr-defined]

    def clean(self) -> None:
        """Валидация модели перед сохранением."""
        super().clean()
        validate_factory_has_no_supplier(self)
        validate_non_factory_has_supplier(self)
        validate_no_circular_dependency(self)

    def save(self, *args: Any, **kwargs: Any) -> None:
        """
        Сохранение узла с автоматическим расчётом уровня иерархии.

        Перед сохранением выполняется валидация и расчёт hierarchy_level.
        """
        self.full_clean()
        self.hierarchy_level = calculate_hierarchy_level(self)
        super().save(*args, **kwargs)


class Product(models.Model):
    """
    Модель продукта, связанного с узлом сети.

    Каждый продукт принадлежит определённому звену сети.
    """

    name = models.CharField(
        max_length=255,
        verbose_name="Название",
    )
    model = models.CharField(
        max_length=100,
        verbose_name="Модель",
    )
    release_date = models.DateField(
        verbose_name="Дата выхода на рынок",
    )
    network_node = models.ForeignKey(
        NetworkNode,
        on_delete=models.CASCADE,
        related_name="products",
        verbose_name="Звено сети",
    )

    class Meta:
        verbose_name = "Продукт"
        verbose_name_plural = "Продукты"
        ordering = ["name"]

    def __str__(self) -> str:
        """Строковое представление продукта."""
        return f"{self.name} ({self.model})"
