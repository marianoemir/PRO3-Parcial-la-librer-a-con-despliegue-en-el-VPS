# Design

## Context

Ver `proposal.md` (motivo) y `specs/editoriales-generos-autores/spec.md` (requisitos). Estado actual: CH-01 (`app/main.py` con lifespan y `create_all`, `app/core/database.py` con `expire_on_commit=False` y `get_session`), CH-02 (`editorial`, `genero` y `autor` ya publicados en `app/modules/{editoriales,generos,autores}/models.py`, con `schemas.py`/`service.py`/`router.py` como stubs) y CH-05 (`/libros` completo, incluida la creación de libros con `editorial_id`, `genero_id` y `autores`) archivados; `app/main.py` registra `health_router` y `libros_router`. Restricciones duras (AGENTS.md; el PDF y la KB prevalecen sobre cualquier skill): `async def` en todos los handlers, sin consultas previas de existencia en escrituras (RT-02/DD-04), sin texto de la base en errores (RN-12), sin SQL concatenado (RT-05), sin migraciones, sin DELETE (DD-02), estructura `app/modules/<módulo>/{models,schemas,service,router}.py` con DTO `Create`/`Update`/`Read`, lógica en el service que recibe la sesión por parámetro y router que solo delega.

## Goals / Non-Goals

**Goals:**
- Publicar los 13 endpoints de editoriales, géneros y autores de la tabla de referencia (PDF p. 11-12; `06_funcionalidades.md`), con los códigos RT-01 y las garantías de la base traducidas a mensajes propios.
- Dejar operables las referencias que CH-05 y CH-08 necesitan (`editorial_id`, `genero_id`, `autor_id`) y verificables las relaciones `/{id}/libros`.

**Non-Goals:**
- Modificar los tres `models.py` de CH-02 ni `app/core/`. Si faltara algo de esquema, se pide explícitamente abajo; hoy no falta nada.
- Libros (CH-05), clientes/perfil (CH-06), ventas (CH-07), seed (CH-08), batería `test/*.http` (CH-09), evidencia (CH-12), Docker/VPS.
- Ningún endpoint fuera de las filas de editoriales/géneros/autores de la tabla de referencia, en particular ningún DELETE ni `PATCH /generos/{id}`.

## Cobertura de códigos por endpoint

Cada código declarado en `proposal.md` tiene al menos un escenario verificable en `specs/editoriales-generos-autores/spec.md`. `n/a` = la tabla de referencia no lo declara y no se inventa.

| Endpoint | 201 | 200 | 404 | 409 | 422 |
|---|---|---|---|---|---|
| `POST /editoriales/` | alta válida | — | — | `uq_editorial_nombre` | cuerpo inválido |
| `GET /editoriales/` | — | listado paginado | — | — | `limit`/`offset` |
| `GET /editoriales/{id}` | — | detalle | inexistente | — | id no entero |
| `PATCH /editoriales/{id}` | — | parcial | inexistente | nombre de otra editorial | `null` explícito / contrato |
| `GET /editoriales/{id}/libros` | — | libros de la editorial / lista vacía | editorial inexistente | — | `limit`/`offset` / id no entero |
| `POST /generos/` | alta válida | — | — | `uq_genero_nombre` | cuerpo inválido |
| `GET /generos/` | — | listado paginado | — | — | `limit`/`offset` |
| `GET /generos/{id}` | — | detalle | inexistente | — | id no entero |
| `GET /generos/{id}/libros` | — | libros del género / lista vacía | género inexistente | — | `limit`/`offset` / id no entero |
| `POST /autores/` | alta válida (repetida incluida) | — | — | **n/a** (sin UNIQUE/FK/CHECK) | cuerpo inválido |
| `GET /autores/{id}` | — | detalle | inexistente | **n/a** | id no entero |
| `PATCH /autores/{id}` | — | parcial (nombre repetido incluido) | inexistente | **n/a** | `null` explícito / contrato |
| `GET /autores/{id}/libros` | — | libros con `rol` y `orden` / lista vacía | autor inexistente | **n/a** | `limit`/`offset` / id no entero |

Además, `DELETE` de los tres recursos y `PATCH /generos/{id}` están cubiertos con un escenario de **405** y verificación de que la fila no cambia (DD-02).

## Decisions

### Alcance de endpoints: lo que declara la tabla, con dos discrepancias documentadas

- **Por qué**: la tabla de endpoints (PDF p. 11-12) es el contrato de referencia y AGENTS.md prohíbe endpoints fuera de ella; `06_funcionalidades.md` y `CHANGES.md` son su transcripción operativa. Se implementan exactamente: `POST /editoriales/` (201/409/422), `GET /editoriales/` (200/422), `GET /editoriales/{id}` (200/404/422), `PATCH /editoriales/{id}` (200/404/409), `GET /editoriales/{id}/libros` (200/404); `POST /generos/` (201/409), `GET /generos/` (200), `GET /generos/{id}/libros` (200/404); `POST /autores/` (201/422), `GET`/`PATCH /autores/{id}` (200/404/422), `GET /autores/{id}/libros` (200/404, con `rol` y `orden`).
- **Discrepancia 1 — `GET /generos/{id}`**: la tabla del PDF (p. 11) NO lo declara (solo `GET /generos/` y `GET /generos/{id}/libros`), pero `06_funcionalidades.md` (fila `POST/GET | /generos/, /generos/{id} | 201/409; 200`) y `CHANGES.md` (CH-04: "`GET /generos/` + `GET /generos/{id}` (200)") sí. Se implementa como detalle simétrico al de editoriales y autores (200/404/422) porque los dos documentos operativos del proyecto lo declaran y su ausencia solo produciría un 404 de ruta que la tabla no prohíbe. No es una regla de negocio inventada: no agrega comportamiento de escritura ni códigos nuevos al catálogo. Si la cátedra confirma que no existe, se retira en un change separado (no se toca nada más).
- **Discrepancia 2 — `PATCH /generos/{id}`**: no está en la tabla del PDF ni en `06_funcionalidades.md` ni en `CHANGES.md`. **No se crea.** Consecuencia asumida y registrada como pregunta abierta: un género mal cargado no se puede corregir por HTTP (solo por SQL manual). Se prefiere dejarlo sin implementar antes que inventar un endpoint.
- **Códigos 422 no listados en algunas filas**: `PATCH /editoriales/{id}` (la tabla declara 200/404/409) y `POST /generos/` (201/409) reciben 422 cuando el cuerpo no cumple el contrato. No es una decisión de dominio: RT-01 fija que el 422 es el código del contrato incumplido y FastAPI lo produce en la validación declarativa antes del handler; la columna "Códigos" de la tabla no es exhaustiva (omite también el 422 de `GET /generos/`). Alternativa descartada: aceptar cuerpos inválidos para "respetar" la tabla — violaría RT-01 y escribiría datos que la base rechazaría.
- **Alternativa descartada**: un único módulo `referencias` con tres routers — rompe la estructura obligatoria de un módulo por recurso (`app/modules/<módulo>/…`, PDF p. 6: "Módulos mínimos: health, editoriales, generos, autores, libros, clientes y ventas").

### Router delgado y registro en `app/main.py`

- **Por qué**: la estructura obligatoria separa `router.py` (recibe, delega, declara la respuesta) de `service.py` (lógica, traducción de errores, precarga). El router no puede tener SQL ni `try/except` de base.
- **Cómo**: cada `router.py` declara `APIRouter(prefix="/editoriales" | "/generos" | "/autores", tags=[...])`, handlers `async def`, parámetros con `Annotated` (`Path()`, `Query(ge=1, le=100)`, `Query(ge=0)`) y `response_model` de salida. La sesión llega con `SessionDep = Annotated[AsyncSession, Depends(get_session)]`. `app/main.py` agrega tres `include_router` junto a `health_router` y `libros_router`, sin tocar el lifespan ni `create_all`.
- **Alternativa descartada**: registrar las rutas con `@app.get` en `main.py` — rompe la estructura por módulo y concentra lógica fuera del service.

### DTO por módulo, sin importar DTOs de otros módulos

- **Por qué**: el patrón del proyecto separa modelo de tabla de contrato (`Create`/`Update`/`Read`) y mantiene la frontera por módulo. CH-05 definió resúmenes locales (`EditorialResumen`, `GeneroResumen`, `AutorResumen`) dentro de `libros/schemas.py` justamente para no acoplar contratos entre módulos.
- **Cómo**:
  - `editoriales/schemas.py`: `EditorialCreate(nombre, pais)`, `EditorialUpdate(nombre?, pais?)`, `EditorialRead(id, nombre, pais)`, `LibroDeEditorialRead(id, isbn, titulo, precio, stock, genero_id)`.
  - `generos/schemas.py`: `GeneroCreate(nombre)`, `GeneroRead(id, nombre)`, `LibroDeGeneroRead(id, isbn, titulo, precio, stock, editorial_id)`. **No hay `GeneroUpdate`** porque no hay PATCH de géneros.
  - `autores/schemas.py`: `AutorCreate(nombre, nacionalidad)`, `AutorUpdate(nombre?, nacionalidad?)`, `AutorRead(id, nombre, nacionalidad)`, `LibroDeAutorRead(libro_id, isbn, titulo, precio, stock, rol, orden)`.
  - Ningún `Create` lleva `id` (Ejercicio 3, PDF p. 7). `precio` viaja como `Decimal` en la respuesta (nunca `float`), consistente con `Numeric(10,2)` del modelo.
  - Los DTO de salida de `/{id}/libros` exponen solo las columnas necesarias y NO anidan editorial/género: en "libros de una editorial" el `editorial_id` es el de la ruta (dato redundante) y se omite; en "libros de un género" se omite `genero_id` por la misma razón. Evita precargas innecesarias y mantiene el contrato mínimo verificable.
- **Alternativa descartada**: importar `LibroListRead` de `app/modules/libros/schemas.py` — acopla el contrato de editoriales/géneros/autores al de libros y arrastra resúmenes anidados que estas respuestas no necesitan. Se importan los **modelos** (`Libro`, `LibroAutor`), no los DTO, porque la consulta de la relación es inevitablemente sobre esas tablas (y `Editorial.libros`/`Genero.libros`/`Autor.autorias` ya las referencian desde CH-02).

### Escritura delegada a la base: `IntegrityError` → 409 propio (RN-12, RT-02, DD-04)

- **Por qué**: RN-12 exige que ningún error devuelva texto interno; RT-02/DD-04 prohíben consultar antes si el valor existe. Las unicidades `uq_editorial_nombre` y `uq_genero_nombre` las declara CH-02, así que se escribe y se traduce el rechazo.
- **Cómo (editoriales y géneros)**: el service hace `session.add(...)` → `await session.flush()` (detecta el UNIQUE dentro de la transacción) → `await session.commit()`. Ante `IntegrityError`, `await session.rollback()` y `HTTPException(409)` con mensaje propio. La traducción se hace por `sqlstate` (`23505` unique violation) y por el `constraint_name` exacto de `models.py`, leídos con `getattr` defensivo sobre `exc.orig` y `exc.orig.__cause__` (asyncpg expone `constraint_name` en la excepción original; el dialecto emulado de SQLAlchemy solo copia `sqlstate`/`pgcode`/`detail` — mismo hallazgo documentado en CH-05). Mapeo: `23505` + `uq_editorial_nombre` → `"Ya existe una editorial con ese nombre"`; `23505` + `uq_genero_nombre` → `"Ya existe un género con ese nombre"`; cualquier otro caso → 409 genérico `"Conflicto de datos en la base de datos"`. Nunca se usa `str(exc)`, ni subcadenas del mensaje, ni se devuelve el nombre de la restricción.
- **Por qué NO se declara 409 en autores**: `autor` tiene columnas `nombre` y `nacionalidad` sin UNIQUE, sin FK y sin CHECK (PDF p. 4: "Sin restricciones extra"; `04_modelo_de_datos.md` §autor). No existe rechazo de negocio que traducir, por lo que `POST /autores/` declara solo 201/422, tal como la tabla de referencia, y el service de autores **no** captura `IntegrityError` para convertirlo en 409: hacerlo crearía un código que el contrato no declara. Si la cátedra responde la duda §(3) agregando una unicidad, se implementa en un change separado (cambio de esquema incluido).
- **Alternativa descartada (para los tres módulos)**: `SELECT` previo y 409 "ya existe" armado a mano — viola RT-02/DD-04, crea TOCTOU y no es lo que la base garantiza.

### PATCH parcial con `exclude_unset` y rechazo de `null` explícito

- **Por qué**: el Ejercicio 3 (PDF p. 7) exige que el PATCH aplique solo los campos enviados. Sin `exclude_unset`, un `{"pais": "Uruguay"}` pisaría `nombre` con su default. `nombre`, `pais`, `nacionalidad` son `NOT NULL` en la tabla, así que un `null` explícito debe ser un 422 de contrato y no un 409/500 de base.
- **Cómo**: `EditorialUpdate` y `AutorUpdate` declaran los campos opcionales (`str | None = None`) y un `field_validator(..., mode="before")` que rechaza `None` explícito (mismo patrón que `LibroUpdate` de CH-05). El service hace `datos.model_dump(exclude_unset=True)`, aplica `setattr` solo de esas claves, `flush` → `commit`, y traduce el `IntegrityError` de editoriales igual que en el alta. El 404 lo produce el service cuando `session.get` devuelve `None`, antes de tocar campos.
- **Alternativa descartada**: `model_dump()` completo — pisa los campos no enviados; o PATCH con PUT semántico — la tabla declara `PATCH`, no `PUT`.

### Paginación RN-10 en todos los listados, incluidas las relaciones `/{id}/libros`

- **Por qué**: RN-10 dice literalmente "**Todo listado** se pagina con `limit` (de 1 a 100, por defecto 20) y `offset` (desde 0)" y su garante es "restricciones en `Query`; 422". Los endpoints `GET /editoriales/{id}/libros`, `GET /generos/{id}/libros` y `GET /autores/{id}/libros` son listados, y `GET /generos/` también. La columna "Cuerpo" de la tabla solo marca `limit, offset` en `GET /editoriales/`, pero esa columna no enumera query params de forma exhaustiva (el mismo `GET /libros/` sí los lista y `GET /ventas/` también), y omitir la paginación devolvería respuestas de tamaño no acotado.
- **Cómo**: en los cinco listados (`/editoriales/`, `/generos/`, `/editoriales/{id}/libros`, `/generos/{id}/libros`, `/autores/{id}/libros`) el router declara `limit: Annotated[int, Query(ge=1, le=100)] = 20` y `offset: Annotated[int, Query(ge=0)] = 0`; el service aplica `.limit(limit).offset(offset)` sobre un `order_by` determinista. Fuera de rango → 422 antes del handler. El efecto observable adicional (truncado por defecto a 20) queda declarado en la spec.
- **Alternativa descartada**: paginar solo `GET /editoriales/` y `GET /generos/` (lectura literal de la columna "Cuerpo") — contradice "todo listado" de RN-10 y deja tres listados sin cota; si la cátedra prefiere esos tres sin paginar, se quitan solo los `Query` y sus escenarios 422 (cambio acotado, sin tocar el service salvo los parámetros).

### Orden determinista y 404 por existencia del recurso padre

- **Por qué**: sin `order_by`, dos páginas pueden solapar u omitir filas; y un listado vacío no distingue "el padre no existe" (404, que la tabla exige) de "el padre existe y no tiene hijos" (200 con `[]`).
- **Cómo**: `order_by(Editorial.id)`, `order_by(Genero.id)`, `order_by(Libro.id)` para las relaciones de editorial/género, y `order_by(LibroAutor.orden, LibroAutor.libro_id)` para las de autor (el `orden` es el dato que la tabla pide mostrar y desempata por `libro_id`). El service verifica la existencia del padre con `session.get(Editorial | Genero | Autor, id)` → si es `None`, 404 propio; después consulta los hijos. Esa lectura previa es una **lectura**, no una escritura: RT-02/DD-04 solo prohíben consultar existencia antes de escribir.
- **Alternativa descartada**: leer los hijos y deducir el 404 de una lista vacía — imposible de distinguir del caso legítimo sin hijos; o navegar `editorial.libros` — dispararía carga perezosa (prohibida, RT-04).

### Precarga en las relaciones `/{id}/libros`

- **Por qué**: RT-04 prohíbe depender de carga perezosa y el stack async lanza `MissingGreenlet` si se accede a una relación no cargada.
- **Cómo**: `GET /autores/{id}/libros` consulta `select(LibroAutor).options(joinedload(LibroAutor.libro)).where(LibroAutor.autor_id == id)` — la relación a uno (`libro`) va con `joinedload` y se serializa sin consultas por fila. Los listados de editorial y género consultan `select(Libro)` filtrando por `editorial_id`/`genero_id` y serializan **solo columnas propias** (`isbn`, `titulo`, `precio`, `stock`, `genero_id`/`editorial_id`): no leen ninguna relación, por lo que no hay nada que precargar ni riesgo de lazy. Los detalles (`GET /{recurso}/{id}`) leen solo columnas escalares de la fila.
- **Alternativa descartada**: `selectinload` para `libro` en autorías — es una relación a uno; `joinedload` evita la consulta extra.

### Sin DELETE (DD-02)

- **Por qué**: la tabla de endpoints no declara DELETE en ningún recurso y DD-02 lo fija; la duda §(5) de `10_preguntas_abiertas.md` sigue pendiente y no se resuelve acá.
- **Cómo**: no se crea ninguna ruta DELETE. El escenario de la spec verifica que `DELETE /editoriales/{id}` responde 405 y no borra la fila, de modo que la ausencia sea observable y comprobable, no solo una omisión.

### Validación declarativa de ruta y query

- **Por qué**: el 422 debe ocurrir sin ejecutar el handler (mismo criterio que C-01 en libros).
- **Cómo**: `{id}` se declara `Annotated[int, Path()]`; FastAPI responde 422 a `/editoriales/abc` antes del handler. No se valida a mano con `if` en el service: duplicaría la validación y rompería el "sin ejecutar el handler".

## PEDIDOS explícitos (sin cambios silenciosos a `models.py`)

- Ninguna modificación de `app/modules/{editoriales,generos,autores}/models.py`: `Editorial` (`uq_editorial_nombre`), `Genero` (`uq_genero_nombre`) y `Autor` (sin restricciones extra) ya existen de CH-02 y se reutilizan tal cual, con sus nombres exactos para la traducción por `constraint_name`.
- No se toca `app/core/` ni el lifespan. `app/main.py` sí se modifica, solo para importar y registrar los tres routers.
- Si hiciera falta un cambio de esquema (por ejemplo, una UNIQUE en `autor` si la cátedra responde §(3) afirmativamente), se abre un change separado: `create_all` no altera tablas ya creadas y no hay migraciones.

## Risks / Trade-offs

- [Riesgo] La traducción depende de que `exc.orig.__cause__` exponga `constraint_name` con asyncpg. → Mitigación: lectura con `getattr` defensivo sobre `exc.orig` y su `__cause__`, y mapeo por `sqlstate` + nombre exacto; si `constraint_name` no estuviera disponible, el fallback es el 409 genérico (sigue cumpliendo RN-12 y RT-01, con un mensaje menos específico).
- [Riesgo] `GET /generos/{id}` no está en la tabla del PDF y podría considerarse fuera de alcance. → Mitigación: decisión documentada arriba con las citas de `06_funcionalidades.md` y `CHANGES.md`; se retira sin impacto si la cátedra confirma que no existe.
- [Trade-off] Paginar `/{id}/libros` con defecto 20 trunca listados largos si el cliente no pasa `limit`. → Aceptado: es exactamente lo que fija RN-10 para todo listado y el cliente puede pedir hasta 100; el escenario de la spec lo deja observable.
- [Trade-off] Sin `PATCH /generos/{id}`, un género mal tipeado requiere SQL manual. → Aceptado y registrado como pregunta abierta; crear el endpoint sería inventar contrato.
- [Riesgo] `POST /autores/` acepta duplicados exactos (sin UNIQUE). → Es el comportamiento que declara el enunciado ("Sin restricciones extra"); se verifica explícitamente para que no se confunda con un olvido.

## Migration Plan

Sin migraciones (regla dura): no hay cambio de esquema; `create_all` del lifespan no se toca y las tres tablas ya existen. Rollback del change: quitar los tres `include_router` de `app/main.py` (los modelos quedan intactos) o revertir el commit; las filas creadas por verificación se limpian a mano en el Query Tool de pgAdmin solo si no están referenciadas por libros (`SELECT count(*) FROM libro WHERE editorial_id=<id>` / `genero_id=<id>` / `SELECT count(*) FROM libro_autor WHERE autor_id=<id>`), porque no hay DELETE por HTTP (DD-02).

## Open Questions

- **PENDIENTE (3)** — `10_preguntas_abiertas.md` §(3): `POST /autores/` declara solo 201/422. No se implementa ningún 409 en autores porque la tabla no tiene UNIQUE/FK/CHECK que lo produzca; queda por confirmar con cátedra si la ausencia es intencional. Si se agregara una unicidad, el cambio de esquema y el 409 van en un change separado.
- **PENDIENTE (5)** — `10_preguntas_abiertas.md` §(5): no se crea ningún DELETE. Confirmación de la cátedra pendiente.
- **PENDIENTE NUEVA — `GET /generos/{id}`**: la tabla del PDF no lo declara; `06_funcionalidades.md` y `CHANGES.md` sí. Se implementa (decisión arriba) y se deja explícito para confirmar con cátedra.
- **PENDIENTE NUEVA — sin `PATCH /generos/{id}`**: la tabla no declara corrección de géneros, así que un género mal cargado no se puede corregir por HTTP. ¿Se espera un PATCH de géneros? No se crea hasta la respuesta; si la cátedra lo pide, se abre un change con su contrato (`GeneroUpdate` con `exclude_unset`) y sus escenarios.
- **PENDIENTE NUEVA — paginación de las relaciones `/{id}/libros`**: RN-10 dice "todo listado" y la columna "Cuerpo" de la tabla no marca `limit`/`offset` en esas tres filas. Se implementa paginado (decisión arriba). Si la cátedra espera esas relaciones sin paginar, se quitan los `Query` y sus escenarios 422 en un change acotado.
