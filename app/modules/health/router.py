from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.modules.health import service
from app.modules.health.schemas import EstadoRead

router = APIRouter(prefix="/health", tags=["health"])

SessionDep = Annotated[AsyncSession, Depends(get_session)]


@router.get("/live", response_model=EstadoRead)
async def live() -> EstadoRead:
    return EstadoRead(estado="vivo")


@router.get("/ready", response_model=EstadoRead)
async def ready(session: SessionDep) -> JSONResponse:
    if await service.base_disponible(session):
        return JSONResponse(content={"estado": "listo"})
    return JSONResponse(status_code=503, content={"estado": "no listo"})
