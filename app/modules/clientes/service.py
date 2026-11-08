"""Operaciones de persistencia y errores del módulo clientes."""

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from sqlmodel import select

from app.modules.clientes.models import Cliente, PerfilCliente
from app.modules.clientes.schemas import ClienteCreate, ClienteUpdate, PerfilCreate
from app.modules.ventas.models import Venta


def _integrity_constraint_name(error: IntegrityError) -> str | None:
    """Obtiene el constraint de asyncpg sin incluir su texto en la respuesta."""
    origin = error.orig
    return getattr(origin, "constraint_name", None) or getattr(
        origin.__cause__, "constraint_name", None
    )


async def _get_cliente_with_perfil(
    session: AsyncSession, cliente_id: int
) -> Cliente | None:
    result = await session.execute(
        select(Cliente)
        .options(joinedload(Cliente.perfil))
        .where(Cliente.id == cliente_id)
    )
    return result.scalar_one_or_none()


async def get_cliente(session: AsyncSession, cliente_id: int) -> Cliente:
    """Devuelve un cliente con su perfil ya precargado o responde 404."""
    cliente = await _get_cliente_with_perfil(session, cliente_id)
    if cliente is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente no encontrado.",
        )
    return cliente


async def create_cliente(
    session: AsyncSession, data: ClienteCreate
) -> Cliente:
    """Inserta un cliente y traduce la unicidad de email a un 409 público."""
    cliente = Cliente.model_validate(data)
    session.add(cliente)
    try:
        await session.commit()
    except IntegrityError as error:
        await session.rollback()
        if _integrity_constraint_name(error) == "uq_cliente_email":
            detail = "El email ya está registrado."
        else:
            detail = "No se pudo registrar el cliente."
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=detail)
    return await get_cliente(session, cliente.id)


async def update_cliente(
    session: AsyncSession, cliente_id: int, data: ClienteUpdate
) -> Cliente:
    """Actualiza solo los campos recibidos y recarga el perfil de la respuesta."""
    cliente = await get_cliente(session, cliente_id)
    cliente.sqlmodel_update(data.model_dump(exclude_unset=True))
    session.add(cliente)
    try:
        await session.commit()
    except IntegrityError as error:
        await session.rollback()
        if _integrity_constraint_name(error) == "uq_cliente_email":
            detail = "El email ya está registrado."
        else:
            detail = "No se pudo actualizar el cliente."
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=detail)
    return await get_cliente(session, cliente_id)


async def create_perfil(
    session: AsyncSession, cliente_id: int, data: PerfilCreate
) -> PerfilCliente:
    """Crea el perfil del cliente de ruta, sin consultar perfiles previamente."""
    cliente = await session.get(Cliente, cliente_id)
    if cliente is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente no encontrado.",
        )

    perfil = PerfilCliente(cliente_id=cliente_id, **data.model_dump())
    session.add(perfil)
    try:
        await session.commit()
        await session.refresh(perfil)
    except IntegrityError as error:
        await session.rollback()
        if _integrity_constraint_name(error) == "uq_perfil_cliente_cliente_id":
            detail = "El cliente ya tiene un perfil."
        else:
            detail = "No se pudo crear el perfil del cliente."
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=detail)
    return perfil


async def list_ventas(
    session: AsyncSession, cliente_id: int, limit: int, offset: int
) -> list[Venta]:
    """Devuelve resúmenes planos de ventas, ordenados y paginados por id."""
    cliente = await session.get(Cliente, cliente_id)
    if cliente is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente no encontrado.",
        )

    result = await session.execute(
        select(Venta)
        .where(Venta.cliente_id == cliente_id)
        .order_by(Venta.id)
        .offset(offset)
        .limit(limit)
    )
    return list(result.scalars().all())
