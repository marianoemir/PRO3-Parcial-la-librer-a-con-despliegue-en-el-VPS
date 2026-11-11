"""Rutas HTTP del módulo autores (CH-04).

Router delgado: recibe, delega en el service y declara la respuesta.
Sin SQL, sin ``try/except`` de base y con todos los handlers ``async def``.
No se declara ningún 409: la tabla ``autor`` no tiene UNIQUE/FK/CHECK.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.modules.autores import service
from app.modules.autores.schemas import (
    AutorCreate,
    AutorRead,
    AutorUpdate,
    LibroDeAutorRead,
)

router = APIRouter(prefix="/autores", tags=["autores"])

# Tope de INTEGER (int4): sin él, un id u offset mayor llega a la base y da 500.
_INT4_MAX = 2147483647

SessionDep = Annotated[AsyncSession, Depends(get_session)]


@router.post("/", response_model=AutorRead, status_code=201)
async def crear_autor(session: SessionDep, datos: AutorCreate) -> AutorRead:
    return await service.crear_autor(session, datos)


@router.get("/{autor_id}", response_model=AutorRead)
async def obtener_autor(
    session: SessionDep, autor_id: Annotated[int, Path(le=_INT4_MAX)]
) -> AutorRead:
    return await service.obtener_autor(session, autor_id)


@router.patch("/{autor_id}", response_model=AutorRead)
async def actualizar_autor(
    session: SessionDep,
    autor_id: Annotated[int, Path(le=_INT4_MAX)],
    datos: AutorUpdate,
) -> AutorRead:
    return await service.actualizar_autor(session, autor_id, datos)


@router.get("/{autor_id}/libros", response_model=list[LibroDeAutorRead])
async def listar_libros_de_autor(
    session: SessionDep,
    autor_id: Annotated[int, Path(le=_INT4_MAX)],
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0, le=_INT4_MAX)] = 0,
) -> list[LibroDeAutorRead]:
    return await service.listar_libros_de_autor(
        session, autor_id, limit=limit, offset=offset
    )
