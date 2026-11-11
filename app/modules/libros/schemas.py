"""DTOs del módulo libros (CH-05, Ejercicio 3).

Contratos Create/Update/Read separados de la tabla (skill sqlmodel:
no mezclar campos de petición/respuesta en el modelo de tabla).
Los resúmenes de editorial/género/autor viven acá sin importar
DTOs de otros módulos (CH-04 aún no construye sus schemas).
"""

from __future__ import annotations

from decimal import Decimal
from typing import Literal

from pydantic import AliasChoices, ConfigDict, field_validator
from sqlmodel import Field, SQLModel

from app.core.constants import INT4_MAX


class EditorialResumen(SQLModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    pais: str


class GeneroResumen(SQLModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str


class AutorResumen(SQLModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str


class LibroAutorCreate(SQLModel):
    autor_id: int = Field(ge=1, le=INT4_MAX)
    rol: Literal["autor", "coautor", "traductor", "ilustrador"]
    orden: int = Field(ge=1, le=INT4_MAX)


class LibroCreate(SQLModel):
    isbn: str
    titulo: str
    precio: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    stock: int = Field(ge=0, le=INT4_MAX)
    editorial_id: int = Field(ge=1, le=INT4_MAX)
    genero_id: int | None = Field(default=None, ge=1, le=INT4_MAX)
    autores: list[LibroAutorCreate]


class LibroUpdate(SQLModel):
    isbn: str | None = None
    titulo: str | None = None
    precio: Decimal | None = Field(default=None, gt=0, max_digits=10, decimal_places=2)
    stock: int | None = Field(default=None, ge=0, le=INT4_MAX)
    editorial_id: int | None = Field(default=None, ge=1, le=INT4_MAX)
    genero_id: int | None = Field(default=None, ge=1, le=INT4_MAX)

    @field_validator("isbn", "titulo", "precio", "stock", "editorial_id", mode="before")
    @classmethod
    def _rechazar_none_explicito(cls, value: object) -> object:
        if value is None:
            raise ValueError("el campo no admite null explícito")
        return value


class LibroAutorRead(SQLModel):
    model_config = ConfigDict(from_attributes=True)

    autor_id: int
    rol: str
    orden: int
    autor: AutorResumen


class LibroRead(SQLModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    isbn: str
    titulo: str
    precio: Decimal
    stock: int
    editorial_id: int
    genero_id: int | None
    editorial: EditorialResumen
    genero: GeneroResumen | None
    autores: list[LibroAutorRead] = Field(
        default_factory=list,
        validation_alias=AliasChoices("autores", "autorias"),
    )


class LibroListRead(SQLModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    isbn: str
    titulo: str
    precio: Decimal
    stock: int
    editorial_id: int
    genero_id: int | None
    editorial: EditorialResumen
    genero: GeneroResumen | None
