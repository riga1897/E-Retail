"""
Настройки Django для проекта electronics_network.

Все чувствительные данные загружаются из переменных окружения.
Поддерживает работу как в Replit, так и на Windows.
"""

from pathlib import Path
from typing import Any

import environ

# Базовая директория проекта
BASE_DIR: Path = Path(__file__).resolve().parent.parent

# Инициализация django-environ
env = environ.Env(
    DEBUG=(bool, False),
    ALLOWED_HOSTS=(list, ["*"]),
    TIME_ZONE=(str, "Europe/Moscow"),
    LANGUAGE_CODE=(str, "ru-ru"),
)

# Чтение .env файла, если он существует
env_file: Path = BASE_DIR / ".env"
if env_file.exists():
    environ.Env.read_env(str(env_file))

# Основные настройки безопасности
SECRET_KEY: str = env("SECRET_KEY")

DEBUG: bool = env.bool("DEBUG", default=True)  # type: ignore[arg-type]

ALLOWED_HOSTS: list[str] = env.list("ALLOWED_HOSTS", default=["*"])  # type: ignore[arg-type]

_csrf_default = ["https://*.replit.dev", "https://*.repl.co"]
CSRF_TRUSTED_ORIGINS: list[str] = env.list("CSRF_TRUSTED_ORIGINS", default=_csrf_default)  # type: ignore[arg-type]

# Установленные приложения
INSTALLED_APPS: list[str] = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Сторонние приложения
    "rest_framework",
    "rest_framework.authtoken",
    "django_filters",
    # Приложения проекта
    "network",
]

MIDDLEWARE: list[str] = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF: str = "electronics_network.urls"

TEMPLATES: list[dict[str, Any]] = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION: str = "electronics_network.wsgi.application"

# Настройка базы данных
# Поддержка DATABASE_URL (Replit) и отдельных переменных (Windows)
DATABASE_URL: str | None = env.str("DATABASE_URL", default=None)  # type: ignore[arg-type, assignment]

if DATABASE_URL:
    import dj_database_url

    DATABASES: dict[str, Any] = {
        "default": dj_database_url.parse(DATABASE_URL),
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": env.str("DB_ENGINE", default="django.db.backends.postgresql"),  # type: ignore[arg-type]
            "NAME": env.str("DB_NAME", default="network_db"),  # type: ignore[arg-type]
            "USER": env.str("DB_USER", default="postgres"),  # type: ignore[arg-type]
            "PASSWORD": env.str("DB_PASSWORD", default=""),  # type: ignore[arg-type]
            "HOST": env.str("DB_HOST", default="localhost"),  # type: ignore[arg-type]
            "PORT": env.str("DB_PORT", default="5432"),  # type: ignore[arg-type]
        }
    }

# Валидация паролей
AUTH_PASSWORD_VALIDATORS: list[dict[str, str]] = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Интернационализация
LANGUAGE_CODE: str = env.str("LANGUAGE_CODE", default="ru-ru")  # type: ignore[arg-type]

TIME_ZONE: str = env.str("TIME_ZONE", default="Europe/Moscow")  # type: ignore[arg-type]

USE_I18N: bool = True

USE_TZ: bool = True

# Статические файлы
STATIC_URL: str = "static/"
STATIC_ROOT: Path = BASE_DIR / "staticfiles"
STATICFILES_STORAGE: str = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Тип первичного ключа по умолчанию
DEFAULT_AUTO_FIELD: str = "django.db.models.BigAutoField"

# Настройки Django REST Framework
REST_FRAMEWORK: dict[str, Any] = {
    "DEFAULT_PERMISSION_CLASSES": [
        "network.permissions.IsActiveEmployee",
    ],
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.TokenAuthentication",
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.BasicAuthentication",
    ],
}
