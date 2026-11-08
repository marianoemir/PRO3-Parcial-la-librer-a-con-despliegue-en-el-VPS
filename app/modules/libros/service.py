"""Lógica del módulo libros (CH-05).

El service recibe la sesión como parámetro y traduce los errores
de la base a HTTP propios (RN-12): nunca expone texto interno ni
usa subcadenas del mensaje (RT-02, DD-04). Todos los handlers
que llaman a este service son `async def`.
"""

from __future__ import annotations

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload
from sqlmodel import select

from app.modules.libros.models import Libro, LibroAutor
from app.modules.libros.schemas import (
    LibroCreate,
    LibroListRead,
    LibroRead,
    LibroUpdate,
)


def _traducir_integrity_error(exc: IntegrityError) -> None:
    """Traduce IntegrityError a 409 propio por sqlstate y constraint_name."""
    orig = getattr(exc, "orig", None)
    cause = getattr(orig, "__cause__", None) if orig is not None else None
    sqlstate = getattr(orig, "sqlstate", None)
    if sqlstate is None and cause is not None:
        sqlstate = getattr(cause, "sqlstate", None)
    if sqlstate is None and orig is not None:
        sqlstate = getattr(orig, "pgcode", None)
    constraint_name = None
    if cause is not None:
        constraint_name = getattr(cause, "constraint_name", None)
    if constraint_name is None and orig is not None:
        constraint_name = getattr(orig, "constraint_name", None)

    if sqlstate == "23505" and constraint_name == "uq_libro_isbn":
        detail = "Ya existe un libro con ese ISBN"
    elif sqlstate == "23503":
        detail = "La referencia indicada no existe"
    elif sqlstate == "23505" and constraint_name == "libro_autor_pkey":
        detail = "Autoría duplicada en la lista de autores"
    elif sqlstate == "23514":
        detail = "Los datos no cumplen una regla de la base de datos"
    else:
        detail = "Conflicto de datos en la base de datos"
    raise HTTPException(status_code=409, detail=detail)


async def _leer_libro_precargado(
    session: AsyncSession, libro_id: int
) -> Libro | None:
    """Lee un libro con editorial, género y autorías->autor precargados (RT-04).

    Usa `select`+`execute` (no `session.get`) para forzar la precarga
    tras `flush` en el alta: el objeto recién insertado ya está en el
    identity map y `session.get` lo devolvería sin cargar relaciones
    (lazy -> MissingGreenlet).
    """
    stmt = (
        select(Libro)
        .options(
            joinedload(Libro.editorial),
            joinedload(Libro.genero),
            selectinload(Libro.autorias).selectinload(LibroAutor.autor),
        )
        .where(Libro.id == libro_id)
        .execution_options(populate_existing=True)
    )
    result = await session.execute(stmt)
    return result.unique().scalar_one_or_none()


async def listar_libros(
    session: AsyncSession,
    limit: int,
    offset: int,
    titulo: str | None = None,
    genero_id: int | None = None,
) -> list[LibroListRead]:
    """Listado paginado (RN-10) con filtros (RN-11) y precarga de editorial/género."""
    stmt = select(Libro).options(
        joinedload(Libro.editorial), joinedload(Libro.genero)
    ).order_by(Libro.id)
    if titulo is not None:
        stmt = stmt.where(Libro.titulo.ilike(f"%{titulo}%"))
    if genero_id is not None:
        stmt = stmt.where(Libro.genero_id == genero_id)
    stmt = stmt.limit(limit).offset(offset)
    result = await session.execute(stmt)
    libros = result.unique().scalars().all()
    return [
        LibroListRead.model_validate(libro, from_attributes=True)
        for libro in libros
    ]


async def crear_libro(session: AsyncSession, datos: LibroCreate) -> LibroRead:
    """Alta de libro con autorías (DD-01) sin consultar ids antes (RT-02)."""
    libro = Libro(
        isbn=datos.isbn,
        titulo=datos.titulo,
        precio=datos.precio,
        stock=datos.stock,
        editorial_id=datos.editorial_id,
        genero_id=datos.genero_id,
    )
    for autor in datos.autores:
        libro.autorias.append(
            LibroAutor(autor_id=autor.autor_id, rol=autor.rol, orden=autor.orden)
        )
    try:
        session.add(libro)
        await session.flush()
        libro_precargado = await _leer_libro_precargado(session, libro.id)
        await session.commit()
    except IntegrityError as exc:
        await session.rollback()
        _traducir_integrity_error(exc)
    if libro_precargado is None:
        raise HTTPException(status_code=500, detail="Error interno al cargar el libro creado")
    return LibroRead.model_validate(libro_precargado, from_attributes=True)


async def _obtener_libro_o_404(session: AsyncSession, libro_id: int) -> Libro:
    libro = await session.get(Libro, libro_id)
    if libro is None:
        raise HTTPException(status_code=404, detail="Libro no encontrado")
    return libro


async def obtener_libro(session: AsyncSession, libro_id: int) -> LibroRead:
    """Detalle precargado con número fijo de consultas (RT-04) y 404 propio."""
    libro_precargado = await _leer_libro_precargado(session, libro_id)
    if libro_precargado is None:
        raise HTTPException(status_code=404, detail="Libro no encontrado")
    return LibroRead.model_validate(libro_precargado, from_attributes=True)


async def actualizar_libro(
    session: AsyncSession, libro_id: int, datos: LibroUpdate
) -> LibroRead:
    """PATCH parcial con `exclude_unset` sobre escalares (sin autorías)."""
    libro = await _obtener_libro_o_404(session, libro_id)
    cambios = datos.model_dump(exclude_unset=True)
    for clave, valor in cambios.items():
        setattr(libro, clave, valor)
    try:
        await session.flush()
        libro_precargado = await _leer_libro_precargado(session, libro_id)
        await session.commit()
    except IntegrityError as exc:
        await session.rollback()
        _traducir_integrity_error(exc)
    if libro_precargado is None:
        raise HTTPException(status_code=500, detail="Error interno al cargar el libro actualizado")
    return LibroRead.model_validate(libro_precargado, from_attributes=True)
