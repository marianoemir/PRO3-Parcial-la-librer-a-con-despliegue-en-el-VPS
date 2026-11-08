# Proposal

## Why

CH-02 publicó `libro` y `libro_autor` con sus garantías (UNIQUE, FK, CHECK) pero sin endpoints: el catálogo no se puede operar por HTTP. Este change expone ese dominio con el alta con relaciones y las lecturas pedidas en ejercicios 3 a 5 del enunciado (PDF p. 7-8) y habilita CH-07 (ventas necesita libros) y CH-09 (casos C-01/C-02/C-04/C-07/C-08).

## What Changes

- Alta `POST /libros/` (201/409/422): recibe `LibroCreate` con `editorial_id`, `genero_id` (nulo permitido) y lista `autores` (`autor_id`, `rol`, `orden`); escribe libro y sus `LibroAutor` sin consultar existencia previa de ids (RT-02, DD-04) en transacción `session.add` -> `flush` -> relectura precargada -> `commit` (`rollback` ante `IntegrityError`); la base rechaza y el service traduce por `sqlstate` y nombre de restricción a 409 con mensaje propio sin texto de la base (RN-12). Cubre C-02 (ISBN repetido `uq_libro_isbn`), C-04 (editorial/género/autor inexistente por FK `23503`) y el mismo `autor_id` repetido en `autores` (PK `libro_autor` -> 409, decisión justificada en `design.md`).
- Listado `GET /libros/` (200/422): paginación `limit` 1-100 defecto 20 + `offset` >= 0 con restricciones en `Query` (RN-10) y filtros `titulo` (filtro por parte, case-insensitive, con parámetro ligado, RN-11) y `genero_id`, con `joinedload(Libro.editorial)` + `joinedload(Libro.genero)` y `order_by(Libro.id)` determinista, respondiendo `LibroListRead` con resúmenes locales de editorial y género definidos en `libros/schemas.py` sin importar DTOs de otros módulos. La búsqueda `' OR '1'='1` devuelve 200 con lista vacía (C-08).
- Detalle `GET /libros/{id}` (200/404/422) y corrección parcial `PATCH /libros/{id}` (200/404/409/422): detalle precargado con `joinedload` (editorial, género) y `selectinload(Libro.autorias).selectinload(LibroAutor.autor)` con número fijo de consultas que no crece con los autores (RT-04, C-07 parcial; evidencia completa en CH-12); `LibroRead` incluye en cada autoría `autor_id`, `rol`, `orden` y `autor` (`id`, `nombre`) para justificar la precarga. PATCH aplica solo campos enviados (`exclude_unset`) sobre escalares; `LibroUpdate` NO lleva `autores` y rechaza con `field_validator` el `null` explícito en `isbn`, `titulo`, `precio`, `stock` y `editorial_id` (422; `genero_id` sí admite `null`). Id no entero devuelve 422 sin ejecutar el handler (C-01).
- Módulo `app/modules/libros/` con `schemas.py`, `service.py` y `router.py` (`models.py` de CH-02 no se modifica) y registro del router en `app/main.py`.
- Sin endpoints fuera de las filas de `POST/GET/PATCH /libros/` de la tabla de endpoints de referencia (PDF p. 12; 06_funcionalidades.md). En particular: NO se crea DELETE (DD-02; pendiente `10_preguntas_abiertas.md` §(5)).

## Capabilities

### New Capabilities

- `libros-autorias`: contrato observable del catálogo de libros con autorías (alta con relaciones, listado paginado y búsqueda por título, detalle y PATCH parcial, precarga sin N+1, códigos RT-01 y errores RN-12). Vive en `app/modules/libros/` y reutiliza sin modificar `libro`/`libro_autor` de `core-models`.

### Modified Capabilities

- Ninguna. `core-models` (esquema) y `foundation` (lifespan/health) no cambian su comportamiento observable; este change solo consume sus garantías ya publicadas.

## Impact

- **Código**: `app/modules/libros/schemas.py` (`LibroCreate`/`LibroUpdate` sin `autores`/`LibroRead`/`LibroListRead` con DTO anidado de autoría y resúmenes `EditorialResumen`/`GeneroResumen`/`AutorResumen` locales, sin importar DTOs de otros módulos; `LibroUpdate` con `field_validator` que rechaza `null` explícito salvo `genero_id`), `app/modules/libros/service.py` (lógica, transacción `add`/`flush`/relectura/`commit` + `rollback`, traducción `IntegrityError` -> 409 por `sqlstate` (`23505`/`23503`/`23514`) y `constraint_name`, precarga con `joinedload`/`selectinload` y `order_by(Libro.id)` en listado), `app/modules/libros/router.py` (router delgado, `async def`, códigos 201/200/404/409/422) e `app/main.py` (importar modelos ya importados + `include_router` de libros, patrón de `health_router`). `app/modules/libros/models.py` NO se toca.
- **APIs**: `POST /libros/`, `GET /libros/`, `GET /libros/{id}`, `PATCH /libros/{id}` según tabla de referencia. No hay DELETE ni otros endpoints (DD-02).
- **Fuera de alcance**: CRUD de editoriales/géneros/autores (CH-04), clientes/perfil (CH-06), ventas/renglones (CH-07), seed (CH-08), casos `.http` C-01 a C-08 como batería (CH-09; acá cada escenario se verifica con su `.http` TEMPORAL fuera de `test/` que NO se commitea y pgAdmin Query Tool, no se crea la batería), evidencia C-07/D (CH-12), Docker/VPS (CH-03/CH-10/CH-11). Pendientes sin resolver: `10_preguntas_abiertas.md` §(4) (unicidad de `orden` dentro de un libro: NO se agrega UNIQUE `libro_id`+`orden`) y §(7) (índice de `autor_id`; ya implementado en CH-02, confirmación pendiente con cátedra), edición de autorías por PATCH ( `LibroUpdate` no lleva `autores`; dónde/cómo se editan queda como pregunta abierta NUEVA en `design.md`) y mismo `autor_id` repetido -> 409 frente a ventas con libro repetido -> 422 (RN-05; diferencia explícita en `design.md`, por confirmar con cátedra, no regla inventada).
- **Dependencias**: CH-02 (modelos `Libro`/`LibroAutor` y Constraints nombrados `uq_libro_isbn`, `ck_libro_precio_positivo`, `ck_libro_stock_no_negativo`, `ck_libro_autor_orden_minimo`, `ck_libro_autor_rol_valido`; PK compuesta `libro_autor` y FK sin nombre propio discriminables solo por `sqlstate`). Reglas que implementa: RN-01, RN-03, RN-10, RN-11, RN-12, RT-01, RT-02, RT-04; decisiones DD-01, DD-02, DD-04.
