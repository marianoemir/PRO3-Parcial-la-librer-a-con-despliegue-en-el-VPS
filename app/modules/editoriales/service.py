"""Lógica del módulo editoriales (CH-04).

El service recibe la sesión como parámetro y traduce los errores de la
base a HTTP propios (RN-12): la unicidad ``uq_editorial_nombre`` la
garantiza la base y se traduce por ``sqlstate`` + ``constraint_name``,
sin consultar existencia antes de escribir (RT-02, DD-04) y sin
exponer texto interno. Todos los handlers que lo llaman son ``async def``.
"""

from __future__ import annotations

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.modules.editoriales.models import Editorial
from app.modules.editoriales.schemas import (
    EditorialCreate,
    EditorialRead,
    EditorialUpdate,
    LibroDeEditorialRead,
)
from app.modules.libros.models import Libro


def _traducir_integrity_error(exc: IntegrityError) -> None:
    """Traduce IntegrityError a 409 propio por sqlstate y constraint_name."""
    orig = getattr(exc, "orig", None)
    cause = getattr(orig, "__cause__", None) if orig is not None else None
    sqlstate = getattr(orig, "sqlstate", None)
    if sqlstate is None and cause is not None:
        sqlstate = getattr(cause, "sqlstate", None)
    if sqlstate is None and orig is not None:
        sqlstate = getattr(orig, "pgcode", None)
    constraint_name = None
    if cause is not None:
        constraint_name = getattr(cause, "constraint_name", None)
    if constraint_name is None and orig is not None:
        constraint_name = getattr(orig, "constraint_name", None)

    if sqlstate == "23505" and constraint_name == "uq_editorial_nombre":
        detail = "Ya existe una editorial con ese nombre"
    else:
        detail = "Conflicto de datos en la base de datos"
    raise HTTPException(status_code=409, detail=detail)


async def crear_editorial(
    session: AsyncSession, datos: EditorialCreate
) -> EditorialRead:
    """Alta de editorial delegando la unicidad a la base (RT-02, DD-04)."""
    editorial = Editorial(nombre=datos.nombre, pais=datos.pais)
    try:
        session.add(editorial)
        await session.flush()
        await session.commit()
    except IntegrityError as exc:
        await session.rollback()
        _traducir_integrity_error(exc)
    return EditorialRead.model_validate(editorial, from_attributes=True)


async def listar_editoriales(
    session: AsyncSession, limit: int, offset: int
) -> list[EditorialRead]:
    """Listado paginado (RN-10) con orden determinista por ``id``."""
    stmt = (
        select(Editorial).order_by(Editorial.id).limit(limit).offset(offset)
    )
    result = await session.execute(stmt)
    editoriales = result.scalars().all()
    return [
        EditorialRead.model_validate(editorial, from_attributes=True)
        for editorial in editoriales
    ]


async def _obtener_editorial_o_404(
    session: AsyncSession, editorial_id: int
) -> Editorial:
    """Lee la editorial y responde 404 propio si no existe (lectura, no escritura)."""
    editorial = await session.get(Editorial, editorial_id)
    if editorial is None:
        raise HTTPException(status_code=404, detail="Editorial no encontrada")
    return editorial


async def obtener_editorial(
    session: AsyncSession, editorial_id: int
) -> EditorialRead:
    """Detalle de editorial con 404 propio."""
    editorial = await _obtener_editorial_o_404(session, editorial_id)
    return EditorialRead.model_validate(editorial, from_attributes=True)


async def actualizar_editorial(
    session: AsyncSession, editorial_id: int, datos: EditorialUpdate
) -> EditorialRead:
    """PATCH parcial con ``exclude_unset`` y misma traducción del UNIQUE."""
    editorial = await _obtener_editorial_o_404(session, editorial_id)
    cambios = datos.model_dump(exclude_unset=True)
    for clave, valor in cambios.items():
        setattr(editorial, clave, valor)
    try:
        await session.flush()
        await session.commit()
    except IntegrityError as exc:
        await session.rollback()
        _traducir_integrity_error(exc)
    return EditorialRead.model_validate(editorial, from_attributes=True)


async def listar_libros_de_editorial(
    session: AsyncSession, editorial_id: int, limit: int, offset: int
) -> list[LibroDeEditorialRead]:
    """Libros de la editorial, paginados y ordenados por ``id`` (RN-10).

    Primero se valida la existencia del padre (404 propio) para no
    confundir "editorial inexistente" con "editorial sin libros".
    """
    await _obtener_editorial_o_404(session, editorial_id)
    stmt = (
        select(Libro)
        .where(Libro.editorial_id == editorial_id)
        .order_by(Libro.id)
        .limit(limit)
        .offset(offset)
    )
    result = await session.execute(stmt)
    libros = result.scalars().all()
    return [
        LibroDeEditorialRead.model_validate(libro, from_attributes=True)
        for libro in libros
    ]
