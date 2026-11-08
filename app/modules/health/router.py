"""Endpoints de salud: ``GET /health/live`` y ``GET /health/ready``.

CH-01 (2.2 + 2.3): ``live`` responde sin tocar la base; ``ready``
ejecuta ``SELECT 1`` y, si falla, responde 503 con cuerpo propio sin
texto interno de la base (RN-12) — decisión del equipo pendiente de
confirmación (Q2, ``10_preguntas_abiertas.md`` §(2)), nunca regla del
enunciado. El 503 queda aislado en este handler.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session

router = APIRouter(prefix="/health", tags=["health"])

SessionDep = Annotated[AsyncSession, Depends(get_session)]


@router.get("/live")
async def live() -> dict[str, str]:
    """Proceso vivo: responde sin tocar la base de datos."""
    return {"estado": "vivo"}


@router.get("/ready")
async def ready(session: SessionDep) -> JSONResponse:
    """Base disponible: ``SELECT 1`` → 200 listo; si falla → 503 no listo."""
    try:
        await session.execute(text("SELECT 1"))
    except Exception:
        # Cuerpo propio sin texto interno (RN-12): sin mensaje de
        # excepción, sin host, sin cadena de conexión ni credenciales.
        return JSONResponse(status_code=503, content={"estado": "no listo"})
    return JSONResponse(content={"estado": "listo"})
