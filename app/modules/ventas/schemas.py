"""DTOs del módulo ventas (CH-07)."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Annotated

from pydantic import ConfigDict, computed_field, field_serializer, field_validator, model_validator
from sqlmodel import Field, SQLModel

from app.core.constants import INT4_MAX

_MONEY_Q = Decimal("0.01")


class RenglonCreate(SQLModel):
    model_config = ConfigDict(extra="forbid")

    libro_id: int = Field(ge=1, le=INT4_MAX)
    cantidad: int = Field(ge=1, le=INT4_MAX)


class VentaCreate(SQLModel):
    model_config = ConfigDict(extra="forbid")

    cliente_id: int = Field(ge=1, le=INT4_MAX)
    renglones: Annotated[list[RenglonCreate], Field(min_length=1)]

    @model_validator(mode="after")
    def validar_libros_no_repetidos(self) -> "VentaCreate":
        ids = [r.libro_id for r in self.renglones]
        if len(ids) != len(set(ids)):
            raise ValueError("No se permiten libros repetidos en los renglones")
        return self


class ClienteResumenRead(SQLModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    email: str


class RenglonVentaRead(SQLModel):
    model_config = ConfigDict(from_attributes=True)

    libro_id: int
    titulo: str = ""
    cantidad: int
    precio_unitario: Decimal

    @field_validator("titulo", mode="before")
    @classmethod
    def _titulo_desde_libro(cls, value: object, info):
        if value not in (None, ""):
            return value
        # when validating from ORM or dicts that include libro
        data = getattr(info, "data", {}) or {}
        libro = data.get("libro")
        if libro is not None:
            return getattr(libro, "titulo", "")
        return value or ""

    @field_serializer("precio_unitario")
    def _ser_precio(self, value: Decimal) -> str:
        return format(Decimal(str(value)).quantize(_MONEY_Q), "f")

    @computed_field(return_type=str)
    @property
    def subtotal(self) -> str:
        precio = Decimal(str(self.precio_unitario)).quantize(_MONEY_Q)
        return format((Decimal(self.cantidad) * precio).quantize(_MONEY_Q), "f")


class VentaRead(SQLModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    fecha: datetime
    total: Decimal
    cliente: ClienteResumenRead
    renglones: list[RenglonVentaRead]

    @field_serializer("total")
    def _ser_total(self, value: Decimal) -> str:
        return format(value.quantize(_MONEY_Q), "f")

