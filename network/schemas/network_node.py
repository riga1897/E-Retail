"""
Pydantic схемы для модели NetworkNode.

Обеспечивает строгую валидацию входных данных
при создании и обновлении узлов сети.
"""

from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, EmailStr, Field, field_validator


class NetworkNodeCreateSchema(BaseModel):
    """Схема Pydantic для создания узла сети с валидацией."""

    name: str = Field(..., min_length=2, max_length=255)
    node_type: str
    email: EmailStr
    country: str = Field(..., min_length=2)
    city: str = Field(..., min_length=2)
    street: str = Field(..., min_length=2)
    house_number: str
    supplier_id: int | None = None
    debt: Decimal = Field(default=Decimal("0.00"), ge=Decimal("0"))

    @field_validator("node_type")
    @classmethod
    def validate_node_type(cls, v: str) -> str:
        """Проверяет допустимость типа узла."""
        allowed_types: list[str] = [
            "FACTORY",
            "RETAIL_NETWORK",
            "INDIVIDUAL_ENTREPRENEUR",
        ]
        if v not in allowed_types:
            msg = f"node_type должен быть одним из: {allowed_types}"
            raise ValueError(msg)
        return v

    @field_validator("supplier_id")
    @classmethod
    def validate_supplier_for_factory(
        cls, v: int | None, info: object
    ) -> int | None:
        """Проверяет, что завод не имеет поставщика."""
        data = info.data if hasattr(info, "data") else {}  # type: ignore[union-attr]
        if data.get("node_type") == "FACTORY" and v is not None:
            msg = "Завод не может иметь поставщика"
            raise ValueError(msg)
        return v


class ProductCreateSchema(BaseModel):
    """Схема Pydantic для создания продукта."""

    name: str = Field(..., min_length=2, max_length=255)
    model: str = Field(..., min_length=1, max_length=100)
    release_date: str
    network_node_id: int
