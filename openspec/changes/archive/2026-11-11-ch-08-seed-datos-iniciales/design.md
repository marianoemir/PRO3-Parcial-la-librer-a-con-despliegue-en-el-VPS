# Design

## Context

CH-08 agrega una carga de datos iniciales sobre modelos y contratos ya cerrados: `editorial`, `genero`, `autor`, `libro`, `libro_autor`, `cliente`, `perfil_cliente`, `venta` y `renglon_venta` existen desde CH-02 con sus UNIQUE, CHECK, FK e índices; CH-04 a CH-07 ya archivados implementaron los CRUD y el alta/lectura de ventas. Ver `proposal.md` (motivación y alcance) y `specs/datos-iniciales/spec.md` (requisitos y escenarios).

Restricciones que condicionan el enfoque:

- Sin migraciones: el esquema lo crea `SQLModel.metadata.create_all` en el lifespan de `app/main.py`. El seed no define ni altera DDL.
- Dinero con `Decimal` (nunca `float`); `precio > 0`, `cantidad > 0`, `stock >= 0`, `total >= 0`.
- Garantías delegadas a la base: el seed no hace pre-chequeos masivos de existencia como sustituto de restricciones; escribe y deja que UNIQUE/FK/CHECK decidan.
- SQL parametrizado; nada de concatenar entrada de usuario. Los únicos identificadores literales son los de una lista constante del propio seed.
- El `Dockerfile` copia **solo** `app/` a la imagen (`COPY app/ ./app/`), corre como `appuser` con `WORKDIR /app` y recibe `DATABASE_URL` por `--env-file`.
- Los tests del proyecto son archivos `test/*.http` más salida real de consola; no hay pytest.

## Goals / Non-Goals

**Goals:**

- Dejar un dataset mínimo, fijo y documentado con ids explícitos que haga reproducibles C-06 y D-03 en local y en el VPS.
- Idempotencia segura: reejecutar no duplica, no rompe unicidades y repone filas faltantes.
- Dejar las secuencias alineadas para que las altas por API posteriores no choquen con los ids del dataset.
- Carga atómica (todo o nada) con salida de consola propia, sin secretos, y códigos de salida claros.

**Non-Goals:**

- Exponer endpoints, tocar routers/services/schemas de dominio o modificar el contrato HTTP.
- Cambiar el esquema, agregar columnas o migraciones; tampoco crear tablas desde el seed.
- Resolver §(1) (descuento de stock) ni §(6) (lista cerrada de filas base) de `10_preguntas_abiertas.md`.
- Implementar pruebas automatizadas con pytest o la batería completa C-01..C-08 (CH-09).
- Despliegue, `DEPLOY.md`, evidencia y zip (CH-10..CH-12).

## Decisions

### 1. Ubicación: `app/seed.py` ejecutable con `python -m app.seed`

- **Decisión**: un único módulo `app/seed.py` (dataset + runner + CLI) fuera de `app/modules/*`, sin `router.py`, `schemas.py` ni `service.py` de dominio. Se ejecuta localmente con `python -m app.seed` y en el contenedor con `docker exec libreria python -m app.seed`.
- **Rationale**: el `Dockerfile` solo copia `app/`, así que un `scripts/seed.py` en la raíz **no existiría dentro de la imagen** y `docker exec` fallaría; ubicarlo bajo `app/` garantiza que viaje en la imagen sin tocar el `Dockerfile`. `python -m app.seed` funciona con el mismo `WORKDIR /app` y el mismo usuario sin privilegios del contenedor, y no depende de que la API esté sirviendo.
- **Alternativas**: (a) `scripts/seed.py` — descartado por no estar en la imagen sin cambiar el `Dockerfile` (que pertenece a CH-03 y no se toca acá). (b) Un endpoint administrativo de seed — descartado: agrega una ruta no prevista por el enunciado, expone una escritura masiva por HTTP y contradice "script fuera de los routers". (c) Cargar el seed automáticamente en el lifespan — descartado: mezcla datos con el ciclo de vida, hace no determinista el arranque y rompería D-04/§(6) al no poder elegir cuándo cargar.

### 2. Contenido del dataset: valores fijos, coherentes con los ejemplos de forma del enunciado

- **Decisión**: el dataset es el siguiente (ids explícitos, documentados también en `README.md`):

| Tabla | id | Contenido |
|-------|----|-----------|
| `editorial` | 1 | Sudamericana — Argentina |
| `editorial` | 2 | Anagrama — España |
| `genero` | 1 | Novela |
| `genero` | 2 | Cuento |
| `autor` | 1 | Julio Cortázar — Argentina |
| `autor` | 2 | Ricardo Piglia — Argentina |
| `autor` | 3 | Adolfo Bioy Casares — Argentina |
| `autor` | 4 | Silvina Ocampo — Argentina |
| `autor` | 5 | Ernesto Sabato — Argentina |
| `libro` | 1 | ISBN `978-950-00-0001-1` — "Rayuela" — 25000.00 — stock 10 — editorial 1 — género 1 |
| `libro` | 2 | ISBN `978-950-00-0002-8` — "Bestiario" — 18000.00 — stock 6 — editorial 1 — género 2 |
| `libro` | 3 | ISBN `978-950-00-0003-5` — "La invención de Morel" — 20000.00 — stock 5 — editorial 1 — género 1 |
| `libro` | 4 | ISBN `978-950-00-0004-2` — "Respiración artificial" — 27000.00 — stock 7 — editorial 2 — género 1 |
| `libro` | 5 | ISBN `978-950-00-0005-9` — "El túnel" — 19500.00 — stock 3 — editorial 1 — género 1 |
| `libro` | 6 | ISBN `978-950-00-0006-6` — "Los que aman, odian" — 21000.00 — stock 4 — editorial 1 — género 1 |
| `libro_autor` | (1, 1) | rol `autor`, orden 1 |
| `libro_autor` | (2, 1) | rol `autor`, orden 1 |
| `libro_autor` | (3, 3) | rol `autor`, orden 1 |
| `libro_autor` | (4, 2) | rol `autor`, orden 1 |
| `libro_autor` | (5, 5) | rol `autor`, orden 1 |
| `libro_autor` | (6, 3) | rol `coautor`, orden 1 |
| `libro_autor` | (6, 4) | rol `coautor`, orden 2 |
| `cliente` | 1 | Ana Gómez — `ana.gomez@example.com` |
| `cliente` | 2 | Bruno Díaz — `bruno.diaz@example.com` |
| `cliente` | 3 | Carla Fernández — `carla.fernandez@example.com` |
| `perfil_cliente` | 1 | cliente 1 — `+54 11 5555-0001` — Av. Corrientes 1234, CABA |
| `perfil_cliente` | 2 | cliente 3 — `+54 11 5555-0003` — Calle 50 456, La Plata |
| `venta` | 1 | cliente 2 — fecha `2026-01-15T12:00:00+00:00` — total 77000.00 |
| `renglon_venta` | 1 | venta 1 — libro 1 — cantidad 2 — precio_unitario 25000.00 |
| `renglon_venta` | 2 | venta 1 — libro 4 — cantidad 1 — precio_unitario 27000.00 |

- **Rationale**: reproduce exactamente la forma de los ejemplos del enunciado (venta con `cliente_id: 2`, renglones libro 1 ×2 a 25000.00 y libro 4 ×1 a 27000.00, total 77000.00; libro con autores 3 y 4, editorial 1, género 1, ISBN `978-950-00-0006-6`, stock 4), sin inventar reglas nuevas. El total de la venta 1 es la suma de `cantidad × precio_unitario` (RN-07) y cada renglón copia el precio del libro (RN-06); los precios, el stock y los datos personales son valores fijos de ejemplo (dominio `@example.com`, no datos reales). La fecha fija con zona horaria hace el dataset determinista. Seis libros dejan un listado visible con la paginación por defecto (20) y dan margen a los casos de CH-09 sin agotar la primera página. El sufijo del ISBN coincide con el id del libro para que la tabla del README sea fácil de verificar.
- **Alternativas**: (a) Copiar literalmente solo las tres filas mencionadas en el enunciado — insuficiente para demostrar listados y FK variadas, y deja el `GET /libros/` con dos filas. (b) Generar datos aleatorios o con `faker` — descartado: rompe la reproducibilidad de C-06/D-03 y agrega dependencias. (c) Insertar sin ids y confiar en la secuencia — descartado: los casos asumen ids concretos (cliente 2, libros 1 y 4) y el dataset dejaría de ser estable entre bases.
- **Naturaleza de los datos**: son datos de ejemplo del implementador, no una regla de negocio. La lista cerrada definitiva es §(6) de `10_preguntas_abiertas.md` y sigue **pendiente de la cátedra**: hasta la respuesta, este dataset es el documentado y cualquier cambio de la cátedra se aplicará como change propio.

### 3. Idempotencia con `INSERT … ON CONFLICT DO NOTHING`, sin pre-chequeos

- **Decisión**: cada fila se inserta con SQLAlchemy Core (`insert(Tabla).values(...).on_conflict_do_nothing()`), sin `index_elements`, de modo que PostgreSQL ignore el conflicto contra **cualquier** restricción de unicidad (PK, `uq_libro_isbn`, `uq_cliente_email`, `uq_editorial_nombre`, `uq_genero_nombre`, `uq_perfil_cliente_cliente_id`, PK compuesta de `libro_autor`). Las filas insertadas se cuentan con `RETURNING id` (o con el conteo de filas devueltas); la diferencia contra el total planificado es "ya existían". El resumen por consola informa insertadas y existentes por tabla.
- **Rationale**: cumple el requisito de idempotencia sin convertir el seed en un checker de existencia (RT-02/DD-04: la base sigue siendo la garante de unicidad) y funciona igual sobre base vacía, base ya sembrada o base con una fila borrada. Es una operación de PostgreSQL, que ya es el motor impuesto.
- **Alternativas**: (a) `SELECT` previo por id/clave natural y `if not exists` — descartado como estrategia principal: es exactamente el pre-chequeo masivo que el proyecto evita, y tiene ventana TOCTOU. (b) `DELETE` + `INSERT` — descartado: borraría datos y rompería FKs de ventas/renglones. (c) Abortar si el seed ya se ejecutó — descartado: no repone filas faltantes y complica D-04.

### 4. Alineación de secuencias después del alta con ids explícitos

- **Decisión**: al final de la transacción, para cada tabla con `id` serial (`editorial`, `genero`, `autor`, `libro`, `cliente`, `perfil_cliente`, `venta`, `renglon_venta`) se ejecuta `SELECT setval(pg_get_serial_sequence('<tabla>', 'id'), COALESCE(MAX(id), 1), true)` sobre la misma conexión. `libro_autor` queda afuera porque su PK es compuesta y no tiene secuencia.
- **Rationale**: insertar ids explícitos **no** avanza la secuencia en PostgreSQL. Sin este paso, el primer `POST /editoriales/` posterior al seed intentaría `id = 1`, chocaría con la PK y devolvería un 409 espurio, rompiendo CH-04 a CH-07 y los casos de CH-09. Alinear la secuencia al máximo cargado hace que el alta obtenga el id siguiente (editorial 3, venta 2) y permite que C-06 observe la venta nueva con id 2, como en el ejemplo del enunciado.
- **Alternativas**: (a) No tocar secuencias y documentar que hay que reiniciar la base — descartado: deja la API inutilizable para altas. (b) Insertar sin ids y reescribir el dataset desde los ids devueltos — descartado: ids no deterministas. (c) `ALTER SEQUENCE … RESTART` — equivalente funcional, pero `setval` es más simple y no requiere conocer el nombre de la secuencia.
- **RT-05**: los nombres de tabla son literales de una lista constante del módulo, nunca entrada del usuario; el valor del `setval` sale de `MAX(id)` de la propia tabla. No hay concatenación con datos externos.

### 5. Transacción única y sin `create_all` en el seed

- **Decisión**: la carga completa ocurre dentro de una transacción (`async with session.begin()` o `commit` único con `rollback` en el `except`). Si una fila es rechazada por CHECK/FK/UNIQUE no ignorable (por ejemplo, una base con la misma clave natural en otro id, o una FK que apunta a un libro ausente), se revierte todo y el comando termina con error. El seed **no** ejecuta `SQLModel.metadata.create_all`: exige que el esquema ya exista y, si falta una tabla (`UndefinedTable`/`ProgrammingError`), informa que hay que iniciar la aplicación al menos una vez y sale con código distinto de 0.
- **Rationale**: el esquema es responsabilidad exclusiva del lifespan (regla dura del proyecto, sin migraciones); duplicar `create_all` en el seed repartiría esa responsabilidad y podría enmascarar un arranque roto. La transacción única garantiza que nunca quede un dataset a medias (por ejemplo venta sin renglones).
- **Alternativas**: (a) `create_all` en el seed para poder correrlo primero — descartado por la regla de esquema y porque D-03/Flujo 6 asumen contenedor arriba y luego carga. (b) Un `commit` por tabla — descartado: deja estados parciales ante error.

### 6. CLI: reutilizar `app.core`, salida propia y códigos de salida

- **Decisión**: `app/seed.py` importa los modelos (para que las FK de metadata resuelvan) sin importar `app.main`, usa `create_engine()`/`create_session_factory()` de `app/core/database.py` y valida `DATABASE_URL` con `app/core/config.py`. `main()` es `async`, se invoca con `asyncio.run(...)` y siempre cierra el motor (`await engine.dispose()`). Códigos: `0` éxito (incluida reejecución sin cambios), `1` error de configuración, conexión, esquema ausente o fallo de integridad. La salida es en español, por tabla, con insertadas/existentes e ids del dataset; nunca imprime `DATABASE_URL` ni credenciales.
- **Rationale**: reutiliza la configuración y el ciclo de vida del motor ya probados, sin abrir una segunda vía de conexión ni leer variables de entorno a mano. Cierra el motor para que el proceso no quede colgado en Windows, Docker o CI. Un mensaje propio y un código distinto de 0 hacen el comando verificable desde `docker exec` y desde consola.
- **Alternativas**: (a) `asyncpg` crudo — descartado: duplica configuración y driver. (b) Imprimir la excepción completa — descartado: puede filtrar SQL/trazas; se traduce a un mensaje propio (mismo espíritu de RN-12). (c) Códigos de salida diferenciados por causa — innecesario para el alcance; 0/1 alcanza y simplifica el `.http`/consola.

### 7. Verificación: `.http` + consola real, sin pytest

- **Decisión**: la verificación de CH-08 se hace con (a) ejecución real del seed en consola (local y, cuando exista CH-11, `docker exec`), (b) consultas de comprobación por `GET /libros/`, `GET /clientes/{id}`, `GET /ventas/1` y `POST /ventas/` documentadas en un `.http` nuevo dentro de `test/`, y (c) lectura de la base por `psql`/pgAdmin para conteos y stock. No se proponen pruebas con pytest ni Strict TDD.
- **Rationale**: respeta la regla del proyecto (los tests son archivos `test/*.http`) y el enunciado exige salidas reales como evidencia; los conteos y las secuencias no se pueden afirmar sin ejecutar.
- **Alternativas**: pytest con base efímera — descartado por regla del proyecto.

## Risks / Trade-offs

- **[Riesgo] Base con datos incompatibles** (misma clave natural en otro id, o filas que referencian ids del dataset que no existen) → ON CONFLICT ignora la fila pero la FK puede fallar y revertir todo. Mitigación: mensaje propio "la base contiene datos incompatibles con el dataset; usar una base limpia", código 1, y dataset documentado para que el operador sepa qué esperar. El seed está pensado para una base recién creada (D-02/D-03).
- **[Riesgo] Secuencias no alineadas** → altas por API con 409 espurio tras el seed. Mitigación: `setval` al máximo cargado en la misma transacción, con verificación explícita de un alta posterior (task de verificación).
- **[Riesgo] Dataset interpretado como regla de negocio** → Mitigación: proposal, design y README declaran que los valores son de ejemplo determinista y que §(6) sigue pendiente; ningún valor se agrega a `05_reglas_de_negocio.md`.
- **[Riesgo] Stock inconsistente con la venta cargada** → la venta 1 vende 2 unidades del libro 1 y 1 del libro 4, pero el stock no se descuenta (§(1) pendiente). Mitigación: se documenta explícitamente el stock cargado (10 y 7) y que no hay descuento; si la cátedra lo pide, será un change propio que también revise el dataset.
- **[Riesgo] Fuga de credenciales en la salida** → Mitigación: nunca se imprime `DATABASE_URL` ni el error crudo del driver; solo mensajes propios.
- **[Riesgo] `ON CONFLICT DO NOTHING` sin target oculta conflictos legítimos** → es el comportamiento buscado (idempotencia total), pero impide distinguir "ya existía" de "conflicto con otra fila". Mitigación: el resumen cuenta y lista por tabla; las pruebas de reejecución y de reponer una fila faltante cubren el caso esperado.

## Migration Plan

1. Local: iniciar la aplicación una vez (`uvicorn app.main:app`) para que el lifespan cree el esquema; detenerla o dejarla corriendo. Ejecutar `python -m app.seed` con `DATABASE_URL` en `.env` y verificar el resumen y los conteos.
2. VPS (cuando exista CH-11): con el contenedor `libreria` en estado `healthy`, ejecutar `docker exec libreria python -m app.seed`; verificar D-03 (`GET /libros/` con datos y `POST /ventas/` del caso C-06).
3. Reejecución: el mismo comando es seguro; informa 0 insertadas si el dataset está completo.
4. Rollback: no hay migración que revertir. Para volver a una base limpia en desarrollo se recrea la base y se deja que el lifespan cree el esquema; no se agregan endpoints de baja ni scripts de borrado. En el VPS no se borran datos: los datos viven en la base del servidor.

## Open Questions

- **KB §(6) (PENDIENTE, cátedra)**: la lista cerrada de filas base no está definida por el enunciado. Este design fija un dataset determinista y lo documenta en `README.md`; si la cátedra responde otra cosa, se ajusta el dataset y el README en un change propio. La observación de que el ejemplo devuelve `id: 2` en `POST /ventas/` —coherente con la venta 1 del seed— queda registrada como pregunta abierta, **no** como regla.
- **KB §(1) (PENDIENTE, cátedra)**: ¿la venta descuenta stock? CH-07 no descuenta y este seed tampoco: carga el stock como valor documentado. Si la cátedra lo exige, cambia el dataset final (stock posterior a la venta) y se trata como change separado.
