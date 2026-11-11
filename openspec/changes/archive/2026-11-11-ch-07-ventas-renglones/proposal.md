# Proposal

## Why

Se necesita completar la épica de ventas del parcial implementando el alta y las lecturas de ventas con renglones anidados, asegurando que el servidor sea la única fuente de verdad para precios, fecha y total, y que las consultas respeten el patrón asincrónico sin N+1. Esto habilita los casos de validación de negocio C-05, C-06, C-07 (parcial) y D-07, sobre modelos ya definidos en CH-02 y sin alterar el contrato ya implementado de `GET /clientes/{id}/ventas` en CH-06.

## What Changes

- Implementar `POST /ventas/` en `app/modules/ventas/` con DTO anidado (`cliente_id` y `renglones[{libro_id, cantidad}]`) sin aceptar `precio_unitario`, `total` ni `fecha` (RN-04, RN-05).
- Validar en DTO que exista al menos un renglón y que no haya libros repetidos; validar límites `int4` (`INT4_MAX`) en ids/cantidad y devolver 422 en entradas fuera de contrato/rango (RN-10, RN-12, RT-01).
- Copiar `precio_unitario` desde `Libro`, calcular `total = Σ cantidad × precio_unitario` con `Decimal` cuantizado a 2 decimales y asignar `fecha` en el servidor con zona horaria; persistir venta y renglones en la misma transacción (RN-06, RN-07, DD-05).
- Traducir rechazos de integridad a 409 con mensaje propio sin pre-checks de existencia ni exposición de internos de la base (cliente/libro inexistente u otras FK/restricciones) (RN-12, RT-02, DD-04).
- Implementar `GET /ventas/{id}` y `GET /ventas/` con carga anticipada fija (`joinedload`/`selectinload`) para cliente, renglones y libro del renglón, paginación estable (`limit` 1–100 default 20, `offset >= 0`, orden por `id`) y respuesta `VentaRead` con la forma exacta del enunciado (RT-04).
- Agendar aviso simulado con `BackgroundTasks` (`await asyncio.sleep(0.5)` + log) después de responder el alta, pasando solo valores simples ya extraídos (id de venta, email del cliente) sin sesión/ORM (RT-03, D-07).
- Agregar casos de verificación HTTP en `test/ch07-ventas-*.http` (éxito, errores de negocio, bordes, evidencia N+1 con `SQL_ECHO=true` y evidencia de log D-07).

## Capabilities

### New Capabilities
- `ventas-renglones`: alta de ventas con renglones anidados y lecturas paginadas/detalle de ventas con precios copiados del catálogo, total calculado por el servidor, carga anticipada sin N+1 y aviso asincrónico diferido.

### Modified Capabilities
<!-- Ninguna. `GET /clientes/{id}/ventas` pertenece a CH-06 y no cambia su contrato/comportamiento. -->

## Impact

- **Código afectado**: `app/modules/ventas/{schemas.py,service.py,router.py}` y registro del router de ventas en `app/main.py` (si aún no está incluido). Reutiliza `app/modules/ventas/models.py` de CH-02 y `app/core/constants.py` (`INT4_MAX`) sin modificarlos.
- **APIs**: nuevos endpoints `POST /ventas/`, `GET /ventas/`, `GET /ventas/{id}`. Sin cambios en endpoints existentes, sin PATCH/DELETE de ventas (RN-08, DD-02).
- **Datos/reglas**: sin cambios de esquema ni constraints; se reutilizan tablas `venta` y `renglon_venta`. El posible desborde de `total NUMERIC(12,2)` por combinaciones extremas de cantidad/precio se trata como decisión de diseño del equipo (no RN del enunciado/KB) y se documenta en `design.md`.
- **Dependencias/sistemas**: FastAPI `BackgroundTasks`, logging estándar, SQLAlchemy async con `joinedload`/`selectinload`; verificación manual con `curl.exe`/`.http` contra uvicorn y PostgreSQL (no pytest).

**Cubre**: RN-04, RN-05, RN-06, RN-07, RN-08, RN-10, RN-12, RT-01, RT-02, RT-03, RT-04, RT-05, DD-02, DD-04, DD-05; casos C-05, C-06, C-07 (parcial) y D-07. **Fuera de alcance**: `GET /clientes/{id}/ventas` (CH-06), descuento de stock (pregunta abierta KB §1), PATCH/DELETE de ventas, cambios de modelos/constraints de CH-02, seed (CH-08), batería completa C (CH-09) y despliegue/evidencia VPS (CH-10/11/12).
