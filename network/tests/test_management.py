"""
Тесты management-команд приложения network.

Проверяют команды создания суперпользователя и загрузки демо-данных.
"""

from __future__ import annotations

from io import StringIO

import pytest
from django.contrib.auth.models import User
from django.core.management import call_command

from network.models import NetworkNode, Product


@pytest.mark.django_db
class TestCreateSuperuserCommand:
    """Тесты команды create_superuser."""

    def test_create_superuser(self) -> None:
        """Тест создания суперпользователя."""
        out = StringIO()
        call_command(
            "create_superuser",
            "--username=testadmin",
            "--email=testadmin@test.com",
            "--password=testpass",
            stdout=out,
        )
        assert User.objects.filter(username="testadmin").exists()
        assert "успешно создан" in out.getvalue()

    def test_create_superuser_already_exists(self) -> None:
        """Тест: суперпользователь уже существует."""
        User.objects.create_superuser(
            username="existingadmin",
            email="existing@test.com",
            password="pass",
        )
        out = StringIO()
        call_command(
            "create_superuser",
            "--username=existingadmin",
            stdout=out,
        )
        assert "уже существует" in out.getvalue()

    def test_create_superuser_default_values(self) -> None:
        """Тест создания суперпользователя из переменных окружения."""
        out = StringIO()
        call_command(
            "create_superuser",
            "--username=envadmin",
            "--password=envpass",
            stdout=out,
        )
        assert User.objects.filter(username="envadmin").exists()

    def test_create_superuser_missing_credentials(self) -> None:
        """Тест: ошибка при отсутствии username и password."""
        err = StringIO()
        with pytest.MonkeyPatch.context() as mp:
            mp.delenv("DJANGO_SUPERUSER_USERNAME", raising=False)
            mp.delenv("DJANGO_SUPERUSER_PASSWORD", raising=False)
            call_command("create_superuser", stderr=err)
        assert "Необходимо указать" in err.getvalue()
        assert not User.objects.filter(username="").exists()


@pytest.mark.django_db
class TestLoadDemoDataCommand:
    """Тесты команды load_demo_data."""

    def test_load_demo_data(self) -> None:
        """Тест загрузки демо-данных."""
        out = StringIO()
        call_command("load_demo_data", stdout=out)
        assert NetworkNode.objects.count() > 0
        assert Product.objects.count() > 0
        assert "успешно загружены" in out.getvalue()

    def test_load_demo_data_already_exists(self) -> None:
        """Тест: данные уже существуют."""
        call_command("load_demo_data", stdout=StringIO())
        out = StringIO()
        call_command("load_demo_data", stdout=out)
        assert "уже существуют" in out.getvalue()
