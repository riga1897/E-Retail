"""
Фабрики для создания тестовых данных.

Используют factory_boy для генерации объектов
моделей NetworkNode и Product.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import factory
from django.contrib.auth.models import User

from network.models import NetworkNode, Product


class UserFactory(factory.django.DjangoModelFactory):
    """Фабрика для создания тестовых пользователей."""

    class Meta:
        model = User
        skip_postgeneration_save = True

    username = factory.Sequence(lambda n: f"user_{n}")
    email = factory.LazyAttribute(lambda obj: f"{obj.username}@example.com")
    password = factory.PostGenerationMethodCall("set_password", "testpass123")
    is_active = True
    is_staff = True


class FactoryNodeFactory(factory.django.DjangoModelFactory):
    """Фабрика для создания узлов типа 'Завод'."""

    class Meta:
        model = NetworkNode

    name = factory.Sequence(lambda n: f"Завод #{n}")
    node_type = NetworkNode.NodeType.FACTORY
    email = factory.Sequence(lambda n: f"factory{n}@test.com")
    country = "Россия"
    city = "Москва"
    street = "Промышленная"
    house_number = "1"
    supplier = None
    debt = Decimal("0.00")


class RetailNetworkFactory(factory.django.DjangoModelFactory):
    """Фабрика для создания узлов типа 'Розничная сеть'."""

    class Meta:
        model = NetworkNode

    name = factory.Sequence(lambda n: f"Розничная сеть #{n}")
    node_type = NetworkNode.NodeType.RETAIL_NETWORK
    email = factory.Sequence(lambda n: f"retail{n}@test.com")
    country = "Россия"
    city = "Санкт-Петербург"
    street = "Невский"
    house_number = "10"
    supplier = factory.SubFactory(FactoryNodeFactory)
    debt = Decimal("10000.00")


class IndividualEntrepreneurFactory(factory.django.DjangoModelFactory):
    """Фабрика для создания узлов типа 'ИП'."""

    class Meta:
        model = NetworkNode

    name = factory.Sequence(lambda n: f"ИП #{n}")
    node_type = NetworkNode.NodeType.INDIVIDUAL_ENTREPRENEUR
    email = factory.Sequence(lambda n: f"ie{n}@test.com")
    country = "Россия"
    city = "Казань"
    street = "Баумана"
    house_number = "5"
    supplier = factory.SubFactory(FactoryNodeFactory)
    debt = Decimal("5000.00")


class ProductFactory(factory.django.DjangoModelFactory):
    """Фабрика для создания тестовых продуктов."""

    class Meta:
        model = Product

    name = factory.Sequence(lambda n: f"Продукт #{n}")
    model = factory.Sequence(lambda n: f"MODEL-{n}")
    release_date = date(2024, 1, 15)
    network_node = factory.SubFactory(FactoryNodeFactory)
