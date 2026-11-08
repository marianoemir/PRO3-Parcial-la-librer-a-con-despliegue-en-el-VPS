"""Modelo de tabla Editorial (CH-02, Ejercicio 2).

``editorial`` (``id``, ``nombre``, ``pais``) con ``nombre`` UNIQUE
delegada a la base (``uq_editorial_nombre``) y navegación bilateral
``Editorial.libros`` compatible con precarga.
"""

from typing import TYPE_CHECKING

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.modules.libros.models import Libro


class Editorial(SQLModel, table=True):
    __tablename__ = "editorial"
    __table_args__ = (UniqueConstraint("nombre", name="uq_editorial_nombre"),)

    id: int | None = Field(default=None, primary_key=True)
    nombre: str
    pais: str

    libros: list["Libro"] = Relationship(back_populates="editorial")
