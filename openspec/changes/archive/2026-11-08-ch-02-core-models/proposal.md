# Proposal

## Why

CH-01 dejó la aplicación levantada con `SQLModel.metadata.create_all` sobre un `metadata` vacío: el log de arranque lista cero tablas y no existe ningún modelo de dominio. Sin el modelo relacional completo no puede existir ningún `service` ni `router` (CH-04 a CH-07), porque todos importan los modelos y delegan en la base las garantías de unicidad, claves foráneas y CHECK. Este change publica ese modelo antes de cualquier lógica de negocio.

## What Changes

- Publicar 9 tablas con los nombres y columnas obligatorios del enunciado (`docs/Parcial_Cap1a4_Consigna.pdf`, tabla de modelo de dominio, p. 4; `knowledge-base/04_modelo_de_datos.md` §Entidades): `editorial` (`id`, `nombre`, `pais`), `genero` (`id`, `nombre`), `autor` (`id`, `nombre`, `nacionalidad`), `libro` (`id`, `isbn`, `titulo`, `precio`, `stock`, `editorial_id`, `genero_id`), `libro_autor` (`libro_id`, `autor_id`, `rol`, `orden`), `cliente` (`id`, `nombre`, `email`), `perfil_cliente` (`id`, `cliente_id`, `telefono`, `direccion`), `venta` (`id`, `cliente_id`, `fecha`, `total`), `renglon_venta` (`id`, `venta_id`, `libro_id`, `cantidad`, `precio_unitario`).
- Declarar en cada modelo las garantías que la base debe rechazar, con nombres explícitos para que los services de CH-04 a CH-07 puedan inspeccionar el nombre de la constraint en el `IntegrityError` y traducirlo a mensajes propios (RN-12/DD-04) sin filtrar internals de la base: `editorial.nombre` UNIQUE `uq_editorial_nombre`, `genero.nombre` UNIQUE `uq_genero_nombre`, `libro.isbn` UNIQUE `uq_libro_isbn` (RN-01), `cliente.email` UNIQUE `uq_cliente_email` (RN-02), `perfil_cliente.cliente_id` UNIQUE `uq_perfil_cliente_cliente_id` (RN-09, uno a uno), CHECK `precio > 0` `ck_libro_precio_positivo` y `stock >= 0` `ck_libro_stock_no_negativo` (RN-03, SU-01 confirmada), CHECK `orden >= 1` `ck_libro_autor_orden_minimo` y `rol` ∈ {`autor`, `coautor`, `traductor`, `ilustrador`} `ck_libro_autor_rol_valido`, CHECK `total >= 0` `ck_venta_total_no_negativo`, CHECK `cantidad > 0` `ck_renglon_cantidad_positiva` y `precio_unitario > 0` `ck_renglon_precio_unitario_positivo`; PK compuesta (`libro_id`, `autor_id`) en `libro_autor` con clase propia `LibroAutor` (DD-01, no `link_model`).
- Modelar dinero con `Decimal` / `NUMERIC` (nunca `float`), `fecha` de `venta` como `Field(sa_type=DateTime(timezone=True))` (SQLAlchemy `DateTime` con `timezone=True`, columna `timestamp with time zone` en la base), y navegación bilateral `Relationship(back_populates)` en ambos extremos de cada FK, lista para `joinedload` para relaciones a uno y `selectinload` para colecciones, como Ejercicio 5 del PDF, sin carga perezosa (RT-04). `Cliente.perfil` devuelve un objeto, no una lista.
- Registrar en `main.py` la importación de TODOS los modelos antes de `create_all` (ya previsto por CH-01) y crear `app/modules/__init__.py`; cada módulo queda con `models.py`, `schemas.py`, `service.py` y `router.py` en la estructura obligatoria del enunciado.
- Mantener como PENDIENTES, sin resolver en este change: `knowledge-base/10_preguntas_abiertas.md` §(4) — ¿`orden` es único dentro de un libro (UNIQUE `libro_id`+`orden`)? — y §(7) — ¿el índice de `autor_id` ya implementado es suficiente / se exige como standalone, y si `libro_autor.libro_id` (cubierto por el prefijo izquierdo de la PK compuesta) necesita índice propio adicional? El índice de `autor_id` SÍ está implementado en este change (`index=True`), tal como exige la regla del enunciado "cada FK lleva índice" y `04_modelo_de_datos.md`; la confirmación sobre su suficiencia y sobre `libro_id` queda registrada como consulta a la cátedra, sin bloquear la implementación. §(4) queda sin implementar (no se agrega UNIQUE `libro_id`+`orden`).

## Capabilities

### New Capabilities

- `core-models`: contrato observable del esquema relacional completo — tablas, columnas, UNIQUE nombrados, FK, CHECK nombrados, índices, tipos (`Decimal`/`NUMERIC`, `fecha` con `DateTime(timezone=True)`), PK compuesta de `libro_autor` y navegación bilateral. Habilita los casos de restricción C-02 a C-06 de CH-09 sin probarlos en este change.

### Modified Capabilities

- Ninguna. No se modifican los REQUIREMENTS de `foundation`: este change cumple el contrato que CH-01 dejó pendiente ("verificación completa de tablas creadas sobre base vacía") sin cambiar su comportamiento observable.

## Impact

- **Código**: `app/modules/{editoriales,generos,autores,libros,clientes,ventas}/models.py` (más `LibroAutor` en `libros`, `PerfilCliente` en `clientes`, `RenglonVenta` en `ventas`), `app/modules/__init__.py` y imports en `app/main.py`. `schemas.py`, `service.py` y `router.py` quedan como stubs mínimos de la estructura obligatoria, sin endpoints ni lógica de CRUD.
- **APIs**: sin endpoints nuevos; no hay DELETE ni PATCH de ventas.
- **Fuera de alcance**: CRUD y endpoints (CH-04 a CH-07), seed (CH-08), casos `.http` C-01 a C-08 (CH-09), Docker/VPS (CH-03, CH-10 a CH-12); las preguntas §(1) (descuento de `stock`), §(3), §(5) y §(6) no se resuelven en este change. Las reglas RT-02, RT-03, RT-05 y RN-04 a RN-08, RN-10, RN-11 se aplican en los changes que las implementan, no acá; este change solo deja el esquema que las hará cumplir.
