# Parcial Programación III — Librería con despliegue en el VPS — Instrucciones para Agentes

## Stack Tecnológico

| Capa | Tecnología | Versión mínima |
|------|------------|----------------|
| Lenguaje | Python | 3.12 |
| Framework web | FastAPI (todos los handlers `async def`) | ≥ 0.111 |
| Modelos y contratos | SQLModel | ≥ 0.0.24 |
| ORM asíncrono, sesión, carga anticipada | SQLAlchemy 2.0 | 2.0 |
| Driver PostgreSQL asíncrono | asyncpg | ≥ 0.30 |
| Base de datos | PostgreSQL | 16 |
| Configuración | python-dotenv | 1.0 |
| Servidor ASGI | uvicorn (vía `fastapi[standard]`) | el que instala `fastapi[standard]` |
| Contenedores | Docker | ≥ 20.10 |

Fuente: `knowledge-base/02_descripcion_general.md`. Stack impuesto — no cambiar sin consultar.

## Base de Conocimiento

- `docs/Parcial_Cap1a4_Consigna.pdf` — fuente de verdad del enunciado (tablas/columnas y reglas obligatorias)

- `knowledge-base/README.md` — índice y resumen ejecutivo
- `knowledge-base/01_vision_y_objetivos.md` — propósito y alcance
- `knowledge-base/04_modelo_de_datos.md` — tablas/columnas obligatorias del enunciado
- `knowledge-base/05_reglas_de_negocio.md` — RN-01 a RN-12 (oficiales) y RT-01 a RT-05 (derivadas, no del enunciado)
- `knowledge-base/06_funcionalidades.md` — endpoints de referencia
- `knowledge-base/07_flujos_principales.md` — arranque, alta de libro, alta de venta
- `knowledge-base/08_arquitectura_propuesta.md` — `app/main.py` + `app/core/` + `app/modules/*/`
- `knowledge-base/09_decisiones_y_supuestos.md` — DD-01 a DD-06, SU-01 a SU-03
- `knowledge-base/10_preguntas_abiertas.md` — dudas abiertas (no reglas)
- `knowledge-base/12_despliegue_docker_y_vps.md` — Dockerfile, `docker run`, DEPLOY.md, D-01 a D-07

## Skills Disponibles

| Agente | Rol | Skills que carga |
|--------|-----|------------------|
| Agente A (Backend Core) | CH-01 foundation-setup, CH-02 core-models, CH-05 libros-autorias, CH-07 ventas-renglones | `fastapi`, `sqlmodel` |
| Agente B (Backend Aux) | CH-04 crud-referencia, CH-06 clientes-perfil, CH-08 seed-datos-iniciales, CH-09 casos-http-C | `fastapi`, `sqlmodel` |
| Agente C (Infra/DevOps) | CH-03 docker-imagen, CH-10 despliegue-vps-inicial, CH-11 despliegue-vps-datos, CH-12 evidencia-entrega | (KB 12 + fastapi para HEALTHCHECK) |
| Orquestación | OPSX/SDD | `kb-creator`, `roadmap-generator`, `agents-md-generator` |

> Los compact rules de cada skill los resuelve el orquestador desde `.atl/skill-registry.md` (generado por `skill-registry`; no versionado — no está en el repo).

## Roadmap de Changes

Ver `CHANGES.md` (CH-01 a CH-13, 4–6 h por change; CH-13 y CH-14 son rectificaciones documentadas/aplicadas según corresponda). CH-01 a CH-11 y CH-13 figuran completados/archivados o hechos a mano según `CHANGES.md` (CH-11 manual, sin carpeta archivada). Primer y único change pendiente: **CH-12 evidencia-entrega** (depende de CH-09 ✓ y CH-11 ✓; revisar brecha de proceso CH-11 en `CHANGES.md`/KB 10). CH-14 `ch-14-rectificacion-active-stack` archivado el 2026-11-12 (rectificación metodológica). Los modelos/esquema (CH-02) van antes de cualquier service/router. Docker/VPS/evidencia son changes propios (CH-03, CH-10, CH-11, CH-12).

## Reglas Duras (específicas del proyecto)

- **NUNCA Docker Compose → usar `docker run` + `--env-file`.** Sin Compose ni por desafío.
- **NUNCA skill por encima del enunciado → PDF/KB prevalecen** ante cualquier conflicto (skill, ejemplo o convención externa).
- **NUNCA migraciones → `SQLModel.metadata.create_all` en el lifespan.**
- **NUNCA float para dinero → `Decimal` siempre.** `precio > 0`, `precio_unitario > 0`, `cantidad > 0`, `stock >= 0`, `total >= 0`.
- **NUNCA consultar existencia antes de escribir → traducir `IntegrityError` a 409 con mensaje propio**, sin texto interno de la base en la respuesta.
- **NUNCA lazy loading → `joinedload`/`selectinload` en lecturas que cruzan relaciones.**
- **NUNCA SQL por concatenación → parámetros ligados siempre; `async def` en todos los handlers.**
- **NUNCA secretos en código/repo/imagen/zip → `.env` no se versiona; `env.example` sin valores reales.** Sin `DATABASE_URL` real en ningún artefacto.
- **NUNCA cambiar el stack impuesto sin consultar** (Python 3.12, FastAPI, SQLModel, SQLAlchemy 2.0 async, asyncpg, PostgreSQL 16, Docker sin Compose).
- **NUNCA inventar reglas de negocio → lo no definido va a `knowledge-base/10_preguntas_abiertas.md`;** toda decisión de dominio se justifica en `design.md`.
- **NUNCA endpoints fuera de la tabla de referencia → no hay DELETE ni PATCH de ventas.**
- **NUNCA renombrar/quitar tablas o columnas del enunciado** → nombres obligatorios.
- **NUNCA evidencia sin salida real → consola/curl/docker reales, no explicación del agente.**
- **NUNCA commitear/pushear sin pedido explícito; commits convencionales (`feat:`, `fix:`, `docs:`, `chore:`).**
- **NUNCA cerrar un change sin verificar cada escenario de su spec.**
- **AGENTS.md y CLAUDE.md idénticos; si se cambia uno, se actualiza el otro.**
- **Estructura de módulo**: todos los módulos (incluido `health`) tienen `models.py`, `schemas.py`, `service.py` y `router.py`. La lógica vive en el `service`, que recibe la sesión como parámetro y traduce los errores; el `router` solo recibe, delega y declara la respuesta, sin SQL ni `try/except` de base. Los DTO se nombran `Create`, `Update` y `Read`.

## Flujo de Trabajo

KB (`knowledge-base/`) → `CHANGES.md` → `/opsx:propose <CH-XX>` → `/opsx:apply` → `/opsx:archive`. Los tests del proyecto son archivos `.http` en `test/*.http`, no pytest. Las dudas abiertas de `10_preguntas_abiertas.md` se citan como pendientes en cada change afectado y no se resuelven en silencio.
