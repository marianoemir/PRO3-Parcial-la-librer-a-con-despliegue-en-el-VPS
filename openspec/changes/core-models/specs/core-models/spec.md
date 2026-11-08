# Spec Delta

## Purpose

Definir el contrato observable del modelo relacional de la librería: las tablas, columnas y garantías que la base rechaza, listas para ser usadas por cualquier service o router.

## ADDED Requirements

### Requirement: Esquema relacional completo creado al arrancar
Al arrancar con una base vacía, el sistema SHALL crear las 9 tablas del dominio con los nombres de tabla y columnas obligatorios del enunciado: `editorial`, `genero`, `autor`, `libro`, `libro_autor`, `cliente`, `perfil_cliente`, `venta` y `renglon_venta`.

#### Scenario: Arranque sobre base vacía crea las 9 tablas
- **WHEN** se inicia la aplicación con `DATABASE_URL` válida sobre una base vacía
- **THEN** el catálogo de la base contiene exactamente las tablas `editorial`, `genero`, `autor`, `libro`, `libro_autor`, `cliente`, `perfil_cliente`, `venta` y `renglon_venta`, y el log de arranque lista esas 9 tablas

#### Scenario: Tablas y columnas con nombres obligatorios
- **WHEN** se inspeccionan las columnas de cada tabla tras el arranque
- **THEN** `editorial` tiene (`id`, `nombre`, `pais`), `genero` (`id`, `nombre`), `autor` (`id`, `nombre`, `nacionalidad`), `libro` (`id`, `isbn`, `titulo`, `precio`, `stock`, `editorial_id`, `genero_id`), `libro_autor` (`libro_id`, `autor_id`, `rol`, `orden`), `cliente` (`id`, `nombre`, `email`), `perfil_cliente` (`id`, `cliente_id`, `telefono`, `direccion`), `venta` (`id`, `cliente_id`, `fecha`, `total`) y `renglon_venta` (`id`, `venta_id`, `libro_id`, `cantidad`, `precio_unitario`)

### Requirement: Unicidades delegadas a la base
El sistema SHALL rechazar en la base con `UNIQUE` nombrados `uq_editorial_nombre`, `uq_genero_nombre`, `uq_libro_isbn`, `uq_cliente_email` y `uq_perfil_cliente_cliente_id` los duplicados de `editorial.nombre`, `genero.nombre`, `libro.isbn`, `cliente.email` y `perfil_cliente.cliente_id`. `libro_autor` usa PK compuesta (`libro_id`, `autor_id`). Los nombres permiten traducir el `IntegrityError` a mensajes propios (RN-12/DD-04) en CH-04 a CH-07 sin filtrar internals de la base.

#### Scenario: ISBN repetido es rechazado por la base
- **WHEN** se intenta insertar un segundo `libro` con un `isbn` ya registrado
- **THEN** la base rechaza la escritura con violación de unicidad `uq_libro_isbn`, sin necesidad de una consulta previa de existencia, con `IntegrityError` y sin fila insertada

#### Scenario: Segundo perfil del mismo cliente es rechazado
- **WHEN** se intenta insertar un segundo `perfil_cliente` con un `cliente_id` que ya tiene perfil
- **THEN** la base rechaza la escritura por `UNIQUE` en `perfil_cliente.cliente_id` (`uq_perfil_cliente_cliente_id`, uno a uno, RN-09), con `IntegrityError` y sin fila insertada

#### Scenario: Email de cliente repetido es rechazado
- **WHEN** se intenta insertar un segundo `cliente` con un `email` ya registrado
- **THEN** la base rechaza la escritura por violación de unicidad `uq_cliente_email` (RN-02), con `IntegrityError` y sin fila insertada

#### Scenario: Nombre de editorial repetido es rechazado
- **WHEN** se intenta insertar una segunda `editorial` con un `nombre` ya registrado
- **THEN** la base rechaza la escritura por violación de unicidad `uq_editorial_nombre`, con `IntegrityError` y sin fila insertada

#### Scenario: Nombre de género repetido es rechazado
- **WHEN** se intenta insertar un segundo `genero` con un `nombre` ya registrado
- **THEN** la base rechaza la escritura por violación de unicidad `uq_genero_nombre`, con `IntegrityError` y sin fila insertada

### Requirement: CHECKs de libro y autoría
El sistema SHALL rechazar en la base los CHECKs nombrados `ck_libro_precio_positivo` (`precio > 0`), `ck_libro_stock_no_negativo` (`stock >= 0`), `ck_libro_autor_orden_minimo` (`orden >= 1`) y `ck_libro_autor_rol_valido` (`rol` en conjunto cerrado). Los nombres permiten traducir el `IntegrityError` a mensajes propios (RN-12/DD-04) en CH-04 a CH-07.

#### Scenario: Precio no positivo es rechazado
- **WHEN** se intenta insertar un `libro` con `precio` igual a cero o negativo
- **THEN** la base rechaza la escritura por CHECK `ck_libro_precio_positivo` (`precio > 0`), con `IntegrityError` y sin fila insertada

#### Scenario: Valores borde en el límite son aceptados
- **WHEN** se inserta un `libro` con `stock = 0`, un `libro_autor` con `orden = 1` y una `venta` con `total = 0`
- **THEN** la base acepta las tres escrituras, porque los CHECK son `>= 0` y `>= 1` (SU-01 confirmada contra el PDF, p. 4)

#### Scenario: Rol fuera del conjunto cerrado es rechazado
- **WHEN** se intenta insertar un `libro_autor` con `rol` fuera de {`autor`, `coautor`, `traductor`, `ilustrador`}
- **THEN** la base rechaza la escritura por CHECK `ck_libro_autor_rol_valido`, con `IntegrityError` y sin fila insertada

#### Scenario: Orden cero es rechazado
- **WHEN** se intenta insertar un `libro_autor` con `orden = 0`
- **THEN** la base rechaza la escritura por CHECK `ck_libro_autor_orden_minimo` (`orden >= 1`), con `IntegrityError` y sin fila insertada

#### Scenario: Stock negativo es rechazado
- **WHEN** se intenta insertar un `libro` con `stock` negativo
- **THEN** la base rechaza la escritura por CHECK `ck_libro_stock_no_negativo` (`stock >= 0`), con `IntegrityError` y sin fila insertada, mientras que `stock = 0` sigue siendo válido

### Requirement: CHECKs de venta y renglón
El sistema SHALL rechazar en la base los CHECKs nombrados `ck_venta_total_no_negativo` (`total >= 0`), `ck_renglon_cantidad_positiva` (`cantidad > 0`) y `ck_renglon_precio_unitario_positivo` (`precio_unitario > 0`). Los nombres permiten traducir el `IntegrityError` a mensajes propios (RN-12/DD-04) en CH-04 a CH-07.

#### Scenario: Cantidad cero es rechazada
- **WHEN** se intenta insertar un `renglon_venta` con `cantidad = 0`
- **THEN** la base rechaza la escritura por CHECK `ck_renglon_cantidad_positiva` (`cantidad > 0`), con `IntegrityError` y sin fila insertada

#### Scenario: Precio unitario cero es rechazado
- **WHEN** se intenta insertar un `renglon_venta` con `precio_unitario = 0`
- **THEN** la base rechaza la escritura por CHECK `ck_renglon_precio_unitario_positivo` (`precio_unitario > 0`), con `IntegrityError` y sin fila insertada

#### Scenario: Total negativo es rechazado
- **WHEN** se intenta insertar una `venta` con `total` negativo
- **THEN** la base rechaza la escritura por CHECK `ck_venta_total_no_negativo` (`total >= 0`), con `IntegrityError` y sin fila insertada, mientras que `total = 0` sigue siendo válido

### Requirement: Claves foráneas, tipos y nulabilidad delegados a la base
El sistema SHALL crear claves foráneas con índice en cada FK (con la excepción de `libro_autor.libro_id` cubierto por la PK compuesta), representar el dinero con `Decimal` / `NUMERIC` (nunca `float`), declarar `venta.fecha` como `Field(sa_type=DateTime(timezone=True))` (SQLAlchemy `DateTime` con `timezone=True`, columna `timestamp with time zone` en la base), y permitir `genero_id` nulo en `libro`.

#### Scenario: FK inexistente es rechazada por la base
- **WHEN** se intenta insertar un `libro` con un `editorial_id` que no existe
- **THEN** la base rechaza la escritura por violación de clave foránea, sin consulta previa de existencia, con `IntegrityError` y sin fila insertada

#### Scenario: Libro sin género es válido
- **WHEN** se inserta un `libro` con `genero_id` nulo y `editorial_id` válido
- **THEN** la base acepta la escritura y el `libro.genero_id` queda nulo

#### Scenario: Fecha con zona horaria verificada en la base
- **WHEN** se inspecciona la columna `fecha` de `venta` en la base
- **THEN** el tipo es `timestamp with time zone`, creado desde `Field(sa_type=DateTime(timezone=True))`

### Requirement: Navegación bilateral y uno a uno sin carga perezosa
El sistema SHALL declarar navegación en ambos extremos de cada relación (editorial–libro, género–libro, libro–libro_autor–autor, cliente–perfil_cliente, cliente–venta, venta–renglon_venta, libro–renglon_venta), de modo que `Cliente.perfil` devuelva un objeto único (no una lista) y toda lectura pueda precargar las relaciones en la misma consulta (`joinedload` para relaciones a uno y `selectinload` para colecciones, como Ejercicio 5 del PDF).

#### Scenario: Navegación de libro a autorías y autor en ambos sentidos
- **WHEN** se consulta un `libro` con precarga de `editorial`, `genero` y `autorias` y se recorre `libro.autorias[i].autor`
- **THEN** cada autoría expone su `autor` con `rol` y `orden`, y desde el `autor` se llega de vuelta a sus autorías con número fijo de consultas (sin N+1, RT-04)

#### Scenario: Perfil del cliente es un objeto único precargable
- **WHEN** se consulta un `cliente` con precarga de su perfil
- **THEN** `cliente.perfil` es un objeto único con `telefono` y `direccion`, o `None` si el cliente no tiene perfil, nunca una lista
