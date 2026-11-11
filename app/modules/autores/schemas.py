"""DTOs del módulo autores (CH-04, Ejercicio 3).

Contratos Create/Update/Read separados de la tabla ``autor``. El alta
no lleva ``id``, el PATCH rechaza el ``null`` explícito y la salida de
``GET /autores/{id}/libros`` expone los datos de la autoría (``rol`` y
``orden``) junto con las columnas del libro.
"""

from __future__ import annotations

from decimal import Decimal

from pydantic import ConfigDict, field_validator
from sqlmodel import SQLModel


class AutorCreate(SQLModel):
    """Cuerpo del alta: ``nombre`` y ``nacionalidad`` obligatorios, sin ``id``."""

    nombre: str
    nacionalidad: str


class AutorUpdate(SQLModel):
    """Cuerpo del PATCH parcial; rechaza el ``null`` explícito (422)."""

    nombre: str | None = None
    nacionalidad: str | None = None

    @field_validator("nombre", "nacionalidad", mode="before")
    @classmethod
    def _rechazar_none_explicito(cls, value: object) -> object:
        if value is None:
            raise ValueError("el campo no admite null explícito")
        return value


class AutorRead(SQLModel):
    """Salida del alta, del detalle y del PATCH."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    nacionalidad: str


class LibroDeAutorRead(SQLModel):
    """Autoría listada desde ``GET /autores/{id}/libros``.

    Se construye explícitamente desde ``LibroAutor`` + su ``libro``
    precargado, por eso no declara ``from_attributes``.
    """

    libro_id: int
    isbn: str
    titulo: str
    precio: Decimal
    stock: int
    rol: str
    orden: int
