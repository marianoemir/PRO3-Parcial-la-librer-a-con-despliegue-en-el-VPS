# Proposal

## Why

La aplicación crea las tablas vacías en el lifespan y los casos C-06 y D-03 dependen de un dataset concreto que hoy no existe: una venta con `cliente_id: 2` y renglones de libro 1 (×2 a 25000.00) y libro 4 (×1 a 27000.00) con total 77000.00, y un libro con autores 3 y 4, editorial 1, género 1, ISBN `978-950-00-0006-6` y stock 4. Sin un conjunto inicial determinista y documentado, esos casos no son reproducibles ni localmente ni en el VPS (`docker exec libreria …`, Flujo 6 paso 4), y el despliegue no puede demostrar lecturas con datos reales. CH-04 a CH-07 ya están archivados, así que el catálogo, los clientes y las ventas tienen contrato y restricciones estables sobre las que apoyar el seed.

## What Changes

- Agregar un comando de datos iniciales (**seed**) ejecutable fuera de los routers, local con `python -m app.seed` y en el contenedor con `docker exec libreria python -m app.seed`, que carga un dataset fijo, mínimo y documentado.
- Fijar ids explícitos y estables para editoriales, géneros, autores, libros, clientes, perfiles, ventas y renglones, con los valores del ejemplo de forma del enunciado (venta 1 con cliente 2 y sus dos renglones; libro 6 con autores 3 y 4, editorial 1, género 1, ISBN `978-950-00-0006-6`, precio 21000.00 y stock 4).
- Hacer el seed **idempotente**: reejecutarlo no duplica filas ni rompe unicidades (ISBN, email, nombre de editorial/género, perfil único), y siempre informa cuántas filas insertó y cuántas ya existían.
- Alinear las secuencias de las tablas con `id` serial después de cargar ids explícitos, para que un alta posterior por API obtenga un id nuevo en lugar de chocar con el dataset.
- Ejecutar la carga en una sola transacción: o queda todo el dataset, o no queda ninguna fila (sin estados parciales).
- Documentar en `README.md` el contenido del dataset (tabla de qué filas, con qué ids) y el procedimiento de carga local y en el VPS.
- Imprimir por consola un resumen legible (por tabla: insertadas/ya existentes) y devolver código de salida 0 en éxito y distinto de 0 ante fallo, sin imprimir `DATABASE_URL` ni credenciales.

## Capabilities

### New Capabilities

- `datos-iniciales`: comportamiento durable del dataset inicial reproducible e idempotente — qué filas deja la base, con qué ids, cómo se reejecuta sin corromper unicidades y cómo se ejecuta localmente y dentro del contenedor.

### Modified Capabilities

<!-- Ninguna: el seed no cambia requisitos de `foundation`, `core-models`, `editoriales-generos-autores`, `libros-autorias`, `clientes-perfil`, `ventas-renglones` ni `docker-imagen`. No expone endpoints ni modifica el esquema. -->

## Impact

- **Código afectado**: nuevo `app/seed.py` (script/comando fuera de `app/modules/*`, sin router, schemas ni service de dominio) y una sección nueva en `README.md` con el dataset y su procedimiento. No se modifican routers, services, schemas ni `models.py`, y no se toca `Dockerfile` (ya copia `app/` completo a la imagen).
- **APIs**: ninguna alta, cambio ni baja de endpoints. El seed no se expone por HTTP y no requiere que la API esté sirviendo, solo que el esquema exista.
- **Datos/reglas**: crea filas en `editorial`, `genero`, `autor`, `libro`, `libro_autor`, `cliente`, `perfil_cliente`, `venta` y `renglon_venta` respetando las restricciones ya definidas en CH-02 (RN-01, RN-02, RN-03, RN-09), la coherencia de renglones y total (RN-05, RN-06, RN-07) y el monto en `Decimal`. Ningún cambio de esquema ni de constraints; no se crean migraciones.
- **Dependencias/sistemas**: `app/core/config.py` y `app/core/database.py` para leer `DATABASE_URL` y abrir la sesión asíncrona; SQLAlchemy Core con `ON CONFLICT DO NOTHING` para la idempotencia; verificación manual por consola y `.http` (no pytest).
- **Consumidores**: CH-09 (batería `.http` C-01..C-08, incluido C-06), CH-11 (`docker exec libreria python -m app.seed` + D-03/D-04) y CH-12 (README final con pasos de carga de datos iniciales).

**Cubre**: RN-01, RN-02, RN-03, RN-05, RN-06, RN-07, RN-09, RN-12 (el seed no expone internos al usuario por HTTP), RT-02/DD-04 (la idempotencia no se apoya en pre-chequeos masivos de existencia), RT-05 (SQL parametrizado; los nombres de tabla salen de una lista constante, nunca de entrada del usuario), DD-05 y los casos **C-06** y **D-03** (los deja reproducibles). **Pendientes citados, no resueltos**: `knowledge-base/10_preguntas_abiertas.md` §(6) (lista cerrada exacta de filas base: hasta la respuesta de la cátedra el seed es determinista y se documenta en `design.md`/`README.md`) y §(1) (descuento de stock: el seed no descuenta stock por la venta cargada; deja los valores documentados). **Fuera de alcance**: endpoints y routers del dominio, PATCH/DELETE, cambios de esquema/migraciones, batería completa C-01..C-08 (CH-09), despliegue y `DEPLOY.md` (CH-10/CH-11), evidencia final y zip (CH-12), pytest (los tests del proyecto son `test/*.http`).
