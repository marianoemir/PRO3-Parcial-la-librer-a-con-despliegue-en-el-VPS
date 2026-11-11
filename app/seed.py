"""Datos iniciales (seed) del catálogo y las ventas (CH-08).

Comando de línea de comandos, independiente de la API y fuera de
``app/modules/*``: no expone endpoints, no define router, schemas ni service
de dominio. Se ejecuta con ``python -m app.seed`` en local y con
``docker exec libreria python -m app.seed`` en el VPS (el ``Dockerfile``
copia ``app/`` a la imagen, así que el módulo viaja con ella).

Garantías:

- **Determinista**: ids y valores fijos, tomados de ``design.md`` §2. Dinero
  siempre ``Decimal`` (nunca ``float``); la fecha de la venta lleva zona
  horaria.
- **Idempotente**: cada fila se inserta con ``INSERT ... ON CONFLICT DO
  NOTHING`` (sin ``index_elements``), así PostgreSQL ignora el conflicto
  contra la PK y contra todas las UNIQUE. Reejecutar no duplica y repone solo
  las filas faltantes; la base sigue siendo la garante de unicidad (RT-02).
- **Atómica**: toda la carga ocurre en una única transacción; ante cualquier
  rechazo de la base se revierte completa y no quedan filas parciales.
- **Secuencias alineadas**: al final de la transacción se ejecuta ``setval``
  sobre las tablas con ``id`` serial para que un alta posterior por API
  obtenga un id nuevo (editorial 3, venta 2) en lugar de chocar con el
  dataset.
- **Sin efectos no definidos**: NO ejecuta ``create_all`` ni migraciones (el
  esquema es responsabilidad del lifespan de ``app/main.py``) y NO descuenta
  stock por la venta cargada (``knowledge-base/10_preguntas_abiertas.md``
  §(1) sigue pendiente).
- **Sin secretos**: nunca imprime ``DATABASE_URL``, usuario, contraseña, SQL
  ni trazas internas; cada fallo se traduce a un mensaje propio y a un código
  de salida distinto de 0.

Uso::

    python -m app.seed

El dataset es de ejemplo del implementador, no una regla de negocio: la
lista cerrada de filas base es §(6) de ``10_preguntas_abiertas.md`` y sigue
pendiente de la cátedra.
"""

from __future__ import annotations

import asyncio
from collections.abc import Mapping, Sequence
from datetime import datetime, timezone
from decimal import Decimal
from types import MappingProxyType
from typing import Any, Final

from sqlalchemy import Table, text
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.exc import (
    IntegrityError,
    InterfaceError,
    OperationalError,
    ProgrammingError,
)

# Importar los modelos registra las tablas y sus claves foráneas en la
# metadata de SQLModel, de modo que las referencias del dataset resuelven
# contra el mismo esquema que crea el lifespan. NO se importa ``app.main``
# (no se levanta la API) ni se llama a ``create_all``.
from app.modules.autores.models import Autor
from app.modules.clientes.models import Cliente, PerfilCliente
from app.modules.editoriales.models import Editorial
from app.modules.generos.models import Genero
from app.modules.libros.models import Libro, LibroAutor
from app.modules.ventas.models import RenglonVenta, Venta

__all__ = ["DATASET", "main", "validar_dataset"]

#: Roles aceptados por ``ck_libro_autor_rol_valido`` (models.py de libros).
ROLES_VALIDOS: Final[frozenset[str]] = frozenset(
    {"autor", "coautor", "traductor", "ilustrador"}
)

#: Orden de carga según dependencias de claves foráneas.
ORDEN_TABLAS: Final[tuple[str, ...]] = (
    "editorial",
    "genero",
    "autor",
    "libro",
    "libro_autor",
    "cliente",
    "perfil_cliente",
    "venta",
    "renglon_venta",
)

#: Tablas con ``id`` serial cuyo valor hay que alinear al terminar la carga.
#: ``libro_autor`` queda afuera: su PK es compuesta y no tiene secuencia.
TABLAS_CON_SECUENCIA: Final[tuple[str, ...]] = (
    "editorial",
    "genero",
    "autor",
    "libro",
    "cliente",
    "perfil_cliente",
    "venta",
    "renglon_venta",
)

#: Tablas de SQLAlchemy Core asociadas a cada nombre del dataset.
TABLAS: Final[dict[str, Table]] = {
    "editorial": Editorial.__table__,
    "genero": Genero.__table__,
    "autor": Autor.__table__,
    "libro": Libro.__table__,
    "libro_autor": LibroAutor.__table__,
    "cliente": Cliente.__table__,
    "perfil_cliente": PerfilCliente.__table__,
    "venta": Venta.__table__,
    "renglon_venta": RenglonVenta.__table__,
}

# ---------------------------------------------------------------------------
# Dataset determinista (design.md §2). Filas inmutables (dict dentro de
# tupla) y con ids explícitos; el orden de las claves es el de dependencias.
# ---------------------------------------------------------------------------

_EDITORIALES: Final[tuple[dict[str, Any], ...]] = (
    {"id": 1, "nombre": "Sudamericana", "pais": "Argentina"},
    {"id": 2, "nombre": "Anagrama", "pais": "España"},
)

_GENEROS: Final[tuple[dict[str, Any], ...]] = (
    {"id": 1, "nombre": "Novela"},
    {"id": 2, "nombre": "Cuento"},
)

_AUTORES: Final[tuple[dict[str, Any], ...]] = (
    {"id": 1, "nombre": "Julio Cortázar", "nacionalidad": "Argentina"},
    {"id": 2, "nombre": "Ricardo Piglia", "nacionalidad": "Argentina"},
    {"id": 3, "nombre": "Adolfo Bioy Casares", "nacionalidad": "Argentina"},
    {"id": 4, "nombre": "Silvina Ocampo", "nacionalidad": "Argentina"},
    {"id": 5, "nombre": "Ernesto Sabato", "nacionalidad": "Argentina"},
)

_LIBROS: Final[tuple[dict[str, Any], ...]] = (
    {
        "id": 1,
        "isbn": "978-950-00-0001-1",
        "titulo": "Rayuela",
        "precio": Decimal("25000.00"),
        "stock": 10,
        "editorial_id": 1,
        "genero_id": 1,
    },
    {
        "id": 2,
        "isbn": "978-950-00-0002-8",
        "titulo": "Bestiario",
        "precio": Decimal("18000.00"),
        "stock": 6,
        "editorial_id": 1,
        "genero_id": 2,
    },
    {
        "id": 3,
        "isbn": "978-950-00-0003-5",
        "titulo": "La invención de Morel",
        "precio": Decimal("20000.00"),
        "stock": 5,
        "editorial_id": 1,
        "genero_id": 1,
    },
    {
        "id": 4,
        "isbn": "978-950-00-0004-2",
        "titulo": "Respiración artificial",
        "precio": Decimal("27000.00"),
        "stock": 7,
        "editorial_id": 2,
        "genero_id": 1,
    },
    {
        "id": 5,
        "isbn": "978-950-00-0005-9",
        "titulo": "El túnel",
        "precio": Decimal("19500.00"),
        "stock": 3,
        "editorial_id": 1,
        "genero_id": 1,
    },
    {
        "id": 6,
        "isbn": "978-950-00-0006-6",
        "titulo": "Los que aman, odian",
        "precio": Decimal("21000.00"),
        "stock": 4,
        "editorial_id": 1,
        "genero_id": 1,
    },
)

_LIBRO_AUTOR: Final[tuple[dict[str, Any], ...]] = (
    {"libro_id": 1, "autor_id": 1, "rol": "autor", "orden": 1},
    {"libro_id": 2, "autor_id": 1, "rol": "autor", "orden": 1},
    {"libro_id": 3, "autor_id": 3, "rol": "autor", "orden": 1},
    {"libro_id": 4, "autor_id": 2, "rol": "autor", "orden": 1},
    {"libro_id": 5, "autor_id": 5, "rol": "autor", "orden": 1},
    {"libro_id": 6, "autor_id": 3, "rol": "coautor", "orden": 1},
    {"libro_id": 6, "autor_id": 4, "rol": "coautor", "orden": 2},
)

_CLIENTES: Final[tuple[dict[str, Any], ...]] = (
    {"id": 1, "nombre": "Ana Gómez", "email": "ana.gomez@example.com"},
    {"id": 2, "nombre": "Bruno Díaz", "email": "bruno.diaz@example.com"},
    {
        "id": 3,
        "nombre": "Carla Fernández",
        "email": "carla.fernandez@example.com",
    },
)

_PERFILES: Final[tuple[dict[str, Any], ...]] = (
    {
        "id": 1,
        "cliente_id": 1,
        "telefono": "+54 11 5555-0001",
        "direccion": "Av. Corrientes 1234, CABA",
    },
    {
        "id": 2,
        "cliente_id": 3,
        "telefono": "+54 11 5555-0003",
        "direccion": "Calle 50 456, La Plata",
    },
)

_VENTAS: Final[tuple[dict[str, Any], ...]] = (
    {
        "id": 1,
        "cliente_id": 2,
        "fecha": datetime(2026, 1, 15, 12, 0, 0, tzinfo=timezone.utc),
        "total": Decimal("77000.00"),
    },
)

_RENGLONES: Final[tuple[dict[str, Any], ...]] = (
    {
        "id": 1,
        "venta_id": 1,
        "libro_id": 1,
        "cantidad": 2,
        "precio_unitario": Decimal("25000.00"),
    },
    {
        "id": 2,
        "venta_id": 1,
        "libro_id": 4,
        "cantidad": 1,
        "precio_unitario": Decimal("27000.00"),
    },
)

#: Dataset completo, inmutable y en orden de dependencias.
DATASET: Final[Mapping[str, tuple[dict[str, Any], ...]]] = MappingProxyType(
    {
        "editorial": _EDITORIALES,
        "genero": _GENEROS,
        "autor": _AUTORES,
        "libro": _LIBROS,
        "libro_autor": _LIBRO_AUTOR,
        "cliente": _CLIENTES,
        "perfil_cliente": _PERFILES,
        "venta": _VENTAS,
        "renglon_venta": _RENGLONES,
    }
)

_CAMPOS_MONETARIOS: Final[dict[str, tuple[str, ...]]] = {
    "libro": ("precio",),
    "venta": ("total",),
    "renglon_venta": ("precio_unitario",),
}


# ---------------------------------------------------------------------------
# Autoverificación del dataset (antes de cualquier escritura)
# ---------------------------------------------------------------------------


def validar_dataset(
    datos: Mapping[str, Sequence[Mapping[str, Any]]] | None = None,
) -> list[str]:
    """Devuelve las incoherencias del dataset (lista vacía si es válido).

    Se ejecuta antes de abrir cualquier conexión: si el dataset se edita de
    forma inconsistente, el comando aborta con código 1 sin tocar la base.
    Verifica precios y cantidades positivas, stock no negativo, total
    coherencia con los renglones, roles y órdenes aceptados por los CHECK de
    ``libro_autor``, tipos ``Decimal``/``datetime`` con zona horaria y que
    toda clave foránea apunte a un id presente en el propio dataset.
    """
    conjunto: Mapping[str, Sequence[Mapping[str, Any]]] = (
        DATASET if datos is None else datos
    )
    errores: list[str] = []

    for tabla in ORDEN_TABLAS:
        if tabla not in conjunto:
            errores.append(f"falta la tabla '{tabla}' en el dataset")
        elif not conjunto[tabla]:
            errores.append(f"la tabla '{tabla}' no tiene filas")
    if errores:
        return errores

    ids: dict[str, set[int]] = {}
    for tabla in ORDEN_TABLAS:
        if tabla == "libro_autor":
            continue
        vistos: set[int] = set()
        for fila in conjunto[tabla]:
            identificador = fila.get("id")
            if not isinstance(identificador, int) or identificador < 1:
                errores.append(f"{tabla}: id inválido {identificador!r}")
            elif identificador in vistos:
                errores.append(f"{tabla}: id duplicado {identificador}")
            else:
                vistos.add(identificador)
            for campo in _CAMPOS_MONETARIOS.get(tabla, ()):
                valor = fila.get(campo)
                if not isinstance(valor, Decimal):
                    errores.append(
                        f"{tabla} id {identificador}: '{campo}' debe ser Decimal, "
                        f"no {type(valor).__name__}"
                    )
        ids[tabla] = vistos

    for fila in conjunto["libro"]:
        identificador = fila.get("id")
        precio = fila.get("precio")
        stock = fila.get("stock")
        if isinstance(precio, Decimal) and precio <= 0:
            errores.append(f"libro id {identificador}: 'precio' debe ser > 0")
        if not isinstance(stock, int) or stock < 0:
            errores.append(f"libro id {identificador}: 'stock' debe ser >= 0")
        if fila.get("editorial_id") not in ids["editorial"]:
            errores.append(
                f"libro id {identificador}: editorial_id {fila.get('editorial_id')!r} "
                "no existe en el dataset"
            )
        genero_id = fila.get("genero_id")
        if genero_id is not None and genero_id not in ids["genero"]:
            errores.append(
                f"libro id {identificador}: genero_id {genero_id!r} no existe en el dataset"
            )

    pares_autorias: set[tuple[int, int]] = set()
    for fila in conjunto["libro_autor"]:
        libro_id = fila.get("libro_id")
        autor_id = fila.get("autor_id")
        rol = fila.get("rol")
        orden = fila.get("orden")
        if libro_id not in ids["libro"]:
            errores.append(
                f"libro_autor: libro_id {libro_id!r} no existe en el dataset"
            )
        if autor_id not in ids["autor"]:
            errores.append(
                f"libro_autor: autor_id {autor_id!r} no existe en el dataset"
            )
        if rol not in ROLES_VALIDOS:
            errores.append(
                f"libro_autor ({libro_id}, {autor_id}): rol {rol!r} fuera de "
                f"{sorted(ROLES_VALIDOS)}"
            )
        if not isinstance(orden, int) or orden < 1:
            errores.append(
                f"libro_autor ({libro_id}, {autor_id}): 'orden' debe ser >= 1"
            )
        clave = (libro_id, autor_id)
        if clave in pares_autorias:
            errores.append(f"libro_autor: autoría duplicada {clave}")
        pares_autorias.add(clave)

    for fila in conjunto["perfil_cliente"]:
        if fila.get("cliente_id") not in ids["cliente"]:
            errores.append(
                f"perfil_cliente id {fila.get('id')}: cliente_id "
                f"{fila.get('cliente_id')!r} no existe en el dataset"
            )

    precios_libro = {
        fila.get("id"): fila.get("precio") for fila in conjunto["libro"]
    }
    for fila in conjunto["renglon_venta"]:
        identificador = fila.get("id")
        cantidad = fila.get("cantidad")
        precio_unitario = fila.get("precio_unitario")
        if fila.get("venta_id") not in ids["venta"]:
            errores.append(
                f"renglon_venta id {identificador}: venta_id "
                f"{fila.get('venta_id')!r} no existe en el dataset"
            )
        if fila.get("libro_id") not in ids["libro"]:
            errores.append(
                f"renglon_venta id {identificador}: libro_id "
                f"{fila.get('libro_id')!r} no existe en el dataset"
            )
        if not isinstance(cantidad, int) or cantidad <= 0:
            errores.append(f"renglon_venta id {identificador}: 'cantidad' debe ser > 0")
        if isinstance(precio_unitario, Decimal) and precio_unitario <= 0:
            errores.append(
                f"renglon_venta id {identificador}: 'precio_unitario' debe ser > 0"
            )
        precio_catalogo = precios_libro.get(fila.get("libro_id"))
        if (
            isinstance(precio_unitario, Decimal)
            and isinstance(precio_catalogo, Decimal)
            and precio_unitario != precio_catalogo
        ):
            errores.append(
                f"renglon_venta id {identificador}: 'precio_unitario' no coincide "
                "con el precio del libro (RN-06)"
            )

    for fila in conjunto["venta"]:
        identificador = fila.get("id")
        fecha = fila.get("fecha")
        total = fila.get("total")
        if not isinstance(fecha, datetime) or fecha.tzinfo is None:
            errores.append(
                f"venta id {identificador}: 'fecha' debe ser datetime con zona horaria"
            )
        if fila.get("cliente_id") not in ids["cliente"]:
            errores.append(
                f"venta id {identificador}: cliente_id "
                f"{fila.get('cliente_id')!r} no existe en el dataset"
            )
        if isinstance(total, Decimal):
            if total < 0:
                errores.append(f"venta id {identificador}: 'total' debe ser >= 0")
            calculado = sum(
                (
                    Decimal(renglon.get("cantidad", 0))
                    * Decimal(renglon.get("precio_unitario", 0))
                    for renglon in conjunto["renglon_venta"]
                    if renglon.get("venta_id") == identificador
                ),
                Decimal("0.00"),
            )
            if total != calculado:
                errores.append(
                    f"venta id {identificador}: 'total' {total} no coincide con la "
                    f"suma de sus renglones ({calculado})"
                )
            if not any(
                renglon.get("venta_id") == identificador
                for renglon in conjunto["renglon_venta"]
            ):
                errores.append(
                    f"venta id {identificador}: no tiene renglones en el dataset"
                )

    return errores


# ---------------------------------------------------------------------------
# Carga transaccional
# ---------------------------------------------------------------------------


def _sqlstate(exc: BaseException) -> str | None:
    """Extrae el código SQLSTATE del error sin exponer el mensaje interno."""
    orig = getattr(exc, "orig", None)
    for candidato in (orig, getattr(orig, "__cause__", None)):
        if candidato is None:
            continue
        valor = getattr(candidato, "sqlstate", None) or getattr(
            candidato, "pgcode", None
        )
        if valor:
            return str(valor)
    return None


def _mensaje_error(exc: BaseException) -> str:
    """Traduce una falla a un mensaje propio, sin SQL ni trazas (RN-12)."""
    sqlstate = _sqlstate(exc)
    nombre_origen = type(getattr(exc, "orig", exc)).__name__

    if sqlstate == "42P01" or "UndefinedTable" in nombre_origen:
        return (
            "El esquema no existe en la base de datos indicada. Iniciá la "
            "aplicación al menos una vez (uvicorn app.main:app) para que el "
            "lifespan cree las tablas y volvé a ejecutar el seed."
        )
    if isinstance(exc, IntegrityError) or (sqlstate or "").startswith("23"):
        return (
            "La base contiene datos incompatibles con el dataset (claves "
            "naturales o referencias en conflicto). Se revirtió toda la carga: "
            "usá una base limpia."
        )
    if (
        isinstance(exc, (OperationalError, InterfaceError, OSError))
        or "Connection" in nombre_origen
        or "Password" in nombre_origen
        or "InvalidAuthorization" in nombre_origen
    ):
        return (
            "No se pudo conectar con la base de datos. Verificá que el servidor "
            "esté disponible y que DATABASE_URL sea correcta."
        )
    return (
        "No se pudieron cargar los datos iniciales. Se revirtió toda la carga; "
        "revisá el estado de la base y volvé a intentar."
    )


async def _cargar(
    session_factory,
    datos: Mapping[str, Sequence[Mapping[str, Any]]],
) -> dict[str, tuple[int, int]]:
    """Carga el dataset en una única transacción y alinea las secuencias.

    Devuelve, por tabla, ``(insertadas, ya_existían)``. Cualquier excepción
    revierte la transacción completa (``session.begin()``) y se propaga para
    que el CLI la traduzca a un mensaje propio.
    """
    resumen: dict[str, tuple[int, int]] = {}
    async with session_factory() as session:
        async with session.begin():
            for nombre in ORDEN_TABLAS:
                tabla = TABLAS[nombre]
                insertadas = 0
                for fila in datos[nombre]:
                    # ON CONFLICT DO NOTHING sin target: cubre la PK y todas
                    # las UNIQUE de la tabla (idempotencia total).
                    stmt = (
                        pg_insert(tabla)
                        .values(**dict(fila))
                        .on_conflict_do_nothing()
                        .returning(*tabla.primary_key.columns)
                    )
                    resultado = await session.execute(stmt)
                    insertadas += len(resultado.fetchall())
                resumen[nombre] = (insertadas, len(datos[nombre]) - insertadas)

            # Insertar ids explícitos NO avanza la secuencia en PostgreSQL:
            # se alinea al máximo cargado para que el próximo alta por API
            # obtenga un id nuevo y no choque con la PK del dataset.
            for nombre in TABLAS_CON_SECUENCIA:
                # El nombre de tabla es un literal de la lista constante de
                # este módulo (nunca entrada del usuario); el valor del setval
                # sale del MAX(id) de la propia tabla.
                await session.execute(
                    text(
                        "SELECT setval(pg_get_serial_sequence("
                        f"'{nombre}', 'id'), COALESCE(MAX(id), 1), true) "
                        f"FROM {nombre}"
                    )
                )
    return resumen


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _imprimir_resumen(
    resumen: dict[str, tuple[int, int]],
    datos: Mapping[str, Sequence[Mapping[str, Any]]],
) -> None:
    """Imprime el resumen por tabla y los ids cargados, sin credenciales."""
    total_insertadas = sum(insertadas for insertadas, _ in resumen.values())
    total_existentes = sum(existentes for _, existentes in resumen.values())

    print("Datos iniciales (seed) — librería")
    print("")
    print(f"{'Tabla':<16}{'Insertadas':>12}{'Ya existían':>14}")
    print(f"{'-' * 16}{'-' * 12}{'-' * 14}")
    for nombre in ORDEN_TABLAS:
        insertadas, existentes = resumen[nombre]
        print(f"{nombre:<16}{insertadas:>12}{existentes:>14}")
    print(f"{'-' * 16}{'-' * 12}{'-' * 14}")
    print(f"{'Total':<16}{total_insertadas:>12}{total_existentes:>14}")
    print("")
    print("Ids del dataset:")
    for nombre in ORDEN_TABLAS:
        if nombre == "libro_autor":
            pares = ", ".join(
                f"(libro {fila['libro_id']}, autor {fila['autor_id']})"
                for fila in datos[nombre]
            )
        else:
            pares = ", ".join(str(fila["id"]) for fila in datos[nombre])
        print(f"  {nombre}: {pares}")
    print("")
    print("Secuencias alineadas con el máximo id cargado de cada tabla.")


async def main(
    datos: Mapping[str, Sequence[Mapping[str, Any]]] | None = None,
) -> int:
    """Ejecuta el seed y devuelve el código de salida (0 éxito, 1 error)."""
    conjunto: Mapping[str, Sequence[Mapping[str, Any]]] = (
        DATASET if datos is None else datos
    )

    # 1) Autoverificación del dataset: antes de cualquier conexión.
    errores = validar_dataset(conjunto)
    if errores:
        print(
            "Datos iniciales (seed): el dataset es inconsistente; "
            "no se escribió nada."
        )
        for error in errores:
            print(f"  - {error}")
        return 1

    # 2) Configuración y motor. La importación de app.core.config valida
    # DATABASE_URL al importarse (fail-fast de CH-01), por eso es perezosa:
    # así una variable faltante se informa con mensaje propio y no con traza.
    try:
        from app.core.config import get_database_url

        get_database_url()
        from app.core.database import create_engine, create_session_factory
    except RuntimeError as exc:
        print(f"Datos iniciales (seed): {exc}")
        return 1

    try:
        engine = create_engine()
    except Exception:  # noqa: BLE001 - URL mal formada: mensaje propio, sin traza
        print(
            "Datos iniciales (seed): DATABASE_URL no es válida para el motor "
            "asíncrono del proyecto (esquema esperado postgresql+asyncpg://)."
        )
        return 1

    try:
        resumen = await _cargar(create_session_factory(engine), conjunto)
    except Exception as exc:  # noqa: BLE001 - toda falla se traduce a mensaje propio
        print(f"Datos iniciales (seed): {_mensaje_error(exc)}")
        return 1
    finally:
        await engine.dispose()

    _imprimir_resumen(resumen, conjunto)
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
