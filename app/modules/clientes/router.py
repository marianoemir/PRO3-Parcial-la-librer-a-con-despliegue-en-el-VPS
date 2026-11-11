"""Rutas HTTP del módulo clientes."""

from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import INT4_MAX
from app.core.database import get_session
from app.modules.clientes import service
from app.modules.clientes.schemas import (
    ClienteCreate,
    ClienteRead,
    ClienteUpdate,
    PerfilCreate,
    PerfilRead,
    VentaResumenRead,
)

router = APIRouter(prefix="/clientes", tags=["clientes"])

SessionDep = Annotated[AsyncSession, Depends(get_session)]
ClienteId = Annotated[int, Path(le=INT4_MAX)]
Limit = Annotated[int, Query(ge=1, le=100)]
Offset = Annotated[int, Query(ge=0, le=INT4_MAX)]


@router.post("/", response_model=ClienteRead, status_code=status.HTTP_201_CREATED)
async def create_cliente(data: ClienteCreate, session: SessionDep) -> ClienteRead:
    """Registra un cliente."""
    return await service.create_cliente(session, data)


@router.get("/{cliente_id}", response_model=ClienteRead)
async def read_cliente(cliente_id: ClienteId, session: SessionDep) -> ClienteRead:
    """Obtiene un cliente y su perfil singular."""
    return await service.get_cliente(session, cliente_id)


@router.patch("/{cliente_id}", response_model=ClienteRead)
async def update_cliente(
    cliente_id: ClienteId, data: ClienteUpdate, session: SessionDep
) -> ClienteRead:
    """Actualiza parcialmente un cliente."""
    return await service.update_cliente(session, cliente_id, data)


@router.post(
    "/{cliente_id}/perfil",
    response_model=PerfilRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_perfil(
    cliente_id: ClienteId, data: PerfilCreate, session: SessionDep
) -> PerfilRead:
    """Crea el perfil del cliente identificado en la ruta."""
    return await service.create_perfil(session, cliente_id, data)


@router.get("/{cliente_id}/ventas", response_model=list[VentaResumenRead])
async def list_ventas(
    cliente_id: ClienteId,
    session: SessionDep,
    limit: Limit = 20,
    offset: Offset = 0,
) -> list[VentaResumenRead]:
    """Lista resúmenes de ventas paginados, sin renglones."""
    return await service.list_ventas(session, cliente_id, limit, offset)
