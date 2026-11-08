"""Configuración por entorno.

Lee ``DATABASE_URL`` y ``SQL_ECHO`` sin secretos en código. La fuente es
el entorno o el archivo ``.env`` (ver ``env.example``) mediante
``load_dotenv``. Si ``DATABASE_URL`` falta o está vacía (``""`` o solo
espacios), el proceso termina con un error claro y sin valor por defecto
(cubre D-05). El log de arranque no imprime ``DATABASE_URL`` ni
credenciales.
"""

from __future__ import annotations

import os

from dotenv import load_dotenv

load_dotenv()


def _parse_bool(value: str | None) -> bool:
    """Convierte un string de entorno a bool (default ``False``)."""
    if value is None:
        return False
    return value.strip().lower() in {"true", "1", "yes", "on"}


def get_database_url() -> str:
    """Devuelve ``DATABASE_URL`` validada o falla con error claro.

    Sin valor por defecto: si la variable no está definida o está vacía
    (``""`` o solo espacios), lanza :class:`RuntimeError` nombrando la
    variable, sin imprimir su valor ni credenciales.
    """
    url = os.getenv("DATABASE_URL")
    if url is None or url.strip() == "":
        raise RuntimeError(
            "Falta la variable de entorno DATABASE_URL (no definida o vacía). "
            "Define DATABASE_URL en el entorno o en el archivo .env "
            "(ver env.example). Sin valor por defecto."
        )
    return url.strip()


def get_sql_echo() -> bool:
    """Devuelve el flag ``SQL_ECHO`` (default ``False``)."""
    return _parse_bool(os.getenv("SQL_ECHO"))


# Validación al importar: fail-fast para que ``uvicorn app.main:app``
# termine con error claro si ``DATABASE_URL`` falta o está vacía,
# incluso antes del lifespan (2.1).
DATABASE_URL = get_database_url()
