# Design: CH-01 — foundation-setup

## Context

Ver `proposal.md` — Why. Estado inicial: no existe `app/`, `requirements.txt` ni `env.example`; `openspec list --specs` no muestra specs existentes. `.gitignore` ya existe en el repo (excluye `.env`, `.venv/`, `__pycache__/`, `*.bak` y `.atl/`) y no se recrea: solo se verifica con `Get-Content .gitignore` y se completa lo que falte, conservando `.atl/`. Restricciones que moldean el diseño, con fuente:

- Stack impuesto (sin cambios): Python 3.12, FastAPI ≥0.111 con handlers `async def`, SQLModel ≥0.0.24, SQLAlchemy 2.0 async, asyncpg, PostgreSQL 16, python-dotenv, uvicorn vía `fastapi[standard]`, Docker ≥20.10 sin Compose (`docker run` + `--env-file`). Fuente: `knowledge-base/02_descripcion_general.md` §Stack tecnológico y `openspec/config.yaml`.
- Estructura obligatoria: `app/main.py`, `app/core/config.py`, `app/core/database.py`, `app/modules/<módulo>/{models,schemas,service,router}.py` (health, editoriales, generos, autores, libros, clientes, ventas); `test/*.http`; `Dockerfile`; `.dockerignore`; `DEPLOY.md`; `evidencia/`. Fuente: `08_arquitectura_propuesta.md` §Estructura de directorios.
- Reglas duras del proyecto (AGENTS.md + config.yaml, prevalecen sobre cualquier skill): sin migraciones (`create_all` en el lifespan), sin secretos en código/repo/imagen, `async def` siempre, SQL con parámetros ligados, sin endpoints fuera de la tabla de referencia, sin renombrar tablas/columnas del enunciado, sin commitear sin pedido explícito.
- Flujo 1 (`07_flujos_principales.md`): lifespan crea motor + fábrica en `app.state`, `create_all` con modelos importados, fallo si la base no responde, cierre del motor al apagar; `DATABASE_URL` ausente → no queda sirviendo (D-05).
- Verificación de no-invención: `05_reglas_de_negocio.md` solo define RN-01…RN-12 y RT-01…RT-05; CH-01 no crea ninguna RN nueva. Lo ambiguo va a `10_preguntas_abiertas.md` (en especial Q2, §(2)).

## Goals / Non-Goals

**Goals:**

- Dejar una aplicación asíncrona arrancable y verificable con `GET /health/live` y `GET /health/ready`, sobre la que CH-02 puede registrar sus tablas sin cambiar el ciclo de vida.
- Aplicar los guardrails del skill `fastapi` dentro del override del proyecto: dependencias con `Annotated[..., Depends(...)]`, sin `...` como default, una función por operación HTTP, `response_model` solo si difiere, sin `ORJSONResponse`/`UJSONResponse`, sin `RootModel`, routers con `prefix`/`tags` en el `APIRouter`. `async def` siempre (regla dura del proyecto, no el criterio del skill de usar `def` si hay bloqueo).
- Aplicar los guardrails del skill `sqlmodel` dentro del stack del proyecto: importar desde `sqlmodel`, `class X(SQLModel, table=True)`, `create_all` solo tras importar todas las tablas (en el lifespan), sin `declarative_base`/`Mapped`/`mapped_column`/`sessionmaker`. Para sesiones async se usa el motor async de SQLAlchemy 2.0 según stack (una sesión por petición vía `get_session` con `expire_on_commit=False`), NO el patrón sync `Session(engine)` del skill.

**Non-Goals:**

- Modelos, routers y servicios de dominio, DTOs `Base/Create/Update/Public`, relaciones y `joinedload`/`selectinload` — eso es CH-02 y siguientes; el diseño de CH-01 solo deja el camino (`metadata`/`create_all`, `app.state`, `get_session`).
- `Dockerfile`, `HEALTHCHECK`, despliegue en VPS, `DEPLOY.md`, seed, batería `test/*.http` de casos C, carpeta `evidencia/` — CH-03, CH-08, CH-09, CH-10, CH-11, CH-12.
- Frontend con `app.frontend("/")`, streaming/SSE, `RootModel`, migraciones, Compose, secretos por defecto.

## Decisions

### 1. Lifespan con motor async + fábrica en `app.state` y `create_all`

**Decisión**: el lifespan de `app/main.py` crea el motor asíncrono y la fábrica de sesiones, los guarda en `app.state`, ejecuta `SQLModel.metadata.create_all` con todos los modelos ya importados (CH-02 registra sus tablas acá), escribe una línea de log tras la creación y, al apagar, cierra el motor.

**Fundamento**: `02_descripcion_general.md` §Arquitectura general, `08_arquitectura_propuesta.md` §Patrones (ciclo de vida con lifespan) y Flujo 1 paso 1–4. Alternativa descartada: crear el motor en tiempo de importación del módulo — pierde el fallo rápido al arranque y complica el cierre.

**Línea de log tras `create_all` (decisión del equipo, RN: ninguna)**: el lifespan escribe una línea en el log con el arranque y las tablas creadas aunque `SQL_ECHO=false`. Fundamento: D-02 exige ver el arranque con las tablas creadas en la consola (`docker logs`/salida real en CH-10…CH-12); si el único aviso dependiera de `SQL_ECHO=true` no habría evidencia. No inventa una RN: es una decisión operativa del equipo, deja rastro para D-02 sin exponer texto interno de la base (RN-12). El log de arranque usa el logger `uvicorn.error` para que sea visible bajo uvicorn sin configurar logging propio.

### 2. Configuración sin valor por defecto + `SQL_ECHO` y `env.example` sin secretos

**Decisión**: `app/core/config.py` lee `DATABASE_URL`; `app/core/database.py` lee `SQL_ECHO` para `echo` del motor (default `false`). `env.example` incluye `DATABASE_URL` con forma `postgresql+asyncpg://` sin valores reales y `SQL_ECHO=false`. `.env` no se versiona; `.gitignore` ya existe y excluye `.env`, `.venv/`, `__pycache__/`, `*.bak` y `.atl/` (solo se verifica y se completa lo que falte, sin recrear el archivo). `DATABASE_URL` vacía cuenta como ausente. El log de arranque no imprime `DATABASE_URL` ni credenciales.

**Fundamento**: `02_descripcion_general.md` §Stack tecnológico (fuente de `DATABASE_URL` desde `.env`, con driver `postgresql+asyncpg`), `08_arquitectura_propuesta.md` §Variables de entorno (tabla `DATABASE_URL` sensible, `SQL_ECHO` no sensible). Alternativa descartada: valor por defecto para `DATABASE_URL` — violaría D-05 (sin `DATABASE_URL` el proceso debe terminar con error claro, no arrancar contra una base equivocada). D-05 es independiente del 503 de `/health/ready`: D-05 mira la configuración ausente al arrancar; el 503 mira la base caída en tiempo de ejecución y solo condiciona el `HEALTHCHECK` de CH-03.

Escucha en `0.0.0.0` (requisito de CH-01 y prerrequisito del despliegue en VPS con `docker run -p` — ver `07_flujos_principales.md` Flujo 6).

### 3. Salud: `live` exacto y `ready` con `SELECT 1` (Q2 pendiente)

**Decisión**: `GET /health/live` responde exactamente `{"estado": "vivo"}` sin tocar la base. `GET /health/ready` ejecuta `SELECT 1` con estos cuerpos exactos (decisión del equipo pendiente de confirmación, Q2):

| Caso | Código | Cuerpo exacto |
|------|--------|---------------|
| La base responde a `SELECT 1` | 200 | `{"estado": "listo"}` |
| `SELECT 1` falla (p. ej. base detenida en ejecución) | 503 | `{"estado": "no listo"}` |

El 503 lleva cuerpo propio y NUNCA texto interno de la base: ni mensajes de excepción, ni host, ni cadena de conexión, ni credenciales (RN-12: sin texto interno en respuestas de error).

**Fundamento**: el 200 `{"estado": "listo"}` es simétrico con el cuerpo de `/health/live` (`{"estado": "vivo"}`) — una sola clave `estado` en ambos endpoints, sin campos extra que habría que mantener en sincronía — y tabla de endpoints de `02_descripcion_general.md` (solo 200 declarado para `/health/ready`, sin cuerpo de error definido) + `10_preguntas_abiertas.md` §(2) Q2 (pregunta abierta, no regla) + CHANGES.md CH-01 ("Decisión del equipo (a documentar en design.md, a confirmar con cátedra — Q2/10_preguntas_abiertas.md pendiente, no es regla del enunciado): GET /health/ready responde 503 con cuerpo propio si SELECT 1 falla; ese código define el `HEALTHCHECK` de CH-03 y el caso D-05 de CH-10"). Nota: la mención a D-05 en esa cita de CHANGES.md es una imprecisión — D-05 no depende del 503; falla el arranque por configuración ausente. El caso D-05 (sin `DATABASE_URL`) es independiente de este 503: D-05 falla el arranque por configuración ausente y no depende de este código; el 503 solo condiciona el `HEALTHCHECK` de CH-03. Lo no definido por el enunciado queda como pregunta abierta citada, nunca como regla confirmada. Alternativa descartada: propagar el error de la base — violaría RN-12.

### 4. Sesiones por petición con `expire_on_commit=False`, `async def` siempre

**Decisión**: cada petición que requiera base recibe una sesión propia provista por `get_session` (`yield`, `expire_on_commit=False`, SU-02); los handlers son `async def` (RT-03); el SQL usa parámetros ligados (RT-05).

**Fundamento**: `02_descripcion_general.md`, `08_arquitectura_propuesta.md` §Patrones (lifespan + `Depends(get_session)`), SU-02 (`expire_on_commit=False`), RT-03 y RT-05. Override explícito sobre el skill `fastapi` (que sugiere `def` si hay bloqueo): gana la regla dura del proyecto (`async def` en todos los handlers). Override sobre el skill `sqlmodel` (que muestra `Session(engine)` sync): gana el stack async del proyecto (`postgresql+asyncpg://`, `echo` desde `SQL_ECHO`).

### 5. Dependencias versionadas y estructura fija

**Decisión**: `requirements.txt` fija exactamente `fastapi[standard]>=0.111`, `sqlmodel>=0.0.24`, `sqlalchemy[asyncio]>=2.0`, `asyncpg>=0.30`, `python-dotenv>=1.0` (uvicorn llega vía `fastapi[standard]`; Python 3.12 no va en este archivo — va en README y en el `Dockerfile` de CH-03). No se agregan otros paquetes: la imagen base alpine no trae compilador. Estructura `app/main.py`, `app/core/{config,database}.py`, `app/modules/<módulo>/{models,schemas,service,router}.py`.

**Motivo del extra `asyncio`**: SQLAlchemy asíncrono necesita `greenlet`. Sin el extra `sqlalchemy[asyncio]`, `import app.main` falla con `ImportError` antes de conectar a la base, y sin declararlo no arranca el contenedor ni desde el README (`pip install -r requirements.txt` no instalaría `greenlet`).

**Fundamento**: `02_descripcion_general.md` §Stack técnico (versiones mínimas) y `08_arquitectura_propuesta.md` §Estructura de directorios. Sin Compose, sin migraciones, sin cambios de stack sin consultar (reglas duras).

## Risks / Trade-offs

- **[Riesgo] Q2 cambia por respuesta de cátedra**: si la cátedra pide otro código/cuerpo para `/health/ready` sin base, solo se ajusta el `HEALTHCHECK` (CH-03); D-05 (CH-10) no depende del 503 y no se toca. **Mitigación**: el 503 con `{"estado": "no listo"}` queda isolated en el handler de `ready` y citado como pendiente en spec/design/tasks; ningún otro change hardcodea el código.
- **[Riesgo] `create_all` sin modelos importados crea esquema incompleto**: **Mitigación**: el lifespan importa todos los modelos antes de `create_all` (CH-02 registra sus tablas acá); el skill `sqlmodel` exige el mismo orden. La tarea de verificación incluye la línea de log con las tablas creadas (D-02).
- **[Riesgo] `SQL_ECHO=false` oculta el diagnóstico**: **Mitigación**: la línea de log del lifespan es independiente de `echo` (decisión 1); `SQL_ECHO=true` queda solo para diagnóstico manual (caso C-07, evidencia en CH-12).
- **[Riesgo] Confundir patrones sync del skill `sqlmodel` con el stack async**: **Mitigación**: decisions 1 y 4 fijan motor async + fábrica async + `get_session`; las tasks lo prohíben explícitamente.
- **[Riesgo] Secreto filtrado en repo/imagen/zip**: **Mitigación**: `env.example` sin valores reales, `.env` no versionado, variables del contenedor vía `--env-file` (fuera del repo y de la imagen); SU-03 en CH-12 verifica la entrega sin secretos.
- **[Riesgo] `config.py` lee `DATABASE_URL` al importarse (dejado así)**: en CH-02 `database.py` importa `config`, por lo que cualquier import de `app` (tests, `uvicorn`, `py_compile` con import) falla en el import si falta `DATABASE_URL`, incluso antes del lifespan. **Mitigación**: las pruebas sin `DATABASE_URL` deben esperar ese fallo de import (fail-fast, D-05); no se crea el motor al importar.
- **[Riesgo] `python:3.12-alpine` no trae compilador y `greenlet` (vía `sqlalchemy[asyncio]`) podría necesitar compilar en CH-03**: **Mitigación**: confirmar en CH-03 (`docker build`) que `greenlet` se instala sin compilar (wheel disponible o dependencia ya satisfecha en la imagen base). No se edita `CHANGES.md` en este change; solo se deja anotado para CH-03.
- **[Recuperación del pool verificada]**: tras la caída simulada de la base (reenvío local `127.0.0.1:15432` → `5432` eliminado), `/health/ready` volvió a 200 en el primer intento sin `pool_pre_ping`; no se agrega esa opción al motor.

## Migration Plan

No aplica migración de datos (proyecto nuevo, sin esquema previo). Plan de introducción:

1. Crear estructura, instalar dependencias en `.venv`, copiar `env.example` → `.env` local con `DATABASE_URL` de prueba y `SQL_ECHO=false`.
2. Arrancar con `uvicorn app.main:app --host 0.0.0.0` (no se usa `fastapi dev` porque escucha en `127.0.0.1` por defecto y el proyecto exige `0.0.0.0`) y verificar los escenarios de la spec (ver `tasks.md`). Comprobar la escucha con `Get-NetTCPConnection -LocalPort 8000 -State Listen` (debe mostrar `LocalAddress 0.0.0.0`).
3. Registrar la confirmación pendiente de Q2 con cátedra; si la respuesta cambia el 503, ajustar solo `/health/ready` y el `HEALTHCHECK` de CH-03 (D-05 es independiente y no se toca).
4. Rollback: al no haber tablas de dominio aún, basta detener el proceso; los cambios son solo archivos nuevos/base de código sin datos.

## Open Questions

- **Q2 (`10_preguntas_abiertas.md` §(2), Media, decisor cátedra)**: ¿qué devuelve `GET /health/ready` y con qué código si la base no responde? Respuesta del equipo: 200 `{"estado": "listo"}` / 503 `{"estado": "no listo"}`. **Pendiente de confirmación**. No bloquea los demás escenarios de CH-01; bloquea el valor final del `HEALTHCHECK` (CH-03). D-05 (CH-10) es independiente del 503 y no se ve afectado. No se resuelve en silencio: se cita en proposal/spec/design/tasks como pendiente y se ajusta como change separado si la cátedra responde distinto.
- Ninguna otra pregunta abierta bloquea CH-01 (Q1, Q3–Q7 son de dominio posterior).
