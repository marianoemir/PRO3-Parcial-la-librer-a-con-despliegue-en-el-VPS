"""Punto de entrada de la aplicación.

Arranque: ``uvicorn app.main:app --host 0.0.0.0``.

CH-01 (2.1): lifespan que crea motor + fábrica en ``app.state``,
ejecuta ``SQLModel.metadata.create_all`` tras importar los modelos
(en CH-01 aún no hay modelos de dominio — la lista de tablas queda
vacía hasta CH-02), escribe UNA línea de log de arranque aunque
``SQL_ECHO=false``, falla rápido si la base no responde (sin capturar
excepciones: el proceso no queda sirviendo) y cierra el motor al
apagar. CH-01 (2.2): registra el router de salud con
``include_router``. El log no imprime ``DATABASE_URL`` ni credenciales.
"""

from __future__ import annotations

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlmodel import SQLModel

# Import intencional para fail-fast: valida DATABASE_URL al arrancar
# (1.3), incluso antes del lifespan. El motor se crea en el lifespan.
from app.core import config  # noqa: F401
from app.core.database import create_engine, create_session_factory
from app.modules.health.router import router as health_router

# CH-02: importar acá TODOS los modelos de dominio (editorial, genero,
# autor, libro, libro_autor, cliente, perfil_cliente, venta,
# renglon_venta) ANTES de crear las tablas; hoy no hay ninguno.
# Ejemplo futuro: from app.modules.libros.models import Libro  # noqa

# uvicorn solo configura sus propios loggers y el root queda en WARNING, así que un logger propio en INFO no se vería.
logger = logging.getLogger("uvicorn.error")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Crea motor + fábrica, crea tablas, loguea y cierra al apagar."""
    engine = create_engine()
    app.state.engine = engine
    app.state.session_factory = create_session_factory(engine)
    # create_all solo tras importar todas las tablas (skill sqlmodel).
    # En CH-01 no hay modelos: metadata está vacía. Si la base no
    # responde, la excepción propaga y el arranque falla (fail-fast).
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    tablas = sorted(SQLModel.metadata.tables.keys())
    logger.info("Arranque completado; tablas creadas: %s", tablas)
    yield
    await engine.dispose()


app = FastAPI(lifespan=lifespan)
app.include_router(health_router)
