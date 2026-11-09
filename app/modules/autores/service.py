"""Lógica del módulo autores (CH-04).

La tabla ``autor`` no tiene UNIQUE, FK ni CHECK (enunciado, PDF p. 4),
así que este service no traduce conflictos de unicidad: el alta y el
PATCH escriben y dejan que la base acepte duplicados. El 404 del
detalle y de la relación es propio (RN-12). Todos los handlers que
llaman a este service son ``async def`` y la sesión llega por parámetro.
"""

from __future__ import annotations

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from sqlmodel import select

from app.modules.autores.models import Autor
from app.modules.autores.schemas import (
    AutorCreate,
    AutorRead,
    AutorUpdate,
    LibroDeAutorRead,
)
from app.modules.libros.models import LibroAutor


async def crear_autor(
    session: AsyncSession, datos: AutorCreate
) -> AutorRead:
    """Alta de autor sin restricciones extra que traducir."""
    autor = Autor(nombre=datos.nombre, nacionalidad=datos.nacionalidad)
    session.add(autor)
    await session.flush()
    await session.commit()
    return AutorRead.model_validate(autor, from_attributes=True)


async def _obtener_autor_o_404(session: AsyncSession, autor_id: int) -> Autor:
    """Lee el autor y responde 404 propio si no existe (lectura, no escritura)."""
    autor = await session.get(Autor, autor_id)
    if autor is None:
        raise HTTPException(status_code=404, detail="Autor no encontrado")
    return autor


async def obtener_autor(session: AsyncSession, autor_id: int) -> AutorRead:
    """Detalle de autor con 404 propio."""
    autor = await _obtener_autor_o_404(session, autor_id)
    return AutorRead.model_validate(autor, from_attributes=True)


async def actualizar_autor(
    session: AsyncSession, autor_id: int, datos: AutorUpdate
) -> AutorRead:
    """PATCH parcial con ``exclude_unset`` sobre los campos enviados."""
    autor = await _obtener_autor_o_404(session, autor_id)
    cambios = datos.model_dump(exclude_unset=True)
    for clave, valor in cambios.items():
        setattr(autor, clave, valor)
    await session.flush()
    await session.commit()
    return AutorRead.model_validate(autor, from_attributes=True)


async def listar_libros_de_autor(
    session: AsyncSession, autor_id: int, limit: int, offset: int
) -> list[LibroDeAutorRead]:
    """Autorías del autor con ``rol`` y ``orden``, paginadas (RN-10).

    El ``joinedload`` de ``LibroAutor.libro`` es obligatorio: sin
    precarga, leer ``aa.libro`` dispararía carga perezosa (RT-04) y
    lanzaría ``MissingGreenlet`` en el stack async. El orden es por
    ``orden`` y desempata por ``libro_id``.
    """
    await _obtener_autor_o_404(session, autor_id)
    stmt = (
        select(LibroAutor)
        .options(joinedload(LibroAutor.libro))
        .where(LibroAutor.autor_id == autor_id)
        .order_by(LibroAutor.orden, LibroAutor.libro_id)
        .limit(limit)
        .offset(offset)
    )
    result = await session.execute(stmt)
    autorias = result.unique().scalars().all()
    return [
        LibroDeAutorRead(
            libro_id=aa.libro_id,
            isbn=aa.libro.isbn,
            titulo=aa.libro.titulo,
            precio=aa.libro.precio,
            stock=aa.libro.stock,
            rol=aa.rol,
            orden=aa.orden,
        )
        for aa in autorias
    ]
