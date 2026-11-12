# CHANGES — Secuencia de Implementación

> Índice canónico de todos los changes del proyecto **Parcial Programación III — La Librería con Despliegue en el VPS**.
> Cada change es atómico: un agente puede implementarlo en una sesión (~4-6 horas).
> **Leer este archivo antes de ejecutar cualquier `/opsx:propose`.**
> **Convención de códigos**: `CH-01`–`CH-12` y `CH-15` = changes propios de este roadmap; `CH-13`–`CH-14` = rectificaciones del roadmap (aplicadas/documentadas); `C-01`–`C-08` = casos de prueba de la cátedra (no confundir). Los casos `D-01`–`D-07` son los de despliegue en VPS.

---

## Cómo usar este documento

1. Identificar el change a implementar (verificar que sus dependencias están en `openspec/changes/archive/`).
2. Leer los docs de la knowledge-base indicados en "Leer antes".
3. Ejecutar `/opsx:propose <nombre-del-change>`.
4. Al terminar el change, archivarlo con `/opsx:archive <nombre-del-change>`.
5. Marcar el checkbox `[x]` en este archivo.

---

## Rectificaciones

- **CH-13 `ch-13-validacion-rango-int4` (aplicado):** corrige de forma transversal el bug de validación de rango `int4` detectado tras CH-04 en los módulos implementados de **CH-05 (`libros-autorias`)** y **CH-06 (`clientes-perfil`)**: ids de ruta, `offset`/`genero_id` de listados y body ids/enteros de entrada (incluido `autores[].orden`) fuera de rango (`> 2147483647`, ej. `99999999999`) responden **422** sin ejecutar handler/consulta de negocio y sin exponer internos de la base (RN-12). `id == 0` mantiene 404 donde la inexistencia la resuelve el service (decisión CH-05). **Ventas queda excluida del alcance de CH-13** porque `app/modules/ventas/` existe solo como stubs y CH-07 (`ventas-renglones`) está pendiente: el change propio de ventas (CH-07) debe nacer con estos límites `int4` desde su origen (path `GET /ventas/{id}`, `offset`/`limit` RN-10 en `GET /ventas/`, body ids `cliente_id` y `renglones[].libro_id`, `id==0`→404, 422 sin internals y sin pre-check RT-02/DD-04). Artefactos: `openspec/changes/ch-13-validacion-rango-int4/` (alcance reducido a libros/clientes).
- **CH-14 `ch-14-rectificacion-active-stack` (documentado 2026-11-11, archivado 2026-11-12):** rectificación metodológica Active Stack/SDD sin tocar app ni `.http` ni archivados. Agrega `specs/casos-http-c/spec.md` para cubrir la omisión de specs en CH-09 (C-01..C-08, referencias a C-05/C-06 existentes, C-07 con conteos observados en base local vacía con seed) y documenta auditoría B.1–B.8 con evidencia de herramienta. **CH-13 está reflejado en `openspec/specs`** (`cli_missing=0` y `lib_missing=0`: los requisitos del delta están en `openspec/specs`; el hash distinto es esperable entre delta y spec consolidada). Hallazgos confirmados: CH-09 sin specs, CH-13 sin `.openspec.yaml`, CH-05 con `README.md` extra, CH-10 con tareas sin tildar, ruta no archivada citada en nota CH-13 y CH-11 manual/no archivado con brecha de proceso respecto a CH-12. CH-11 queda registrado como completado a mano (2026-11-11) sin propose/apply ni carpeta archivada. Se propone una excepción formal al checklist 4.4 de la guía para que CH-12 pueda avanzar (recomendación O3 + nota de evidencia O1); pendiente de confirmación de Facundo y Andrés, que fijará la fecha de la excepción. Evidencia: DEPLOY.md y evidencia/D-03, D-04 y D-07. No se inventa propose retroactivo.

---

## Árbol de dependencias

```
CH-01 foundation-setup
  │
  ├── CH-02 core-models (los modelos y el esquema van antes de cualquier service/router)
  │     │
  │     ├── CH-04 crud-editoriales-generos-autores
  │     ├── CH-05 libros-autorias
  │     │     └── CH-13 validacion-rango-int4 (rectificación aplicada, CH-05 ✓ + CH-06 ✓)
  │     └── CH-06 clientes-perfil
  │           ├── CH-13 validacion-rango-int4 (ver arriba)
  │           └── CH-07 ventas-renglones (CH-05 ✓ + CH-06 ✓)
  │                    │
  │                    └── CH-08 seed-datos-iniciales
  │                          │
  │                          ├── CH-09 casos-http-C
  │                          │      └── CH-15 seed-fiel-enunciado (CH-08 ✓ + CH-09 ✓)
  │                          │            └── CH-12 evidencia-entrega (CH-09 ✓ + CH-11 ✓ + CH-15)
  │                          │                  └── CH-16 mapa-casos-y-evidencia-c07 (CH-12 tanda a ✓ + CH-15 ✓ + CH-09 ✓)
  │                          ├── CH-11 despliegue-vps-datos (CH-10 ✓ + CH-08 ✓; DEPLOY.md se escribe acá)
  │                          │      └── CH-12 evidencia-entrega (ver arriba)
  │
  └── CH-03 docker-imagen (solo necesita CH-01; arranca temprano, DD-06)
        └── CH-10 despliegue-vps-inicial (CH-02 ✓ + CH-03 ✓; detección temprana red/host.docker.internal)
              └── CH-11 despliegue-vps-datos (ver arriba)

CH-14 rectificacion-active-stack (rectificación documental/método, 2026-11-11): spec CH-09 + auditoría; no altera dependencias ni estados de CH-01–CH-13
```

### Paralelismo por fase

> Cada "gate" es un punto de sincronización. Los changes dentro de un grupo pueden ejecutarse en paralelo.

```
GATE 0: ninguna
  → CH-01 foundation-setup (solo)

GATE 1: CH-01 ✓
  → CH-02 core-models                 [Agente A — Backend Core]
  → CH-03 docker-imagen               [Agente C — Infra/DevOps · arranca temprano, DD-06]

GATE 2: CH-02 ✓                     ← FORK (4 cambios)
  → CH-04 crud-editoriales-generos-autores  [Agente B — Backend Aux]
  → CH-05 libros-autorias            [Agente A]
  → CH-06 clientes-perfil            [Agente B]
  → CH-10 despliegue-vps-inicial      [Agente C — si CH-03 ✓; detección temprana de red y host.docker.internal]

GATE 3: CH-05 ✓ + CH-06 ✓
  → CH-07 ventas-renglones           [Agente A]

GATE 4: CH-07 ✓ (+ CH-04 ✓)
  → CH-08 seed-datos-iniciales       [Agente B]

GATE 5: CH-08 ✓
  → CH-09 casos-http-C               [Agente B]
  → CH-11 despliegue-vps-datos       [Agente C — si CH-10 ✓]

GATE 6: CH-09 ✓ + CH-11 ✓
  → CH-12 evidencia-entrega          [Agente C]
```

### Camino crítico (7 changes — mínimo irreducible)

```
CH-01 → CH-02 → CH-05 → CH-07 → CH-08 → CH-11 → CH-12
```

> `CH-09` corre en paralelo con `CH-11` y **también bloquea** el cierre (`CH-12` espera a `CH-09` y `CH-11`); por eso no aparece en la cadena lineal, pero ningún change de cierre puede saltearlo. `CH-03` y `CH-04` / `CH-06` son paralelos que adelantan el despliegue y la cobertura, no el mínimo irreducible. `CH-10` (despliegue-vps-inicial) corre temprano en paralelo tras `CH-02`+`CH-03` para detectar problemas de red/`host.docker.internal` antes de los datos; `CH-11` espera a `CH-10` y a `CH-08`. `CH-13` (rectificación aplicada) depende de `CH-05` y `CH-06` y no altera el camino crítico pendiente.

### Plan óptimo con 3 agentes

```
Paso │ Agente A (Backend Core) │ Agente B (Backend Aux)        │ Agente C (Infra/DevOps)
─────┼─────────────────────────┼───────────────────────────────┼──────────────────────────────
  1  │ CH-01 foundation-setup  │              —                │             —
  2  │ CH-02 core-models       │              —                │ CH-03 docker-imagen
  3  │ CH-05 libros-autorias   │ CH-06 clientes-perfil         │ CH-10 despliegue-vps-inicial
  4  │ CH-07 ventas-renglones  │ CH-04 crud-referencia         │             —
  5  │            —            │ CH-08 seed-datos-iniciales    │             —
  6  │            —            │ CH-09 casos-http-C            │ CH-11 despliegue-vps-datos
  7  │            —            │              —                │ CH-12 evidencia-entrega
```

---

## FASE 0 — Cimientos

### [CH-01] `foundation-setup`
- **Estado**: `[x]` completado
- **Scope**: Levantar la aplicación asincrónica con lifespan y health (US-001)
  - Dueño potencial: Agente A (Backend Core) — una sesión (~4-6 h)
  - Casos cubiertos: ninguno directo; habilita el arranque para todos los casos C/D
  - Estructura: `app/main.py`, `app/core/config.py` (lee `DATABASE_URL`), `app/core/database.py` (motor async + fábrica de sesiones, `get_session`), `requirements.txt` (Python 3.12, FastAPI ≥0.111, SQLModel, SQLAlchemy 2.0 async, asyncpg, python-dotenv), `env.example` (forma de `DATABASE_URL` con driver `postgresql+asyncpg` + `SQL_ECHO=false`, sin secretos), `.env` no versionado, `.gitignore` excluye `.env`, `.venv`, `__pycache__` y `*.bak`
  - Lifespan: crea motor + fábrica de sesiones en `app.state`, `SQLModel.metadata.create_all` con todos los modelos importados (el change CH-02 registra sus tablas acá), **si la base no responde el arranque falla** (no queda sirviendo), al apagar cierra el motor; sesiones por petición con `expire_on_commit=False` (SU-02)
  - `GET /health/live` (no toca la base) y `GET /health/ready` (`SELECT 1`); escucha en `0.0.0.0`
  - Si `DATABASE_URL` no está definida, el proceso termina con error claro y sin valor por defecto (cubre D-05); `database.py` lee `SQL_ECHO` para `echo` del motor (default `false`)
  - **PENDIENTE (no resolver acá)** — `10_preguntas_abiertas.md` §(2) (Q2): qué devuelve `GET /health/ready` y con qué código si la base no responde. Decisión del equipo (a documentar en design.md, a confirmar con cátedra — Q2/10_preguntas_abiertas.md pendiente, no es regla del enunciado): GET /health/ready responde 503 con cuerpo propio si SELECT 1 falla; ese código define el `HEALTHCHECK` de CH-03 y el caso D-05 de CH-10
- **Dependencias**: ninguna
- **Governance**: MEDIO
- **Leer antes**:
  - `knowledge-base/02_descripcion_general.md` §Stack tecnológico y §Arquitectura general
  - `knowledge-base/08_arquitectura_propuesta.md` §Patrones (lifespan, `app.state`, `get_session`) y §Variables de entorno
  - `knowledge-base/07_flujos_principales.md` §Flujo 1: Arranque y ciclo de vida
  - `knowledge-base/10_preguntas_abiertas.md` §(2) — PENDIENTE

### [CH-02] `core-models`
- **Estado**: `[x]` completado
- **Scope**: Publicar el modelo relacional completo — va ANTES de cualquier service o router (US-002)
  - Dueño potencial: Agente A (Backend Core) — una sesión (~4-6 h)
  - Casos cubiertos: ninguno directo; habilita los casos de restricción C-02 a C-06 (los prueba CH-09)
  - Tablas (nombres obligatorios, no quitar ni renombrar): `editorial` (`nombre` UNIQUE), `genero` (`nombre` UNIQUE), `autor`, `libro` (`isbn` UNIQUE, CHECK `precio > 0`, CHECK `stock >= 0`, FK `editorial_id`, FK `genero_id` nula permitida), `libro_autor` (clase `LibroAutor` propia, DD-01, no `link_model`; PK compuesta, CHECK `rol` ∈ autor/coautor/traductor/ilustrador, CHECK `orden >= 1`), `cliente` (`email` UNIQUE), `perfil_cliente` (`cliente_id` UNIQUE, uno a uno), `venta` (`fecha` con zona, `total` NUMERIC(12,2), CHECK `total >= 0`), `renglon_venta` (composición con `venta`, CHECK `cantidad > 0`, `precio_unitario > 0`)
  - Dinero con `Decimal`, nunca `float`; navegación bilateral `Relationship(back_populates=.)` en ambos extremos de cada FK; `Cliente.perfil` devuelve un objeto, no una lista
  - CHECK con `≥` ya confirmados contra el PDF (IN-01 resuelta, SU-01 confirmada): `stock >= 0`, `orden >= 1`, `total >= 0`
  - **PENDIENTE (no resolver acá)** — `10_preguntas_abiertas.md` §(4): ¿`orden` es único dentro de un libro (UNIQUE `libro_id`+`orden`)? §(7): ¿`autor_id` lleva índice propio en `libro_autor`? Se implementa lo que exige el enunciado (índice de cada FK) y lo que ya dice `04_modelo_de_datos.md` para `autor_id`, y se registra la confirmación pendiente
- **Dependencias**: CH-01
- **Governance**: CRITICO
- **Leer antes**:
  - `knowledge-base/04_modelo_de_datos.md` §ERD y §Entidades (fuente de verdad, oráculo `docs/Parcial_Cap1a4_Consigna.pdf`)
  - `knowledge-base/05_reglas_de_negocio.md` §Catálogo y clientes y §Ventas y renglones (RN-01 a RN-03, RN-09, RN-12)
  - `knowledge-base/09_decisiones_y_supuestos.md` §DD-01, §DD-04, §SU-01 (confirmada)
  - `knowledge-base/10_preguntas_abiertas.md` §(4) y §(7) — PENDIENTES

### [CH-03] `docker-imagen`
- **Estado**: `[x]` completado
- **Scope**: Empaquetar la imagen Docker — change propio, arranca temprano en paralelo al dominio (DD-06)
  - Dueño potencial: Agente C (Infra/DevOps) — una sesión (~4-6 h)
  - Casos cubiertos: D-01 (base `python:3.12-alpine` < 100 MB según `docker images`), D-06 (`docker exec libreria id` no es root), verificado localmente; evidencia final en CH-12
  - `Dockerfile` desde `python:3.12-alpine` (74,7 MB; no instalar compiladores, las dependencias se instalan sin compilar según `12_despliegue_docker_y_vps.md`)
  - Capas: copiar e instalar `requirements.txt` con `--no-cache-dir` **antes** de copiar el código; usuario sin privilegios con `USER`; escucha en `0.0.0.0`; `.dockerignore` excluye `.env`, `.venv`, `.git`, `__pycache__`; sin secretos en la imagen
  - `HEALTHCHECK` sobre `GET /health/ready` con `127.0.0.1` (nunca `localhost`: en Alpine/`wget` `localhost` resuelve primero a `::1` IPv6 y uvicorn escucha solo IPv4, ver `12_despliegue_docker_y_vps.md` §El HEALTHCHECK)
  - **PENDIENTE (no resolver acá)** — `10_preguntas_abiertas.md` §(2): el `HEALTHCHECK` depende del código de error de `/health/ready`; se deja configurable según lo que confirme la cátedra
- **Dependencias**: CH-01
- **Governance**: MEDIO
- **Leer antes**:
  - `knowledge-base/12_despliegue_docker_y_vps.md` §La imagen, §Capas/usuario/sin secretos, §El HEALTHCHECK y localhost
  - `knowledge-base/08_arquitectura_propuesta.md` §Estructura de directorios (`Dockerfile`, `.dockerignore`)
  - `knowledge-base/07_flujos_principales.md` §Flujo 6: Contenedor y despliegue en el VPS
  - `knowledge-base/10_preguntas_abiertas.md` §(2) — PENDIENTE

---

## FASE 1 — CRUD y dominio

> CH-04, CH-05 y CH-06 son independientes entre sí (solo dependen de CH-02) y pueden proponerse en paralelo. CH-07 exige CH-05 y CH-06.

### [CH-04] `crud-editoriales-generos-autores`
- **Estado**: `[x]` completado
- **Scope**: Recursos de referencia simples con DTO separados (US-003, parte editorial/género/autor)
  - Dueño potencial: Agente B (Backend Aux) — una sesión (~4-6 h)
  - Casos cubiertos: habilita el caso C-04 (las editoriales/autores existen como recursos para el caso FK de libros)
  - Módulos `app/modules/{editoriales,generos,autores}/{models,schemas,service,router}.py`; lógica en el `service` (recibe la sesión), router delgado, traducción del `IntegrityError` a 409 con mensaje propio (RN-12, DD-04 — sin consultas previas de existencia, RT-02)
  - Endpoints: `POST /editoriales/` (201/409/422), `GET /editoriales/` + `GET /editoriales/{id}` (200/422, 404), `PATCH /editoriales/{id}` (200/404/409), `GET /editoriales/{id}/libros` (200/404); `POST /generos/` (201/409), `GET /generos/` + `GET /generos/{id}` (200), `GET /generos/{id}/libros` (200/404); `POST /autores/` (201/422), `GET /autores/{id}` (200/404), `PATCH /autores/{id}` (200/404/422), `GET /autores/{id}/libros` (con `rol` y `orden`, 200/404)
  - DTO: los `Create` no llevan `id`; los `Update` aplican solo los campos enviados (`exclude_unset`); listados paginados (`limit` 1–100 defecto 20, `offset` ≥ 0, RN-10)
  - **PENDIENTE (no resolver acá)** — `10_preguntas_abiertas.md` §(3): `POST /autores/` solo declara 201/422, ¿no tiene 409? §(5): sin endpoints DELETE/baja en todo el enunciado — no crear ninguno (DD-02)
- **Dependencias**: CH-02
- **Governance**: BAJO
- **Leer antes**:
  - `knowledge-base/06_funcionalidades.md` §Épica 3: Contratos y CRUD y tabla de endpoints de referencia
  - `knowledge-base/05_reglas_de_negocio.md` §Listados, filtros y errores (RN-10, RN-12) y reglas transversales RT-01, RT-02
  - `knowledge-base/08_arquitectura_propuesta.md` §Patrones (modelo vs DTO, service, router delgado)
  - `knowledge-base/10_preguntas_abiertas.md` §(3) y §(5) — PENDIENTES

### [CH-05] `libros-autorias`
- **Estado**: `[x]` completado
- **Scope**: CRUD de libros con autorías, paginación y búsqueda (US-003 + parte de US-004: alta con relaciones)
  - Dueño potencial: Agente A (Backend Core) — una sesión (~4-6 h)
  - Casos cubiertos: C-01 (id de ruta no entero → 422 sin ejecutar el handler), C-02 (ISBN repetido → 409 propio), C-04 (editorial/autor inexistente → 409), C-08 (búsqueda `' OR '1'='1` → 200 lista vacía), C-07 parcial (detalle de libro con número fijo de consultas — la evidencia va en CH-12)
  - Módulo `app/modules/libros/` (incluye `LibroAutor`); `POST /libros/` (201/409/422): viajan `editorial_id`, `genero_id` y lista `autores` (`autor_id`, `rol`, `orden`); se escribe sin consultar antes la existencia de los ids (RT-02, DD-04) y la base responde FK/UNIQUE/CHECK → 409 con mensaje propio
  - `GET /libros/` (200/422) con paginación `limit 1–100` defecto 20 + `offset` ≥ 0 (RN-10) y filtro por parte del título case-insensitive con parámetro ligado (RN-11); `GET /libros/{id}` (200/404/422) y `PATCH /libros/{id}` (200/404/409/422)
  - Detalle y respuesta de alta precargados con `joinedload` (editorial, género) / `selectinload` (autorías→autor): número fijo de consultas que no crece con la cantidad de autores (RT-04, caso C-07)
  - **PENDIENTE (no resolver acá)** — `10_preguntas_abiertas.md` §(4): unicidad de `orden` dentro de un libro; §(5): sin DELETE
- **Dependencias**: CH-02
- **Governance**: MEDIO
- **Leer antes**:
  - `knowledge-base/04_modelo_de_datos.md` §libro y §libro_autor
  - `knowledge-base/06_funcionalidades.md` §Épica 4: Altas con relaciones (criterios del alta de libro) y tabla de endpoints
  - `knowledge-base/07_flujos_principales.md` §Flujo 2: Alta de un libro con autorías y §Flujo 4: Lectura sin N+1, listado paginado y búsqueda
  - `knowledge-base/05_reglas_de_negocio.md` §Listados (RN-10, RN-11), §Catálogo (RN-01, RN-03) y RT-02/RT-04
  - `knowledge-base/10_preguntas_abiertas.md` §(4) — PENDIENTE

### [CH-06] `clientes-perfil`
- **Estado**: `[x]` completado
- **Scope**: Clientes y perfil uno a uno (US-003, parte clientes)
  - Dueño potencial: Agente B (Backend Aux) — una sesión (~4-6 h)
  - Casos cubiertos: C-02 (email repetido → 409 propio), C-03 (segundo perfil para el mismo cliente → 409)
  - Módulo `app/modules/clientes/` (incluye `PerfilCliente`); `POST /clientes/` (201/409/422), `GET /clientes/{id}` (200/404, precarga el perfil como objeto único — no lista), `PATCH /clientes/{id}` (200/404/409/422)
  - `POST /clientes/{id}/perfil` (201/404/409): escribe con `cliente_id` del path; el 409 del segundo perfil lo garantiza el UNIQUE de `perfil_cliente.cliente_id` (RN-09) traducido por el service, sin consulta previa (RT-02)
  - `GET /clientes/{id}/ventas` (200/404): lista las ventas del cliente (lee `Venta` sin cargar renglones); DTO/patrón iguales al resto de módulos
  - Sin endpoints DELETE (DD-02) — **PENDIENTE**: `10_preguntas_abiertas.md` §(5) (confirmar que no se crean bajas)
- **Dependencias**: CH-02
- **Governance**: BAJO
- **Leer antes**:
  - `knowledge-base/04_modelo_de_datos.md` §cliente y §perfil_cliente
  - `knowledge-base/06_funcionalidades.md` §Épica 3 y tabla de endpoints (filas de `clientes`)
  - `knowledge-base/07_flujos_principales.md` §Flujo 5: Alta y lectura de perfil de cliente
  - `knowledge-base/05_reglas_de_negocio.md` §Catálogo y clientes (RN-02, RN-09)
  - `knowledge-base/10_preguntas_abiertas.md` §(5) — PENDIENTE

### [CH-07] `ventas-renglones`
- **Estado**: `[x]` completado
- **Scope**: Altas de ventas con renglones anidados, precios y total del servidor, aviso simulado (US-004, parte ventas + US-005 parcial)
  - Dueño potencial: Agente A (Backend Core) — una sesión (~4-6 h)
  - Casos cubiertos: C-05 (libro/cliente inexistente → 409), C-06 (venta válida de dos renglones → 201, precios copiados, total `77000.00`), C-07 parcial (detalle de venta sin N+1), D-07 (mensaje del aviso en `docker logs` tras el alta)
  - Módulo `app/modules/ventas/` (incluye `RenglonVenta`); `POST /ventas/` (201/409/422) con DTO anidado: viajan `cliente_id` y `renglones` (`libro_id`, `cantidad`); al menos un renglón y ningún libro repetido (RN-04, RN-05 → 422); **nunca** viajan `precio_unitario`, `total` ni `fecha`
  - El `service` copia `precio_unitario` del libro (RN-06, DD-05) y calcula `total = Σ cantidad × precio_unitario` (RN-07); venta y renglones se escriben juntos (composición); FK inválida → 409 (RT-02)
  - `GET /ventas/` (200/422, paginado RN-10) y `GET /ventas/{id}` (200/404) con cliente y renglones precargados (`joinedload`/`selectinload`, número fijo de consultas — C-07); **sin PATCH de ventas** (RN-08, DD-02)
  - Aviso del comprobante con `BackgroundTasks` + `await asyncio.sleep(0.5)` + mensaje en el log, agendado **después** de responder (RT-03: ningún bloqueante)
  - **PENDIENTE (no resolver acá)** — `10_preguntas_abiertas.md` §(1) **ALTA**: ¿la venta descuenta `stock` del libro? No se implementa ningún descuento hasta la respuesta de la cátedra; la decisión se documenta en el change. §(5): sin DELETE
- **Dependencias**: CH-05, CH-06
- **Governance**: MEDIO
- **Leer antes**:
  - `knowledge-base/04_modelo_de_datos.md` §venta y §renglon_venta
  - `knowledge-base/06_funcionalidades.md` §Épica 4 (criterios del alta de venta: ejemplo `cliente_id: 2`, libros 1×2 y 4×1 → total `77000.00`, subtotales `50000.00` y `27000.00`) y §Épica 5 (US-005: lecturas sin N+1 + `BackgroundTasks`)
  - `knowledge-base/07_flujos_principales.md` §Flujo 3: Alta de una venta con renglones y §Flujo 4 (detalle sin N+1)
  - `knowledge-base/05_reglas_de_negocio.md` §Ventas y renglones (RN-04 a RN-08) y RT-03
  - `knowledge-base/10_preguntas_abiertas.md` §(1) — PENDIENTE ALTA

---

## FASE 2 — Datos iniciales y pruebas locales

### [CH-08] `seed-datos-iniciales`
- **Estado**: `[x]` completado
- **Scope**: Script/comando de datos iniciales determinista y documentado (seed)
  - Dueño potencial: Agente B (Backend Aux) — una sesión (~4-6 h)
  - Casos cubiertos: deja reproducibles el caso C-06 y el caso D-03 (los datos que esos casos asumen)
  - Script fuera de los routers (ejecutable localmente y vía `docker exec libreria …` en el VPS — Flujo 6 paso 4); filas estables con ids fijos documentadas en el README del proyecto (qué filas, con qué ids), coherentes con los ejemplos de forma del enunciado (venta `cliente_id: 2`, renglones libro 1 ×2 a 25000.00 y libro 4 ×1 a 27000.00, total 77000.00; libro con autores 3 y 4, editorial 1, género 1, ISBN `978-950-00-0006-6`, stock 4)
  - El seed es idempotente o notifica su re-ejecución sin corromper unicidades; no depende del orden de los changes de CRUD (consume CH-04 a CH-07 ya archivados)
  - **PENDIENTE (no resolver acá)** — `10_preguntas_abiertas.md` §(6): contenido exacto del seed (lista cerrada de filas base) — hasta la respuesta de la cátedra, el seed es determinista y documentado acá; §(1) (descuento de stock) afecta el stock que el seed deja
  - Nota baja prioridad — `10_preguntas_abiertas.md` §(6): el ejemplo del enunciado devuelve id 2 en `POST /ventas/`, lo que sugiere que el seed ya trae venta id 1; se registra como pregunta abierta, NO regla
- **Dependencias**: CH-04, CH-07
- **Governance**: BAJO
- **Leer antes**:
  - `knowledge-base/04_modelo_de_datos.md` §Seed data inicial
  - `knowledge-base/06_funcionalidades.md` §Casos de prueba mínimos (C-06) y §US-006 (carga de datos en el despliegue)
  - `knowledge-base/07_flujos_principales.md` §Flujo 6 (paso 4: `docker exec libreria …`)
  - `knowledge-base/10_preguntas_abiertas.md` §(6) y §(1) — PENDIENTES

### [CH-09] `casos-http-C`
- **Estado**: `[x]` completado
- **Scope**: Batería `test/*.http` con los casos C-01 a C-08 ejecutables en orden
  - Dueño potencial: Agente B (Backend Aux) — una sesión (~4-6 h)
  - Casos cubiertos: C-01, C-02, C-03, C-04, C-05, C-06, C-07 (request) y C-08
  - Un archivo `.http` por caso (o agrupados por épica) con la petición exacta y la respuesta esperada (método, ruta, cuerpo, código); quedan en `test/` según la estructura de `08_arquitectura_propuesta.md`
  - C-01: parámetro de ruta no entero → 422 sin handler; C-02: ISBN y email repetidos → 409 propio; C-03: segundo perfil → 409; C-04: libro con editorial/autor inexistente → 409; C-05: venta con libro/cliente inexistente → 409; C-06: venta válida de dos renglones → 201 con precios copiados y total `77000.00`; C-08: búsqueda con `' OR '1'='1` → 200 lista vacía
  - El caso C-07 (conteo fijo de consultas) se ejecuta con la consola de SQL visible (`SQL_ECHO`) y su evidencia se genera en CH-12
  - **PENDIENTE (no resolver acá)** — ninguna respuesta nueva: los casos se escriben contra las reglas RN-01 a RN-12 tal como están citadas; si las dudas §(1), §(3), §(4) se responden en contra, los casos afectados se ajustan como changes separados
- **Dependencias**: CH-08
- **Governance**: BAJO
- **Leer antes**:
  - `knowledge-base/06_funcionalidades.md` §Casos de prueba mínimos (C-01 a C-08) y tabla de endpoints de referencia
  - `knowledge-base/05_reglas_de_negocio.md` §Listados, filtros y errores y reglas transversales RT-01 (códigos por caso)
  - `knowledge-base/07_flujos_principales.md` §Flujo 2, §Flujo 3 y §Flujo 4 (casos de error por flujo)
  - `knowledge-base/08_arquitectura_propuesta.md` §Estructura de directorios (`test/`)

---

## FASE 3 — Contenedor, despliegue y entrega

### [CH-10] `despliegue-vps-inicial`
- **Estado**: `[x]` archivado (2026-11-11)
- **Scope**: Despliegue inicial en el VPS — change propio de infraestructura en producción, detección temprana de red y `host.docker.internal` (D-02, D-05, D-06; más contenedor vuelve a `healthy` tras `docker rm -f` + `run`)
  - Dueño potencial: Agente C (Infra/DevOps) — una sesión (~4-6 h)
  - Casos cubiertos: D-02 (build + run limpio, contenedor `healthy`), D-05 (sin `DATABASE_URL` el contenedor no queda sirviendo), D-06 (usuario del proceso no root); más contenedor vuelve a `healthy` tras `docker rm -f` + `run`
  - En el VPS: `docker build` + `docker run -d --name libreria -p <puerto>:8000 --restart unless-stopped --env-file <archivo> libreria`; el archivo de variables vive en el servidor (fuera del repo y de la imagen) con `DATABASE_URL` (host provisto por la cátedra; si la base está en el mismo servidor, `host.docker.internal` con `--add-host=host.docker.internal:host-gateway` en Linux, nunca `localhost`)
  - **PENDIENTE (no resolver acá)** — `10_preguntas_abiertas.md` §(2): el comportamiento de `GET /health/ready` sin base define el `HEALTHCHECK` y el caso D-05; se sigue la respuesta de CH-01 / CH-03 y lo que responda la cátedra
- **Dependencias**: CH-02, CH-03
- **Governance**: MEDIO
- **Leer antes**:
  - `knowledge-base/12_despliegue_docker_y_vps.md` §Cómo se corre, §La base no está en localhost, §Despliegue en el VPS y DEPLOY.md y §Casos D
  - `knowledge-base/07_flujos_principales.md` §Flujo 6 (casos de error: `localhost` y `HEALTHCHECK`)
  - `knowledge-base/02_descripcion_general.md` §Integraciones externas (PostgreSQL provista por el servidor)
  - `knowledge-base/10_preguntas_abiertas.md` §(2) — PENDIENTE

### [CH-11] `despliegue-vps-datos`
- **Estado**: `[x]` completado (2026-11-11), hecho a mano en el VPS sin propose/apply; evidencia en evidencia/D-03, D-04 y D-07, y DEPLOY.md actualizado
- **Scope**: Despliegue con datos iniciales + `DEPLOY.md` escrito mientras se despliega — change propio de infraestructura en producción (D-03, D-04) y documentación operativa (persistencia solo comprobable con seed cargado)
  - Dueño potencial: Agente C (Infra/DevOps) — una sesión (~4-6 h)
  - Casos cubiertos: D-03 (desde afuera: `GET /health/ready` 200, `GET /libros/` con datos iniciales 200, `POST /ventas/` del caso C-06 → 201), D-04 (`docker rm -f` + re-run con seed cargado: vuelve a `healthy` y los datos persisten; persistencia solo comprobable con seed cargado)
  - Carga de datos iniciales con el seed de CH-08 vía `docker exec libreria …`; el contenedor queda **en línea hasta que se publiquen las notas**
  - `DEPLOY.md` se escribe mientras se despliega (documenta el procedimiento de D-02 a D-05, no es un change separado): URL pública del despliegue; día y hora del despliegue; comandos `docker build` y `docker run` completos (con el nombre del archivo de variables, sin su contenido); cualquier cambio hecho al proyecto para que corra en el contenedor; procedimiento de actualización (reconstruir la imagen, eliminar el contenedor, volver a correrlo) con la nota de que los datos no se pierden porque viven en la base del servidor; registro de las correcciones propias detectadas en el contenedor en línea (si las hubiera); la URL queda en línea hasta que se publiquen las notas y el documento la declara (criterio de corrección)
- **Dependencias**: CH-10, CH-08
- **Governance**: MEDIO
- **Leer antes**:
  - `knowledge-base/12_despliegue_docker_y_vps.md` §Cómo se corre, §La base no está en localhost, §Despliegue en el VPS y DEPLOY.md y §Casos D
  - `knowledge-base/07_flujos_principales.md` §Flujo 6 (paso 4: `docker exec libreria …`)
  - `knowledge-base/03_actores_y_roles.md` §Rutas públicas (acceso de correctores a la URL pública)
  - `knowledge-base/01_vision_y_objetivos.md` §Objetivos por actor (correctores) y §Métricas de éxito (despliegue 10 %)
  - `knowledge-base/10_preguntas_abiertas.md` §(2) — PENDIENTE

### [CH-12] `evidencia-entrega`
- **Estado**: `[ ]` pendiente
  - **Nota de alcance (12/11/2026)**: Tanda a = README final, DEPLOY.md, organización de evidencia/ (vigente vs histórica ch-07-local/) y auditoría de ausencia de secretos en el historial Git; la verificación del .zip queda para la tanda b, después de la revisión exhaustiva.
- **Scope**: Carpeta `evidencia/` completa + README final + verificación del `.zip` de entrega
  - Dueño potencial: Agente C (Infra/DevOps) — una sesión (~4-6 h)
  - Casos cubiertos: evidencia del caso C-07 (captura o fragmento de consola con el conteo fijo de consultas) y de los casos D-01 a D-07, salida por salida, en `evidencia/`
  - `README.md` final: nombres y apellidos de los integrantes + pasos para levantar desde cero (entorno virtual, dependencias, `.env` desde `env.example`, arranque del servidor que crea las tablas, carga de datos iniciales con el seed de CH-08)
  - Verificación del único `.zip` `Parcial_Cap1a4_<NombreDelGrupo>.zip` (un solo integrante lo sube): código fuente, `requirements.txt`, `env.example` sin valores reales, `test/`, `Dockerfile`, `.dockerignore`, `README.md`, `DEPLOY.md`, `evidencia/`; **sin** `.venv`, `__pycache__` ni `.env`; si se incluye `.git`, historial limpio de credenciales reales (SU-03: una contraseña subida y borrada sigue en el historial y exige cambiarla)
- **Dependencias**: CH-09, CH-11, CH-15
- **Governance**: BAJO
- **Leer antes**:
  - `knowledge-base/12_despliegue_docker_y_vps.md` §Casos D y §Entrega (cátedra)
  - `knowledge-base/06_funcionalidades.md` §Casos de prueba mínimos (C-07: evidencia en consola)
  - `knowledge-base/01_vision_y_objetivos.md` §Alcance v1.0 y §Métricas de éxito
  - `knowledge-base/09_decisiones_y_supuestos.md` §SU-03 (entrega sin secretos)
### [CH-15] `seed-fiel-enunciado`
- **Estado**: `[x]` completado (archivado 2026-11-12)
- **Scope**: Alinear el dataset determinista de `app/seed.py` a los ejemplos del enunciado (27 filas: cliente 2 Tomás Ríos `tomas@example.com`, libros 1–5, sin precargar libro 6 / ISBN `978-950-00-0006-6`, venta 1 conservada) y transformar la estrategia de carga en reiniciable mediante `TRUNCATE TABLE ... RESTART IDENTITY CASCADE` de las 9 tablas del proyecto en una única transacción. Actualización de specs delta (`datos-iniciales`, `casos-http-c`), `.http` dependientes, `README.md` (sección seed) y `DEPLOY.md`. Mariano aprobó el 12/11/2026, por su cuenta, el plan del seed y la excepción O3+O1 de CH-11 (sin carpeta archivada, con la evidencia de DEPLOY.md y evidencia/D-03, D-04 y D-07).
- **Dependencias**: CH-08, CH-09
- **Governance**: MEDIO
- **Leer antes**:
  - `openspec/changes/archive/2026-11-12-ch-15-seed-fiel-enunciado/proposal.md`, `design.md`, `tasks.md`, y deltas en `specs/`
  - `docs/Parcial_Cap1a4_Consigna.pdf` y `knowledge-base/`

### [CH-16] `mapa-casos-y-evidencia-c07`
- **Estado**: `[ ]` en progreso
- **Scope**: Ajustes de trazabilidad y evidencia docente previa al cierre:
  - Encabezado histórico de advertencia en `test/ch07-ventas-exito.http` (no altera peticiones).
  - Aviso de acceso HTTP plano en `README.md` y mapa exhaustivo de casos de prueba C-01 a C-08 con rótulos exactos y precondiciones de seed.
  - Generación y registro de evidencia complementaria de C-07 (`evidencia/C-07-ventas-un-renglon.log` y `C-07-ventas-un-renglon-conteo.txt`) comparando venta de 1 renglón vs 2 renglones en base limpia `libreria_c16`.
  - Actualización documental de `evidencia/LEEME.md`.
- **Dependencias**: CH-12 tanda a (rama encadenada, README y LEEME editados ahí), CH-15 (seed) y CH-09 (casos C-07)
- **Governance**: BAJO
- **Leer antes**:
  - `openspec/changes/ch-16-mapa-casos-y-evidencia-c07/proposal.md`, `design.md`, `tasks.md`
  - `docs/Parcial_Cap1a4_Consigna.pdf` (C-07) y `knowledge-base/06_funcionalidades.md`

---

## Rectificación aplicada (fuera de fase original)

### [CH-13] `ch-13-validacion-rango-int4`
- **Estado**: `[x]` completado (aplicado)
- **Scope**: Rectificación transversal de validación de rango PostgreSQL `int4` (`INT4_MAX = 2147483647`) en módulos implementados de **CH-05 (`libros-autorias`)** y **CH-06 (`clientes-perfil`)**. Endurece ids de ruta, `offset` y filtro `genero_id` en query params, y body ids/enteros de entrada (`editorial_id`, `genero_id`, `autor_id`, `autores[].orden`, `stock`) para responder **422** por validación declarativa antes de ejecutar handler/consulta/escritura, sin exponer internals de base (RN-12). Mantiene `id == 0` → 404 cuando la inexistencia la resuelve el service. **Ventas excluido** (CH-07 pendiente/stubs): el change propio de ventas debe nacer con estos límites desde su origen.
  - Casos/cobertura: overflow de path/query/body en libros/clientes → 422 sin `DataError`/`Traceback`/`asyncpg`/SQL; controles `GET /libros/0` y `GET /clientes/0` → 404; filtros/listados válidos dentro de rango siguen operando (ej. `GET /libros/?genero_id=1` → 200).
  - Artefactos: `openspec/changes/ch-13-validacion-rango-int4/` (proposal, design, tasks, specs) y `test/ch13-libros-rango-int4.http`, `test/ch13-clientes-rango-int4.http`.
- **Dependencias**: CH-05, CH-06
- **Governance**: BAJO
- **Leer antes**:
  - `openspec/changes/ch-13-validacion-rango-int4/proposal.md`, `design.md`, `tasks.md` y deltas en `specs/`
  - `knowledge-base/05_reglas_de_negocio.md` (RN-10, RN-12, RT-01, RT-02)
  - `knowledge-base/06_funcionalidades.md` (contratos de libros/clientes) y `knowledge-base/09_decisiones_y_supuestos.md` (DD-04)

### [CH-14] `ch-14-rectificacion-active-stack`
- **Estado**: `[x]` archivado (2026-11-12)
- **Scope**: Rectificación Active Stack/SDD sin tocar código de la app ni `.http` ni changes archivados. (A) Agrega `specs/casos-http-c/spec.md` (Purpose, ADDED Requirements, un requirement por C-01 a C-08, escenarios verificables y referenciados a evidencia existente; C-05/C-06 referenciados en artefactos CH-07/CH-08 sin duplicar). (B) Auditoría B.1–B.8 en `design.md` con comandos/salidas y `[VERIFICAR]` donde no hay evidencia (incluye hallazgos CH-09 sin specs, CH-13 sin `.openspec.yaml` y CH-13 reflejado en `openspec/specs` por encabezados/contenido con hash distinto esperable, CH-05 con `README.md`, CH-10 con tareas sin tildar, nota CH-13 con ruta no archivada, y CH-11 manual/no archivado con brecha de proceso respecto a CH-12 con recomendación O3 + nota de evidencia O1 pendiente de confirmación de Facundo y Andrés, sin propose retroactivo).
  - Artefactos: `openspec/changes/ch-14-rectificacion-active-stack/` (proposal, design, specs, tasks), actualización acotada de `CHANGES.md`, pregunta abierta en `knowledge-base/10_preguntas_abiertas.md` y actualización de `.active-orchestrator-state.json`.
- **Dependencias**: CH-09 (contexto de spec faltante), CH-13/roadmap archivado (auditoría)
- **Governance**: BAJO
- **Leer antes**:
  - `openspec/changes/ch-14-rectificacion-active-stack/proposal.md`, `design.md`, `tasks.md`, `specs/casos-http-c/spec.md`
  - `CHANGES.md`, `AGENTS.md`, `CLAUDE.md`, `knowledge-base/10_preguntas_abiertas.md`
