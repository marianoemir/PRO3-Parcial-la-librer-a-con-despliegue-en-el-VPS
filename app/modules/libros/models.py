"""Modelos de tabla Libro y LibroAutor (CH-02, Ejercicio 2).

``libro`` (``id``, ``isbn``, ``titulo``, ``precio``, ``stock``,
``editorial_id``, ``genero_id``) con ``isbn`` UNIQUE ``uq_libro_isbn``
(RN-01), ``precio`` NUMERIC(10,2) con CHECK ``precio > 0``
(``ck_libro_precio_positivo``) y ``stock`` con CHECK ``stock >= 0``
(``ck_libro_stock_no_negativo``); ``editorial_id`` obligatoria y
``genero_id`` nula, ambas con índice. ``libro_autor`` como entidad
con clase propia y PK compuesta (``libro_id``, ``autor_id``) sin
``link_model`` (DD-01), con CHECK ``orden >= 1``
(``ck_libro_autor_orden_minimo``) y ``rol`` en el conjunto cerrado
(``ck_libro_autor_rol_valido``); ``autor_id`` con índice propio y
``libro_id`` cubierto por el prefijo izquierdo de la PK.
"""

from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from sqlalchemy import CheckConstraint, Numeric, UniqueConstraint
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.modules.autores.models import Autor
    from app.modules.editoriales.models import Editorial
    from app.modules.generos.models import Genero
    from app.modules.ventas.models import RenglonVenta


class Libro(SQLModel, table=True):
    __tablename__ = "libro"
    __table_args__ = (
        UniqueConstraint("isbn", name="uq_libro_isbn"),
        CheckConstraint("precio > 0", name="ck_libro_precio_positivo"),
        CheckConstraint("stock >= 0", name="ck_libro_stock_no_negativo"),
    )

    id: int | None = Field(default=None, primary_key=True)
    isbn: str
    titulo: str
    precio: Decimal = Field(sa_type=Numeric(10, 2))
    stock: int
    editorial_id: int = Field(foreign_key="editorial.id", index=True)
    genero_id: int | None = Field(
        default=None, foreign_key="genero.id", index=True
    )

    editorial: "Editorial" = Relationship(back_populates="libros")
    genero: Optional["Genero"] = Relationship(back_populates="libros")
    autorias: list["LibroAutor"] = Relationship(back_populates="libro")
    renglones: list["RenglonVenta"] = Relationship(back_populates="libro")


class LibroAutor(SQLModel, table=True):
    __tablename__ = "libro_autor"
    __table_args__ = (
        CheckConstraint("orden >= 1", name="ck_libro_autor_orden_minimo"),
        CheckConstraint(
            "rol IN ('autor', 'coautor', 'traductor', 'ilustrador')",
            name="ck_libro_autor_rol_valido",
        ),
    )

    libro_id: int = Field(foreign_key="libro.id", primary_key=True)
    autor_id: int = Field(foreign_key="autor.id", primary_key=True, index=True)
    rol: str
    orden: int

    libro: Libro = Relationship(back_populates="autorias")
    autor: "Autor" = Relationship(back_populates="autorias")
