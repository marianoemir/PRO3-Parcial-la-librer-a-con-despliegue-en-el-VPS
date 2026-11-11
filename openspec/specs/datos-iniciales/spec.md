# datos-iniciales Specification

## Purpose
Dejar la base en un estado inicial conocido, reproducible e idempotente, con filas e ids fijos que hacen verificables los casos C-06 y D-03 tanto en local como dentro del contenedor del VPS.

## Requirements

### Requirement: Dataset inicial determinista con ids fijos

El sistema SHALL proveer una carga de datos iniciales que, sobre una base con el esquema ya creado y sin filas de dominio, inserte un dataset fijo con ids explícitos: editoriales 1–2, géneros 1–2, autores 1–5, libros 1–6, clientes 1–3, perfiles 1 y 2, venta 1 y renglones 1–2. El contenido SHALL ser idéntico en cada ejecución y quedar documentado en el README del proyecto.

#### Scenario: Carga sobre base vacía deja el dataset documentado (D-03)

- **WHEN** se ejecuta el seed contra una base con el esquema creado y sin filas de dominio
- **THEN** la base queda con 2 editoriales, 2 géneros, 5 autores, 6 libros, 7 autorías, 3 clientes, 2 perfiles, 1 venta y 2 renglones, con los ids indicados en el README, y `GET /libros/` devuelve 200 con esos libros

#### Scenario: El dataset deja reproducible el caso C-06 con total 77000.00

- **WHEN** tras el seed se envía `POST /ventas/` con `cliente_id: 2` y renglones libro 1 ×2 y libro 4 ×1, tal como define el caso C-06
- **THEN** el libro 1 tiene precio 25000.00 y stock 10, el libro 4 tiene precio 27000.00 y stock 7, la venta 1 ya existe con `total: 77000.00` para el cliente 2, y el alta responde 201 con precios copiados y `total: "77000.00"` en una venta nueva con id 2 (siguiente al máximo cargado)

#### Scenario: El libro con autores 3 y 4 queda cargado con los valores del enunciado

- **WHEN** se inspecciona el libro con ISBN `978-950-00-0006-6` después del seed
- **THEN** es el libro 6, con título "Los que aman, odian", precio 21000.00, stock 4, editorial 1, género 1, y sus autorías son autor 3 (coautor, orden 1) y autor 4 (coautor, orden 2), con `rol` y `orden` aceptados por los CHECK de `libro_autor`

### Requirement: Idempotencia y secuencias alineadas tras la carga

Reejecutar el seed SHALL ser seguro: no duplica filas, no viola unicidades ni claves primarias, informa qué filas ya existían y restaura solo las faltantes. Tras la carga, las secuencias de las tablas con `id` serial SHALL quedar en el máximo id cargado para que las altas por API obtengan ids nuevos.

#### Scenario: Segunda ejecución no duplica ni corrompe unicidades

- **WHEN** se ejecuta el seed por segunda vez sobre la misma base
- **THEN** los conteos por tabla no cambian, el resumen informa 0 filas insertadas y las unicidades `uq_libro_isbn`, `uq_cliente_email`, `uq_editorial_nombre`, `uq_genero_nombre` y `uq_perfil_cliente_cliente_id` siguen satisfechas

#### Scenario: Alta por API después del seed obtiene un id nuevo

- **WHEN** tras el seed se envía `POST /editoriales/` con un nombre nuevo, o `POST /libros/` con un ISBN nuevo
- **THEN** la respuesta es 201 con un id mayor que el máximo cargado (por ejemplo editorial 3), sin 409 espurio por colisión con los ids del dataset

#### Scenario: Reejecución repone una fila faltante sin duplicar el resto

- **WHEN** se elimina una sola fila del dataset (por ejemplo el cliente 3) y se vuelve a ejecutar el seed
- **THEN** el resumen informa exactamente esa fila como insertada, el resto de los conteos no cambia y no aparece ningún duplicado por ISBN, email, nombre de editorial/género ni perfil

### Requirement: Carga atómica sin estados parciales

El seed SHALL ejecutar toda la carga en una única transacción: si una fila es rechazada por la base o la conexión se interrumpe, la base SHALL quedar como estaba, sin dataset incompleto ni filas huérfanas.

#### Scenario: Un rechazo de la base revierte todo el dataset

- **WHEN** una de las filas del dataset es rechazada por una restricción de la base durante la carga sobre una base vacía
- **THEN** la transacción se revierte y la base queda sin ninguna fila del dataset y sin renglones huérfanos respecto de su venta

#### Scenario: Error de conexión no deja filas parciales

- **WHEN** la conexión con la base se pierde antes de confirmar la transacción
- **THEN** no se confirma ninguna fila y el comando termina con error, informando que la carga no se aplicó

### Requirement: Ejecución fuera de los routers, local y dentro del contenedor

El seed SHALL ser un comando de línea de comandos independiente de la API, sin exponer endpoints ni modificar routers: ejecutable localmente con `python -m app.seed` y dentro del contenedor con `docker exec libreria python -m app.seed`. SHALL requerir solo que el esquema exista, sin exigir que la API esté sirviendo peticiones.

#### Scenario: Ejecución local contra la base de desarrollo

- **WHEN** se ejecuta `python -m app.seed` con `DATABASE_URL` válida y el esquema ya creado por el arranque de la aplicación
- **THEN** el comando carga el dataset y termina con código de salida 0, sin levantar uvicorn ni abrir puertos

#### Scenario: Ejecución en el VPS mediante docker exec (Flujo 6 paso 4)

- **WHEN** se ejecuta `docker exec libreria python -m app.seed` en el contenedor desplegado
- **THEN** el comando usa la `DATABASE_URL` del contenedor, carga el mismo dataset documentado y termina con código de salida 0

#### Scenario: El seed no agrega ni modifica rutas de la API

- **WHEN** se compara `GET /openapi.json` antes y después de agregar el seed al proyecto
- **THEN** no aparece ninguna ruta nueva ni cambia el contrato de las existentes, porque el seed no se expone por HTTP

### Requirement: Salida de consola propia, sin secretos, y sin efectos no definidos

El seed SHALL informar por consola un resumen propio por tabla (insertadas y ya existentes) y los ids cargados, sin imprimir `DATABASE_URL` ni credenciales. Ante base inalcanzable, esquema ausente o `DATABASE_URL` faltante SHALL terminar con código distinto de 0 y un mensaje propio. El seed SHALL NO crear ni modificar el esquema y SHALL NO aplicar reglas de negocio no definidas, en particular no descontar stock por la venta que carga.

#### Scenario: Resumen de éxito legible y sin credenciales

- **WHEN** el seed termina correctamente
- **THEN** la salida muestra por tabla cuántas filas insertó y cuántas ya existían, lista los ids del dataset y no contiene la URL de la base ni usuario ni contraseña

#### Scenario: Esquema ausente se informa sin volcar internals de la base

- **WHEN** se ejecuta el seed contra una base donde la aplicación nunca arrancó y las tablas no existen
- **THEN** el comando termina con código distinto de 0, indica que debe iniciarse la aplicación al menos una vez para crear el esquema y no imprime SQL, trazas internas ni nombres de constraints

#### Scenario: No se descuenta stock por la venta cargada (KB §1 pendiente)

- **WHEN** se inspecciona el stock de los libros 1 y 4 después del seed, que incluye la venta 1 con 2 unidades del libro 1 y 1 del libro 4
- **THEN** el stock queda en los valores documentados del dataset (libro 1 en 10 y libro 4 en 7), sin descuento, porque el descuento de stock es una pregunta abierta de la KB y no una regla implementada
