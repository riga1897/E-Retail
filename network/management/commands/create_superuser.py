"""
Management-команда для создания суперпользователя.

Создаёт суперпользователя из переменных окружения
или с параметрами по умолчанию.
"""

from __future__ import annotations

import os
from typing import Any

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandParser


class Command(BaseCommand):
    """Команда для создания суперпользователя из переменных окружения."""

    help: str = "Создаёт суперпользователя из переменных окружения"

    def add_arguments(self, parser: CommandParser) -> None:
        """
        Добавляет аргументы командной строки.

        Args:
            parser: Парсер аргументов.
        """
        parser.add_argument(
            "--username",
            type=str,
            default=None,
            help="Имя пользователя (по умолчанию из DJANGO_SUPERUSER_USERNAME)",
        )
        parser.add_argument(
            "--email",
            type=str,
            default=None,
            help="Email (по умолчанию из DJANGO_SUPERUSER_EMAIL)",
        )
        parser.add_argument(
            "--password",
            type=str,
            default=None,
            help="Пароль (по умолчанию из DJANGO_SUPERUSER_PASSWORD)",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        """
        Выполняет создание суперпользователя.

        Args:
            args: Позиционные аргументы.
            options: Именованные аргументы командной строки.
        """
        username: str = options["username"] or os.environ.get(
            "DJANGO_SUPERUSER_USERNAME", ""
        )
        email: str = options["email"] or os.environ.get(
            "DJANGO_SUPERUSER_EMAIL", ""
        )
        password: str = options["password"] or os.environ.get(
            "DJANGO_SUPERUSER_PASSWORD", ""
        )

        if not username or not password:
            self.stderr.write(
                self.style.ERROR(
                    "Необходимо указать DJANGO_SUPERUSER_USERNAME и "
                    "DJANGO_SUPERUSER_PASSWORD в переменных окружения "
                    "или передать --username и --password."
                )
            )
            return

        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.WARNING(
                    f'Суперпользователь "{username}" уже существует.'
                )
            )
            return

        User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
        )
        self.stdout.write(
            self.style.SUCCESS(
                f'Суперпользователь "{username}" успешно создан.'
            )
        )
