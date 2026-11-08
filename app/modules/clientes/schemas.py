"""DTOs de entrada y salida del módulo clientes."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, model_validator


class ClienteCreate(BaseModel):
    """Datos permitidos para dar de alta un cliente."""

    model_config = ConfigDict(extra="forbid")

    nombre: str
    email: str


class ClienteUpdate(BaseModel):
    """Datos permitidos para actualizar parcialmente un cliente."""

    model_config = ConfigDict(extra="forbid")

    nombre: str = None
    email: str = None

    @model_validator(mode="after")
    def require_at_least_one_field(self) -> ClienteUpdate:
        """Evita PATCH vacíos antes de acceder al servicio."""
        if not self.model_fields_set:
            raise ValueError("Debe enviar al menos un campo para actualizar.")
        return self


class PerfilCreate(BaseModel):
    """Datos permitidos para crear el perfil del cliente de la ruta."""

    model_config = ConfigDict(extra="forbid")

    telefono: str
    direccion: str


class PerfilRead(BaseModel):
    """Representación pública de un perfil de cliente."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    cliente_id: int
    telefono: str
    direccion: str


class ClienteRead(BaseModel):
    """Representación pública de un cliente y su perfil singular."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    email: str
    perfil: PerfilRead | None


class VentaResumenRead(BaseModel):
    """Resumen plano de una venta, sin renglones ni relaciones."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    cliente_id: int
    fecha: datetime
    total: Decimal
