"""Lógica del módulo ventas (CH-07)."""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from typing import Sequence

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload
from sqlmodel import select

from app.modules.clientes.models import Cliente
from app.modules.libros.models import Libro
from app.modules.ventas.models import RenglonVenta, Venta
from app.modules.ventas.schemas import RenglonVentaRead, VentaCreate, VentaRead

logger = logging.getLogger("uvicorn.error")

_MONEY_Q = Decimal("0.01")
_TOTAL_MAX = Decimal("9999999999.99")


def _venta_options():
    return (
        joinedload(Venta.cliente),
        selectinload(Venta.renglones).joinedload(RenglonVenta.libro),
    )


async def _leer_venta_precargada(session: AsyncSession, venta_id: int) -> Venta | None:
    stmt = (
        select(Venta)
        .options(*_venta_options())
        .where(Venta.id == venta_id)
        .execution_options(populate_existing=True)
    )
    result = await session.execute(stmt)
    return result.unique().scalar_one_or_none()


def _serializar_venta(venta: Venta) -> VentaRead:
    renglones = []
    for r in venta.renglones:
        titulo = r.libro.titulo if getattr(r, "libro", None) is not None else ""
        precio = Decimal(str(r.precio_unitario)).quantize(_MONEY_Q)
        renglones.append(
            {
                "libro_id": r.libro_id,
                "titulo": titulo,
                "cantidad": r.cantidad,
                "precio_unitario": format(precio, "f"),
                "subtotal": format((Decimal(r.cantidad) * precio).quantize(_MONEY_Q), "f"),
            }
        )
    data = {
        "id": venta.id,
        "fecha": venta.fecha,
        "total": format(Decimal(str(venta.total)).quantize(_MONEY_Q), "f"),
        "cliente": {
            "id": venta.cliente.id,
            "nombre": venta.cliente.nombre,
            "email": venta.cliente.email,
        },
        "renglones": renglones,
    }
    return VentaRead.model_validate(data, from_attributes=False)


async def crear_venta(session: AsyncSession, datos: VentaCreate) -> VentaRead:
    ids = [r.libro_id for r in datos.renglones]
    stmt = select(Libro).where(Libro.id.in_(ids))
    result = await session.execute(stmt)
    libros: Sequence[Libro] = result.scalars().all()
    libros_por_id = {libro.id: libro for libro in libros}
    if set(libros_por_id.keys()) != set(ids):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El libro indicado no existe")

    renglones: list[RenglonVenta] = []
    total = Decimal("0.00")
    for item in datos.renglones:
        libro = libros_por_id[item.libro_id]
        precio = Decimal(libro.precio).quantize(_MONEY_Q)
        subtotal = (Decimal(item.cantidad) * precio).quantize(_MONEY_Q)
        total += subtotal
        renglones.append(
            RenglonVenta(
                libro_id=item.libro_id,
                cantidad=item.cantidad,
                precio_unitario=precio,
            )
        )
    total = total.quantize(_MONEY_Q)
    if total > _TOTAL_MAX:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="El total de la venta excede el máximo permitido",
        )

    venta = Venta(
        cliente_id=datos.cliente_id,
        fecha=datetime.now(timezone.utc),
        total=total,
        renglones=renglones,
    )
    session.add(venta)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        # FK cliente (u otras) sin pre-checks -> 409 propio
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="La referencia indicada no existe o hay un conflicto de datos",
        )

    precargada = await _leer_venta_precargada(session, int(venta.id))
    if precargada is None:
        raise HTTPException(status_code=500, detail="Error interno al cargar la venta creada")
    return _serializar_venta(precargada)


async def obtener_venta(session: AsyncSession, venta_id: int) -> VentaRead:
    venta = await _leer_venta_precargada(session, venta_id)
    if venta is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Venta no encontrada")
    return _serializar_venta(venta)


async def listar_ventas(session: AsyncSession, limit: int, offset: int) -> list[VentaRead]:
    stmt = (
        select(Venta)
        .options(*_venta_options())
        .order_by(Venta.id)
        .limit(limit)
        .offset(offset)
    )
    result = await session.execute(stmt)
    ventas = result.unique().scalars().all()
    return [_serializar_venta(v) for v in ventas]


async def avisar_comprobante(venta_id: int, email: str) -> None:
    await asyncio.sleep(0.5)
    logger.info("Aviso comprobante venta_id=%s email=%s", venta_id, email)

