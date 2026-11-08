"""Modelo de tabla Autor (CH-02, Ejercicio 2).

``autor`` (``id``, ``nombre``, ``nacionalidad``) sin restricciones
extra (enunciado) y navegación bilateral ``Autor.autorias``.
"""

from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.modules.libros.models import LibroAutor


class Autor(SQLModel, table=True):
    __tablename__ = "autor"

    id: int | None = Field(default=None, primary_key=True)
    nombre: str
    nacionalidad: str

    autorias: list["LibroAutor"] = Relationship(back_populates="autor")
