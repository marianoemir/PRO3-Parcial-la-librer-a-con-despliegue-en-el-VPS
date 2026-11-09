"""DTOs del módulo editoriales (CH-04, Ejercicio 3).

Contratos Create/Update/Read separados de la tabla ``editorial``: el
alta no lleva ``id``, el PATCH aplica solo los campos enviados y las
salidas declaran ``from_attributes`` para serializar la fila sin
acoplarse a los DTO de otros módulos.
"""

from __future__ import annotations

from decimal import Decimal

from pydantic import ConfigDict, field_validator
from sqlmodel import SQLModel


class EditorialCreate(SQLModel):
    """Cuerpo del alta: ``nombre`` y ``pais`` obligatorios, sin ``id``."""

    nombre: str
    pais: str


class EditorialUpdate(SQLModel):
    """Cuerpo del PATCH parcial; rechaza el ``null`` explícito (422)."""

    nombre: str | None = None
    pais: str | None = None

    @field_validator("nombre", "pais", mode="before")
    @classmethod
    def _rechazar_none_explicito(cls, value: object) -> object:
        if value is None:
            raise ValueError("el campo no admite null explícito")
        return value


class EditorialRead(SQLModel):
    """Salida del alta, del detalle, del PATCH y del listado."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    pais: str


class LibroDeEditorialRead(SQLModel):
    """Libro listado desde ``GET /editoriales/{id}/libros``.

    Omite ``editorial_id`` porque es el de la ruta y expone ``genero_id``
    para identificar el género del libro sin anidar su resumen.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    isbn: str
    titulo: str
    precio: Decimal
    stock: int
    genero_id: int | None
