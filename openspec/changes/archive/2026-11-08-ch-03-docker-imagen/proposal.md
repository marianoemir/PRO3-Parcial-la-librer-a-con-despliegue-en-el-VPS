# Proposal: ch-03-docker-imagen

## Why

La aplicación (CH-01) ya arranca con FastAPI + lifespan + `create_all`, pero no existe imagen Docker: sin `Dockerfile` ni `.dockerignore` no hay forma de empaquetar, probar con `docker run` ni desplegar en el VPS, y quedan sin cubrir los casos D-01 (base `python:3.12-alpine` < 100 MB) y D-06 (usuario no root). CH-03 arranca temprano en paralelo al dominio (DD-06) porque la imagen y la detección de red/`host.docker.internal` pueden validarse sin esperar a los changes de CRUD.

## What Changes

- Crear `Dockerfile` desde `python:3.12-alpine` (encabezado exacto y valor de cada columna de tamaño de `docker images` se registran y se comparan contra el límite 100 MB; referencia KB 12 y consigna Ejercicio 7 ≈74,7 MB; no `slim` de 180 MB), con arranque `uvicorn app.main:app --host 0.0.0.0 --port 8000` (no `fastapi run`).
- Orden de capas para caché: `COPY requirements.txt` + `pip install --no-cache-dir` antes de `COPY app/ ./app/` (sólo el código, nunca `COPY . .`); en runtime la app sólo necesita el paquete `app/` (más las dependencias ya instaladas en el build y el arranque uvicorn; ningún otro archivo del repo se requiere en runtime — ver `app/main.py` y KB 08 estructura `app/main.py` + `app/core/` + `app/modules/*/`).
- Usuario sin privilegios con `USER` (caso D-06: `docker exec libreria id` no es root).
- `HEALTHCHECK` con `wget` a `http://127.0.0.1:8000/health/ready` (nunca `localhost`: Alpine/`wget` resuelve primero a `::1` IPv6 y uvicorn escucha IPv4 — KB 12 §El HEALTHCHECK, consigna Ejercicio 7; el código exacto de error de `/health/ready` sigue sujeto a Q2 de `10_preguntas_abiertas.md` §(2), ver Open Questions).
- Crear `.dockerignore` que excluye exactamente `.env`, `.venv/`, `.git/`, `**/__pycache__/`, `**/*.pyc`, `**/*.bak`: sin secretos en la imagen ni en el repo.
- Sin Docker Compose: la imagen se prueba sólo con `docker run` + `--env-file` (hards `NUNCA Docker Compose`, consigna Ejercicio 7, DD-03; los archivos de prueba viven fuera del repo — `$env:TEMP\libreria-test.env` con `host.docker.internal` y `SQL_ECHO=false` (3.1, 4.3) y `$env:TEMP\libreria-localhost.env` con `localhost` y `SQL_ECHO=false` (4.2) — y se borran una sola vez en 5.1 (y Migration Plan); nunca dentro del repo).
- Sin tocar `app/`, `models.py` ni `requirements.txt`: sólo `Dockerfile` y `.dockerignore` (más lo que la spec justifique; si la imagen necesitara un cambio en esos archivos, se avisa y no se hace).
- El script de datos iniciales (CH-08) debe vivir dentro de `app/` (p. ej. `app/seed.py`) para ejecutarse con `docker exec libreria python -m app.seed`, porque `COPY app/ ./app/` no copia nada fuera de `app/`.
- Si apply detecta un defecto propio de app/ que impide el arranque en contenedor, no se corrige en CH-03: se registra como pregunta abierta para un change aparte y se anota para DEPLOY.md (CH-11).

## Capabilities

### New Capabilities

- `docker-imagen`: empaquetado de la aplicación en imagen Docker con arranque uvicorn, usuario no root, HEALTHCHECK sobre `/health/ready` y exclusión de secretos del contexto de build.

### Modified Capabilities

Ninguna. No cambia ningún requisito de `foundation`, `core-models` ni `libros-autorias`.

## Impact

- **Código afectado**: sólo raíz del repo (`Dockerfile`, `.dockerignore`). NO se toca `app/`, `models.py` ni `requirements.txt`.
- **Casos cubiertos**: D-01 (base `python:3.12-alpine` < 100 MB; encabezado exacto y valor de cada columna de tamaño de `docker images` se registran; referencia KB 74,7 MB; límite 100 MB; evidencia final en CH-12; si el tamaño en disco supera 100 MB, qué valor cuenta lo consulta la cátedra — ver Preguntas abiertas en `design.md`) y D-06 (`docker exec libreria id` no es root). La evidencia D-01 muestra `docker images` con `python:3.12-alpine` y la imagen `libreria`; el valor a registrar es el uso en disco (consigna Ejercicio 7: «en disco»). Habilita D-02 (build + run limpio, contenedor `healthy`), D-05 (sin `DATABASE_URL` el contenedor no queda sirviendo) para CH-10/CH-11, sin cerrarlas acá.
- **Reglas que la gobiernan**: consigna Ejercicio 7 (contenedor: la imagen) y Ejercicio 8 (despliegue con `docker run`); KB `12_despliegue_docker_y_vps.md` §§ La imagen, Capas/usuario/sin secretos, El HEALTHCHECK y localhost, La base no está en localhost; KB `07_flujos_principales.md` §Flujo 6; KB `10_preguntas_abiertas.md` §(2) — PENDIENTE. No se inventan reglas de negocio (RN-xx/RT-xx de dominio no aplican a este change de infra).
- **Fuera de alcance**: Docker Compose (prohibido), cambios de código en `app/`, cambios en `requirements.txt`, migraciones (se usa `create_all` en el lifespan de CH-01), DEPLOY.md (lo escribe CH-11), despliegue en VPS y evidencia final (CH-10, CH-11, CH-12), endpoints nuevos.
- **Riesgos / dependencias**: depende de CH-01 (lifespan, `GET /health/live` y `GET /health/ready`, escucha en `0.0.0.0`, `DATABASE_URL` obligatoria sin defecto — D-05). CH-02 ya está archivado y no bloquea la imagen. Ver Preguntas abiertas en `design.md` sobre el código de error de `/health/ready` (Q2, pendiente de cátedra) y `host.docker.internal` en Linux.
- **Restricción para CH-08**: el script de datos iniciales debe vivir dentro de `app/` (p. ej. `app/seed.py`) para poder ejecutarse con `docker exec libreria python -m app.seed`, porque `COPY app/ ./app/` no copia nada fuera de `app/` (scripts de raíz, `scripts/` u otros dirs quedarían fuera de la imagen en runtime).
- Si apply detecta un defecto propio de app/ que impide el arranque en contenedor, no se corrige en CH-03: se registra como pregunta abierta para un change aparte y se anota para DEPLOY.md (CH-11).
