# Design

## Context

CH-07 implementa el módulo `app/modules/ventas/` (router, schemas, service) reutilizando los modelos de tabla `Venta` y `RenglonVenta` definidos en CH-02, sin modificar esquema ni constraints. CH-05 y CH-06 ya están completados y CH-13 aplicó validaciones de rango `int4`; CH-07 debe nacer con esos límites desde su origen. El contrato y el flujo están definidos por la KB y la consigna (RN-04..RN-08, RN-10, RN-12, RT-01..RT-05, DD-02, DD-04, DD-05) y cubren C-05, C-06, C-07 parcial y D-07. Ver `proposal.md` (motivación/alcance) y `specs/ventas-renglones/spec.md` (requisitos y escenarios).

Restricciones relevantes: handlers `async def`, sin SQL concatenado, sin lazy loading (usar `joinedload`/`selectinload`), sin pre-checks de existencia (traducir `IntegrityError` a 409 con mensaje propio), dinero con `Decimal` (nunca `float`), `expire_on_commit=False`, sin PATCH/DELETE de ventas y `GET /clientes/{id}/ventas` ya resuelto en CH-06 (no tocar).

## Goals / Non-Goals

**Goals:**
- Exponer `POST /ventas/`, `GET /ventas/` y `GET /ventas/{id}` con la forma de respuesta exacta del enunciado y serialización monetaria a 2 decimales.
- Garantizar que `precio_unitario`, `total` y `fecha` los defina el servidor: precios copiados del libro (RN-06, DD-05), total calculado con `Decimal` (RN-07) y fecha con zona horaria.
- Persistir venta y renglones juntos, con validaciones declarativas (DTO/rangos `int4`, renglones no vacíos, sin libro repetido) y traducción uniforme de rechazos de integridad a 409 (RT-02, RN-12).
- Lecturas sin N+1 y con paginación estable (`order_by id`) usando carga anticipada fija (RT-04, C-07).
- Aviso diferido no bloqueante con `BackgroundTasks` y valores simples (RT-03, D-07).

**Non-Goals:**
- Modificar o extender modelos/constraints de CH-02 (`Venta`, `RenglonVenta`) ni agregar migraciones.
- Implementar PATCH/DELETE de ventas (RN-08, DD-02) o modificar `GET /clientes/{id}/ventas` (CH-06).
- Descontar stock, implementar seed, batería completa `.http` de C-01..C-08, despliegue VPS o evidencia final (CH-08..CH-12). El descuento de stock permanece como pregunta abierta KB §1.

## Decisions

### 1. Contrato de entrada y validaciones declarativas (DTO)
- **Decisión**: `VentaCreate` acepta solo `cliente_id: int` y `renglones: list[RenglonCreate]` (mínimo 1). `RenglonCreate` acepta solo `libro_id` y `cantidad`. Campos prohibidos (`precio_unitario`, `total`, `fecha`) no se declaran y el modelo rechaza extras (422). `cliente_id` y `renglones[].libro_id` usan `Field(ge=1, le=INT4_MAX)`; `cantidad` usa `Field(ge=1, le=INT4_MAX)` (límite `int4` desde el origen, alineado a CH-13). Un validador de modelo/colección detecta `libro_id` repetidos y responde 422.
- **Rationale**: Cumple RN-04/RN-05 y evita que el cliente fije valores calculados por el servidor (RN-06, RN-07). Los límites declarativos producen 422 antes del handler/lógica de negocio y evitan `DataError`/overflow de parámetros en la base (RN-10, RN-12, RT-01).
- **Alternativas**: (a) Aceptar y descartar `precio_unitario/total/fecha` silenciosamente — rechazado porque oculta errores de contrato y debilita RT-01. (b) Validar rangos en el service — rechazado porque puede llegar tarde y generar errores internos; se mantiene la convención CH-05/CH-06/CH-13 de validación en frontera.

### 2. Lectura de precios y cálculo en una transacción, sin pre-checks
- **Decisión**: En `POST /ventas/`, el service extrae los `libro_id` únicos del DTO y ejecuta **una sola** consulta `select(Libro).where(Libro.id.in_(ids))` con parámetros ligados para obtener precios (y títulos no son necesarios aquí, pero el objeto provee `precio`). Si la cantidad de libros devueltos difiere de los ids solicitados, se eleva 409 con mensaje propio (libro inexistente detectado por conjunto faltante, sin consulta de existencia previa por id). Para cada renglón se copia `precio_unitario = libro.precio` (RN-06, DD-05). El `subtotal` se calcula como `cantidad * precio_unitario` y el `total` como la suma de subtotales, ambos `Decimal` cuantizados a 2 decimales (`ROUND_HALF_UP` o cuantización explícita consistente). La `fecha` se asigna con `datetime.now(timezone.utc)` (zona horaria). Se agregan `Venta` y sus `RenglonVenta` en la misma sesión/transacción y se hace `flush/commit`.
- **Rationale**: Garantiza una única lectura de precios, evita TOCTOU por pre-checks (RT-02, DD-04) y asegura atomicidad de venta+renglones (composición, RN-04). `Decimal` evita errores de punto flotante (regla dura del proyecto).
- **Alternativas**: (a) Consultar cada libro por separado — rechazado por N+1 y mayor latencia. (b) Verificar existencia con `SELECT EXISTS` antes — rechazado por RT-02/DD-04.

### 3. Traducción de `IntegrityError` a 409 con mensaje propio
- **Decisión**: Cualquier `IntegrityError` durante el alta se captura, se hace `rollback` y se traduce a 409 con mensajes propios genéricos/seguros (p.ej. cliente o referencia inexistente / conflicto de datos), leyendo `sqlstate`/`constraint_name` cuando esté disponible (patrón de `libros`/`clientes`) pero **sin** incluir texto interno de la base en la respuesta (RN-12, RT-02). No se distingue por consultas previas: la FK de `cliente_id` inválido llegará como rechazo de base y se mapeará a 409.
- **Rationale**: Unifica el manejo de C-05 (cliente/libro inexistente) y otros conflictos de integridad con el resto del proyecto, evitando fugas de detalles internos.
- **Alternativas**: (a) Pre-validar cliente con `session.get` — rechazado por RT-02 y carrera innecesaria. (b) Propagar el error — rechazado por RN-12/RT-01.

### 4. Respuesta `VentaRead` exacta y releída precargada tras commit
- **Decisión**: Definir schemas de salida que produzcan exactamente `{id, fecha, total, cliente:{id,nombre,email}, renglones:[{libro_id, titulo, cantidad, precio_unitario, subtotal}]}`. `subtotal` es un campo calculado/serializado (`cantidad * precio_unitario`, cuantizado a 2 decimales) en el DTO de renglón de lectura (no columna en tabla). Como `expire_on_commit=False`, tras `commit` se realiza una **releída** de la venta por id con carga anticipada (`joinedload(Venta.cliente)` y `selectinload(Venta.renglones).joinedload(RenglonVenta.libro)`) y se devuelve ese objeto validado a `VentaRead`; no se retornan instancias recién creadas con relaciones sin cargar para evitar `MissingGreenlet`/lazy loads.
- **Rationale**: Cumple la forma exacta del enunciado y la regla de no lazy loading (RT-04) con el patrón ya usado en `libros` (`_leer_libro_precargado` + `flush/commit`).
- **Alternativas**: (a) `refresh` manual de relaciones — más frágil y propenso a cargas implícitas. (b) Construir dicts a mano — posible, pero más propenso a desvíos de contrato; se prefiere validar desde ORM precargado.

### 5. Lecturas sin N+1 y paginación estable
- **Decisión**: `GET /ventas/{id}` y `GET /ventas/` usan `select(Venta).options(joinedload(Venta.cliente), selectinload(Venta.renglones).joinedload(RenglonVenta.libro))`. El listado añade `.order_by(Venta.id).limit(limit).offset(offset)` (orden estable, decisión del equipo para que la paginación sea determinista entre páginas). `GET /ventas/{id}` usa `Path(le=INT4_MAX)` sin `ge=1`; un id 0 inexistente produce 404 desde el service (consistente con convención CH-05/CH-13). Listado: `limit` Query `ge=1, le=100` default 20, `offset` `ge=0, le=INT4_MAX` (RN-10).
- **Rationale**: `joinedload` para relaciones a uno (cliente, libro del renglón) y `selectinload` para la colección de renglones evita producto cartesiano y mantiene número fijo de consultas independiente de la cantidad de renglones (C-07, RT-04).
- **Alternativas**: (a) Solo `joinedload` anidado sobre colección — puede multiplicar filas; se evita. (b) Cargar títulos en consulta separada manual — innecesario si el grafo de opciones cubre `renglon.libro`.

### 6. Aviso diferido con `BackgroundTasks` y valores simples (D-07, RT-03)
- **Decisión**: El router/service del alta agenda `background_tasks.add_task(aviso_comprobante, venta_id, email_cliente)` **después** de tener la respuesta lista (FastAPI ejecuta la tarea tras enviar la respuesta). La función `aviso_comprobante(venta_id: int, email: str)` es `async`, hace `await asyncio.sleep(0.5)` y escribe un `logger.info(...)` con id y email. No recibe `AsyncSession`, ni modelos ORM, ni objetos con relaciones.
- **Rationale**: Cumple RT-03 y D-07 y evita usar una sesión cerrada o atributos diferidos post-commit.
- **Alternativas**: (a) Pasar la entidad `Venta` — rechazado (riesgo de lazy/estado de sesión). (b) Ejecutar el sleep en el handler — rechazado (bloqueante para la respuesta).

### 7. Desborde de `total` NUMERIC(12,2) (decisión del equipo, NO RN de KB/enunciado)
- **Decisión**: Antes de persistir, el service valida que el `total` calculado sea representable en `NUMERIC(12,2)` (máximo absoluto `9999999999.99`, i.e. hasta 10 dígitos enteros y 2 decimales tras cuantización). Si excede, se rechaza con **422** y mensaje propio ("El total de la venta excede el máximo permitido") sin intentar el `INSERT`.
- **Rationale**: `cantidad` admite hasta `INT4_MAX` y `precio` hasta `NUMERIC(10,2)`, por lo que el producto/suma puede superar `NUMERIC(12,2)` y provocar `DataError` (500) en PostgreSQL. Rechazar en capa de aplicación con 422 convierte un caso de borde en error de contrato/controlado y preserva RN-12/RT-01. No es una regla del enunciado ni de la KB: es una decisión defensiva del equipo ante una limitación aritmética real del esquema obligatorio.
- **Alternativas consideradas**: (a) Dejar que la base falle y traducir `DataError` a 409 — descartado porque `DataError` no es violación de integridad del mismo tipo y mezclarlo con 409 de FK/UNIQUE puede confundir; además depende de llegar a la base. (b) Traducir a 500 controlado — descartado porque el cliente envió una combinación inválida desde el punto de vista representable, y 422 comunica mejor el problema de entrada calculada. (c) Rechazar con 409 — posible por analogía a "conflicto", pero menos preciso que 422 para un desborde de valor; se prefiere 422.
- **Seguimiento**: Registrar esta decisión en la verificación/borde de tasks y en evidencia de `.http`.

## Risks / Trade-offs

- **[Riesgo] Desborde de total por cantidades/precios extremos** → Mitigación: validación previa a escritura y respuesta 422 controlada (Decisión 7); caso borde cubierto en spec/tasks.
- **[Riesgo] `MissingGreenlet`/lazy load al serializar respuesta post-commit** → Mitigación: releída con `joinedload`+`selectinload` tras `commit` (Decisión 4) y `expire_on_commit=False`.
- **[Riesgo] Conteo de consultas N+1 variable por estrategia de carga** → Mitigación: grafo de opciones fijo (`joinedload(cliente)` + `selectinload(renglones).joinedload(libro)`), verificación comparando 1 vs 3 renglones con `SQL_ECHO=true` (C-07).
- **[Riesgo] Fuga de detalles internos en errores de integridad** → Mitigación: mapeo centralizado a mensajes propios, nunca incluir `str(exc)`/orig en respuestas (RN-12).
- **[Riesgo] Detección de libros faltantes con una sola consulta** → Mitigación: comparar conjunto de ids solicitados vs ids encontrados tras `IN` y devolver 409 propio si difieren (sin pre-check por existencia individual).

## Open Questions

- **KB §1 (PENDIENTE, cátedra)**: ¿la venta descuenta `stock` del libro? **No se implementa** ningún descuento en CH-07; no se altera `Libro.stock`. Si la cátedra lo requiere, se abordará en un change separado.
- **KB §2 (PENDIENTE, cátedra)**: comportamiento de `GET /health/ready` sin base (no afecta directamente a ventas, pero es contexto del proyecto).
- **KB §6 (PENDIENTE, cátedra)**: contenido exacto del seed; CH-07 asume datos reproducibles coherentes con C-06 (cliente 2, libros 1 y 4 con precios 25000.00 y 27000.00) provistos por CH-08.
