"""
Представления (views) API для приложения network.

Содержит ViewSet для CRUD операций с узлами сети
и API Root для корневого эндпоинта.
"""

from __future__ import annotations

from typing import Any

from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect
from rest_framework import serializers, status, viewsets
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.serializers import BaseSerializer
from rest_framework.views import APIView

from network.filters import NetworkNodeFilter
from network.models import NetworkNode, Product
from network.permissions import IsActiveEmployee
from network.serializers import (
    NetworkNodeCreateUpdateSerializer,
    NetworkNodeSerializer,
    ProductSerializer,
)


class TokenSerializer(serializers.Serializer):
    """Сериализатор для получения токена авторизации."""

    username = serializers.CharField(label="Имя пользователя")
    password = serializers.CharField(
        label="Пароль", style={"input_type": "password"}
    )


class ApiRootTokenSerializer(serializers.Serializer):
    """Сериализатор для проверки токена через API Root."""

    token = serializers.CharField(
        label="Токен авторизации",
        help_text="Вставьте только значение токена, без кавычек и скобок. Например: a1b2c3***...***x8y9z0",
    )



class ApiRootView(APIView):
    """
    Корневой эндпоинт API.

    GET: отображает список доступных API-ресурсов.
    POST: принимает токен для авторизации и показывает ресурсы.
    """

    permission_classes = [AllowAny]
    serializer_class = ApiRootTokenSerializer

    def get_serializer(self, *args: Any, **kwargs: Any) -> ApiRootTokenSerializer:
        """Возвращает сериализатор для отображения формы в Browsable API."""
        return ApiRootTokenSerializer(*args, **kwargs)

    def get(self, request: Request, format: str | None = None) -> Response:  # noqa: A002
        """Отображает список доступных API-ресурсов."""
        data_response: dict[str, Any] = {
            "auth": {
                "obtain_token": reverse(
                    "api-token", request=request, format=format
                ),
            },
        }

        if request.user and request.user.is_authenticated:
            data_response["network-nodes"] = reverse(
                "networknode-list", request=request, format=format
            )
            data_response["products"] = reverse(
                "product-list", request=request, format=format
            )
        else:
            data_response["подсказка"] = (
                "Для доступа к API получите токен по ссылке obtain_token выше, отправив POST с username и password."
            )

        return Response(data_response)

    def post(self, request: Request, format: str | None = None) -> Response | HttpResponseRedirect:  # noqa: A002
        """Принимает токен для авторизации и устанавливает сессию."""
        from rest_framework.authtoken.models import Token

        serializer = ApiRootTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        token_key = serializer.validated_data["token"]

        try:
            token_obj = Token.objects.select_related("user").get(key=token_key)
        except Token.DoesNotExist:
            return Response(
                {"error": "Недействительный токен."},
                status=401,
            )

        user = token_obj.user
        if not user.is_active:
            return Response(
                {"error": "Пользователь неактивен."},
                status=403,
            )

        login(request._request, user)

        if request.accepted_renderer.format == "api":
            return HttpResponseRedirect(reverse("api-root", request=request, format=format))

        data: dict[str, Any] = {
            "message": f"Авторизация успешна. Пользователь: {user.username}",
            "auth": {
                "obtain_token": reverse(
                    "api-token", request=request, format=format
                ),
            },
            "network-nodes": reverse(
                "networknode-list", request=request, format=format
            ),
            "products": reverse(
                "product-list", request=request, format=format
            ),
        }
        return Response(data)


api_root_view = ApiRootView.as_view()


class ObtainTokenView(APIView):
    """
    Эндпоинт для получения токена авторизации.

    GET: возвращает инструкцию по использованию.
    POST: принимает username и password, возвращает токен.
    """

    permission_classes = [AllowAny]
    serializer_class = TokenSerializer

    def get_serializer(self, *args: Any, **kwargs: Any) -> TokenSerializer:
        """Возвращает сериализатор для отображения формы в Browsable API."""
        return TokenSerializer(*args, **kwargs)

    def get(self, request: Request) -> Response:
        """Возвращает инструкцию по получению токена."""
        return Response(
            {
                "описание": "Отправьте POST-запрос с username и password для получения токена.",
                "параметры": {
                    "username": "Имя пользователя",
                    "password": "Пароль",
                },
                "пример_ответа": {
                    "token": "your-auth-token-here",
                },
                "использование": 'Authorization: Token <ваш_токен>',
            }
        )

    def post(self, request: Request) -> Response:
        """Аутентификация по username/password, возвращает токен."""
        from rest_framework.authtoken.models import Token

        serializer = TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data["username"]
        password = serializer.validated_data["password"]

        user = authenticate(username=username, password=password)
        if user is None:
            return Response(
                {"non_field_errors": ["Невозможно войти с указанными учётными данными."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        token, _created = Token.objects.get_or_create(user=user)
        return Response({"token": token.key})


obtain_token_view = ObtainTokenView.as_view()


class NetworkNodeViewSet(viewsets.ModelViewSet):
    """
    ViewSet для CRUD операций с узлами сети.

    Обеспечивает полный набор операций:
    создание, чтение, обновление, удаление.
    Поле debt (задолженность) защищено от изменения через API.
    Доступ разрешён только активным сотрудникам.
    """

    queryset = NetworkNode.objects.select_related("supplier").prefetch_related(
        "products"
    )
    permission_classes = [IsActiveEmployee]
    filterset_class = NetworkNodeFilter

    def get_serializer_class(self) -> type[BaseSerializer[Any]]:
        """
        Возвращает класс сериализатора в зависимости от действия.

        Для создания и обновления используется
        NetworkNodeCreateUpdateSerializer,
        для остальных — NetworkNodeSerializer.

        Returns:
            Класс сериализатора.
        """
        if self.action in ("create", "update", "partial_update"):
            return NetworkNodeCreateUpdateSerializer
        return NetworkNodeSerializer


class ProductViewSet(viewsets.ModelViewSet):
    """
    ViewSet для CRUD операций с продуктами.

    Обеспечивает полный набор операций с продуктами.
    Доступ разрешён только активным сотрудникам.
    """

    queryset = Product.objects.select_related("network_node")
    serializer_class = ProductSerializer
    permission_classes = [IsActiveEmployee]
