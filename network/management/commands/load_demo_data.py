"""
Management-команда для загрузки демо-данных.

Создаёт тестовые данные для демонстрации работы приложения:
заводы, розничные сети, ИП и продукты.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Any

from django.core.management.base import BaseCommand
from django.db import transaction

from network.models import NetworkNode, Product


class Command(BaseCommand):
    """Команда для загрузки демонстрационных данных."""

    help: str = "Загружает демонстрационные данные в базу"

    def handle(self, *args: Any, **options: Any) -> None:
        """
        Создаёт демо-данные: заводы, розничные сети, ИП и продукты.

        Args:
            args: Позиционные аргументы.
            options: Именованные аргументы командной строки.
        """
        if NetworkNode.objects.exists():
            self.stdout.write(
                self.style.WARNING("Данные уже существуют. Пропускаем загрузку.")
            )
            return

        with transaction.atomic():
            self._create_demo_data()

        self.stdout.write(
            self.style.SUCCESS("Демо-данные успешно загружены!")
        )

    def _create_demo_data(self) -> None:
        """Создаёт все демо-данные в транзакции."""
        # Заводы (уровень 0)
        factory_1: NetworkNode = NetworkNode(
            name="ЭлектроТех Завод",
            node_type=NetworkNode.NodeType.FACTORY,
            email="factory1@electrotech.ru",
            country="Россия",
            city="Москва",
            street="Промышленная",
            house_number="15",
            debt=Decimal("0.00"),
        )
        factory_1.save()

        factory_2: NetworkNode = NetworkNode(
            name="ТехноПром",
            node_type=NetworkNode.NodeType.FACTORY,
            email="info@technoprom.ru",
            country="Россия",
            city="Санкт-Петербург",
            street="Заводская",
            house_number="42",
            debt=Decimal("0.00"),
        )
        factory_2.save()

        factory_3: NetworkNode = NetworkNode(
            name="Digital Factory",
            node_type=NetworkNode.NodeType.FACTORY,
            email="contact@digitalfactory.kz",
            country="Казахстан",
            city="Алматы",
            street="Индустриальная",
            house_number="7",
            debt=Decimal("0.00"),
        )
        factory_3.save()

        # Розничные сети (уровень 1 — напрямую от заводов)
        retail_1: NetworkNode = NetworkNode(
            name="ЭлектроМаркет",
            node_type=NetworkNode.NodeType.RETAIL_NETWORK,
            supplier=factory_1,
            email="sales@electromarket.ru",
            country="Россия",
            city="Москва",
            street="Тверская",
            house_number="10",
            debt=Decimal("150000.50"),
        )
        retail_1.save()

        retail_2: NetworkNode = NetworkNode(
            name="ТехноСити",
            node_type=NetworkNode.NodeType.RETAIL_NETWORK,
            supplier=factory_2,
            email="info@technocity.ru",
            country="Россия",
            city="Новосибирск",
            street="Красный проспект",
            house_number="25",
            debt=Decimal("250000.00"),
        )
        retail_2.save()

        retail_3: NetworkNode = NetworkNode(
            name="Цифровой Мир",
            node_type=NetworkNode.NodeType.RETAIL_NETWORK,
            supplier=factory_1,
            email="shop@digitalworld.ru",
            country="Россия",
            city="Екатеринбург",
            street="Ленина",
            house_number="33",
            debt=Decimal("75000.25"),
        )
        retail_3.save()

        # Розничная сеть уровня 2 (от розничной сети)
        retail_4: NetworkNode = NetworkNode(
            name="МегаЭлектро",
            node_type=NetworkNode.NodeType.RETAIL_NETWORK,
            supplier=retail_1,
            email="mega@electromarket.ru",
            country="Россия",
            city="Казань",
            street="Баумана",
            house_number="5",
            debt=Decimal("50000.00"),
        )
        retail_4.save()

        # ИП (разные уровни)
        ie_1: NetworkNode = NetworkNode(
            name="ИП Иванов А.С.",
            node_type=NetworkNode.NodeType.INDIVIDUAL_ENTREPRENEUR,
            supplier=factory_3,
            email="ivanov@mail.ru",
            country="Казахстан",
            city="Нур-Султан",
            street="Кабанбай батыра",
            house_number="12",
            debt=Decimal("30000.00"),
        )
        ie_1.save()

        ie_2: NetworkNode = NetworkNode(
            name="ИП Петров Б.В.",
            node_type=NetworkNode.NodeType.INDIVIDUAL_ENTREPRENEUR,
            supplier=retail_2,
            email="petrov@mail.ru",
            country="Россия",
            city="Омск",
            street="Ленина",
            house_number="8",
            debt=Decimal("12500.75"),
        )
        ie_2.save()

        ie_3: NetworkNode = NetworkNode(
            name="ИП Сидорова К.М.",
            node_type=NetworkNode.NodeType.INDIVIDUAL_ENTREPRENEUR,
            supplier=retail_4,
            email="sidorova@mail.ru",
            country="Россия",
            city="Москва",
            street="Арбат",
            house_number="20",
            debt=Decimal("8000.00"),
        )
        ie_3.save()

        # Продукты
        products_data: list[dict[str, Any]] = [
            {"name": "Смартфон Galaxy Pro", "model": "GP-2024", "release_date": date(2024, 3, 15), "network_node": factory_1},
            {"name": "Ноутбук UltraBook", "model": "UB-500", "release_date": date(2024, 1, 10), "network_node": factory_1},
            {"name": "Планшет TabMax", "model": "TM-10", "release_date": date(2023, 11, 20), "network_node": factory_2},
            {"name": "Наушники SoundPro", "model": "SP-300", "release_date": date(2024, 5, 1), "network_node": factory_2},
            {"name": "Умные часы WatchX", "model": "WX-2", "release_date": date(2024, 2, 28), "network_node": factory_3},
            {"name": "Телевизор ViewMax", "model": "VM-55", "release_date": date(2023, 8, 15), "network_node": retail_1},
            {"name": "Колонка BassBox", "model": "BB-100", "release_date": date(2024, 4, 10), "network_node": retail_2},
            {"name": "Фитнес-браслет FitBand", "model": "FB-5", "release_date": date(2024, 6, 1), "network_node": ie_1},
            {"name": "Роутер NetSpeed", "model": "NS-1000", "release_date": date(2023, 9, 25), "network_node": retail_3},
            {"name": "Веб-камера CamHD", "model": "CH-720", "release_date": date(2024, 1, 5), "network_node": ie_2},
        ]

        for p_data in products_data:
            Product.objects.create(**p_data)

        self.stdout.write("  Создано заводов: 3")
        self.stdout.write("  Создано розничных сетей: 4")
        self.stdout.write("  Создано ИП: 3")
        self.stdout.write(f"  Создано продуктов: {len(products_data)}")
