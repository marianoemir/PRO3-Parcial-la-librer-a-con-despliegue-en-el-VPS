# Spec Delta

## Purpose

Definir el contrato observable para registrar ventas con renglones anidados y consultar ventas con detalle y paginación, donde el servidor copia precios del catálogo, calcula el total y la fecha, responde con la forma exacta del enunciado y ejecuta lecturas sin N+1 con un aviso diferido en segundo plano.

## ADDED Requirements

### Requirement: Alta de venta con renglones anidados y valores calculados por el servidor
El sistema SHALL aceptar `POST /ventas/` con un cuerpo que contenga únicamente `cliente_id` y `renglones` (lista de objetos con `libro_id` y `cantidad`). El sistema SHALL rechazar con 422 cuerpos que incluyan `precio_unitario`, `total` o `fecha`, que no tengan al menos un renglón, que repitan el mismo `libro_id`, o que incumplan el contrato/rangos de tipo (RN-04, RN-05, RT-01). Para una venta válida, el sistema SHALL leer los libros referenciados en una única consulta por ids, copiar `precio_unitario` desde cada `Libro`, calcular `subtotal = cantidad × precio_unitario` por renglón y `total = Σ(cantidad × precio_unitario)` con `Decimal` cuantizado a 2 decimales, asignar `fecha` en el servidor con zona horaria, y persistir la venta junto con sus renglones antes de responder (RN-06, RN-07, DD-05). La respuesta SHALL ser 201 con `VentaRead` en la forma `{ id, fecha, total, cliente:{id,nombre,email}, renglones:[{libro_id, titulo, cantidad, precio_unitario, subtotal}] }`, con `total`, `precio_unitario` y `subtotal` serializados como valores decimales de 2 decimales (ej. `"77000.00"`), obtenida mediante releída precargada tras el commit para evitar relaciones no cargadas.

#### Scenario: Alta válida calcula precios, subtotales y total (C-06)
- **WHEN** se envía `POST /ventas/` con `cliente_id: 2` y `renglones: [{libro_id: 1, cantidad: 2}, {libro_id: 4, cantidad: 1}]`, donde los libros existen con precios 25000.00 y 27000.00 respectivamente
- **THEN** el sistema responde 201 con una venta cuyo `cliente` es `{id: 2, nombre, email}` correspondiente, `renglones` contiene libro 1 con `cantidad: 2`, `precio_unitario: "25000.00"`, `subtotal: "50000.00"` y libro 4 con `cantidad: 1`, `precio_unitario: "27000.00"`, `subtotal: "27000.00"`, `total: "77000.00"`, `fecha` asignada por el servidor y sin campos `precio_unitario`, `total` ni `fecha` aceptados desde el cuerpo de entrada

#### Scenario: Cliente o libro inexistente devuelve 409 propio (C-05)
- **WHEN** se envía `POST /ventas/` con un `cliente_id` inexistente o con algún `renglones[].libro_id` inexistente (detectado porque falta en el resultado de la lectura de libros)
- **THEN** el sistema responde 409 con mensaje propio, sin realizar pre-checks de existencia previos a la escritura y sin exponer nombres de tablas, constraints, SQL ni trazas internas (RN-12, RT-02, DD-04)

#### Scenario: Renglones vacíos, libro repetido o campos prohibidos devuelven 422
- **WHEN** se envía `POST /ventas/` con `renglones: []`, o con dos renglones que referencian el mismo `libro_id`, o con `precio_unitario`, `total` o `fecha` presentes en el cuerpo
- **THEN** el sistema responde 422, no persiste venta ni renglones y no expone detalles internos de la base (RN-04, RN-05, RT-01)

#### Scenario: Total desbordado del rango NUMERIC(12,2) se rechaza con error controlado (decisión de diseño)
- **WHEN** se envía `POST /ventas/` cuyos `cantidad` y precios copiados producen un `total` que excede la precisión/escala soportada por `NUMERIC(12,2)`
- **THEN** el sistema rechaza la operación antes de escribir con un error HTTP controlado (422 según la decisión de `design.md`), con mensaje propio y sin `DataError`, SQL, trazas ni nombres de tablas/constraints en la respuesta (RN-12)

### Requirement: Lectura de ventas con forma exacta, paginación estable y sin N+1
El sistema SHALL exponer `GET /ventas/{id}` y `GET /ventas/` devolviendo `VentaRead` (o lista de `VentaRead`) con la forma `{ id, fecha, total, cliente:{id,nombre,email}, renglones:[{libro_id, titulo, cantidad, precio_unitario, subtotal}] }`. Las consultas SHALL precargar de forma anticipada el cliente, los renglones y el libro de cada renglón (`joinedload`/`selectinload`) para resolver `cliente` y `titulo` sin carga perezosa y con número fijo de consultas independiente de la cantidad de renglones (RT-04, C-07). `GET /ventas/` SHALL ordenar por `id` ascendente para paginación estable y aceptar `limit` entre 1 y 100 (default 20) y `offset >= 0` dentro de `INT4_MAX`; `GET /ventas/{id}` SHALL validar `id <= INT4_MAX` sin imponer `ge=1` (id 0 responde 404 si no existe). Los valores monetarios SHALL serializarse como decimales de 2 decimales.

#### Scenario: Detalle de venta existente con relaciones precargadas
- **WHEN** se consulta `GET /ventas/{id}` para una venta existente con uno o más renglones
- **THEN** el sistema responde 200 con `VentaRead` incluyendo `cliente{id,nombre,email}` y cada renglón con `libro_id`, `titulo`, `cantidad`, `precio_unitario` y `subtotal`, sin errores de carga perezosa

#### Scenario: Listado paginado estable y ordenado por id
- **WHEN** se consulta `GET /ventas/?limit=20&offset=0` con ventas existentes
- **THEN** el sistema responde 200 con una lista de `VentaRead` ordenada por `id` ascendente, respetando `limit` y `offset`, con la misma forma de respuesta que el detalle

#### Scenario: Id 0 inexistente y parámetros de paginación inválidos devuelven errores controlados
- **WHEN** se consulta `GET /ventas/0`, o `GET /ventas/?limit=0`, o `GET /ventas/?limit=101`, o `GET /ventas/?offset=-1`
- **THEN** el detalle con id 0 responde 404 si no existe (sin imponer `ge=1`), y los parámetros de paginación fuera de rango responden 422, en todos los casos sin exponer internos de la base (RN-10, RN-12, RT-01)

#### Scenario: Evidencia de consultas fijas sin N+1 (C-07)
- **WHEN** se ejecuta `GET /ventas/{id}` con `SQL_ECHO=true` para una venta con 1 renglón y para otra con 3 renglones
- **THEN** la cantidad total de consultas SQL emitidas para resolver cada detalle es la misma, y la salida se puede guardar como evidencia en `test/` o consola según la tarea de verificación

### Requirement: Límites de rango int4 y validaciones declarativas en ventas
El sistema SHALL aplicar límites declarativos usando `INT4_MAX` de `app/core/constants.py`: `GET /ventas/{id}` con `Path(le=INT4_MAX)` (sin `ge=1`), `GET /ventas/` con `limit` 1–100 y `offset >= 0` y `<= INT4_MAX`, y `POST /ventas/` con `cliente_id` y `renglones[].libro_id` como `Field(ge=1, le=INT4_MAX)` y `cantidad` como `Field(ge=1, le=INT4_MAX)`. Cualquier valor fuera de rango o tipo inválido SHALL responder 422 por validación antes de ejecutar lógica de negocio/consultas de escritura, sin pre-checks y sin exponer `DataError`, `Traceback`, `asyncpg`, SQL ni nombres de tablas/constraints (RN-10, RN-12, RT-01).

#### Scenario: Id de detalle fuera de int4 devuelve 422 sin internals
- **WHEN** se consulta `GET /ventas/99999999999`
- **THEN** el sistema responde 422 por validación declarativa sin ejecutar el handler de negocio y sin exponer detalles internos de la base

#### Scenario: Body con ids o cantidad fuera de int4 devuelve 422 sin internals
- **WHEN** se envía `POST /ventas/` con `cliente_id`, algún `renglones[].libro_id` o alguna `cantidad` igual a `99999999999` (o cualquier valor > `INT4_MAX`)
- **THEN** el sistema responde 422, no realiza consultas de escritura ni pre-checks de existencia y la respuesta no contiene internos de la base

### Requirement: Aviso diferido de comprobante sin bloquear la respuesta (D-07)
El sistema SHALL agendar, mediante `BackgroundTasks`, una tarea asíncrona que ejecute `await asyncio.sleep(0.5)` y registre un mensaje en el log indicando el aviso del comprobante de la venta, únicamente después de preparar/devolver la respuesta exitosa del alta. La tarea NO SHALL recibir ni usar la sesión de base de datos ni objetos ORM; SHALL recibir solo valores simples ya extraídos (id de la venta y email del cliente). El handler y la tarea SHALL ser no bloqueantes (RT-03).

#### Scenario: Mensaje de aviso aparece en el log después de la respuesta del alta (D-07)
- **WHEN** se realiza un `POST /ventas/` exitoso
- **THEN** la respuesta HTTP 201 se completa sin esperar el sleep y, aproximadamente 0.5 segundos después, aparece en los logs del servidor/contenedor una línea de aviso con los valores simples de la venta (id y email del cliente)

#### Scenario: La tarea en segundo plano no depende de la sesión ni de relaciones ORM
- **WHEN** la tarea diferida se ejecuta tras el commit de la venta
- **THEN** utiliza únicamente los valores simples provistos (id de venta, email) y no accede a `AsyncSession` ni a instancias ORM, evitando errores por sesión cerrada u objetos expirados
