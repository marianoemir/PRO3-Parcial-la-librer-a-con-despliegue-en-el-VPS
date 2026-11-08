# Spec Delta

## Purpose

Definir el contrato observable del catálogo de libros con autorías: alta con editorial, género y autores, listado paginado y búsqueda por título, detalle y corrección parcial con número fijo de consultas, sin exponer internales de la base.

## ADDED Requirements

### Requirement: Alta de libro con autorías

El sistema SHALL crear un libro con su editorial obligatoria, su género opcional y su lista de autorías (`autor_id`, `rol`, `orden`) en una sola operación, respondiendo 201 con el detalle precargado (editorial, género, autorías con `autor_id`, `rol`, `orden` y `autor` con `id`/`nombre`) (RN-03, DD-01).

#### Scenario: Alta válida con ejemplo del enunciado

- **WHEN** `POST /libros/` con `isbn="978-950-00-0006-6"`, `titulo="Los que aman, odian"`, `precio="21000.00"`, `stock=4`, `editorial_id=1`, `genero_id=1` y `autores=[{autor_id: 3, rol: "coautor", orden: 1}, {autor_id: 4, rol: "coautor", orden: 2}]`
- **THEN** responde 201 con el detalle del libro que incluye editorial, género y las dos autorías con su `rol`, `orden` y `autor` (`id`, `nombre`), y en el Query Tool de pgAdmin `SELECT count(*) FROM libro WHERE isbn='978-950-00-0006-6'` devuelve 1 y `SELECT count(*) FROM libro_autor WHERE libro_id=<id>` devuelve 2

### Requirement: Errores del alta de libro sin exponer la base

El sistema SHALL responder 409 con mensaje propio sin texto de la base cuando la base rechaza el alta (ISBN repetido, FK inexistente, PK de autoría duplicada) sin haber consultado existencia antes, y 422 si el cuerpo no cumple el contrato (RT-01, RN-01, RN-12).

#### Scenario: ISBN repetido devuelve 409 propio (C-02)

- **WHEN** `POST /libros/` repite un `isbn` ya registrado (caso C-02)
- **THEN** responde 409 con mensaje propio sobre ISBN duplicado, sin exponer `uq_libro_isbn` ni texto de la base (RN-01, RN-12), y en pgAdmin `SELECT count(*) FROM libro WHERE isbn='<repetido>'` sigue devolviendo 1

#### Scenario: Editorial o autor inexistente devuelve 409 sin consulta previa (C-04)

- **WHEN** `POST /libros/` viaja `editorial_id=999999` inexistente, o un `autores[]` con `autor_id=999999` inexistente (caso C-04)
- **THEN** responde 409 con mensaje propio, sin haber consultado existencia antes (RT-02, DD-04), y en pgAdmin `SELECT count(*) FROM libro WHERE isbn='<nuevo>'` devuelve 0

#### Scenario: Género inexistente devuelve 409 sin consulta previa (C-04)

- **WHEN** `POST /libros/` viaja `genero_id=999999` inexistente con `editorial_id` y `autores` válidos (caso C-04)
- **THEN** responde 409 con mensaje propio sin haber consultado existencia antes (RT-02, DD-04), y en pgAdmin `SELECT count(*) FROM libro WHERE isbn='<nuevo>'` devuelve 0

#### Scenario: Mismo autor dos veces en la lista devuelve 409

- **WHEN** `POST /libros/` trae `autores=[{autor_id: 3, rol: "autor", orden: 1}, {autor_id: 3, rol: "coautor", orden: 2}]`
- **THEN** responde 409 con mensaje propio por autoría duplicada (PK compuesta `libro_id`+`autor_id` de `LibroAutor`, DD-01), sin texto de la base, y en pgAdmin `SELECT count(*) FROM libro WHERE isbn='<nuevo>'` devuelve 0

#### Scenario: Cuerpo inválido devuelve 422 sin escribir (borde)

- **WHEN** `POST /libros/` trae `precio="0"`, o `rol="editor"`, o `orden=0`, o `stock=-1`
- **THEN** responde 422 sin ejecutar la escritura (RN-03 validada en el DTO y CHECK en la base), y en pgAdmin `SELECT count(*) FROM libro WHERE isbn='<nuevo>'` devuelve 0

#### Scenario: Valores fuera del tipo de columna devuelven 422 sin escribir

- **WHEN** `POST /libros/` trae `precio` con más de 10 dígitos totales o más de 2 decimales (por ejemplo `"12345678.901"` o `"1.234"`), o `stock=2147483648`, o `editorial_id=2147483648`, o `genero_id=2147483648`, o `autores[0].autor_id=2147483648`, o `PATCH /libros/<id>` trae `precio` o `stock` con el mismo desborde
- **THEN** responde 422 sin ejecutar la escritura (el DTO refleja `NUMERIC(10,2)` de `precio` y `Integer` int32 de los enteros), y en pgAdmin `SELECT count(*) FROM libro WHERE isbn='<nuevo>'` devuelve 0 / la fila de `<id>` queda sin cambio

### Requirement: Listado paginado y búsqueda por título y género

El sistema SHALL listar libros con paginación `limit` (1 a 100, defecto 20) y `offset` (desde 0) (RN-10), filtros opcionales `titulo` (parte del título, case-insensitive, parámetro ligado, RN-11) y `genero_id`, con editorial y género precargados y orden determinista por id, respondiendo 200 con la lista. La paginación fuera de rango SHALL responder 422 (RT-01).

#### Scenario: Listado con paginación y filtros devuelve 200

- **WHEN** `GET /libros/?limit=20&offset=0&titulo=que+aman` sobre una base con "Los que aman, odian" y otros títulos
- **THEN** responde 200 con los libros cuyo título contiene "que aman" sin importar mayúsculas y que coinciden con `genero_id` cuando se pasa, ordenados por `Libro.id` y cada uno con `editorial` y `genero` resumen (con `genero=null` si no tiene), respetando `limit`/`offset`, sin texto de la base

#### Scenario: Búsqueda de inyección devuelve 200 con lista vacía (C-08)

- **WHEN** `GET /libros/?titulo=' OR '1'='1` (caso C-08)
- **THEN** responde 200 con lista vacía, porque el filtro viaja como parámetro ligado nunca concatenado (RN-11, RT-05), sin exponer trazas ni SQL

#### Scenario: Paginación fuera de rango devuelve 422 (borde)

- **WHEN** `GET /libros/?limit=0`, `GET /libros/?limit=101` o `GET /libros/?offset=-1`
- **THEN** responde 422 sin ejecutar la consulta, con restricciones en `Query` (RN-10)

### Requirement: Detalle de libro precargado

El sistema SHALL devolver un libro por su id con editorial, género y autorías con autor (`id`/`nombre`) precargados, con un número fijo de consultas que no crece con la cantidad de autores (RT-04, C-07 parcial). Si el id no es entero SHALL responder 422 sin ejecutar el handler (C-01); si no existe SHALL responder 404 (RT-01).

#### Scenario: Detalle existente devuelve 200 con relaciones

- **WHEN** `GET /libros/<id>` de un libro con `genero_id=1` y dos autorías
- **THEN** responde 200 con `editorial`, `genero` y `autores` (cada uno con `autor_id`, `rol`, `orden` y `autor` con `id` y `nombre`), y con `SQL_ECHO=true` la consola muestra un número fijo de consultas independiente de que el libro tenga 1 o varios autores (RT-04)

#### Scenario: Detalle sin género devuelve 200 con genero nulo (borde)

- **WHEN** `GET /libros/<id>` de un libro creado con `genero_id=null`
- **THEN** responde 200 con `genero_id=null` y `genero=null`, sin error, y con el mismo número fijo de consultas que el caso con género (agregación opcional, PDF p. 2)

#### Scenario: Id no entero devuelve 422 sin ejecutar el handler (C-01)

- **WHEN** `GET /libros/abc` (caso C-01)
- **THEN** responde 422 sin ejecutar el handler de detalle y sin emitir consultas de lectura en consola

#### Scenario: Id inexistente devuelve 404

- **WHEN** `GET /libros/999999` sin libro con ese id
- **THEN** responde 404 con mensaje propio, sin texto de la base (RN-12)

### Requirement: Actualización parcial de libro

El sistema SHALL aplicar solo los campos enviados en `PATCH /libros/{id}` (`exclude_unset`, sin `autores`), respondiendo 200 con el detalle precargado y traduciendo el rechazo de la base a 409 propio. Si el id no existe SHALL responder 404; si el cuerpo o los parámetros no cumplen el contrato SHALL responder 422 (RT-01, RN-12). No existe DELETE de libros (DD-02).

#### Scenario: PATCH parcial actualiza solo lo enviado

- **WHEN** `PATCH /libros/<id>` con `{"titulo": "Nuevo título"}` sobre un libro con ISBN, precio y autorías previos
- **THEN** responde 200 con el libro cuyo `titulo` es el nuevo y el resto de los campos, editorial, género y autorías sin cambios, y en pgAdmin `SELECT titulo FROM libro WHERE id=<id>` devuelve "Nuevo título"

#### Scenario: PATCH con null explícito rechazado salvo genero_id

- **WHEN** `PATCH /libros/<id>` con `{"isbn": null}`, o `{"titulo": null}`, o `{"precio": null}`, o `{"stock": null}`, o `{"editorial_id": null}`
- **THEN** responde 422 sin modificar la fila (en pgAdmin cada columna de `<id>` sigue con su valor original), porque `LibroUpdate` rechaza `null` explícito con `field_validator`

#### Scenario: PATCH con genero_id null borra el género

- **WHEN** `PATCH /libros/<id>` con `{"genero_id": null}` sobre un libro que tiene género
- **THEN** responde 200 con `genero_id=null` y `genero=null`, y en pgAdmin `SELECT genero_id FROM libro WHERE id=<id>` devuelve `NULL`

#### Scenario: PATCH con ISBN de otro libro devuelve 409 propio

- **WHEN** `PATCH /libros/<idA>` con `{"isbn": "<isbn de idB>"}` (RN-01)
- **THEN** responde 409 con mensaje propio sobre ISBN duplicado, sin exponer `uq_libro_isbn`, y en pgAdmin `SELECT isbn FROM libro WHERE id=<idA>` sigue devolviendo el ISBN original

#### Scenario: PATCH con editorial inexistente devuelve 409

- **WHEN** `PATCH /libros/<id>` con `{"editorial_id": 999999}` inexistente
- **THEN** responde 409 con mensaje propio sin consulta previa de existencia (RT-02, DD-04), y en pgAdmin `SELECT editorial_id FROM libro WHERE id=<id>` sigue devolviendo el valor original

#### Scenario: PATCH con cuerpo inválido o id inexistente (borde)

- **WHEN** `PATCH /libros/<id>` con `{"precio": "0"}`, o `PATCH /libros/999999` sin libro, o `PATCH /libros/abc`
- **THEN** responde 422, 404 o 422 respectivamente, sin modificar la fila (en pgAdmin el `precio` de `<id>` sigue igual), sin texto de la base
