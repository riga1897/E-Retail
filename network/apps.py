"""Конфигурация приложения network."""

from django.apps import AppConfig


class NetworkConfig(AppConfig):
    """Класс конфигурации приложения network."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "network"
    verbose_name = "Сеть по продаже электроники"
