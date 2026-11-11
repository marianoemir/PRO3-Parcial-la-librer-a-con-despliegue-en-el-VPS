# Spec Delta

## Purpose

Permitir administrar clientes y su perfil uno a uno, y consultar de forma paginada las ventas resumidas de cada cliente sin exponer renglones.

## Requirements

### Requirement: Alta y actualización parcial de clientes
El sistema SHALL crear clientes con `nombre` y `email` mediante `POST /clientes/`, devolver 201 y un `ClienteRead`, y SHALL actualizar solamente los campos enviados en `PATCH /clientes/{id}`. `ClienteCreate` y `ClienteUpdate` SHALL rechazar todo campo no declarado, incluido `id` en el alta; `ClienteUpdate` SHALL admitir `nombre` y/o `email` omitidos, pero SHALL rechazar `{}` y `null` explícito para cualquiera de sus campos. Las respuestas SHALL usar `ClienteRead`.

#### Scenario: Alta válida de cliente
- **WHEN** se envía `POST /clientes/` con `nombre` y un `email` válidos y no registrados
- **THEN** el sistema responde 201 con `id`, `nombre`, `email` y `perfil: null`

#### Scenario: Email repetido no expone detalles de la base
- **WHEN** se envía un alta o una actualización con un `email` ya registrado para otro cliente
- **THEN** el sistema responde 409 con un mensaje propio que no contiene nombres de tablas, constraints ni trazas (RN-02, RN-12)

#### Scenario: Actualización parcial de cliente inexistente
- **WHEN** se envía `PATCH /clientes/{id}` para un id que no existe
- **THEN** el sistema responde 404

#### Scenario: Contrato de cliente inválido
- **WHEN** se envía un cuerpo que no satisface el DTO de alta o actualización, o un id de ruta que no es entero
- **THEN** el sistema responde 422 sin aplicar una escritura

#### Scenario: Campo no declarado, nulo o PATCH vacío no cambia el cliente
- **WHEN** se envía `POST /clientes/` con `id` u otro campo no declarado, o `PATCH /clientes/{id}` con un campo no declarado, con `{}`, o con `nombre` o `email` explícitamente en `null`
- **THEN** el sistema responde 422 y no crea ni modifica el cliente

### Requirement: Perfil único asociado al cliente de la ruta
El sistema SHALL crear un perfil con `POST /clientes/{id}/perfil` usando exclusivamente el id de la ruta como `cliente_id`. El `cliente_id` de ruta SHALL cumplir el rango `int4` soportado; si está fuera de rango responderá 422 sin ejecutar el handler. `PerfilCreate` SHALL incluir únicamente `telefono` y `direccion`, SHALL rechazar todo campo no declarado, incluido `id` o `cliente_id`, y la respuesta SHALL ser `PerfilRead` con `id`, `cliente_id`, `telefono` y `direccion`.

#### Scenario: Creación de perfil para cliente existente
- **WHEN** se envía un `PerfilCreate` válido a un cliente existente sin perfil
- **THEN** el sistema responde 201 con el perfil creado y su `cliente_id` coincide con el id de la ruta

#### Scenario: Segundo perfil es rechazado
- **WHEN** se intenta crear otro perfil para un cliente que ya tiene uno
- **THEN** el sistema responde 409 con un mensaje propio, sin detalles internos de la base (RN-09, RN-12; C-03)

#### Scenario: Cliente ausente al crear perfil
- **WHEN** se solicita `POST /clientes/{id}/perfil` para un id de cliente inexistente dentro de rango
- **THEN** el sistema responde 404 antes de intentar crear un perfil

#### Scenario: Id de cliente fuera de rango int4 al crear perfil devuelve 422 sin internals (rectificación CH-13)
- **WHEN** se solicita `POST /clientes/99999999999/perfil` con un cuerpo válido
- **THEN** el sistema responde 422 por validación declarativa de `Path` sin ejecutar el handler, y el cuerpo no contiene `DataError`, `Traceback`, `asyncpg`, SQL ni nombres de tablas/restricciones (RN-12)

#### Scenario: Campo no declarado en perfil no crea una fila
- **WHEN** se envía `POST /clientes/{id}/perfil` con `id`, `cliente_id` u otro campo no declarado
- **THEN** el sistema responde 422 y no crea un perfil

### Requirement: Detalle de cliente con perfil singular
El sistema SHALL responder `GET /clientes/{id}` con 200 y un `ClienteRead` que contenga `id`, `nombre`, `email` y `perfil` como un objeto `PerfilRead` o `null`. La relación perfil SHALL estar incluida sin carga perezosa y no SHALL presentarse como lista. Si el id de ruta está fuera del rango `int4` SHALL responder 422 sin ejecutar el handler.

#### Scenario: Cliente con perfil
- **WHEN** se consulta un cliente existente que tiene perfil
- **THEN** el sistema responde 200 con un único objeto `perfil` que contiene `id`, `cliente_id`, `telefono` y `direccion`

#### Scenario: Cliente sin perfil
- **WHEN** se consulta un cliente existente que todavía no tiene perfil
- **THEN** el sistema responde 200 con `perfil: null`

#### Scenario: Detalle de cliente inexistente
- **WHEN** se consulta `GET /clientes/{id}` con un id que no existe dentro de rango (incluido `999999`)
- **THEN** el sistema responde 404

#### Scenario: Id de cliente cero devuelve 404 (regresión)
- **WHEN** se consulta `GET /clientes/0`
- **THEN** el sistema responde 404 con mensaje propio (no overflow `int4`)

#### Scenario: Id de cliente fuera de rango int4 devuelve 422 sin internals (rectificación CH-13)
- **WHEN** se consulta `GET /clientes/99999999999` (o cualquier id `> 2147483647`)
- **THEN** el sistema responde 422 por validación declarativa de `Path` sin ejecutar el handler, y el cuerpo no contiene `DataError`, `Traceback`, `asyncpg`, SQL ni nombres de tablas/restricciones (RN-12)

### Requirement: Ventas resumidas de un cliente sin renglones
El sistema SHALL responder `GET /clientes/{id}/ventas` con 200 y una lista paginada de `VentaResumenRead`, que contiene `id`, `cliente_id`, `fecha` datetime y `total` Decimal, sin `renglones` ni detalles de libros y sin representar `total` como `float`.

#### Scenario: Ventas del cliente sin renglones
- **WHEN** se consulta el listado de ventas de un cliente existente con ventas y parámetros de paginación válidos
- **THEN** el sistema responde 200 con hasta `limit` resúmenes desde `offset`, ordenados ascendentemente por `id`, con `fecha` datetime, `total` Decimal y sin `renglones`

#### Scenario: Cliente existente sin ventas
- **WHEN** se consulta el listado de ventas de un cliente existente que no tiene ventas
- **THEN** el sistema responde 200 con una lista vacía

### Requirement: Paginación y validación de rango en ventas de un cliente
El sistema SHALL ordenar el listado por `Venta.id` antes de aplicar `offset` y `limit`, aceptar `limit` de 1 a 100 (20 por defecto) y `offset >= 0` dentro de `int4`, y responder 404 si el cliente no existe dentro de rango o 422 si `cliente_id` u `offset` están fuera de rango `int4`, sin ejecutar el handler.

#### Scenario: Paginación fuera de rango devuelve 422
- **WHEN** se consulta el listado con `limit` menor que 1 o mayor que 100, o con `offset` negativo
- **THEN** el sistema responde 422

#### Scenario: Id de cliente u offset fuera de rango int4 devuelve 422 sin internals (rectificación CH-13)
- **WHEN** se consulta `GET /clientes/99999999999/ventas` o `GET /clientes/<id-existente>/ventas?offset=99999999999`
- **THEN** el sistema responde 422 por validación declarativa sin ejecutar el handler ni consultas, y el cuerpo no contiene `DataError`, `Traceback`, `asyncpg`, SQL ni nombres de tablas/restricciones (RN-12)

#### Scenario: Ventas de cliente inexistente
- **WHEN** se consulta `GET /clientes/{id}/ventas` para un id que no existe dentro de rango
- **THEN** el sistema responde 404

### Requirement: Rango int4 en id de ruta para actualización de cliente

El sistema SHALL validar que el `id` de ruta en `PATCH /clientes/{id}` esté dentro del rango `int4` soportado antes de ejecutar el handler. Valores fuera de rango SHALL responder 422 sin exponer internals (RN-12); `id == 0` mantiene la semántica de inexistencia (404) cuando corresponda.

#### Scenario: Id fuera de rango en PATCH de cliente devuelve 422 (rectificación CH-13)
- **WHEN** se envía `PATCH /clientes/99999999999` con un cuerpo válido
- **THEN** el sistema responde 422 sin ejecutar el handler ni modificar filas, y el cuerpo no contiene `DataError`, `Traceback`, `asyncpg`, SQL ni nombres de tablas/restricciones

#### Scenario: Id cero en PATCH de cliente no se trata como overflow (regresión)
- **WHEN** se envía `PATCH /clientes/0` con un cuerpo válido
- **THEN** el sistema responde 404 si el cliente no existe (no 422 por overflow)
