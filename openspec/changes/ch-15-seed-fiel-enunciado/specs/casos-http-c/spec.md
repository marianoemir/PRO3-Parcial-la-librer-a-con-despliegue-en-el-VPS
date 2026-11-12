# Spec Delta

## ADDED Requirements

### Requirement: Regresión de casos C-01 a C-08 con el dataset de CH-15
Los casos C-01 a C-08 SHALL seguir cumpliéndose sobre una base local vacía y dedicada con esquema creado y seed de CH-15 cargado, preservando el orden obligatorio del ciclo de verificación. Los ajustes en `.http` SHALL limitarse a lo que dependía del libro 6 o de "Bruno Díaz"; los casos referenciados en otros artefactos (C-05 en `test/ch07-ventas-errores.http`, C-06 según el seed vigente) SHALL permanecer válidos bajo las nuevas precondiciones.

#### Scenario: C-01 a C-08 se ejecutan en orden sobre el nuevo dataset
- **WHEN** se ejecuta el ciclo limpio documentado (C-01, C-02, C-03, C-04, C-08 y reutilización de C-05, C-06, C-07 según sus archivos) contra una base local vacía con seed de CH-15
- **THEN** cada caso obtiene el resultado esperado por su contrato observable (422, 409 propios sin internals, 200 `[]` en C-08, 201 con total correcto en C-06 y conteos fijos 3/3 y 2/2 en C-07), sin depender de fixtures obsoletas del libro 6 ni de "Bruno Díaz"

## MODIFIED Requirements

### Requirement: C-02 — Unicidad rechazada con 409 propio sin huérfanos
El sistema SHALL rechazar con 409 y `detail` propio (sin texto interno de la base) los intentos de crear recursos que violen unicidades del dominio: ISBN de libro repetido y email de cliente repetido. La violación no SHALL dejar registros huérfanos asociados al intento rechazado. En el ciclo de verificación C sobre base local vacía con el seed de CH-15, C-02a SHALL usar el ISBN existente del libro 1 del dataset (no el ISBN del ejemplo de `POST /libros/` del enunciado, que debe quedar disponible tras el seed).

#### Scenario: ISBN repetido devuelve 409 propio (error esperado)
- **WHEN** se ejecuta `POST /libros/` con el cuerpo C-02a de `test/ch09-casos-http-c.http`, usando un ISBN ya existente en el seed vigente
- **THEN** la respuesta HTTP es 409 con `detail` propio y el cuerpo no contiene SQL, constraints, tracebacks, `asyncpg` ni nombres de tablas

#### Scenario: Email repetido devuelve 409 propio (error esperado)
- **WHEN** se ejecuta `POST /clientes/` con el cuerpo C-02b de `test/ch09-casos-http-c.http`, usando un email ya existente en el seed vigente (`tomas@example.com` del cliente 2 sembrado)
- **THEN** la respuesta HTTP es 409 con `detail` `"El email ya está registrado."` y el cuerpo no contiene SQL, constraints, tracebacks, `asyncpg` ni nombres de tablas

#### Scenario: Intento rechazado no crea libro huérfano (borde/integridad)
- **WHEN** tras ejecutar la solicitud C-02a se consulta `GET /libros/?titulo=CH09`
- **THEN** la respuesta HTTP es 200 con lista vacía `[]`, evidenciando que no se persistió un libro huérfano por el rechazo de C-02a

### Requirement: C-06 — Alta de venta válida calcula totales del servidor (referencia)
El sistema SHALL crear una venta válida copiando precios del catálogo y calculando el total en el servidor. Con el seed de CH-15, el cliente 2 sembrado es "Tomás Ríos" (`tomas@example.com`) y la venta 1 ya ocupa el id 1, por lo que el ejemplo de venta del enunciado (cliente 2, libro 1 ×2 y libro 4 ×1) SHALL producir una respuesta 201 con id 2 y `total: "77000.00"`. Este requisito se verifica con los artefactos `.http` ajustados del change y no duplica lógica de negocio fuera del contrato observable.

#### Scenario: Venta válida con dos renglones devuelve 201 y total correcto (referencia a CH-08)
- **WHEN** se ejecuta la solicitud C-06 definida en `test/ch08-seed-datos-iniciales.http` sobre base local vacía con esquema creado y seed de CH-15 cargado
- **THEN** la respuesta HTTP es 201 con `id: 2`, `total: "77000.00"`, cliente con email `tomas@example.com` y renglones con `titulo`, `precio_unitario` y `subtotal` calculados por el servidor según el catálogo (precios unitarios 25000.00 y 27000.00; subtotales 50000.00 y 27000.00)

### Requirement: C-07 — Detalles de libro y venta con cantidad fija de consultas
El sistema SHALL resolver los detalles de libro y venta con una cantidad fija de consultas SQL independiente de la cardinalidad de relaciones cargadas (autores en libro, renglones en venta), verificable con diagnóstico SQL/consola en el entorno de prueba. En el ciclo limpio de CH-15, el libro con varias autorías usado para la comparación SHALL crearse mediante el `POST /libros/` del ejemplo del enunciado (ISBN `978-950-00-0006-6`) dentro del archivo `test/ch09-c07-consultas-fijas.http`, de modo que sus ids no dependan de una fixture fija del seed; el archivo `.http` y las tareas documentan cómo obtener el id resultante para el detalle.

#### Scenario: Detalle de libros con 1 y 2 autorías usa consultas fijas (caso esperado)
- **WHEN** se consultan `GET /libros/1` (una autoría, del seed) y el detalle del libro con varias autorías creado en `test/ch09-c07-consultas-fijas.http` con el `POST /libros/` del ejemplo del enunciado en base local vacía con seed y ciclo limpio documentado
- **THEN** cada detalle responde 200 y la cantidad de consultas SQL observada es fija e igual para ambos casos: 3 SELECT por detalle

#### Scenario: Detalle de ventas con distinto número de renglones usa consultas fijas (caso esperado)
- **WHEN** se consultan los detalles de venta del ciclo limpio según `test/ch09-c07-consultas-fijas.http` (venta con dos renglones y venta con un renglón, creadas tras el seed de CH-15)
- **THEN** cada detalle responde 200 y la cantidad de consultas SQL observada es fija e igual para ambos casos: 2 SELECT por detalle
