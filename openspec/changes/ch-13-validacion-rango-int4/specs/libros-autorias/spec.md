# Delta for libros-autorias

## MODIFIED Requirements

### Requirement: Listado paginado y búsqueda por título y género

El sistema SHALL listar libros con paginación `limit` (1 a 100, defecto 20) y `offset` (desde 0) (RN-10), filtros opcionales `titulo` (parte del título, case-insensitive, parámetro ligado, RN-11) y `genero_id`, con editorial y género precargados y orden determinista por id, respondiendo 200 con la lista. La paginación fuera de rango, incluido un `offset` fuera del rango `int4` soportado por la base, SHALL responder 422 sin ejecutar la consulta ni exponer texto interno de la base (RT-01, RN-12).

#### Scenario: Listado con paginación y filtros devuelve 200
- **WHEN** `GET /libros/?limit=20&offset=0&titulo=que+aman` sobre una base con "Los que aman, odian" y otros títulos
- **THEN** responde 200 con los libros cuyo título contiene "que aman" sin importar mayúsculas y que coinciden con `genero_id` cuando se pasa, ordenados por `Libro.id` y cada uno con `editorial` y `genero` resumen (con `genero=null` si no tiene), respetando `limit`/`offset`, sin texto de la base

#### Scenario: Búsqueda de inyección devuelve 200 con lista vacía (C-08)
- **WHEN** `GET /libros/?titulo=' OR '1'='1` (caso C-08)
- **THEN** responde 200 con lista vacía, porque el filtro viaja como parámetro ligado nunca concatenado (RN-11, RT-05), sin exponer trazas ni SQL

#### Scenario: Paginación fuera de rango devuelve 422 (borde)
- **WHEN** `GET /libros/?limit=0`, `GET /libros/?limit=101` o `GET /libros/?offset=-1`
- **THEN** responde 422 sin ejecutar la consulta, con restricciones en `Query` (RN-10)

#### Scenario: Id u offset fuera de rango int4 devuelve 422 sin internals (rectificación CH-13)
- **WHEN** `GET /libros/?offset=99999999999` (o cualquier `offset > 2147483647`)
- **THEN** responde 422 por validación declarativa de `Query` sin ejecutar la consulta ni el handler, y el cuerpo no contiene `DataError`, `Traceback`, `asyncpg`, SQL ni nombres de tablas/restricciones (RN-12)

#### Scenario: genero_id de filtro fuera de rango int4 devuelve 422 sin internals (rectificación CH-13)
- **WHEN** `GET /libros/?genero_id=99999999999` (o cualquier `genero_id > 2147483647`)
- **THEN** responde 422 por validación declarativa de `Query` sin ejecutar la consulta ni el handler, y el cuerpo no contiene `DataError`, `Traceback`, `asyncpg`, SQL ni nombres de tablas/restricciones (RN-12)

### Requirement: Detalle de libro precargado

El sistema SHALL devolver un libro por su id con editorial, género y autorías con autor (`id`/`nombre`) precargados, con un número fijo de consultas que no crece con la cantidad de autores (RT-04, C-07 parcial). Si el id no es entero o está fuera del rango `int4` soportado SHALL responder 422 sin ejecutar el handler (C-01); si no existe (incluido `id == 0`, decisión CH-05) SHALL responder 404 (RT-01).

#### Scenario: Detalle existente devuelve 200 con relaciones
- **WHEN** `GET /libros/<id>` de un libro con `genero_id=1` y dos autorías
- **THEN** responde 200 con `editorial`, `genero` y `autores` (cada uno con `autor_id`, `rol`, `orden` y `autor` con `id` y `nombre`), y con `SQL_ECHO=true` la consola muestra un número fijo de consultas independiente de que el libro tenga 1 o varios autores (RT-04)

#### Scenario: Detalle sin género devuelve 200 con genero nulo (borde)
- **WHEN** `GET /libros/<id>` de un libro creado con `genero_id=null`
- **THEN** responde 200 con `genero_id=null` y `genero=null`, sin error, y con el mismo número fijo de consultas que el caso con género

#### Scenario: Id no entero devuelve 422 sin ejecutar el handler (C-01)
- **WHEN** `GET /libros/abc` (caso C-01)
- **THEN** responde 422 sin ejecutar el handler de detalle y sin emitir consultas de lectura en consola

#### Scenario: Id inexistente devuelve 404
- **WHEN** `GET /libros/999999` sin libro con ese id
- **THEN** responde 404 con mensaje propio, sin texto de la base (RN-12)

#### Scenario: Id cero devuelve 404 (decisión CH-05, regresión)
- **WHEN** `GET /libros/0`
- **THEN** responde 404 con mensaje propio, sin texto de la base, porque `0` no es overflow `int4` y la inexistencia la resuelve el service

#### Scenario: Id fuera de rango int4 devuelve 422 sin internals (rectificación CH-13)
- **WHEN** `GET /libros/99999999999` (o cualquier id de ruta `> 2147483647`)
- **THEN** responde 422 por validación declarativa de `Path` sin ejecutar el handler ni consultas, y el cuerpo no contiene `DataError`, `Traceback`, `asyncpg`, SQL ni nombres de tablas/restricciones (RN-12)

### Requirement: Actualización parcial de libro

El sistema SHALL aplicar solo los campos enviados en `PATCH /libros/{id}` (`exclude_unset`, sin `autores`), respondiendo 200 con el detalle precargado y traduciendo el rechazo de la base a 409 propio. Si el id no existe SHALL responder 404; si el id o el cuerpo no cumplen el contrato, incluido overflow `int4` en path o en body ids (`editorial_id`, `genero_id`), SHALL responder 422 sin ejecutar la escritura (RT-01, RN-12, RT-02). No existe DELETE de libros (DD-02).

#### Scenario: PATCH parcial actualiza solo lo enviado
- **WHEN** `PATCH /libros/<id>` con `{"titulo": "Nuevo título"}` sobre un libro con ISBN, precio y autorías previos
- **THEN** responde 200 con el libro cuyo `titulo` es el nuevo y el resto de los campos, editorial, género y autorías sin cambios

#### Scenario: PATCH con id fuera de rango int4 devuelve 422 sin internals (rectificación CH-13)
- **WHEN** `PATCH /libros/99999999999` con un cuerpo válido
- **THEN** responde 422 por validación declarativa de `Path` sin ejecutar el handler ni modificar filas, y el cuerpo no contiene `DataError`, `Traceback`, `asyncpg`, SQL ni nombres de tablas/restricciones (RN-12)

#### Scenario: PATCH con cuerpo inválido, id inexistente o id cero (borde/regresión)
- **WHEN** `PATCH /libros/<id>` con `{"precio": "0"}`, o `PATCH /libros/999999` sin libro, o `PATCH /libros/abc`, o `PATCH /libros/0`
- **THEN** responde 422, 404, 422 o 404 respectivamente, sin modificar la fila y sin texto de la base

### Requirement: Errores del alta de libro sin exponer la base

El sistema SHALL responder 409 con mensaje propio sin texto de la base cuando la base rechaza el alta por reglas de integridad con ids dentro de rango (ISBN repetido, FK inexistente, PK de autoría duplicada) sin haber consultado existencia antes, y 422 si el cuerpo no cumple el contrato, incluidos ids de cuerpo fuera del rango `int4` (`editorial_id`, `genero_id`, `autor_id`) (RT-01, RN-01, RN-12, RT-02).

#### Scenario: Valores fuera del tipo de columna devuelven 422 sin escribir
- **WHEN** `POST /libros/` o `PATCH /libros/<id>` trae `precio` fuera de `NUMERIC(10,2)`, `stock` fuera de `int4`, o body ids/enteros `editorial_id`, `genero_id`, `autores[].autor_id`, `autores[].orden` con valor `99999999999` (`> 2147483647`)
- **THEN** responde 422 sin ejecutar la escritura ni consultas de existencia previa (RT-02), y el cuerpo no contiene `DataError`, `Traceback`, `asyncpg`, SQL ni nombres de tablas/restricciones (RN-12)

#### Scenario: FK inexistente dentro de rango devuelve 409 (regresión)
- **WHEN** `POST /libros/` o `PATCH /libros/<id>` trae `editorial_id=999999` (dentro de `int4`) inexistente
- **THEN** responde 409 con mensaje propio traducido del rechazo de la base, sin consulta previa de existencia y sin exponer internals
