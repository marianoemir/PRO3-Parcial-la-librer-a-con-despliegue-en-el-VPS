"""DTOs del módulo géneros (CH-04, Ejercicio 3).

Contratos Create/Read separados de la tabla ``genero``. No hay DTO de
actualización porque la tabla de referencia no declara la corrección
parcial de géneros (decisión registrada en ``design.md``).
"""

from __future__ import annotations

from decimal import Decimal

from pydantic import ConfigDict
from sqlmodel import SQLModel


class GeneroCreate(SQLModel):
    """Cuerpo del alta: ``nombre`` obligatorio, sin ``id``."""

    nombre: str


class GeneroRead(SQLModel):
    """Salida del alta, del detalle y del listado."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str


class LibroDeGeneroRead(SQLModel):
    """Libro listado desde ``GET /generos/{id}/libros``.

    Omite ``genero_id`` porque es el de la ruta y expone ``editorial_id``
    para identificar la editorial del libro sin anidar su resumen.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    isbn: str
    titulo: str
    precio: Decimal
    stock: int
    editorial_id: int
