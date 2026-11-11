"""Rutas HTTP del módulo ventas (CH-07)."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, Path, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import INT4_MAX
from app.core.database import get_session
from app.modules.ventas import service
from app.modules.ventas.schemas import VentaCreate, VentaRead

router = APIRouter(prefix="/ventas", tags=["ventas"])

SessionDep = Annotated[AsyncSession, Depends(get_session)]
VentaId = Annotated[int, Path(le=INT4_MAX)]
Limit = Annotated[int, Query(ge=1, le=100)]
Offset = Annotated[int, Query(ge=0, le=INT4_MAX)]


@router.post("/", response_model=VentaRead, status_code=status.HTTP_201_CREATED)
async def crear_venta(
    datos: VentaCreate,
    session: SessionDep,
    background_tasks: BackgroundTasks,
) -> VentaRead:
    venta = await service.crear_venta(session, datos)
    # pasar solo valores simples ya extraídos (id, email) - sin sesión/ORM
    background_tasks.add_task(service.avisar_comprobante, venta.id, venta.cliente.email)
    return venta


@router.get("/", response_model=list[VentaRead])
async def listar_ventas(
    session: SessionDep,
    limit: Limit = 20,
    offset: Offset = 0,
) -> list[VentaRead]:
    return await service.listar_ventas(session, limit=limit, offset=offset)


@router.get("/{venta_id}", response_model=VentaRead)
async def obtener_venta(venta_id: VentaId, session: SessionDep) -> VentaRead:
    return await service.obtener_venta(session, venta_id)

