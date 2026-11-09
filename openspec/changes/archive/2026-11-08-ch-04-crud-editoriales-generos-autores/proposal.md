# Proposal

## Why

CH-02 publicó las tablas `editorial` (`nombre` UNIQUE), `genero` (`nombre` UNIQUE) y `autor` (sin restricciones extra) pero sin endpoints, y CH-05 ya necesita que esas filas existan para dar de alta libros con `editorial_id`, `genero_id` y `autores[].autor_id`. Sin este change el catálogo de referencia no se puede operar por HTTP, el caso C-04 (libro con editorial/autor inexistente → 409) no tiene cómo crear sus referencias válidas y CH-08 (seed) no puede dejar datos iniciales estables.

## What Changes

- Módulo `app/modules/editoriales/` con `schemas.py`, `service.py` y `router.py` (el `models.py` de CH-02 NO se modifica): `POST /editoriales/` (201/409/422), `GET /editoriales/` (200/422, paginado), `GET /editoriales/{id}` (200/404/422), `PATCH /editoriales/{id}` (200/404/409/422) y `GET /editoriales/{id}/libros` (200/404/422). El 409 del alta y del PATCH es el `UNIQUE` `uq_editorial_nombre` traducido por el service a mensaje propio (RN-12, DD-04), sin consultar existencia antes (RT-02) y sin exponer el nombre de la restricción.
- Módulo `app/modules/generos/`: `POST /generos/` (201/409/422), `GET /generos/` (200/422, paginado), `GET /generos/{id}` (200/404/422) y `GET /generos/{id}/libros` (200/404/422). El 409 es `uq_genero_nombre`. No se crea `PATCH /generos/{id}` porque la tabla de endpoints no lo declara (queda como pregunta abierta en `design.md`).
- Módulo `app/modules/autores/`: `POST /autores/` (201/422), `GET /autores/{id}` (200/404/422), `PATCH /autores/{id}` (200/404/422) y `GET /autores/{id}/libros` (200/404/422) con `rol` y `orden` de cada autoría. **No se declara ni se implementa 409 en autores**: `autor` no tiene UNIQUE, FK ni CHECK, así que no hay rechazo de negocio que traducir (PDF p. 4, "Sin restricciones extra"); la duda §(3) de `10_preguntas_abiertas.md` se cita como pendiente y no se resuelve inventando un 409.
- DTO separados de la tabla en cada módulo (`Create` sin `id`, `Update` solo con los campos escalares opcionales, `Read` de salida) y PATCH que aplica solo los campos enviados con `model_dump(exclude_unset=True)`. Los `Update` rechazan con `field_validator` el `null` explícito en los campos obligatorios de la tabla (422 de contrato).
- Todos los listados se paginan con `limit` 1–100 (defecto 20) y `offset` ≥ 0 con restricciones en `Query` (RN-10), incluidas las relaciones `/{id}/libros`, y responden 422 fuera de rango.
- Registro de los tres routers en `app/main.py` con `include_router`, junto a `health_router` y `libros_router`.
- Sin endpoints DELETE ni ningún otro fuera de las filas de editoriales/géneros/autores de la tabla de referencia (DD-02; pendiente §(5)).

## Capabilities

### New Capabilities

- `editoriales-generos-autores`: contrato observable de los recursos de referencia del catálogo (editoriales, géneros y autores): altas, listados paginados, detalles, corrección parcial de editorial/autor, listado de los libros de cada recurso y traducción de las unicidades de la base a 409 propio. Vive en `app/modules/{editoriales,generos,autores}/` y reutiliza sin modificar las tablas de `core-models`.

### Modified Capabilities

- Ninguna. `core-models` (esquema) y `libros-autorias` (libros) no cambian su comportamiento observable: este change solo publica endpoints sobre tablas ya existentes y lee libros ya expuestos.

## Impact

- **Código**: `app/modules/editoriales/{schemas,service,router}.py`, `app/modules/generos/{schemas,service,router}.py`, `app/modules/autores/{schemas,service,router}.py` y `app/main.py` (`include_router` de los tres routers). Los tres `models.py` de CH-02 quedan intactos (`git diff -- app/modules/*/models.py` vacío). No se toca `app/core/` ni el lifespan.
- **APIs**: 13 operaciones sobre `/editoriales`, `/generos` y `/autores` según la tabla de referencia (PDF p. 11-12; `06_funcionalidades.md`). No hay DELETE ni PATCH de géneros.
- **Fuera de alcance**: libros (CH-05, ya archivado), clientes/perfil (CH-06), ventas/renglones (CH-07), seed (CH-08), la batería `test/*.http` de C-01 a C-08 (CH-09; acá cada escenario se verifica con un `.http` TEMPORAL fuera de `test/` que NO se commitea), evidencia C-07/D (CH-12), Docker/VPS (CH-03/CH-10/CH-11). Pendientes sin resolver que se citan y NO se resuelven acá: `10_preguntas_abiertas.md` §(3) (`POST /autores/` sin 409) y §(5) (sin DELETE); más dos discrepancias registradas en `design.md` (la tabla del PDF no declara `GET /generos/{id}` pero `06_funcionalidades.md` y `CHANGES.md` sí; la tabla no declara `PATCH /generos/{id}` y no se crea).
- **Dependencias**: CH-02 (tablas `editorial`, `genero`, `autor` y los nombres exactos `uq_editorial_nombre` / `uq_genero_nombre`) y CH-05 (endpoints de libros, necesarios para verificar las relaciones `/{id}/libros`). Reglas que implementa: RN-10, RN-12, RT-01, RT-02, RT-05; decisiones DD-02, DD-04. Casos que habilita: C-04 (crear las referencias válidas del alta de libro); C-01 se verifica de forma puntual sobre los ids de ruta de estos módulos.
