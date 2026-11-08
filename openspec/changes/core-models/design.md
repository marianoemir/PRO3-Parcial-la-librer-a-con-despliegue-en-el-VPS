# Design

## Context

CH-01 archivó `foundation`: `app/main.py` con lifespan que crea motor + fábrica en `app.state` y ejecuta `SQLModel.metadata.create_all` tras importar modelos (hoy ninguno), `app/core/config.py` (lee `DATABASE_URL`, sin defecto) y `app/core/database.py` (`expire_on_commit=False`, SU-02). La spec `foundation` declara explícitamente que la verificación de "tablas creadas sobre base vacía" se completa en CH-02. Este change es el Ejercicio 2 de la consigna (PDF p. 7, 22 %): modelos, restricciones y relaciones con navegación bilateral y `Decimal` siempre. Ver `proposal.md` y la delta `specs/core-models/spec.md` como motivo y requisitos; acá solo se explica el cómo.

Restricciones que condicionan el diseño (AGENTS.md, PDF/KB prevalecen sobre cualquier skill): sin migraciones (`create_all` en lifespan), sin `float` para dinero, sin carga perezosa, sin SQL por concatenación, sin secretos, nombres de tablas/columnas del enunciado intocables, y la interacción entre módulos es solo a través de imports de modelos (skills `fastapi`/`sqlmodel` aportan patrones — `SQLModel, table=True`, `Field`, `Relationship(back_populates)`, `create_all` tras importar todo — pero no prevalecen sobre el enunciado).

## Goals / Non-Goals

**Goals:**
- Publicar los 9 modelos de tabla con todas sus restricciones de base (UNIQUE, FK con índice, CHECK), tipos y navegación bilateral, de modo que el log de arranque de `foundation` liste las 9 tablas y la base rechace por sí misma las escrituras que violan RN-01, RN-02, RN-03, RN-09 y los CHECK de autoría, venta y renglón.
- Dejar la relación lista para lecturas con precarga (`joinedload` para relaciones a uno y `selectinload` para colecciones, como Ejercicio 5 del PDF, RT-04) sin depender de carga perezosa.

**Non-Goals:**
- Endpoints, DTOs de negocio, lógica de servicio, traducción de `IntegrityError` a 409 (RN-12) y manejo de `BackgroundTasks`: eso es CH-04 a CH-07. Acá `schemas.py`, `service.py` y `router.py` de cada módulo quedan como stubs mínimos de la estructura obligatoria (`app/modules/<modulo>/{models,schemas,service,router}.py`), sin rutas ni queries.
- Seed (CH-08), casos `.http` C-01 a C-08 (CH-09) y Docker/VPS (CH-03, CH-10 a CH-12).

## Decisions

### Ubicación de cada modelo (`models.py`)

- `app/modules/editoriales/models.py` → `Editorial`, `app/modules/generos/models.py` → `Genero`, `app/modules/autores/models.py` → `Autor`, `app/modules/libros/models.py` → `Libro` + `LibroAutor`, `app/modules/clientes/models.py` → `Cliente` + `PerfilCliente`, `app/modules/ventas/models.py` → `Venta` + `RenglonVenta`. `LibroAutor` vive en `libros`, `PerfilCliente` en `clientes` y `RenglonVenta` en `ventas`, como ordena la consigna (PDF p. 6, estructura obligatoria). `health/models.py` ya existe y no se toca. Alternativa descartada: un único `models.py` global — rompería la estructura por módulo obligatoria.

### `libro_autor` como entidad con clase propia y PK compuesta (DD-01)

- `LibroAutor(SQLModel, table=True)` con `libro_id` y `autor_id` como PK compuesta (`primary_key=True` en ambos) más `rol` y `orden`. No se usa `link_model` porque el enunciado lo prohíbe expresamente ("la tabla intermedia es una entidad", PDF p. 5): `rol` y `orden` son datos propios de la relación que `link_model` escondería. Trade-off aceptado (09_decisiones_y_supuestos.md DD-01): navegación en dos saltos `libro.autorias[i].autor`. La PK compuesta además impide duplicar el par (`libro_id`, `autor_id`) sin añadir una UNIQUE artificial.

### Lado de cada clave foránea

- `libro.editorial_id → editorial.id` (agregación, PDF p. 2): la editorial ya existe y la comparten muchos libros; viajar su id es agregación. El FK vive en `libro` porque no todas las editoriales tienen libros, pero ningún libro existe sin editorial.
- `libro.genero_id → genero.id` (agregación opcional): mismo razonamiento, pero nullable porque "un libro puede no tener género" (PDF p. 2; `04_modelo_de_datos.md` §ERD). No se pone el FK en `genero` porque un género puede existir sin libros.
- `libro_autor.libro_id → libro.id` y `libro_autor.autor_id → autor.id` (muchos a muchos con datos): el FK vive en la intermedia porque la relación es muchos a muchos y el `rol`/`orden` no pertenecen a ninguno de los extremos. No se agregan columnas de autoría dentro de `libro` (no escala a varios autores) ni en `autor`.
- `perfil_cliente.cliente_id → cliente.id` (uno a uno): el FK vive en el perfil porque el perfil es parte dependiente opcional del cliente; `cliente_id` es además UNIQUE (RN-09), lo que garantiza "como máximo un perfil" sin columna inversa.
- `venta.cliente_id → cliente.id` (asociación): la venta conoce al cliente que compró, pero ninguno es parte del otro; FK en `venta` porque un cliente puede tener muchas ventas o ninguna, y una venta tiene exactamente un cliente.
- `renglon_venta.venta_id → venta.id` (composición): el renglón no tiene sentido sin su venta (PDF p. 2); FK en el renglón porque la venta es dueña del conjunto y los renglones se crean con ella (RN-04).
- `renglon_venta.libro_id → libro.id` (asociación): el renglón nombra un libro que ya existe (PDF p. 2); FK en el renglón porque la venta solo conoce libros a través de sus renglones.

### Índices (uno por FK, salvedad de la PK compuesta)

- El enunciado exige "cada clave foránea lleva un índice (PostgreSQL no lo crea solo, sección 4.10)" (PDF p. 5) y `04_modelo_de_datos.md` lo reitera: las FK se declaran con `Field(foreign_key=..., index=True)` en `libro.editorial_id`, `libro.genero_id`, `venta.cliente_id`, `renglon_venta.venta_id` y `renglon_venta.libro_id`. `perfil_cliente.cliente_id` NO lleva `index=True`: su índice es únicamente el creado por la UNIQUE `uq_perfil_cliente_cliente_id` en `__table_args__`, que ya satisface la regla sin duplicar índice.
- `libro_autor.libro_id` no lleva índice propio: está cubierto como prefijo izquierdo de la PK compuesta (`libro_id`, `autor_id`) y PostgreSQL lo usa para joins y búsquedas desde `libro`.
- `libro_autor.autor_id` lleva índice propio (`index=True`), tal como ya dice `04_modelo_de_datos.md` §libro_autor ("necesario para navegar desde `autor`; la PK solo cubre el prefijo izquierdo `libro_id`, como `turno_practica.turno_id` en el TP anterior"). Su confirmación con la cátedra queda como PENDIENTE (7) — ver "Open Questions".

### UNIQUE (delegadas a la base, DD-04 / RT-02)

- `editorial.nombre` UNIQUE `uq_editorial_nombre`, `genero.nombre` UNIQUE `uq_genero_nombre`, `libro.isbn` UNIQUE `uq_libro_isbn` (RN-01), `cliente.email` UNIQUE `uq_cliente_email` (RN-02): declaradas en `__table_args__` con `UniqueConstraint(..., name="uq_...")`, con nombres explícitos `uq_editorial_nombre`, `uq_genero_nombre`, `uq_libro_isbn`, `uq_cliente_email`. No se verifica existencia con consulta previa en ningún service (RT-02): se escribe y la base rechaza.
- `perfil_cliente.cliente_id` UNIQUE `uq_perfil_cliente_cliente_id` (RN-09): es a la vez FK e índice de unicidad; la UNIQUE se declara en `__table_args__` con `UniqueConstraint(..., name="uq_perfil_cliente_cliente_id")` y la columna se declara con `Field(foreign_key=...)` sin `index=True` (la UNIQUE ya crea el índice, uno a uno). No se agrega un `id` surrogate inverso ni UNIQUE en `cliente`.
- Todas las UNIQUE se declaran en `__table_args__` con `UniqueConstraint(..., name=...)`; no se declara ninguna UNIQUE por columna.
- Los nombres permiten a los services de CH-04 a CH-07 inspeccionar el nombre de la constraint en el `IntegrityError` y traducirlo a mensajes propios (RN-12/DD-04) sin filtrar internals de la base.
- `autor` no lleva UNIQUE extra (enunciado: "sin restricciones extra"). No se inventa ninguna UNIQUE adicional (respuesta a la duda (4): ver "Open Questions").

### CHECK (con `>=` confirmado, SU-01)

Verificados en la página 4 del PDF original, donde aparece `≥` (la extracción de texto los truncaba como `= 0` / `= 1`; ver SU-01 confirmada e IN-01 resuelta):

- `libro.precio > 0` `ck_libro_precio_positivo` y `libro.stock >= 0` `ck_libro_stock_no_negativo` (RN-03, "stock nunca es negativo").
- `libro_autor.orden >= 1` `ck_libro_autor_orden_minimo` y CHECK de conjunto cerrado para `rol` ∈ {`autor`, `coautor`, `traductor`, `ilustrador`} `ck_libro_autor_rol_valido`: ambos declarados en `__table_args__` con `CheckConstraint(..., name=...)` (el conjunto es de strings, no un CHECK numérico simple).
- `venta.total >= 0` `ck_venta_total_no_negativo`, `renglon_venta.cantidad > 0` `ck_renglon_cantidad_positiva`, `renglon_venta.precio_unitario > 0` `ck_renglon_precio_unitario_positivo`.
- Todos los CHECK se declaran en `__table_args__` con `CheckConstraint(..., name="ck_...")`, con nombres explícitos para la misma traducción a 409 propio que las UNIQUE (RN-12/DD-04); no se declara ningún CHECK por columna.

No se agregan CHECK no pedidos (por ejemplo, nada sobre `titulo` ni `nombre`).

### Tipos, nulabilidad y `Decimal`

- Dinero: `precio` y `precio_unitario` como `NUMERIC(10,2)` y `total` como `NUMERIC(12,2)`, en Python como `Decimal` (nunca `float`), según `04_modelo_de_datos.md` §Entidades y regla dura de AGENTS.md. Se usa `Field(sa_type=Numeric(10,2))` / `Numeric(12,2)` de SQLModel — escape hatch acotado de la skill, justificado porque el enunciado fija la precisión.
- `libro.genero_id` nullable (`int | None`, `nullable=True`); todos los demás FK son no nulos. `perfil_cliente.cliente_id` no nulo (sin perfil no hay fila). `fecha` de `venta` como `Field(sa_type=DateTime(timezone=True))` (SQLAlchemy `DateTime` con `timezone=True`, columna `timestamp with time zone` en la base), no `datetime` plano; se entrega tiempo aware iniciado en el servidor al crear la venta — en CH-07, no acá.
- NOT NULL: `editorial.pais`, `autor.nacionalidad`, `perfil_cliente.telefono` y `perfil_cliente.direccion` se declaran NOT NULL, igual que el resto de las columnas; la única nullable es `libro.genero_id`. **SUPUESTO explícito, no regla del enunciado**: ni la tabla del modelo de dominio del PDF (p. 4) ni `knowledge-base/04_modelo_de_datos.md` (§Entidades) declaran nulabilidad para esas cuatro columnas —solo anotan `genero_id` como "nulo permitido"—. Se asume NOT NULL para todo lo demás (tipos `str` no `Optional`, `Field(...)` sin `nullable=True`) y queda pendiente de confirmación (ver "Open Questions"); si la cátedra indica nulabilidad distinta, se ajusta como change separado.
- `id` enteros autoincrementales salvo la PK compuesta de `libro_autor` (sin columna `id` propia).

### Navegación bilateral y uno a uno

- Cada FK tiene `Relationship(back_populates=...)` en ambos extremos (PDF p. 5): `Editorial.libros` ↔ `Libro.editorial`, `Genero.libros` ↔ `Libro.genero`, `Libro.autorias` ↔ `LibroAutor.libro` y `Autor.autorias` ↔ `LibroAutor.autor`, `Cliente.perfil` ↔ `PerfilCliente.cliente`, `Cliente.ventas` ↔ `Venta.cliente`, `Venta.renglones` ↔ `RenglonVenta.venta`, `Libro.renglones` ↔ `RenglonVenta.libro`. La skill `sqlmodel` lo exige con el mismo patrón; el PDF/KB lo imponen, así que no hay conflicto.
- `Cliente.perfil` es `PerfilCliente | None` (objeto, no lista). `PerfilCliente.cliente` es el extremo inverso. `Libro.autorias` es la colección y `LibroAutor.autor` el salto al autor, para la navegación `libro.autorias[i].autor` que exige la consigna.
- La navegación queda lista para `joinedload` para relaciones a uno y `selectinload` para colecciones, como Ejercicio 5 del PDF, en CH-05/CH-07 (RT-04): ninguna lectura en este change usa carga perezosa, y `expire_on_commit=False` (SU-02, ya en `database.py`) evita expirados tras el commit.

### Stubs de `schemas.py`, `service.py`, `router.py` y `app/modules/__init__.py`

- Se crea `app/modules/__init__.py` (paquete regular; hoy solo existe `health` dentro de `modules` sin paquete propio). Cada módulo nuevo (`editoriales`, `generos`, `autores`, `libros`, `clientes`, `ventas`) recibe `schemas.py`, `service.py` y `router.py` vacíos de negocio (solo `__all__` / docstring de módulo, sin DTOs de CRUD, sin queries y sin `APIRouter` registrado), porque la estructura de 4 archivos por módulo es obligatoria (PDF p. 6) pero los contratos y endpoints llegan en CH-04 a CH-07. Declarar DTOs `Create`/`Update`/`Read` ahora duplicaría decisiones de CH-04/CH-05 y violaría el principio de que CH-02 es solo el esquema; por eso el stub es deliberado y se deja explícito acá.
- En `app/main.py` se importan TODOS los modelos (`Editorial`, `Genero`, `Autor`, `Libro`, `LibroAutor`, `Cliente`, `PerfilCliente`, `Venta`, `RenglonVenta`) ANTES de `create_all`, sustituyendo el comentario `# CH-02: importar acá...` que dejó CH-01. Sin esto, `SQLModel.metadata` quedaría incompleto y `create_all` crearía solo un subconjunto de tablas (skill `sqlmodel` §Metadata). Alternativa descartada: imports perezosos en los routers — no llegan a ejecutarse antes del `create_all` del lifespan.

### Género nullable vs. editorial obligatoria

- Solo `genero_id` es nullable. `editorial_id` es obligatorio: el enunciado no admite "libro sin editorial" (agregación obligatoria) y ningún CHECK ni UNIQUE lo sustituye. Tampoco se agrega `ondelete=CASCADE` ni borrado en cadena: no hay DELETE en todo el enunciado (DD-02, pendiente (5) confirmada por no crear endpoints).

## Risks / Trade-offs

- [Riesgo] `create_all` no altera tablas ya creadas (PDF Ejercicio 1): si la base local ya existe de CH-01 sin tablas de dominio, hay que recrearla. → Mitigación: la verificación exige base vacía y se documenta en `tasks.md` (inspección en pgAdmin Query Tool con `information_schema`).
- [Riesgo] CHECK de `rol` como conjunto cerrado implementado con `CheckConstraint` crudo: si el skill o una versión de SQLModel lo expresa distinto, la migración de sintaxis puede desviarse. → Mitigación: validar contra la salida de `pg_get_constraintdef` en pgAdmin Query Tool en la verificación.
- [Riesgo] Índice propio de `autor_id` y unicidad de `orden` pendientes de cátedra: si la cátedra responde en contra, CH-05 deberá ajustarse. → Mitigación: quedan como PENDIENTES explícitos (ver "Open Questions"); este change implementa solo lo que exige el enunciado + `04_modelo_de_datos.md` y registra la confirmación pendiente, sin resolver en silencio.
- [Trade-off] Clase propia `LibroAutor` con navegación en dos saltos: una clase más que mantener y consultas más complejas en CH-05. → Aceptado por DD-01 y la imposición explícita del enunciado.
- [Trade-off] `NUMERIC(12,2)` fijo para `total`: si un total futuro supera 10 dígitos enteros, la base lo rechazaría. → Aceptado: es la precisión del enunciado; CH-07 calcula el total por suma y no hay señal de desborde.

## Migration Plan

Sin migraciones (regla dura del enunciado): el esquema se crea con `create_all` en el lifespan. Rollback: soltar la base y volver a arrancar con base vacía. Si la base ya tenía tablas incompletas de una corrida anterior, se eliminan las tablas de dominio en el orden de composición (renglón → venta/perfil → libro_autor → libro → cliente/autor/genero/editorial) y se re-ejecuta el arranque.

## Open Questions

- **PENDIENTE (4)** — `knowledge-base/10_preguntas_abiertas.md` §(4): ¿`orden` es único dentro de un libro (UNIQUE `libro_id`+`orden`)? En este change NO se agrega esa UNIQUE; solo CHECK `orden >= 1` `ck_libro_autor_orden_minimo` + PK (`libro_id`, `autor_id`), como ordena el enunciado y `04_modelo_de_datos.md`. Confirmación pendiente con cátedra; si la respuesta es afirmativa, se agrega como change separado sobre este modelo.

- **PENDIENTE (7)** — `knowledge-base/10_preguntas_abiertas.md` §(7) más extensión: la implementación ya incluye índice propio de `autor_id` (`index=True`) según la regla del enunciado "cada FK lleva índice" (PDF p. 5) y `04_modelo_de_datos.md` §libro_autor, y `libro_id` se considera cubierto por el prefijo izquierdo de la PK compuesta. La pregunta abierta es la confirmación de suficiencia — ¿ese índice de `autor_id` es suficiente / se exige como standalone? — más la nueva duda: ¿`libro_autor.libro_id` necesita índice propio adicional más allá de la cobertura del prefijo de la PK? Igual que (4), no se resuelve en silencio: si la cátedra decide lo contrario, se ajusta como change separado.

- **SUPUESTO explícito — NOT NULL en `editorial.pais`, `autor.nacionalidad`, `perfil_cliente.telefono` y `perfil_cliente.direccion`** (sin número en `10_preguntas_abiertas.md`): el PDF (p. 4) y `04_modelo_de_datos.md` (§Entidades) no declaran nulabilidad para esas columnas —solo anotan `genero_id` como nulo permitido—, por lo que tratarlas como NOT NULL es un supuesto del equipo y no una regla del enunciado. Se implementan NOT NULL (única nullable: `libro.genero_id`) y queda pendiente la confirmación con la cátedra; si la respuesta es afirmativa, no hay cambio, y si es negativa, se ajusta la nulabilidad como change separado.

- Las demás preguntas de `10_preguntas_abiertas.md` (§(1) descuento de `stock`, §(3), §(5), §(6)) no afectan al esquema de este change y no se resuelven acá.
