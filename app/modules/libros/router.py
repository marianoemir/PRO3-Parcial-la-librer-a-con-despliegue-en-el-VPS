from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.modules.libros import service
from app.modules.libros.schemas import (
    LibroCreate,
    LibroListRead,
    LibroRead,
    LibroUpdate,
)

router = APIRouter(prefix="/libros", tags=["libros"])

SessionDep = Annotated[AsyncSession, Depends(get_session)]


@router.post("/", response_model=LibroRead, status_code=201)
async def crear_libro(session: SessionDep, datos: LibroCreate) -> LibroRead:
    return await service.crear_libro(session, datos)


@router.get("/", response_model=list[LibroListRead])
async def listar_libros(
    session: SessionDep,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
    titulo: Annotated[str | None, Query()] = None,
    genero_id: Annotated[int | None, Query()] = None,
) -> list[LibroListRead]:
    return await service.listar_libros(
        session, limit=limit, offset=offset, titulo=titulo, genero_id=genero_id
    )


@router.get("/{libro_id}", response_model=LibroRead)
async def obtener_libro(
    session: SessionDep, libro_id: Annotated[int, Path()]
) -> LibroRead:
    return await service.obtener_libro(session, libro_id)


@router.patch("/{libro_id}", response_model=LibroRead)
async def actualizar_libro(
    session: SessionDep,
    libro_id: Annotated[int, Path()],
    datos: LibroUpdate,
) -> LibroRead:
    return await service.actualizar_libro(session, libro_id, datos)
