"""Motor asíncrono y fábrica de sesiones.

Crea el motor async ``postgresql+asyncpg://`` con ``echo`` desde
``SQL_ECHO`` (default ``False``) y la fábrica de sesiones async con
``expire_on_commit=False`` (SU-02). La creación física del motor ocurre
en el lifespan (2.1, en ``app/state``); acá se proveen las factorías y
la dependencia ``get_session`` por petición. NO se crea el motor al
importar (decisión de diseño 1).
"""

from __future__ import annotations

from collections.abc import AsyncGenerator

from fastapi import Request
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
)
from sqlalchemy.ext.asyncio import (
    create_async_engine as sa_create_async_engine,
)

from app.core.config import get_database_url, get_sql_echo


def create_engine() -> AsyncEngine:
    """Crea el motor asíncrono con la configuración por entorno."""
    return sa_create_async_engine(get_database_url(), echo=get_sql_echo())


def create_session_factory(engine: AsyncEngine):
    """Crea la fábrica de sesiones async para un motor dado."""
    return async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )


async def get_session(
    request: Request,
) -> AsyncGenerator[AsyncSession, None]:
    """Provee una sesión propia por petición (``expire_on_commit=False``).

    La fábrica vive en ``app.state.session_factory`` (fijada por el
    lifespan en 2.1). Cada petición recibe una sesión propia con
    ``yield``.
    """
    session_factory = request.app.state.session_factory
    async with session_factory() as session:
        yield session
