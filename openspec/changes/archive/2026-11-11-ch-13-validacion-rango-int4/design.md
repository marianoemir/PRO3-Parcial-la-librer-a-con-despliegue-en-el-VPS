# Design

## Context

CH-04 introdujo `_INT4_MAX = 2147483647` localmente en `app/modules/{editoriales,generos,autores}/router.py`, aplicando `Path(le=_INT4_MAX)` y `Query(ge=0, le=_INT4_MAX)` en listados para evitar `DataError` (overflow PostgreSQL `integer`/int4) y responder 422 sin exponer internos (RN-12). Los módulos `libros` y `clientes` no aplican aún el tope superior en path ids ni en `offset`. El módulo `ventas` existe en el repo solo como stubs de CH-02 (sin endpoints/DTOs de negocio implementados) y CH-07 permanece pendiente; **queda excluido del alcance de este change** por dirección vigente (ver constancia en `proposal.md`). La verificación HTTP realizada en este entorno (2026-11-11, contra app en `127.0.0.1:8000`, `GET /health/live` → 200) mostró que los **body ids de libros ya responden 422** en el estado actual:

- `POST /libros/` con `editorial_id: 99999999999` → `422` (validación de schema; `app/modules/libros/schemas.py` ya declara `Field(..., le=2147483647)` en `editorial_id/genero_id/autor_id` de create/update y `autor_id` anidado).
- `PATCH /libros/1` con `{"editorial_id": 99999999999}` → `422`.

No fue posible forzar por HTTP un `DataError` de path/query en libros/clientes porque la instancia en ejecución puede diferir del código fuente actual del repo; por análisis de código, `app/modules/libros/router.py` declara `libro_id: Annotated[int, Path()]` (sin `le`) y `offset: Annotated[int, Query(ge=0)]` (sin `le`), y `app/modules/clientes/router.py` declara ids de ruta sin `le` y `offset` sin `le` en `GET /{cliente_id}/ventas`, por lo que valores como `99999999999` pueden llegar al handler/DB y producir `DataError`/500 en una ejecución alineada a este código. El diseño debe cubrir explícitamente ambos casos (endurecer donde falte, mantener/normalizar donde ya exista) sin cambiar semántica de negocio.

Restricciones: sin consultas previas de existencia para body/path ids (RT-02/DD-04), sin texto interno de DB (RN-12), sin migraciones, sin renombrar tablas/columnas, sin `extra="forbid"` ni cambio de `PATCH {}` en este change.

## Goals / Non-Goals

**Goals:**
- Garantizar 422 declarativo (FastAPI/Pydantic) para overflow `int4` en path ids, `offset`/listados relevantes y body ids de `libros` y `clientes`, sin ejecutar lógica de negocio ni consultas SQL cuando el valor ya es inválido por rango.
- Preservar `id == 0` → 404 en recursos donde el service hoy resuelve inexistencia (no introducir `ge=1` en path ids salvo que el contrato actual ya lo exija).
- Centralizar `INT4_MAX` en `app/core` y definir estrategia de adopción consistente para los módulos en alcance.
- Definir escenarios verificables y casos `.http` planificados para `libros` y `clientes`, incluyendo “sin internals de DB”.
- Dejar constancia explícita (forward-looking) de que el change propio de ventas (CH-07) debe nacer con límites `int4` desde su origen.

**Non-Goals:**
- Implementar o modificar `app/modules/ventas/` ni definir delta de spec/tareas `.http` de ventas en este change (excluido; responsabilidad de CH-07).
- Cambiar reglas de negocio (descuento de stock, unicidades, FKs), respuestas 409, ni contratos funcionales existentes más allá de la validación de rango.
- Introducir `extra="forbid"`, modificar semántica de PATCH vacío, ni agregar DELETE/PATCH de ventas.
- Apply, commit, o modificar `openspec/changes/archive/`.

## Decisions

### 1. Constante compartida en `app/core`
- **Decisión:** crear `app/core/constants.py` (o equivalente explícito en `app/core`) con `INT4_MAX: int = 2147483647` y reutilizarla desde routers/schemas de módulos afectados; opcionalmente actualizar los tres routers de CH-04 para importar la misma constante sin alterar comportamiento (refactor mecánico en apply).
- **Rationale:** elimina duplicación (`_INT4_MAX` repetido), evita divergencias futuras y hace auditable el límite de contrato (PostgreSQL `integer` int4, usado por ids/offsets en este proyecto).
- **Alternativas:** mantener por router (descartada: propensa a drift) o definir en `database.py` (descartada: mezcla concerns; `config.py` es de env, `database.py` de engine/session).

### 2. Path ids: `Path(le=INT4_MAX)` sin forzar `ge=1`
- **Decisión:** declarar `Annotated[int, Path(le=INT4_MAX)]` en `libro_id` y `cliente_id` (y cualquier path id equivalente en los módulos en alcance). No agregar `ge=1` en rutas donde hoy `0` debe devolver 404 (p.ej. detalle libro, per CH-05; consistente en clientes).
- **Rationale:** `0` es un entero válido para el tipo `int4` pero semánticamente inexistente; el 404 proviene del service/lookup, no de un overflow. Forzar 422 para `0` cambiaría comportamiento y rompería la decisión registrada. Overflow (`> INT4_MAX`) sí debe ser 422 antes del handler.
- **Trade-off:** un valor negativo muy grande (p.ej. `< -INT4_MAX-1`) también puede ser inválido para int4; si se detecta en apply, puede añadirse `ge=-2147483648` o una política explícita, pero el alcance requerido se centra en `> INT4_MAX` (ej. `99999999999`). Se documenta como verificación de borde en tasks.

### 3. Offset (y limit donde corresponda): tope superior `le=INT4_MAX`
- **Decisión:** en `GET /libros/` y `GET /clientes/{id}/ventas`, declarar `offset: Annotated[int, Query(ge=0, le=INT4_MAX)] = 0`. No relajar `limit` existente (RN-10, 1–100, defecto 20 donde ya aplica).
- **Rationale:** `offset` se envía a SQL como parámetro; valores fuera de int4 provocan `DataError`. `limit` ya está acotado a 100 en módulos existentes, pero se valida coherencia en diseño para evitar regresiones.

### 4. Body ids: `Field(..., le=INT4_MAX)` en schemas, sin pre-check de existencia
- **Decisión:** asegurar `ge=1, le=INT4_MAX` en campos de id de cuerpo en alcance: `LibroCreate/LibroUpdate` (`editorial_id`, `genero_id`, `autor_id` en lista). La ausencia de la entidad referenciada **dentro de rango** sigue produciendo 409 vía traducción de `IntegrityError` en service (RT-02/DD-04).
- **Rationale:** cumple 422 para overflow sin ejecutar escritura ni `SELECT` de existencia; preserva la responsabilidad de la base para FKs válidas en rango pero inexistentes. En libros el contrato ya refleja este tope (verificado por HTTP 422), por lo que apply será idempotente/normalizador (posible refactor a constante compartida).

### 5. Ventas excluido (constancia para CH-07)
- **Decisión:** `app/modules/ventas/` (stubs, CH-07 pendiente) queda fuera del alcance de CH-13: sin cambios de código, sin delta de spec `ventas-renglones` y sin tareas/casos `.http` de ventas en este change. La constancia contractual de que **ventas debe nacer con límites `int4` desde su propio change** queda registrada en `proposal.md` y `CHANGES.md`.
- **Rationale:** el módulo no está implementado; aplicar parches parciales sobre stubs no aporta valor verificable y mezclaría alcance. La corrección debe materializarse en CH-07 con path ids (`GET /ventas/{id}`), `offset`/`limit` de listados (`GET /ventas/`), body ids (`cliente_id`, `renglones[].libro_id`), `id==0`→404, 422 sin internals/pre-check (RN-12, RT-02), y sin stock discount ni endpoints no previstos.

### 6. Especificación de escenarios y evidencia
- **Decisión:** cada capability afectada en alcance (`libros-autorias`, `clientes-perfil`) recibe al menos el escenario “id u offset fuera de rango” con: valor `> 2147483647` (ej. `99999999999`) → 422, cuerpo de error sin `Traceback`, sin `DataError`, sin nombres de tablas/constraints/SQL internos (RN-12), y sin ejecutar handler/consulta cuando sea validación declarativa. Mantener escenario de `id == 0` → 404 donde ya exista.
- **`.http` planificados (apply):** `test/ch13-libros-rango-int4.http`, `test/ch13-clientes-rango-int4.http`.

## Risks / Trade-offs

- **[Riesgo] Divergencia entre instancia en ejecución y repo** → La verificación HTTP confirmó 422 en body ids de libros pero no pudo demostrar 500 en path/offset en la instancia actual. **Mitigación:** basar corrección en análisis de código + patrón CH-04; tasks exigen verificación post-apply con `.http` y observación de que no hay consulta/handler en overflow.
- **[Riesgo] `id == 0` mal interpretado como overflow** → **Mitigación:** decisión explícita de no usar `ge=1` en path; escenario de regresión 404 para `0`.
- **[Riesgo] Cambio cosmético en CH-04 routers al centralizar constante** → **Mitigación:** solo refactor de import/valor idéntico; verificación de no-regresión de editoriales/generos/autores.
- **[Riesgo] Ventas implementado sin límites int4 en CH-07** → **Mitigación:** constancia explícita en proposal/CHANGES.md y en este design para que el apply de CH-07 incluya path/query/body ids, 422 sin internals y sin pre-check desde su nacimiento.
- **[Trade-off] Validación en schema vs router** → Body ids pertenecen al contrato de entrada (schema/Pydantic/FastAPI), coherente con el stack; path/query se validan en `Path/Query`.

## Migration Plan

- Sin migraciones de base. Rollback: revertir cambios de validación en routers/schemas/core y restaurar constantes locales si se hubieran movido.
- Orden sugerido en apply: introducir constante en `app/core` → actualizar routers/schemas de libros/clientes → alinear CH-04 modules (opcional pero recomendado) → ejecutar `.http` de libros/clientes y revisar respuestas.

## Open Questions

- **`extra="forbid"` y `PATCH {}` vacío:** explícitamente fuera de alcance por instrucción; permanecen como comportamientos actuales.
- **Límite inferior de path ids:** el alcance pide cubrir `> INT4_MAX`; valores negativos extremos no fueron solicitados explícitamente. Si se observa `DataError` por underflow en apply, se añadirá `ge=-2147483648` como extensión menor dentro del mismo criterio RN-12/422.
