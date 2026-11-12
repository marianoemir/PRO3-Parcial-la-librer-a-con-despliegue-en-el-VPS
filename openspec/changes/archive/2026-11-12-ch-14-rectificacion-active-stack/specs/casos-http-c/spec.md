# Spec Delta

## Purpose

Especificar los casos de prueba HTTP C-01 a C-08 como requisitos verificables del contrato observable de la API, usando una base local vacía con seed y los artefactos `.http` del proyecto como evidencia. La spec cubre la capability faltante de CH-09: referencia los artefactos `.http` existentes para C-05 y C-06 sin duplicarlos y define C-07 como verificación de consultas fijas observable con diagnóstico SQL/consola (la captura formal de evidencia corresponde a CH-12).

## ADDED Requirements

### Requirement: C-01 — Parámetro de ruta no entero rechazado por validación

El sistema SHALL rechazar con 422 una solicitud a un endpoint con parámetro de ruta tipado como entero cuando el valor recibido no es convertible a entero.

#### Scenario: Ruta de libro con id no entero devuelve 422 (caso esperado)

- **WHEN** se ejecuta `GET /libros/no-es-entero` contra la API con el entorno de prueba preparado según `test/ch09-casos-http-c.http`
- **THEN** la respuesta HTTP es 422 y el cuerpo es un error de validación público, sin detalle de BD

#### Scenario: Ruta válida no se confunde con C-01 (borde)

- **WHEN** se ejecuta `GET /libros/1` en el entorno preparado para C-07 según `test/ch09-c07-consultas-fijas.http`
- **THEN** la solicitud no es rechazada por tipo de ruta y responde 200 con el detalle del libro esperado por la fixture de C-07

### Requirement: C-02 — Unicidad rechazada con 409 propio sin huérfanos

El sistema SHALL rechazar con 409 y `detail` propio (sin texto interno de la base) los intentos de crear recursos que violen unicidades del dominio: ISBN de libro repetido y email de cliente repetido. La violación no SHALL dejar registros huérfanos asociados al intento rechazado.

#### Scenario: ISBN repetido devuelve 409 propio (error esperado)

- **WHEN** se ejecuta `POST /libros/` con el cuerpo C-02a de `test/ch09-casos-http-c.http`, usando un ISBN ya existente en el seed
- **THEN** la respuesta HTTP es 409 con `detail` `"Ya existe un libro con ese ISBN"` y el cuerpo no contiene SQL, constraints, tracebacks, `asyncpg` ni nombres de tablas

#### Scenario: Email repetido devuelve 409 propio (error esperado)

- **WHEN** se ejecuta `POST /clientes/` con el cuerpo C-02b de `test/ch09-casos-http-c.http`, usando un email ya existente en el seed
- **THEN** la respuesta HTTP es 409 con `detail` `"El email ya está registrado."` y el cuerpo no contiene SQL, constraints, tracebacks, `asyncpg` ni nombres de tablas

#### Scenario: Intento rechazado no crea libro huérfano (borde/integridad)

- **WHEN** tras ejecutar la solicitud C-02a se consulta `GET /libros/?titulo=CH09`
- **THEN** la respuesta HTTP es 200 con lista vacía `[]`, evidenciando que no se persistió un libro huérfano por el rechazo de C-02a

### Requirement: C-03 — Segundo perfil para el mismo cliente rechazado

El sistema SHALL rechazar con 409 y `detail` propio el intento de crear un segundo perfil para un cliente que ya posee perfil, respetando la relación uno a uno.

#### Scenario: Cliente con perfil existente recibe 409 al crear otro perfil (caso esperado)

- **WHEN** se ejecuta `POST /clientes/1/perfil` con el cuerpo válido C-03 de `test/ch09-casos-http-c.http` sobre base local con seed (el seed define `perfil_cliente` para `cliente_id` 1 en `app/seed.py`)
- **THEN** la respuesta HTTP es 409 con `detail` `"El cliente ya tiene un perfil."` y sin internals de base

### Requirement: C-04 — Referencias inexistentes en alta de libro rechazadas con 409

El sistema SHALL rechazar con 409 y `detail` propio los intentos de alta de libro que referencien `editorial_id` o `autor_id` inexistentes dentro de rango válido, sin exponer internals de la base.

#### Scenario: Editorial inexistente devuelve 409 propio (error esperado)

- **WHEN** se ejecuta `POST /libros/` con `editorial_id` inexistente dentro de `int4` según C-04a de `test/ch09-casos-http-c.http`
- **THEN** la respuesta HTTP es 409 con `detail` `"La referencia indicada no existe"` y sin SQL, constraints, tracebacks, `asyncpg` ni nombres de tablas

#### Scenario: Autor inexistente devuelve 409 propio (error esperado)

- **WHEN** se ejecuta `POST /libros/` con `autor_id` inexistente dentro de `int4` según C-04b de `test/ch09-casos-http-c.http`
- **THEN** la respuesta HTTP es 409 con `detail` `"La referencia indicada no existe"` y sin internals de base

#### Scenario: Rechazos C-04 no generan libros huérfanos (borde)

- **WHEN** se consulta `GET /libros/?titulo=CH09` tras las solicitudes C-04
- **THEN** la respuesta HTTP es 200 con lista vacía `[]`

### Requirement: C-05 — Venta con referencias inexistentes rechazada con 409 (referencia)

El sistema SHALL rechazar con 409 propio los intentos de alta de venta cuando el cliente o algún libro referenciado no exista. Este requisito se verifica con el artefacto existente de CH-07 y no se duplica en `test/ch09-casos-http-c.http`.

#### Scenario: Cliente inexistente en venta devuelve 409 (referencia a CH-07)

- **WHEN** se ejecuta la solicitud de cliente inexistente definida en `test/ch07-ventas-errores.http`
- **THEN** la respuesta HTTP es 409 con `detail` `"La referencia indicada no existe o hay un conflicto de datos"` y sin internals de base (cobertura propiedad de CH-07, referenciada por CH-09)

#### Scenario: Libro inexistente en venta devuelve 409 (referencia a CH-07)

- **WHEN** se ejecuta la solicitud de libro inexistente definida en `test/ch07-ventas-errores.http`
- **THEN** la respuesta HTTP es 409 con `detail` `"El libro indicado no existe"` y sin internals de base (cobertura propiedad de CH-07)

### Requirement: C-06 — Alta de venta válida calcula totales del servidor (referencia)

El sistema SHALL crear una venta válida copiando precios del catálogo y calculando el total en el servidor. Este requisito se verifica con artefactos existentes de CH-08/CH-07 y no se duplica en `test/ch09-casos-http-c.http`.

#### Scenario: Venta válida con dos renglones devuelve 201 y total correcto (referencia a CH-08)

- **WHEN** se ejecuta la solicitud C-06 definida en `test/ch08-seed-datos-iniciales.http` sobre base local vacía con seed
- **THEN** la respuesta HTTP es 201 con `total: "77000.00"` y precios/subtotales copiados del servidor según el dataset del seed (cobertura propiedad de CH-08, referenciada por CH-09)

### Requirement: C-07 — Detalles de libro y venta con cantidad fija de consultas

El sistema SHALL resolver los detalles de libro y venta con una cantidad fija de consultas SQL independiente de la cardinalidad de relaciones cargadas (autores en libro, renglones en venta), verificable con diagnóstico SQL/consola en el entorno de prueba.

#### Scenario: Detalle de libros con 1 y 2 autorías usa consultas fijas (caso esperado)

- **WHEN** se consultan `GET /libros/1` y `GET /libros/6` según `test/ch09-c07-consultas-fijas.http` en base local vacía con seed siguiendo el ciclo limpio documentado
- **THEN** cada detalle responde 200 y la cantidad de consultas SQL observada es fija e igual para ambos casos: 3 SELECT por detalle

#### Scenario: Detalle de ventas con distinto número de renglones usa consultas fijas (caso esperado)

- **WHEN** se consultan `GET /ventas/2` y `GET /ventas/3` según `test/ch09-c07-consultas-fijas.http` tras completar el ciclo limpio documentado
- **THEN** cada detalle responde 200 y la cantidad de consultas SQL observada es fija e igual para ambos casos: 2 SELECT por detalle

### Requirement: C-08 — Búsqueda de libros segura ante intento de inyección

El sistema SHALL tratar el parámetro `titulo` como dato ligado (no como SQL concatenado) y devolver 200 con lista vacía cuando el valor no coincida con títulos existentes, incluso si el texto simula una inyección (RN-11, RT-05, `knowledge-base/05_reglas_de_negocio.md`).

#### Scenario: Patrón de inyección en filtro de título no devuelve catálogo ni error SQL (caso esperado y borde)

- **WHEN** se ejecuta `GET /libros/?titulo=%27%20OR%20%271%27%3D%271` según C-08 de `test/ch09-casos-http-c.http` sobre base local vacía con seed
- **THEN** la respuesta HTTP es 200 con cuerpo JSON `[]` y no enumera el catálogo completo ni produce error de SQL, evidenciando parametrización del filtro
