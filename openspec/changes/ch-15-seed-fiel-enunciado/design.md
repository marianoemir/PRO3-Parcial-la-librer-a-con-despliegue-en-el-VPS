# Design

## Context

CH-08 archivó un seed idempotente aditivo (`INSERT ... ON CONFLICT DO NOTHING`) con 30 filas que incluía el libro 6 (`978-950-00-0006-6`) y al cliente 2 como "Bruno Díaz". Eso impide reproducir literalmente los ejemplos JSON del enunciado (`POST /libros/` con ese ISBN y `POST /ventas/` con cliente 2 "Tomás Ríos" `tomas@example.com`, respuesta esperada id 2 y `total: "77000.00"`) y no garantiza un estado conocido si ya hay datos creados después. Este change (nuevo, no rectificación de CH-08) redefine el seed como carga reiniciable y fiel a esos ejemplos. Ver `proposal.md` para motivación y alcance.

Fuente de verdad: `docs/Parcial_Cap1a4_Consigna.pdf` y `knowledge-base/`. Restricciones del proyecto: sin migraciones, sin tocar routers/services/models de la API, sin `Dockerfile` ni VPS en este change, sin secretos en salida/artefactos, PostgreSQL 16 con `SQLModel.metadata.create_all` en lifespan, y las dudas no resueltas van a `knowledge-base/10_preguntas_abiertas.md`.

## Goals / Non-Goals

**Goals:**
- Dejar un dataset determinista de 27 filas alineado con los ejemplos del enunciado (cliente 2 "Tomás Ríos" `tomas@example.com`, venta 1 conservada para que el ejemplo de venta produzca id 2, sin libro 6/ISBN `978-950-00-0006-6` en el seed).
- Garantizar que cada ejecución del seed deje la base en el mismo estado inicial conocido, incluso si hay datos creados por API después.
- Preservar atomicidad total (vaciado + carga en una única transacción, rollback completo ante falla), alcance limitado a las 9 tablas del proyecto y mensajes propios sin secretos/internals.
- Actualizar specs delta (`datos-iniciales`, `casos-http-c`), `.http` dependientes, documentación de seed (`README.md`, `DEPLOY.md`), roadmap/estado (`CHANGES.md`, `.active-orchestrator-state.json`) y registrar la inferencia del "sexto libro" en KB 10.

**Non-Goals:**
- No modificar routers, services, models, `Dockerfile` ni ejecutar/resetear el VPS (D-03, D-04, D-07 quedan como tareas manuales finales).
- No implementar descuento de stock ni resolver preguntas abiertas del enunciado/cátedra; no inventar reglas.
- No reescribir CH-08 archivado ni tocar `openspec/changes/archive/`.
- No corregir el arranque "CH-01 a CH-13" de `AGENTS.md`/`CLAUDE.md` (responsabilidad de CH-12).

## Decisions

### 1. Reinicio por defecto mediante `TRUNCATE ... RESTART IDENTITY CASCADE` + recarga
- **Decisión:** El comportamiento por defecto de `python -m app.seed` será reiniciar el estado de datos del proyecto: en una única transacción ejecutar `TRUNCATE` de las 9 tablas del proyecto nombradas explícitamente con `RESTART IDENTITY CASCADE`, insertar el dataset completo y alinear secuencias según corresponda, luego confirmar. No se introduce un flag opcional.
- **Rationale:** Cumple literalmente "reejecutar reinicia los datos" y garantiza estado conocido aun con ventas/libros creados después, algo que `ON CONFLICT DO NOTHING` no puede asegurar. Hacerlo por defecto evita ambigüedad operativa en verificación local/VPS y simplifica el contrato de C-06/D-03 y los ejemplos del enunciado. El comando ya se ejecuta explícitamente y está documentado; la advertencia de reinicio se documenta en `README.md`/`DEPLOY.md`.
- **Alternativas consideradas:**
  - *Flag `--reset`*: más seguro ante ejecuciones accidentales, pero deja el modo por defecto sin garantía de estado conocido y complica la reproducibilidad exigida. Descartado para este alcance.
  - *Borrado selectivo de filas conocidas + upsert*: no elimina datos "extra" creados por API, por lo que no restablece el estado. Descartado.
  - *`DELETE` por tabla*: logra vaciado pero es más costoso y requiere cuidado con orden/FK; `TRUNCATE ... CASCADE` sobre el conjunto explícito es más directo y, combinado con `RESTART IDENTITY`, deja secuencias coherentes. Elegido `TRUNCATE`.

### 2. Alcance estricto del vaciado a las 9 tablas del proyecto
- **Decisión:** El `TRUNCATE` nombrará explícitamente `editorial`, `genero`, `autor`, `libro`, `libro_autor`, `cliente`, `perfil_cliente`, `venta`, `renglon_venta` (y solo esas), nunca `TRUNCATE` genérico sobre todo el schema ni sobre otras bases.
- **Rationale:** Evita efectos colaterales sobre tablas ajenas que pudieran coexistir en el schema y hace el impacto auditable. `RESTART IDENTITY` se aplica a las identidades/secuencias de esas tablas; la alineación final asegura ids esperados para altas posteriores.

### 3. Atomicidad y rollback total (incluido el vaciado)
- **Decisión:** Vaciado, inserciones y alineación de secuencias se ejecutan dentro de una misma transacción de base de datos. Ante cualquier excepción/error de restricción o de confirmación, se revierte toda la transacción.
- **Rationale:** PostgreSQL permite que `TRUNCATE` sea transaccional; esto garantiza que si falla una fila (o la carga) la base quede exactamente como antes, incluido lo que el vaciado habría borrado. Evita estados parciales/vacíos. Se mantiene la traducción a mensajes propios sin exponer SQL, trazas, constraints ni credenciales (RN-12).

### 4. Dataset determinista fiel al enunciado (27 filas) y sin descuento de stock
- **Decisión:** El dataset queda en: 2 editoriales, 2 géneros, 5 autores, 5 libros (ids 1–5, se elimina el antiguo libro 6 y sus 2 autorías), 5 autorías, 3 clientes, 2 perfiles, 1 venta, 2 renglones (27 filas). Cliente 2 pasa a `{"id": 2, "nombre": "Tomás Ríos", "email": "tomas@example.com"}`. La venta 1 se conserva (cliente 2, libro 1 ×2 a 25000.00, libro 4 ×1 a 27000.00, total 77000.00, fecha fija) para que el `POST /ventas/` del ejemplo reciba id 2. Precios/totales en `Decimal`, fecha con zona horaria. No se descuenta stock.
- **Rationale:** Alinea el estado sembrado con los ejemplos del enunciado y libera el ISBN `978-950-00-0006-6` para el `POST /libros/` del ejemplo (201, no 409). Autores 3 y 4, editorial 1 y género 1 se conservan (siguen referenciados). Los datos son del implementador, no reglas (KB 10 §6 pendiente). El descuento de stock sigue siendo pregunta abierta (KB 10 §1).

### 5. Resumen de consola y mensajes de error tras el cambio de estrategia
- **Decisión:** Reemplazar el resumen "insertadas / ya existían" (propio de la carga aditiva) por un resumen del estado cargado/reiniciado: conteos por tabla e ids del dataset final (y, si aplica, indicación clara de que el seed reinicia los datos de las 9 tablas del proyecto). Ante `DATABASE_URL` faltante, esquema ausente, base inalcanzable o datos/estado incompatible, terminar con código de salida distinto de 0 y mensaje propio sin credenciales, SQL, trazas ni nombres de constraints. El mensaje anterior específico de "datos incompatibles con el dataset..." se adapta para seguir siendo propio y seguro bajo la nueva estrategia (puede ocurrir, por ejemplo, ante fallos de integridad/estado que impidan completar la carga), sin filtrar internals.
- **Rationale:** El contrato observable cambia con el reinicio; el resumen debe reflejar la realidad ("estado inicial cargado") y no métricas aditivas engañosas. Se preserva RN-12/seguridad operativa.
- **Alternativas consideradas:** mantener columnas insertadas/existentes calculadas contra conteos previos; descartado por complejidad y porque el estado objetivo es siempre el dataset completo.

### 6. Ajustes en `.http` y C-07: creación única del libro del ejemplo y orden del ciclo
- **Decisión:** Resolver el choque del ISBN `978-950-00-0006-6` asegurando que dicho libro se crea **UNA SOLA VEZ** dentro de todo el ciclo de pruebas:
  - En `test/ch08-seed-datos-iniciales.http`: **NO** crea el libro con ISBN `978-950-00-0006-6`. Se limita a verificar el estado sembrado tras `python -m app.seed` (`GET /libros/` con 5 libros, `GET /clientes/2` con "Tomás Ríos", `GET /ventas/1`) y a ejecutar el `POST /ventas/` del ejemplo del enunciado (cliente 2, libro 1 ×2 a 25000.00 y libro 4 ×1 a 27000.00), verificando la respuesta 201 con `id: 2` y `total: "77000.00"`.
  - En `test/ch09-casos-http-c.http`: se ejecutan en orden C-01, C-02, C-03, C-04, C-08. En C-02a se utiliza el ISBN del libro 1 (`978-950-00-0001-1`) para verificar el rechazo 409 por ISBN repetido (dejando intacto el ISBN `978-950-00-0006-6`). En C-02b se utiliza explícitamente `tomas@example.com` (email del cliente 2 en el seed vigente) para verificar el rechazo 409 por email duplicado.
  - En `test/ch09-c07-consultas-fijas.http`: aquí es donde se ejecuta **POR ÚNICA VEZ** el `POST /libros/` con el JSON del ejemplo del enunciado (ISBN `978-950-00-0006-6`), verificando la respuesta 201 y capturando el `id` resultante para consultar su detalle y comparar la fijeza de consultas (3 SELECT vs 3 SELECT para libro 1 de una autoría vs libro creado de dos autorías).
  - En `test/ch07-ventas-errores.http`: se verifica que no dependa de "Bruno Díaz" ni del libro 6; los casos 409/422 se mantienen válidos con ids de prueba/inexistentes.
- **Orden del ciclo de pruebas:**
  1. Base vacía con esquema creado por el lifespan.
  2. Ejecución de `python -m app.seed` (carga las 27 filas iniciales).
  3. Verificación de `test/ch08-seed-datos-iniciales.http`: consulta de 5 libros, cliente 2 Tomás Ríos, venta 1 y creación de venta 2 del ejemplo con `POST /ventas/` (201, id 2, total 77000.00). Sin `POST /libros/`.
  4. Verificación de `test/ch09-casos-http-c.http`: C-01 (422), C-02a (409 usando ISBN de libro 1), C-02b (409 usando `tomas@example.com`), C-03 (409 perfil duplicado cliente 1), C-04a/b (409 referencias inexistentes), C-08 (200 `[]` ante inyección).
  5. Reutilización de C-05 desde `test/ch07-ventas-errores.http` (409 referencias inexistentes en venta).
  6. Reutilización de C-06: el `POST /ventas/` ya se ejecutó en ch08 creando la venta 2; en este paso solo se consulta `GET /ventas/2` para verificar el contrato de venta válida con subtotales calculados por el servidor sin volver a emitir el POST.
  7. Ejecución de `test/ch09-c07-consultas-fijas.http`: creación por única vez del libro con ISBN `978-950-00-0006-6` (201), comparaciones de consultas fijas (3 SELECT para libro y 2 SELECT para ventas).
- **Rationale:** Elimina la colisión 409 que ocurría si tanto ch08 como C-07 intentaban hacer el mismo `POST /libros/`, garantiza que el ISBN se prueba como alta exitosa exactamente donde se requiere su id dinámico para medir consultas fijas, y mantiene la coherencia de todo el ciclo.

### 7. Análisis de escenarios en Specs Delta (conservados, cambiados, quitados)
A continuación se detalla la correspondencia exacta por requisito contra las especificaciones consolidadas (`openspec/specs/`):

#### En `datos-iniciales/spec.md`:
- **Requirement: Dataset inicial determinista con ids fijos** (MODIFIED):
  - *Carga sobre base vacía deja el dataset documentado (D-03)*: **CAMBIADO** en el delta para reflejar el dataset de 27 filas (5 libros, 5 autorías, cliente 2 "Tomás Ríos", 2 editoriales, 2 géneros, 3 clientes, 2 perfiles, 1 venta y 2 renglones) en lugar de las 30 filas anteriores.
  - *El dataset deja reproducible el caso C-06 con total 77000.00*: **CAMBIADO** en el delta para explicitar que el cliente 2 es "Tomás Ríos" y que el alta responde 201 con id 2 y `total: "77000.00"`.
  - *El libro con autores 3 y 4 queda cargado con los valores del enunciado*: **CAMBIADO** en el delta para explicitar que los autores 3 y 4 existen en el dataset, pero el libro con ISBN `978-950-00-0006-6` NO se precarga en el seed para permitir su posterior creación con `POST /libros/` con los valores del ejemplo del enunciado (título "Los que aman, odian", precio 21000.00, stock 4, editorial 1, género 1, autor 3 coautor orden 1 y autor 4 coautor orden 2) respondiendo 201 en lugar de 409.
- **Requirement: Salida de consola propia, sin secretos, y sin efectos no definidos** (MODIFIED):
  - *Resumen de éxito legible y sin credenciales*: **CAMBIADO** para indicar que el resumen muestra el estado/dataset cargado y los ids relevantes (adaptado de la antigua métrica "insertadas / ya existían"), sin credenciales ni internals.
  - *Esquema ausente se informa sin volcar internals de la base*: **CONSERVADO / AJUSTADO** contemplando esquema ausente, `DATABASE_URL` faltante, base inalcanzable o fallo de carga con código distinto de 0 y mensaje propio.
  - *No se descuenta stock por la venta cargada (KB §1 pendiente)*: **CONSERVADO** idéntico al consolidado (libros 1 y 4 mantienen stock 10 y 7).
- **Requirement: Ejecución fuera de los routers, local y dentro del contenedor**: **QUITADO DEL DELTA** porque su texto y sus 3 escenarios son idénticos a la spec consolidada y no sufren modificaciones de comportamiento ni de contrato.
- **Requirement: Repetibilidad por reinicio en la misma transacción**: **ADDED** (nuevo requisito en el delta con 4 escenarios nuevos: reejecución tras datos por API, ids coherentes tras seed, rollback total ante fallo de carga con código 1 y mensaje propio sin internals, y alcance estricto a las 9 tablas del proyecto).
- **Requirement: Idempotencia y secuencias alineadas tras la carga**: **REMOVED** (el encabezado existe idéntico en la spec consolidada; se reemplaza la idempotencia aditiva por la repetibilidad destructiva en transacción única).

#### En `casos-http-c/spec.md`:
- **Requirement: C-02 — Unicidad rechazada con 409 propio sin huérfanos** (MODIFIED):
  - *ISBN repetido devuelve 409 propio (error esperado)*: **CONSERVADO** (usa el ISBN existente del libro 1 en C-02a).
  - *Email repetido devuelve 409 propio (error esperado)*: **CONSERVADO / AJUSTADO** (aclara que usa el email `tomas@example.com` del cliente 2 sembrado).
  - *Intento rechazado no crea libro huérfano (borde/integridad)*: **CONSERVADO** idéntico al consolidado.
- **Requirement: C-06 — Alta de venta válida calcula totales del servidor (referencia)** (MODIFIED):
  - *Venta válida con dos renglones devuelve 201 y total correcto (referencia a CH-08)*: **CONSERVADO / AJUSTADO** precisando que responde con id 2, total `"77000.00"`, precios unitarios 25000.00 y 27000.00 y subtotales 50000.00 y 27000.00 copiados del catálogo del seed de CH-15.
- **Requirement: C-07 — Detalles de libro y venta con cantidad fija de consultas** (MODIFIED):
  - *Detalle de libros con 1 y 2 autorías usa consultas fijas (caso esperado)*: **CAMBIADO** indicando que el libro con varias autorías se crea en `test/ch09-c07-consultas-fijas.http` con el `POST /libros/` del ejemplo del enunciado (ISBN `978-950-00-0006-6`) en lugar de asumir una fixture fija sembrada.
  - *Detalle de ventas con distinto número de renglones usa consultas fijas (caso esperado)*: **CONSERVADO** adaptado a las ventas creadas en el ciclo tras el seed de CH-15 (2 SELECT fijos).
- **Requirement: Regresión de casos C-01 a C-08 con el dataset de CH-15**: **ADDED** (nuevo requisito en el delta que formaliza la ejecución ordenada y regresión de C-01 a C-08 con el nuevo dataset).

### 8. Documentación y roadmap
- **Decisión:** `README.md` (solo sección seed) y `DEPLOY.md` reflejarán el dataset de 27 filas, el comando (`python -m app.seed` / `docker exec libreria python -m app.seed`) y que reejecutar reinicia los datos de las 9 tablas del proyecto. `CHANGES.md` incorporará CH-15 como change propio (estado, scope, dependencias CH-08 y CH-09, governance MEDIO, "Leer antes"), ajustará la convención (CH-15 no es rectificación), hará que CH-12 dependa también de CH-15 en texto/árbol, agregará nota fechada y conservará CRLF tocando solo líneas editadas. `.active-orchestrator-state.json` sube `roadmap.revision` a 4 y agrega CH-15. `AGENTS.md` y `CLAUDE.md` no se modifican.
- **Rationale:** Mantiene la trazabilidad del roadmap y la guía operativa coherente con el nuevo comportamiento, respetando las restricciones de formato y de identidad de instrucciones.

### 9. Pregunta abierta registrada: inferencia del "sexto libro"
- **Decisión:** Registrar en `knowledge-base/10_preguntas_abiertas.md` que "el ejemplo de `POST /libros/` crea el sexto libro" es una inferencia del equipo y no algo afirmado explícitamente por el PDF; responsable: Equipo. Mantener explícito que el seed sigue sin descontar stock.
- **Rationale:** Cumple la regla de no inventar hechos/reglas del enunciado y deja trazada la interpretación usada para alinear ids/comportamiento esperado.

## Risks / Trade-offs

- **[Reinicio destructivo de datos de proyecto en cada ejecución] →** `python -m app.seed` borra sin confirmación previa todos los datos de las 9 tablas del proyecto (`editorial`, `genero`, `autor`, `libro`, `libro_autor`, `cliente`, `perfil_cliente`, `venta`, `renglon_venta`). Apuntado contra el VPS (o cualquier base en producción/evaluación), resetea por completo lo que haya en esas tablas. **Mitigación obligatoria:** se debe incluir una advertencia altamente visible y explícita en `DEPLOY.md` y `README.md` alertando de este comportamiento destructivo antes de ejecutar `docker exec libreria python -m app.seed` o `python -m app.seed`.
- **[Pérdida de datos si falla la carga tras el TRUNCATE] →** Mitigado por transacción única: el `TRUNCATE` se revierte junto con cualquier inserción fallida.
- **[Cambios en expectativas de tests `.http`/conteos] →** Mitigado acotando ajustes a dependencias del libro 6/Bruno Díaz, preservando orden de C-01..C-08 y documentando el procedimiento de C-07 con creación única del libro del ejemplo y captura del id dinámico.
- **[C-07: ids no fijos tras reinicio+creaciones] →** Mitigado haciendo que el `.http`/tareas indiquen cómo capturar/usar el id devuelto por el `POST` del ejemplo y el orden de creación de ventas para comparar los pares correctos con conteos fijos 3/3 y 2/2.
- **[Suposiciones sobre PDF/ejemplos] →** La inferencia del "sexto libro" se registra como pregunta abierta; el dataset y expectativas se basan en los ejemplos provistos y KB, sin afirmar reglas no escritas.

## Migration Plan

1. Actualizar `app/seed.py` (dataset y carga transaccional por vaciado+recarga) y validar en base local vacía dedicada (p.ej. `libreria_c09`) con esquema creado por la app.
2. Ajustar `.http`, `README.md`, `DEPLOY.md`, `CHANGES.md`, `.active-orchestrator-state.json` y `knowledge-base/10_preguntas_abiertas.md` según alcance.
3. Verificar escenarios con `curl.exe`/`.http` y consultas SQL/`SQL_ECHO` según tasks (nunca contra VPS). Registrar evidencia como salidas reales.
4. **[MANUAL]** En el VPS: actualizar código (`git pull`), reconstruir imagen (`docker build`), recrear contenedor (`docker run`), esperar estado `healthy`, ejecutar `docker exec libreria python -m app.seed`, ejecutar D-03 y capturar D-07 con el mismo alta de venta en `docker logs`, recrear contenedor para D-04 (`docker rm -f`, `docker run`), y actualizar la hora de despliegue en `DEPLOY.md` después de este último `docker run` (Mariano, después de este change).

**Rollback (desarrollo/local):** Revertir los cambios del change en el repositorio; si se necesita volver al estado de datos anterior, restaurar desde una base/backup previo o ejecutar el seed de la versión anterior. No aplica rollback automático en VPS dentro de este change.

## Open Questions

- (Heredada, KB 10 §1) ¿La venta descuenta stock del libro? No se implementa descuento; el seed conserva stocks documentados. Responsable/decisor: Cátedra.
- (Heredada, KB 10 §6) Lista cerrada y definitiva de filas base del seed pendiente de la cátedra; el dataset es determinista y del implementador.
- (Registrada en este change, KB 10) "El ejemplo de `POST /libros/` crea el sexto libro" es una inferencia del equipo, no una afirmación explícita del PDF (responsable: Equipo).
