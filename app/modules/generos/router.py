"""Rutas HTTP del módulo géneros (CH-04).

Router delgado: recibe, delega en el service y declara la respuesta.
Sin SQL, sin ``try/except`` de base y con todos los handlers ``async def``.
No se expone corrección parcial de géneros porque la tabla de referencia
no la declara (decisión registrada en ``design.md``).
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import INT4_MAX
from app.core.database import get_session
from app.modules.generos import service
from app.modules.generos.schemas import (
    GeneroCreate,
    GeneroRead,
    LibroDeGeneroRead,
)

router = APIRouter(prefix="/generos", tags=["generos"])

SessionDep = Annotated[AsyncSession, Depends(get_session)]


@router.post("/", response_model=GeneroRead, status_code=201)
async def crear_genero(session: SessionDep, datos: GeneroCreate) -> GeneroRead:
    return await service.crear_genero(session, datos)


@router.get("/", response_model=list[GeneroRead])
async def listar_generos(
    session: SessionDep,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0, le=INT4_MAX)] = 0,
) -> list[GeneroRead]:
    return await service.listar_generos(session, limit=limit, offset=offset)


@router.get("/{genero_id}", response_model=GeneroRead)
async def obtener_genero(
    session: SessionDep, genero_id: Annotated[int, Path(le=INT4_MAX)]
) -> GeneroRead:
    return await service.obtener_genero(session, genero_id)


@router.get("/{genero_id}/libros", response_model=list[LibroDeGeneroRead])
async def listar_libros_de_genero(
    session: SessionDep,
    genero_id: Annotated[int, Path(le=INT4_MAX)],
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0, le=INT4_MAX)] = 0,
) -> list[LibroDeGeneroRead]:
    return await service.listar_libros_de_genero(
        session, genero_id, limit=limit, offset=offset
    )
