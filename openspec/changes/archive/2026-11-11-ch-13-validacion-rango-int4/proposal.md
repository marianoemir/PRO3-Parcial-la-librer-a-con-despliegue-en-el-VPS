# Proposal

## Why

CH-04 corrigió la validación de rango `int4` (422 para ids/offsets fuera de rango, sin filtrar internos de la base) en los módulos de referencia `editoriales`, `generos` y `autores`. El mismo defecto es transversal y permanecía en los módulos `libros` y `clientes`: un `id` u `offset` fuera de rango `int4` puede llegar a la capa de base y producir un `DataError` (500) con texto interno, violando RN-12 y la expectativa de 422 (RT-01) establecida en CH-04. Este change propone la rectificación para cerrar esa brecha en CH-05/CH-06.

**Rectificación registrada (CHANGES.md):** este change corrige el bug transversal de validación de rango `int4` en los módulos implementados en CH-05 (`libros-autorias`) y CH-06 (`clientes-perfil`). El módulo `ventas` (CH-07) queda fuera del alcance de este change y debe incorporar estos límites desde su propio change (ver constancia abajo).

## What Changes

- **Path ids (`le=2147483647`, `INT4_MAX`)** en routers de `libros` y `clientes`: `GET/PATCH /libros/{id}`, `GET/PATCH /clientes/{id}`, `POST /clientes/{id}/perfil`, `GET /clientes/{id}/ventas`. Un valor fuera de rango responde 422 sin ejecutar el handler ni consultar la base. **`id == 0` sigue respondiendo 404** (decisión vigente de CH-05: el path acepta el valor y el service resuelve recurso inexistente), preservando el comportamiento observable actual.
- **Query de listados**: agregar límite superior `le=INT4_MAX` a `offset` (y validar coherencia de `limit` donde aplique) en `GET /libros/` y `GET /clientes/{id}/ventas`. `limit` mantiene las restricciones RN-10 existentes (1–100, defecto 20) cuando ya están definidas.
- **Body ids validados en schemas (422, sin consulta previa)**: `editorial_id`, `genero_id`, `autor_id` (en `LibroCreate`/`LibroUpdate` y DTOs anidados de autorías). Tratamiento propuesto: `Field(ge=1, le=INT4_MAX)` (o equivalente) en el contrato de entrada para responder 422 por validación declarativa. **No se consulta existencia antes de escribir** (RT-02/DD-04, regla dura del enunciado); las FK inexistentes dentro de rango siguen traduciéndose a 409 por `IntegrityError` como hoy.
- **Ubicación compartida de la constante**: mover/centralizar `INT4_MAX` (hoy repetido como `_INT4_MAX` en routers de editoriales/generos/autores) a `app/core` para reutilización transversal, con decisión de diseño documentada.
- **Specs**: agregar escenario “id u offset fuera de rango” (422, sin internals de DB, RN-12) en las capacidades afectadas (`libros-autorias`, `clientes-perfil`).
- **Pruebas `.http` planificadas**: definir casos en `test/` (a crear en apply) que cubran path id, offset/limit y body ids fuera de rango para `libros` y `clientes`.
- **Documentación de rectificación**: nota explícita en `CHANGES.md` y en los artefactos del change indicando la corrección transversal respecto de CH-05/CH-06 y la constancia de exclusión de ventas.

## Constancia: ventas excluido de este change (debe nacer con límites int4 desde su propio change)

El módulo `app/modules/ventas/` existe en el repo solo como stubs de CH-02 (`router.py`, `schemas.py`, `service.py` sin endpoints ni DTOs de negocio implementados) y CH-07 (`ventas-renglones`) permanece pendiente. Por dirección vigente, **`ventas` queda excluido del alcance de este change** (sin delta de spec ni tareas/artefactos de implementación aquí).

**El change propio de ventas (CH-07 / capability `ventas-renglones`) debe nacer con los límites `int4` desde su origen**, incorporando al menos:
- **Path ids**: `GET /ventas/{id}` con `Path(le=2147483647, INT4_MAX)`; `id == 0` → 404 (inexistencia resuelta por el service), overflow → 422 sin ejecutar handler ni consultar la base.
- **Query de listados**: `GET /ventas/` con `offset` `Query(ge=0, le=INT4_MAX)` y `limit` según RN-10 (`ge=1, le=100`, defecto 20); overflow de `offset` → 422 sin ejecutar consulta ni exponer internals (RN-12).
- **Body ids validados en schemas (422, sin consulta previa)**: `cliente_id` y `renglones[].libro_id` en `VentaCreate`/renglones con `Field(ge=1, le=INT4_MAX)` (o equivalente). **No se consulta existencia antes de escribir** (RT-02/DD-04); referencias inexistentes dentro de rango se traducen según contrato vigente (409 por `IntegrityError`) sin pre-check.
- **Sin DELETE/PATCH de ventas** (RN-08/DD-02) salvo que el contrato lo incorpore explícitamente en el futuro; este change no los agrega.

Esta definición debe materializarse en el proposal/design/specs/tasks y pruebas `.http` del change de ventas, no como alcance retroactivo de CH-13.

## Capabilities

### New Capabilities

- Ninguna (la capacidad es transversal sobre contratos ya existentes).

### Modified Capabilities

- `libros-autorias`: validación de rango `int4` en path ids, query `offset` y body ids (`editorial_id`, `genero_id`, `autor_id`) con 422 y sin exponer internos.
- `clientes-perfil`: validación de rango `int4` en path ids (`cliente_id` en detalle, patch, perfil y ventas) y query `offset/limit` del listado de ventas del cliente.

## Impact

- **Código (en apply, no en este delivery)**: `app/core/` (constante compartida), `app/modules/libros/{router.py,schemas.py}`, `app/modules/clientes/router.py`, y potencial alineación de `app/modules/{editoriales,generos,autores}/router.py` para importar la constante común sin cambiar comportamiento. **Sin cambios en `app/modules/ventas/` en este change.**
- **APIs afectadas (alcance CH-13)**: `GET /libros/`, `GET|PATCH /libros/{id}`, `GET|PATCH /clientes/{id}`, `POST /clientes/{id}/perfil`, `GET /clientes/{id}/ventas`.
- **APIs de ventas (fuera de alcance, constancia para CH-07)**: `GET /ventas/`, `GET /ventas/{id}` y body de `POST /ventas/` (`cliente_id`, `renglones[].libro_id`) deberán nacer con límites int4 en el change propio de ventas.
- **Reglas/casos**: RN-10, RN-12, RT-01, RT-02, RT-05; refuerza C-01 (422 sin ejecutar handler para parámetros inválidos) extendiéndolo a overflow `int4` y a queries/body ids en módulos en alcance; no modifica semántica de 404/409 existente.
- **Fuera de alcance**: módulo `ventas`/CH-07 (excluido aquí, ver constancia), no implementar descuento de stock (pregunta abierta §1), no agregar `extra="forbid"` ni cambiar comportamiento de `PATCH {}` vacío, no introducir DELETE/PATCH de ventas ni endpoints fuera de la tabla de referencia, no renombrar/quitar tablas/columnas, no migraciones, no apply/commit en este delivery.
- **Dependencias**: referencia CH-04 archivado (`2026-11-08-ch-04-crud-editoriales-generos-autores`) como patrón; coherencia con CH-05/CH-06 archivados. CH-07 deberá incorporar la constancia de límites int4 al implementarse.
