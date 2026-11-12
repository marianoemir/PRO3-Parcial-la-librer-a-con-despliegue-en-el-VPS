# Spec Delta

## ADDED Requirements

### Requirement: Repetibilidad por reinicio en la misma transacción
El seed SHALL dejar la base en el mismo estado inicial conocido cada vez que se ejecuta, incluso si existen datos creados después del último seed. Para lograrlo, la carga SHALL vaciar y recargar los datos en una única transacción: `TRUNCATE` de las 9 tablas del proyecto nombradas explícitamente (`editorial`, `genero`, `autor`, `libro`, `libro_autor`, `cliente`, `perfil_cliente`, `venta`, `renglon_venta`) con `RESTART IDENTITY CASCADE`, seguido de la inserción del dataset y la alineación de secuencias. El seed SHALL NO truncar tablas ajenas al proyecto. La operación SHALL ser atómica: si algo falla, toda la transacción se revierte, incluido el vaciado.

#### Scenario: Reejecución tras datos creados por API restablece el estado inicial
- **WHEN** tras el seed se crea una venta y un libro por la API y luego se vuelve a ejecutar el seed
- **THEN** la base vuelve al mismo estado inicial: 27 filas con los conteos e ids documentados, `GET /ventas/2` y `GET /libros/6` responden 404, y el siguiente `POST /ventas/` con el ejemplo del enunciado vuelve a responder 201 con id 2

#### Scenario: Alta por API después del seed obtiene ids coherentes con el estado inicial
- **WHEN** tras el seed se envía `POST /libros/` con el JSON del enunciado o `POST /ventas/` con el JSON del enunciado
- **THEN** las respuestas usan ids coherentes con el estado reiniciado (el libro creado obtiene el siguiente id disponible tras los 5 libros sembrados y la venta del ejemplo obtiene id 2), sin colisiones espurias con el dataset

#### Scenario: Rollback total ante falla preserva el estado previo
- **WHEN** falla la inserción de una fila del dataset durante la carga dentro de la transacción
- **THEN** la transacción se revierte completa, incluida la operación de vaciado, la base queda exactamente como estaba antes de ejecutar el seed, sin dataset parcial ni filas huérfanas, y el comando termina con código de salida 1 y mensaje propio sin internals (sin exponer SQL ni nombres de constraints)

#### Scenario: El seed solo afecta las 9 tablas del proyecto
- **WHEN** se ejecuta el seed en una base que contiene, además del esquema del proyecto, otras tablas ajenas en el mismo schema
- **THEN** el seed trunca y recarga únicamente las 9 tablas del proyecto nombradas explícitamente y no modifica ni elimina datos de tablas ajenas ni de otras bases

## MODIFIED Requirements

### Requirement: Dataset inicial determinista con ids fijos
El sistema SHALL proveer una carga de datos iniciales que, sobre una base con el esquema ya creado, inserte un dataset fijo con ids explícitos: editoriales 1–2, géneros 1–2, autores 1–5, libros 1–5, clientes 1–3, perfiles 1 y 2, venta 1 y renglones 1–2. El dataset SHALL contener 27 filas en total (2 editoriales, 2 géneros, 5 autores, 5 libros, 5 autorías, 3 clientes, 2 perfiles, 1 venta y 2 renglones), sin el libro con ISBN `978-950-00-0006-6` ni sus autorías, y con el cliente 2 como "Tomás Ríos" (`tomas@example.com`). El contenido SHALL ser idéntico en cada ejecución y quedar documentado en el README del proyecto. Los valores son datos del implementador, no reglas del enunciado.

#### Scenario: Carga sobre base vacía deja el dataset documentado (D-03)
- **WHEN** se ejecuta el seed contra una base con el esquema creado
- **THEN** la base queda con 2 editoriales, 2 géneros, 5 autores, 5 libros, 5 autorías, 3 clientes, 2 perfiles, 1 venta y 2 renglones (27 filas), con los ids indicados en el README, y `GET /libros/` devuelve 200 con 5 libros y `GET /clientes/2` devuelve 200 con nombre "Tomás Ríos" y email `tomas@example.com`

#### Scenario: El dataset deja reproducible el caso C-06 con total 77000.00
- **WHEN** tras el seed se envía `POST /ventas/` con `cliente_id: 2` y renglones libro 1 ×2 y libro 4 ×1, tal como define el caso C-06
- **THEN** el libro 1 tiene precio 25000.00 y stock 10, el libro 4 tiene precio 27000.00 y stock 7, la venta 1 ya existe con `total: 77000.00` para el cliente 2 ("Tomás Ríos"), y el alta responde 201 con precios copiados y `total: "77000.00"` en una venta nueva con id 2 (siguiente al máximo cargado)

#### Scenario: El libro con autores 3 y 4 queda cargado con los valores del enunciado
- **WHEN** se inspecciona el estado sembrado respecto al ISBN `978-950-00-0006-6` y los autores 3 y 4
- **THEN** los autores 3 y 4 existen en el dataset (autores 1–5 conservados), mientras que el libro con ISBN `978-950-00-0006-6` no está precargado en el seed para permitir su posterior creación con `POST /libros/` con los valores del ejemplo del enunciado (título "Los que aman, odian", precio 21000.00, stock 4, editorial 1, género 1, autor 3 coautor orden 1 y autor 4 coautor orden 2) respondiendo 201 en lugar de 409

### Requirement: Salida de consola propia, sin secretos, y sin efectos no definidos
El seed SHALL informar por consola un resumen propio del estado cargado y los ids relevantes del dataset, sin imprimir `DATABASE_URL` ni credenciales ni volcar SQL, trazas internas o nombres de constraints. Ante `DATABASE_URL` faltante, base inalcanzable, esquema ausente o fallo de carga SHALL terminar con código distinto de 0 y un mensaje propio. El seed SHALL NO crear ni modificar el esquema y SHALL NO aplicar reglas de negocio no definidas, en particular no descontar stock por la venta que carga.

#### Scenario: Resumen de éxito legible y sin credenciales
- **WHEN** el seed termina correctamente
- **THEN** la salida muestra el estado/dataset cargado y los ids relevantes de forma legible y no contiene la URL de la base, usuario, contraseña, SQL ni trazas internas

#### Scenario: Esquema ausente se informa sin volcar internals de la base
- **WHEN** se ejecuta el seed contra una base donde la aplicación nunca arrancó y las tablas no existen, o con `DATABASE_URL` faltante o base inalcanzable
- **THEN** el comando termina con código distinto de 0, emite un mensaje propio orientativo (indicando que debe iniciarse la aplicación al menos una vez para crear el esquema si ese es el caso) y no imprime credenciales, SQL, trazas internas ni nombres de constraints

#### Scenario: No se descuenta stock por la venta cargada (KB §1 pendiente)
- **WHEN** se inspecciona el stock de los libros 1 y 4 después del seed, que incluye la venta 1 con 2 unidades del libro 1 y 1 del libro 4
- **THEN** el stock queda en los valores documentados del dataset (libro 1 en 10 y libro 4 en 7), sin descuento, porque el descuento de stock es una pregunta abierta de la KB y no una regla implementada

## REMOVED Requirements

### Requirement: Idempotencia y secuencias alineadas tras la carga
**Reason**: El criterio anterior de idempotencia aditiva (`INSERT ... ON CONFLICT DO NOTHING`, informar insertadas/ya existían y reponer solo faltantes sin vaciar) no garantiza un estado conocido cuando existen datos creados fuera del seed y entra en conflicto con la necesidad de alinear el seed a los ejemplos del enunciado. Se reemplaza por "Repetibilidad por reinicio en la misma transacción".
**Migration**: Usar la carga por vaciado y recarga en una única transacción sobre las 9 tablas del proyecto (`TRUNCATE ... RESTART IDENTITY CASCADE` + inserción + alineación de secuencias). El resumen de consola pasa a describir el estado cargado/reiniciado en lugar de "insertadas / ya existían"; la documentación y los `.http` deben asumir que reejecutar el seed reinicia los datos al dataset documentado.
