"""Rutas HTTP del módulo editoriales (CH-04).

Router delgado: recibe, delega en el service y declara la respuesta.
Sin SQL, sin ``try/except`` de base y con todos los handlers ``async def``.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import INT4_MAX
from app.core.database import get_session
from app.modules.editoriales import service
from app.modules.editoriales.schemas import (
    EditorialCreate,
    EditorialRead,
    EditorialUpdate,
    LibroDeEditorialRead,
)

router = APIRouter(prefix="/editoriales", tags=["editoriales"])

SessionDep = Annotated[AsyncSession, Depends(get_session)]


@router.post("/", response_model=EditorialRead, status_code=201)
async def crear_editorial(
    session: SessionDep, datos: EditorialCreate
) -> EditorialRead:
    return await service.crear_editorial(session, datos)


@router.get("/", response_model=list[EditorialRead])
async def listar_editoriales(
    session: SessionDep,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0, le=INT4_MAX)] = 0,
) -> list[EditorialRead]:
    return await service.listar_editoriales(session, limit=limit, offset=offset)


@router.get("/{editorial_id}", response_model=EditorialRead)
async def obtener_editorial(
    session: SessionDep, editorial_id: Annotated[int, Path(le=INT4_MAX)]
) -> EditorialRead:
    return await service.obtener_editorial(session, editorial_id)


@router.patch("/{editorial_id}", response_model=EditorialRead)
async def actualizar_editorial(
    session: SessionDep,
    editorial_id: Annotated[int, Path(le=INT4_MAX)],
    datos: EditorialUpdate,
) -> EditorialRead:
    return await service.actualizar_editorial(session, editorial_id, datos)


@router.get("/{editorial_id}/libros", response_model=list[LibroDeEditorialRead])
async def listar_libros_de_editorial(
    session: SessionDep,
    editorial_id: Annotated[int, Path(le=INT4_MAX)],
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0, le=INT4_MAX)] = 0,
) -> list[LibroDeEditorialRead]:
    return await service.listar_libros_de_editorial(
        session, editorial_id, limit=limit, offset=offset
    )
