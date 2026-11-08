# Proposal: CH-01 — foundation-setup

## Why

Sin una fundación asíncrona verificable no se puede construir ningún dominio posterior (modelos, routers, seed, despliegue). CH-01 levanta la aplicación FastAPI con lifespan, configuración por entorno y endpoints de salud, y deja el camino único para CH-02…CH-12. Es el primer gate del roadmap (CHANGES.md) y el camino crítico comienza acá.

## What Changes

- Estructura base: `app/main.py`, `app/core/config.py` (lee `DATABASE_URL`), `app/core/database.py` (motor async + fábrica de sesiones + `get_session`), `requirements.txt`, `env.example`. `.gitignore` ya existe en el repo y no se recrea: solo se verifica que excluya `.env`, `.venv/`, `__pycache__/`, `*.bak` y `.atl/`, y se agrega lo que falte conservando `.atl/`.
- Lifespan de FastAPI: crea motor + fábrica de sesiones en `app.state`, ejecuta `SQLModel.metadata.create_all` con los modelos importados (en CH-01 todavía no hay modelos — llegan en CH-02 — por lo que la lista de tablas creadas queda vacía hasta entonces), si la base no responde el arranque falla (no queda sirviendo), al apagar cierra el motor. Sesiones por petición con `expire_on_commit=False` (SU-02).
- Endpoints de salud: `GET /health/live` (no toca la base) y `GET /health/ready` (`SELECT 1`). Escucha en `0.0.0.0`.
- Configuración sin secretos: si `DATABASE_URL` no está definida o está vacía (`DATABASE_URL=` cuenta como ausente), el proceso termina con error claro y sin valor por defecto (cubre D-05); `database.py` lee `SQL_ECHO` para `echo` del motor (default `false`). `env.example` incluye `DATABASE_URL` con forma `postgresql+asyncpg://` sin valores reales y `SQL_ECHO=false`. `.env` no versionado; el `.gitignore` preexistente excluye `.env`, `.venv/`, `__pycache__/`, `*.bak` y `.atl/`. El log de arranque no imprime `DATABASE_URL` ni credenciales.
- Al terminar `create_all`, el lifespan escribe una línea en el log con el arranque y la lista de tablas creadas (vacía en CH-01, completa desde CH-02), aunque `SQL_ECHO` sea `false` (necesario para D-02).
- `requirements.txt`: `fastapi[standard]>=0.111`, `sqlmodel>=0.0.24`, `sqlalchemy[asyncio]>=2.0`, `asyncpg>=0.30`, `python-dotenv>=1.0`. Python 3.12 no va en este archivo (va en README y en el `Dockerfile` de CH-03). No se agregan otros paquetes (la imagen base alpine no trae compilador).

## Capabilities

### New Capabilities

- `foundation`: arranque asíncrono con lifespan, configuración por entorno (`DATABASE_URL`, `SQL_ECHO`), endpoints de salud (`/health/live`, `/health/ready`), gestión de sesiones por petición y dependencias versionadas. Incluye el log de arranque tras `create_all` y el fallo rápido sin `DATABASE_URL`.

### Modified Capabilities

- Ninguna — `openspec list --specs` no muestra specs existentes; todo es nuevo.

## Impact

- **Código**: nuevos archivos `app/main.py`, `app/core/config.py`, `app/core/database.py`, `requirements.txt`, `env.example`. `.gitignore` NO es nuevo: ya existe en el repo, se verifica y se completa lo que falte (conservando `.atl/`). Sin tablas ni routers de dominio (eso es CH-02 y siguientes). Sin migraciones (regla dura del proyecto).
- **APIs**: dos rutas nuevas de salud. Sin endpoints de dominio ni fuera de la tabla de referencia (regla dura del proyecto).
- **Dependencias**: Python 3.12 + FastAPI ≥0.111 + SQLModel ≥0.0.24 + SQLAlchemy 2.0 async + asyncpg + PostgreSQL 16 + python-dotenv + Docker ≥20.10 sin Compose (stack impuesto, fuente KB).
- **Sistemas**: ninguna integración externa nueva; la base PostgreSQL se alcanza solo vía `DATABASE_URL` (driver `postgresql+asyncpg`).

## Casos y reglas cubiertos (config.yaml: `proposal`)

- **RN-xx**: ninguna regla de negocio RN-01…RN-12 se implementa ni se cubre directamente en CH-01 (no hay tablas con UNIQUE/FK/CHECK, ni DTOs, ni listados). Verificado contra `knowledge-base/05_reglas_de_negocio.md`: nada de CH-01 inventa una RN.
- **RT-xx**: habilita las reglas transversales RT-03 (`async def` en todos los handlers, sin bloqueo) y RT-05 (SQL con parámetros ligados, nunca concatenación) como base; prepara RT-01 (códigos por caso) y RT-04 (carga anticipada) para los changes de dominio. No se contradicen.
- **C-xx**: ningún caso C-01…C-08 directamente; habilita el arranque para todos los casos C (las pruebas `.http` de dominio llegan en CH-09).
- **D-xx**: cubre parcialmente D-05 (arranque sin `DATABASE_URL` → proceso termina con error, sin valor por defecto; `DATABASE_URL` vacía cuenta como ausente) y deja cubierto el requisito de log de D-02 (línea tras `create_all` aunque `SQL_ECHO=false`). El despliegue completo D-02/D-05/D-06 y la evidencia final son de CH-10…CH-12. No se cubren D-01, D-03, D-04, D-07.
- **PENDIENTE (no es regla del enunciado)**: `knowledge-base/10_preguntas_abiertas.md` §(2) pregunta Q2 — qué devuelve `GET /health/ready` y con qué código si la base no responde. En CHANGES.md figura como decisión del equipo a documentar en `design.md` y a confirmar con cátedra: **GET /health/ready responde 200 `{"estado": "listo"}` si `SELECT 1` responde, y 503 `{"estado": "no listo"}` con cuerpo propio si falla**; ese 503 solo condiciona el `HEALTHCHECK` de CH-03. El caso D-05 (sin `DATABASE_URL`) es independiente del 503 y no depende de él. En esta proposal, el spec, el design y las tasks queda citado como *decisión del equipo pendiente de confirmación*, nunca como regla confirmada del enunciado.

## Fuera de alcance (config.yaml: `proposal`)

- Modelos y esquema del dominio (`editorial`, `genero`, `autor`, `libro`, `libro_autor`, `cliente`, `perfil_cliente`, `venta`, `renglon_venta`) — CH-02.
- Routers/servicios de dominio (editoriales, géneros, autores, libros, clientes, ventas) y sus DTOs — CH-04…CH-07.
- Seed (CH-08), batería `test/*.http` de casos C (CH-09), `Dockerfile`/`HEALTHCHECK` (CH-03), despliegue en VPS y `DEPLOY.md` (CH-10/CH-11), carpeta `evidencia/` (CH-12).
- Cualquier endpoint fuera de la tabla de referencia del enunciado (incluidos DELETE y PATCH de ventas).
- Cualquier regla de negocio no definida en RN-01…RN-12 (va como pregunta abierta en `10_preguntas_abiertas.md`, no se resuelve en silencio).
- Commits, push, apply de producción, evidencia con salida real (eso es de apply/archive, no de esta proposal).

## Leer antes (CHANGES.md — CH-01)

- `knowledge-base/02_descripcion_general.md` §Stack tecnológico y §Arquitectura general
- `knowledge-base/08_arquitectura_propuesta.md` §Patrones (lifespan, `app.state`, `get_session`) y §Variables de entorno
- `knowledge-base/07_flujos_principales.md` §Flujo 1: Arranque y ciclo de vida
- `knowledge-base/10_preguntas_abiertas.md` §(2) — PENDIENTE
- Verificación de no-invención de reglas: `knowledge-base/05_reglas_de_negocio.md` (RN-01…RN-12, RT-01…RT-05)
