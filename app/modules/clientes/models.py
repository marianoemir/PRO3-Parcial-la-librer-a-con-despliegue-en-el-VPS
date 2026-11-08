"""Modelos de tabla Cliente y PerfilCliente (CH-02, Ejercicio 2).

``cliente`` (``id``, ``nombre``, ``email``) con ``email`` UNIQUE
delegada a la base (``uq_cliente_email``). ``perfil_cliente``
(``id``, ``cliente_id``, ``telefono``, ``direccion``) con
``cliente_id`` FK + UNIQUE ``uq_perfil_cliente_cliente_id``
(uno a uno, RN-09) y navegación ``Cliente.perfil`` como objeto
único (no lista).
"""

from typing import TYPE_CHECKING, Optional

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.modules.ventas.models import Venta


class Cliente(SQLModel, table=True):
    __tablename__ = "cliente"
    __table_args__ = (UniqueConstraint("email", name="uq_cliente_email"),)

    id: int | None = Field(default=None, primary_key=True)
    nombre: str
    email: str

    perfil: Optional["PerfilCliente"] = Relationship(back_populates="cliente")
    ventas: list["Venta"] = Relationship(back_populates="cliente")


class PerfilCliente(SQLModel, table=True):
    __tablename__ = "perfil_cliente"
    __table_args__ = (
        UniqueConstraint("cliente_id", name="uq_perfil_cliente_cliente_id"),
    )

    id: int | None = Field(default=None, primary_key=True)
    cliente_id: int = Field(foreign_key="cliente.id")
    telefono: str
    direccion: str

    cliente: Cliente = Relationship(back_populates="perfil")
