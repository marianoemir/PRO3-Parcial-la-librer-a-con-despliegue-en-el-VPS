"""Punto de entrada de la aplicación.

Arranque: ``uvicorn app.main:app --host 0.0.0.0``.

CH-01 (2.1): lifespan que crea motor + fábrica en ``app.state``,
ejecuta ``SQLModel.metadata.create_all`` tras importar los modelos
(CH-02 ya importó los 9 modelos de dominio), escribe UNA línea de log de arranque aunque
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
from app.modules.clientes.router import router as clientes_router
from app.modules.health.router import router as health_router
from app.modules.libros.router import router as libros_router

# CH-02: importar TODOS los modelos de dominio ANTES de create_all,
# para que SQLModel.metadata esté completo cuando el lifespan crea
# las tablas (skill sqlmodel: create_all solo tras importar todo).
from app.modules.autores.models import Autor  # noqa: F401
from app.modules.clientes.models import Cliente, PerfilCliente  # noqa: F401
from app.modules.editoriales.models import Editorial  # noqa: F401
from app.modules.generos.models import Genero  # noqa: F401
from app.modules.libros.models import Libro, LibroAutor  # noqa: F401
from app.modules.ventas.models import RenglonVenta, Venta  # noqa: F401

# uvicorn solo configura sus propios loggers y el root queda en WARNING, así que un logger propio en INFO no se vería.
logger = logging.getLogger("uvicorn.error")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Crea motor + fábrica, crea tablas, loguea y cierra al apagar."""
    engine = create_engine()
    app.state.engine = engine
    app.state.session_factory = create_session_factory(engine)
    # create_all solo tras importar todas las tablas (skill sqlmodel).
    # CH-02 importó los 9 modelos arriba. Si la base no
    # responde, la excepción propaga y el arranque falla (fail-fast).
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    tablas = sorted(SQLModel.metadata.tables.keys())
    logger.info("Arranque completado; tablas creadas: %s", tablas)
    yield
    await engine.dispose()


app = FastAPI(lifespan=lifespan)
app.include_router(health_router)
app.include_router(clientes_router)
app.include_router(libros_router)
