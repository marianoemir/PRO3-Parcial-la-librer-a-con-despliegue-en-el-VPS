# Spec Delta

## Purpose

Definir el contrato observable de los recursos de referencia del catálogo —editoriales, géneros y autores—: altas, listados paginados, detalles, corrección parcial de editorial y autor, listado de los libros de cada recurso y traducción de las unicidades de la base a un 409 con mensaje propio.

## ADDED Requirements

### Requirement: Alta de editorial

El sistema SHALL crear una editorial con `nombre` y `pais` obligatorios, sin `id` en el cuerpo, respondiendo 201 con `id`, `nombre` y `pais`. El `nombre` es único y esa garantía la da la base (`uq_editorial_nombre`), no una consulta previa.

#### Scenario: Alta válida devuelve 201

- **WHEN** `POST /editoriales/` con `{"nombre": "Sudamericana", "pais": "Argentina"}`
- **THEN** responde 201 con `id`, `nombre="Sudamericana"` y `pais="Argentina"`, y en el Query Tool de pgAdmin `SELECT count(*) FROM editorial WHERE nombre='Sudamericana'` devuelve 1

#### Scenario: Nombre de editorial repetido devuelve 409 propio

- **WHEN** `POST /editoriales/` repite un `nombre` ya registrado (por ejemplo `"Sudamericana"`)
- **THEN** responde 409 con `detail="Ya existe una editorial con ese nombre"`, sin exponer `uq_editorial_nombre`, el nombre de la tabla ni una traza (RN-12), y en pgAdmin `SELECT count(*) FROM editorial WHERE nombre='Sudamericana'` sigue devolviendo 1

#### Scenario: Alta sin consulta previa de existencia (RT-02)

- **WHEN** `POST /editoriales/` con un `nombre` nuevo, con `SQL_ECHO=true` en la consola del servidor
- **THEN** responde 201 y en la consola se ve el `INSERT` sin ningún `SELECT` a `editorial` anterior que verifique si el `nombre` ya existe (RT-02, DD-04)

#### Scenario: Cuerpo inválido devuelve 422 sin escribir (borde)

- **WHEN** `POST /editoriales/` con `{}`, o sin `pais`, o con `nombre` numérico (`{"nombre": 123, "pais": "Argentina"}`)
- **THEN** responde 422 sin ejecutar la escritura, y en pgAdmin `SELECT count(*) FROM editorial` no aumenta

### Requirement: Listado paginado de editoriales

El sistema SHALL listar editoriales con `limit` de 1 a 100 (defecto 20) y `offset` desde 0, ordenadas por `id`, respondiendo 200 con la lista de `id`, `nombre` y `pais`. La paginación fuera de rango SHALL responder 422 sin ejecutar la consulta (RN-10, RT-01).

#### Scenario: Listado devuelve 200 respetando limit y offset

- **WHEN** `GET /editoriales/?limit=2&offset=0` sobre una base con al menos 3 editoriales
- **THEN** responde 200 con exactamente 2 editoriales ordenadas por `id` ascendente, y `GET /editoriales/?limit=2&offset=2` devuelve las siguientes sin repetir ninguna de las dos primeras

#### Scenario: Paginación fuera de rango devuelve 422 (borde)

- **WHEN** `GET /editoriales/?limit=0`, `GET /editoriales/?limit=101` o `GET /editoriales/?offset=-1`
- **THEN** responde 422 sin ejecutar la consulta, con las restricciones declaradas en `Query` (RN-10)

### Requirement: Detalle de editorial

El sistema SHALL devolver una editorial por su `id`, respondiendo 200 con `id`, `nombre` y `pais`. Si no existe SHALL responder 404 con mensaje propio y, si el `id` de ruta no es entero, 422 sin ejecutar el handler (RT-01).

#### Scenario: Detalle existente devuelve 200

- **WHEN** `GET /editoriales/<id>` de una editorial creada previamente
- **THEN** responde 200 con el `id`, `nombre` y `pais` de esa editorial

#### Scenario: Editorial inexistente devuelve 404

- **WHEN** `GET /editoriales/999999` sin editorial con ese id
- **THEN** responde 404 con `detail="Editorial no encontrada"`, sin texto interno de la base (RN-12)

#### Scenario: Id no entero devuelve 422 sin ejecutar el handler (borde)

- **WHEN** `GET /editoriales/abc`
- **THEN** responde 422 sin ejecutar el handler de detalle y sin emitir un `SELECT` a `editorial` en la consola con `SQL_ECHO=true`

### Requirement: Corrección parcial de editorial

El sistema SHALL aplicar en `PATCH /editoriales/{id}` solo los campos enviados (`exclude_unset`), respondiendo 200 con la editorial actualizada. Un `nombre` que choque con otra editorial SHALL responder 409 propio; un `null` explícito en `nombre` o `pais` SHALL responder 422; un `id` inexistente SHALL responder 404.

#### Scenario: PATCH parcial actualiza solo lo enviado

- **WHEN** `PATCH /editoriales/<id>` con `{"pais": "Uruguay"}` sobre una editorial con `nombre` y `pais` previos
- **THEN** responde 200 con `pais="Uruguay"` y el `nombre` original sin cambios, y en pgAdmin `SELECT nombre, pais FROM editorial WHERE id=<id>` lo confirma

#### Scenario: PATCH con el nombre de otra editorial devuelve 409 propio

- **WHEN** `PATCH /editoriales/<idA>` con `{"nombre": "<nombre de idB>"}`
- **THEN** responde 409 con `detail="Ya existe una editorial con ese nombre"`, sin exponer `uq_editorial_nombre` (RN-12), y en pgAdmin `SELECT nombre FROM editorial WHERE id=<idA>` sigue devolviendo el nombre original

#### Scenario: PATCH con null explícito o id inexistente (borde)

- **WHEN** `PATCH /editoriales/<id>` con `{"nombre": null}` o `{"pais": null}`, o `PATCH /editoriales/999999` con un cuerpo válido
- **THEN** responde 422 en el primer caso sin modificar la fila (en pgAdmin `nombre` y `pais` de `<id>` siguen igual) y 404 en el segundo

### Requirement: Libros de una editorial

El sistema SHALL devolver los libros cuyo `editorial_id` es el de la ruta, paginados con `limit` y `offset` (RN-10) y ordenados por `id`, respondiendo 200 con una lista de `id`, `isbn`, `titulo`, `precio`, `stock` y `genero_id`. Si la editorial no existe SHALL responder 404; si existe pero no tiene libros, 200 con lista vacía.

#### Scenario: Editorial con libros devuelve solo los suyos

- **WHEN** `GET /editoriales/<id>/libros` de una editorial con dos libros y existiendo libros de otra editorial
- **THEN** responde 200 con exactamente esos dos libros ordenados por `id`, cada uno con `id`, `isbn`, `titulo`, `precio`, `stock` y `genero_id`, y sin libros de la otra editorial

#### Scenario: Editorial inexistente devuelve 404

- **WHEN** `GET /editoriales/999999/libros` sin editorial con ese id
- **THEN** responde 404 con `detail="Editorial no encontrada"`, sin texto interno de la base (RN-12)

#### Scenario: Editorial sin libros devuelve 200 con lista vacía (borde)

- **WHEN** `GET /editoriales/<id>/libros` de una editorial recién creada y sin libros
- **THEN** responde 200 con `[]`, no 404

#### Scenario: Parámetros inválidos en la relación devuelven 422 (borde)

- **WHEN** `GET /editoriales/<id>/libros?limit=0`, `?limit=101`, `?offset=-1` o `GET /editoriales/abc/libros`
- **THEN** responde 422 sin ejecutar la consulta de libros, con las restricciones declaradas en `Query` y `Path` (RN-10, RT-01)

### Requirement: Alta de género

El sistema SHALL crear un género con `nombre` obligatorio, sin `id` en el cuerpo, respondiendo 201 con `id` y `nombre`. El `nombre` es único y esa garantía la da la base (`uq_genero_nombre`).

#### Scenario: Alta válida devuelve 201

- **WHEN** `POST /generos/` con `{"nombre": "Policial"}`
- **THEN** responde 201 con `id` y `nombre="Policial"`, y en pgAdmin `SELECT count(*) FROM genero WHERE nombre='Policial'` devuelve 1

#### Scenario: Nombre de género repetido devuelve 409 propio

- **WHEN** `POST /generos/` repite un `nombre` ya registrado
- **THEN** responde 409 con `detail="Ya existe un género con ese nombre"`, sin exponer `uq_genero_nombre` ni texto de la base (RN-12), y en pgAdmin `SELECT count(*) FROM genero WHERE nombre='<repetido>'` sigue devolviendo 1

#### Scenario: Alta sin consulta previa de existencia (RT-02)

- **WHEN** `POST /generos/` con un `nombre` nuevo, con `SQL_ECHO=true` en la consola del servidor
- **THEN** responde 201 y en la consola se ve el `INSERT` sin ningún `SELECT` a `genero` anterior que verifique si el `nombre` ya existe (RT-02, DD-04)

#### Scenario: Cuerpo inválido devuelve 422 sin escribir (borde)

- **WHEN** `POST /generos/` con `{}` o con `nombre` numérico
- **THEN** responde 422 sin ejecutar la escritura, y en pgAdmin `SELECT count(*) FROM genero` no aumenta

### Requirement: Listado y detalle de géneros

El sistema SHALL listar géneros con `limit` de 1 a 100 (defecto 20) y `offset` desde 0, ordenados por `id` (RN-10), y devolver un género por su `id`, respondiendo 200 en ambos casos y 404 si el detalle no existe.

#### Scenario: Listado devuelve 200 paginado y ordenado por id

- **WHEN** `GET /generos/?limit=2&offset=0` sobre una base con al menos 3 géneros
- **THEN** responde 200 con exactamente 2 géneros ordenados por `id` ascendente, y `GET /generos/?limit=2&offset=2` devuelve los siguientes sin repetir los dos primeros

#### Scenario: Paginación fuera de rango devuelve 422 (borde)

- **WHEN** `GET /generos/?limit=0`, `GET /generos/?limit=101` o `GET /generos/?offset=-1`
- **THEN** responde 422 sin ejecutar la consulta (RN-10)

#### Scenario: Detalle existente e inexistente

- **WHEN** `GET /generos/<id>` de un género existente y `GET /generos/999999`
- **THEN** responde 200 con `id` y `nombre` en el primer caso y 404 con `detail="Género no encontrado"` en el segundo, sin texto interno de la base (RN-12)

#### Scenario: Id no entero devuelve 422 sin ejecutar el handler (borde)

- **WHEN** `GET /generos/abc`
- **THEN** responde 422 sin ejecutar el handler de detalle y sin emitir un `SELECT` a `genero` en la consola con `SQL_ECHO=true`

### Requirement: Libros de un género

El sistema SHALL devolver los libros cuyo `genero_id` es el de la ruta, paginados con `limit` y `offset` (RN-10) y ordenados por `id`, respondiendo 200 con una lista de `id`, `isbn`, `titulo`, `precio`, `stock` y `editorial_id`. Si el género no existe SHALL responder 404; si existe pero no tiene libros, 200 con lista vacía.

#### Scenario: Género con libros devuelve solo los suyos

- **WHEN** `GET /generos/<id>/libros` de un género con un libro y existiendo libros de otro género
- **THEN** responde 200 con exactamente ese libro, con `id`, `isbn`, `titulo`, `precio`, `stock` y `editorial_id`, sin incluir los libros del otro género

#### Scenario: Género inexistente devuelve 404

- **WHEN** `GET /generos/999999/libros` sin género con ese id
- **THEN** responde 404 con `detail="Género no encontrado"`, sin texto interno de la base (RN-12)

#### Scenario: Género sin libros devuelve 200 con lista vacía (borde)

- **WHEN** `GET /generos/<id>/libros` de un género recién creado y sin libros
- **THEN** responde 200 con `[]`, no 404

#### Scenario: Parámetros inválidos en la relación devuelven 422 (borde)

- **WHEN** `GET /generos/<id>/libros?limit=0`, `?limit=101`, `?offset=-1` o `GET /generos/abc/libros`
- **THEN** responde 422 sin ejecutar la consulta de libros, con las restricciones declaradas en `Query` y `Path` (RN-10, RT-01)

### Requirement: Alta de autor sin garantía de unicidad

El sistema SHALL crear un autor con `nombre` y `nacionalidad` obligatorios, sin `id` en el cuerpo, respondiendo 201 con `id`, `nombre` y `nacionalidad`. La tabla `autor` no tiene UNIQUE, FK ni CHECK, por lo que este contrato NO declara 409 y dos autores con el mismo `nombre` y `nacionalidad` SHALL crearse ambos.

#### Scenario: Alta válida devuelve 201

- **WHEN** `POST /autores/` con `{"nombre": "Julio Cortázar", "nacionalidad": "Argentina"}`
- **THEN** responde 201 con `id`, `nombre="Julio Cortázar"` y `nacionalidad="Argentina"`, y en pgAdmin `SELECT count(*) FROM autor WHERE nombre='Julio Cortázar'` devuelve 1

#### Scenario: Autor repetido se crea igual y no devuelve 409

- **WHEN** `POST /autores/` dos veces con el mismo `{"nombre": "Julio Cortázar", "nacionalidad": "Argentina"}`
- **THEN** las dos respuestas son 201 con `id` distintos y en pgAdmin `SELECT count(*) FROM autor WHERE nombre='Julio Cortázar'` devuelve 2, porque `autor` no tiene restricción de unicidad (PDF p. 4) y no se inventa un 409 (pendiente §(3) de `10_preguntas_abiertas.md`)

#### Scenario: Cuerpo inválido devuelve 422 sin escribir (borde)

- **WHEN** `POST /autores/` con `{}`, sin `nacionalidad`, o con `nombre` numérico
- **THEN** responde 422 sin ejecutar la escritura, y en pgAdmin `SELECT count(*) FROM autor` no aumenta

### Requirement: Detalle de autor

El sistema SHALL devolver un autor por su `id`, respondiendo 200 con `id`, `nombre` y `nacionalidad`; 404 con mensaje propio si no existe y 422 si el `id` de ruta no es entero.

#### Scenario: Detalle existente devuelve 200

- **WHEN** `GET /autores/<id>` de un autor creado previamente
- **THEN** responde 200 con `id`, `nombre` y `nacionalidad` de ese autor

#### Scenario: Autor inexistente devuelve 404

- **WHEN** `GET /autores/999999` sin autor con ese id
- **THEN** responde 404 con `detail="Autor no encontrado"`, sin texto interno de la base (RN-12)

#### Scenario: Id no entero devuelve 422 sin ejecutar el handler (borde)

- **WHEN** `GET /autores/abc`
- **THEN** responde 422 sin ejecutar el handler de detalle y sin emitir un `SELECT` a `autor` en la consola con `SQL_ECHO=true`

### Requirement: Corrección parcial de autor

El sistema SHALL aplicar en `PATCH /autores/{id}` solo los campos enviados (`exclude_unset`), respondiendo 200 con el autor actualizado. Como `autor` no tiene unicidad, repetir el `nombre` de otro autor SHALL responder 200; un `null` explícito SHALL responder 422 y un `id` inexistente 404.

#### Scenario: PATCH parcial actualiza solo lo enviado

- **WHEN** `PATCH /autores/<id>` con `{"nacionalidad": "Belga"}` sobre un autor con `nombre` y `nacionalidad` previos
- **THEN** responde 200 con `nacionalidad="Belga"` y el `nombre` original sin cambios, y en pgAdmin `SELECT nombre, nacionalidad FROM autor WHERE id=<id>` lo confirma

#### Scenario: PATCH con el nombre de otro autor devuelve 200, no 409

- **WHEN** `PATCH /autores/<idA>` con `{"nombre": "<nombre de idB>"}`
- **THEN** responde 200 con el nuevo `nombre` y en pgAdmin `SELECT count(*) FROM autor WHERE nombre='<nombre de idB>'` devuelve 2, porque no existe UNIQUE que traducir (no se inventa un 409)

#### Scenario: PATCH con null explícito o id inexistente (borde)

- **WHEN** `PATCH /autores/<id>` con `{"nombre": null}` o `{"nacionalidad": null}`, o `PATCH /autores/999999` con un cuerpo válido
- **THEN** responde 422 en el primer caso sin modificar la fila (en pgAdmin `nombre` y `nacionalidad` de `<id>` siguen igual) y 404 en el segundo

### Requirement: Libros de un autor con rol y orden

El sistema SHALL devolver las autorías del autor de la ruta como libros con los datos de la relación, paginadas con `limit` y `offset` (RN-10) y ordenadas por `orden` ascendente, respondiendo 200 con `libro_id`, `isbn`, `titulo`, `precio`, `stock`, `rol` y `orden`. Si el autor no existe SHALL responder 404; si existe pero no tiene libros, 200 con lista vacía.

#### Scenario: Autor con libros devuelve rol y orden de cada autoría

- **WHEN** `GET /autores/<id>/libros` de un autor que figura en dos libros con `rol="coautor"` y `orden` 1 y 2
- **THEN** responde 200 con las dos entradas ordenadas por `orden` ascendente, cada una con `libro_id`, `isbn`, `titulo`, `precio`, `stock`, `rol` y `orden`, sin omitir `rol` ni `orden`

#### Scenario: Autor inexistente devuelve 404

- **WHEN** `GET /autores/999999/libros` sin autor con ese id
- **THEN** responde 404 con `detail="Autor no encontrado"`, sin texto interno de la base (RN-12)

#### Scenario: Autor sin libros devuelve 200 con lista vacía (borde)

- **WHEN** `GET /autores/<id>/libros` de un autor recién creado y sin autorías
- **THEN** responde 200 con `[]`, no 404

#### Scenario: Parámetros inválidos en la relación devuelven 422 (borde)

- **WHEN** `GET /autores/<id>/libros?limit=0`, `?limit=101`, `?offset=-1` o `GET /autores/abc/libros`
- **THEN** responde 422 sin ejecutar la consulta de autorías, con las restricciones declaradas en `Query` y `Path` (RN-10, RT-01)

### Requirement: Ningún error expone texto interno de la base

El sistema SHALL responder todos sus errores con un `detail` propio en español y NUNCA con nombres de tablas, de restricciones, sentencias SQL ni trazas, en los tres módulos de este change (RN-12).

#### Scenario: Los errores de los tres módulos no filtran internals

- **WHEN** se provocan el 409 de editorial repetida, el 409 de género repetido, un 404 de cada recurso y un 422 de paginación
- **THEN** ningún cuerpo de respuesta contiene `uq_`, `_pkey`, `SELECT`, `Traceback`, `asyncpg` ni el nombre de una tabla, y el 409 de cada recurso repite exactamente el mensaje propio declarado en su escenario

### Requirement: Sin bajas ni endpoints fuera de alcance

El sistema SHALL exponer solo las operaciones declaradas para editoriales, géneros y autores, sin endpoints DELETE ni PATCH de géneros (DD-02, pendiente §(5) de `10_preguntas_abiertas.md`).

#### Scenario: DELETE no está expuesto y no borra filas

- **WHEN** `DELETE /editoriales/<id>`, `DELETE /generos/<id>` o `DELETE /autores/<id>` sobre una fila existente
- **THEN** responde 405 (método no permitido), y en pgAdmin `SELECT count(*) FROM editorial WHERE id=<id>` (o `genero`/`autor`) sigue devolviendo 1

#### Scenario: PATCH de género no está expuesto

- **WHEN** `PATCH /generos/<id>` con `{"nombre": "Otro"}` sobre un género existente
- **THEN** responde 405, y en pgAdmin `SELECT nombre FROM genero WHERE id=<id>` sigue devolviendo el nombre original
