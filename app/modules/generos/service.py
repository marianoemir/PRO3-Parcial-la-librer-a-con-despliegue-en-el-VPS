"""Lógica del módulo géneros (CH-04).

El service recibe la sesión como parámetro y traduce los errores de la
base a HTTP propios (RN-12): la unicidad ``uq_genero_nombre`` la
garantiza la base y se traduce por ``sqlstate`` + ``constraint_name``,
sin consultar existencia antes de escribir (RT-02, DD-04) y sin
exponer texto interno. No hay corrección de géneros: la tabla de
referencia no declara ``PATCH /generos/{id}``.
"""

from __future__ import annotations

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.modules.generos.models import Genero
from app.modules.generos.schemas import (
    GeneroCreate,
    GeneroRead,
    LibroDeGeneroRead,
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

    if sqlstate == "23505" and constraint_name == "uq_genero_nombre":
        detail = "Ya existe un género con ese nombre"
    else:
        detail = "Conflicto de datos en la base de datos"
    raise HTTPException(status_code=409, detail=detail)


async def crear_genero(
    session: AsyncSession, datos: GeneroCreate
) -> GeneroRead:
    """Alta de género delegando la unicidad a la base (RT-02, DD-04)."""
    genero = Genero(nombre=datos.nombre)
    try:
        session.add(genero)
        await session.flush()
        await session.commit()
    except IntegrityError as exc:
        await session.rollback()
        _traducir_integrity_error(exc)
    return GeneroRead.model_validate(genero, from_attributes=True)


async def listar_generos(
    session: AsyncSession, limit: int, offset: int
) -> list[GeneroRead]:
    """Listado paginado (RN-10) con orden determinista por ``id``."""
    stmt = select(Genero).order_by(Genero.id).limit(limit).offset(offset)
    result = await session.execute(stmt)
    generos = result.scalars().all()
    return [
        GeneroRead.model_validate(genero, from_attributes=True)
        for genero in generos
    ]


async def _obtener_genero_o_404(
    session: AsyncSession, genero_id: int
) -> Genero:
    """Lee el género y responde 404 propio si no existe (lectura, no escritura)."""
    genero = await session.get(Genero, genero_id)
    if genero is None:
        raise HTTPException(status_code=404, detail="Género no encontrado")
    return genero


async def obtener_genero(
    session: AsyncSession, genero_id: int
) -> GeneroRead:
    """Detalle de género con 404 propio."""
    genero = await _obtener_genero_o_404(session, genero_id)
    return GeneroRead.model_validate(genero, from_attributes=True)


async def listar_libros_de_genero(
    session: AsyncSession, genero_id: int, limit: int, offset: int
) -> list[LibroDeGeneroRead]:
    """Libros del género, paginados y ordenados por ``id`` (RN-10).

    Primero se valida la existencia del padre (404 propio) para no
    confundir "género inexistente" con "género sin libros".
    """
    await _obtener_genero_o_404(session, genero_id)
    stmt = (
        select(Libro)
        .where(Libro.genero_id == genero_id)
        .order_by(Libro.id)
        .limit(limit)
        .offset(offset)
    )
    result = await session.execute(stmt)
    libros = result.scalars().all()
    return [
        LibroDeGeneroRead.model_validate(libro, from_attributes=True)
        for libro in libros
    ]
