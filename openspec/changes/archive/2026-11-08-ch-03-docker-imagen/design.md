# Design: ch-03-docker-imagen

## Context

Ver `proposal.md` — Why. Estado actual: CH-01 archivado expone `GET /health/live` y `GET /health/ready` (`SELECT 1`), lifespan con `SQLModel.metadata.create_all` y `DATABASE_URL` obligatoria sin defecto; CH-02 archivado registra los 9 modelos. No existe `Dockerfile` ni `.dockerignore` en la raíz. Restricción dura: sin Docker Compose (`docker run` + `--env-file`); Alpine con musl; fuente de verdad PDF/KB sobre skills.

## Goals / Non-Goals

**Goals:**

- `docker build` produce una imagen `libreria` que arranca con `uvicorn app.main:app --host 0.0.0.0 --port 8000` y queda `healthy` con base disponible.
- Caso D-01: base `python:3.12-alpine` < 100 MB comprobable con `docker images` (encabezado exacto y valor de cada columna de tamaño mostrada en esta máquina; referencia KB 12 ≈74,7 MB; la evidencia D-01 muestra `docker images` con `python:3.12-alpine` y la imagen `libreria`, con uso en disco registrado — consigna Ejercicio 7: «en disco»). Caso D-06: proceso no root comprobable con `docker exec libreria id`.
- Caché de capas: los cambios de código no reinstalan `requirements.txt`.
- Sin secretos en imagen ni contexto de build.

**Non-Goals:**

- No se toca `app/`, `models.py` ni `requirements.txt` (si hiciera falta, se avisa y no se hace). Si apply detecta un defecto propio de app/ que impide el arranque en contenedor, no se corrige en CH-03: se registra como pregunta abierta para un change aparte y se anota para DEPLOY.md (CH-11).
- No Docker Compose, no migraciones, no DEPLOY.md (CH-11), no despliegue en VPS (CH-10/CH-11), no evidencia final (CH-12).

## Decisions

### Imagen base: `python:3.12-alpine`
Justificación: consigna Ejercicio 7 — «El Dockerfile parte de python:3.12-alpine. Medida con Docker 29.2 … 74,7 MB; python:3.12-slim, la alternativa habitual, ocupa 180 MB y por eso no cumple. El límite es de la imagen base». KB `12_despliegue_docker_y_vps.md` §La imagen — «Base python:3.12-alpine: el límite de 100 MB es sobre la base (… 74,7 MB … frente a 180 MB de python:3.12-slim)». La comparación se hace sobre el valor medido en `docker images` para `python:3.12-alpine`, registrando el encabezado exacto (línea de encabezado de `docker images` en esta máquina) y el valor de cada columna de tamaño mostrada, que se comparan contra el límite 100 MB (referencia KB 12 ≈74,7 MB; Docker 29 puede mostrar más de una columna de tamaño). La evidencia D-01 muestra `docker images` con `python:3.12-alpine` y la imagen `libreria`, con uso en disco registrado (consigna Ejercicio 7: «en disco»): registrar el valor de uso en disco de cada línea (base Python y `libreria`). Como contraste secundario sirve `docker image inspect python:3.12-alpine --format "{{.Size}}"` en bytes. Alternativa rechazada: `python:3.12-slim` (180 MB > 100 MB, caso D-01).

### Alpine y greenlet/asyncpg (musl, sin compiladores)
Justificación: consigna Ejercicio 7 — «Alpine usa musl … se verificó que las dependencias de este stack (asyncpg, pydantic-core y el resto del requirements.txt) se instalan en esa imagen sin compilar nada, así que no hace falta instalar ningún compilador». KB 12 §La imagen — «se verificó que las dependencias de este stack (asyncpg, pydantic-core y el resto del requirements.txt) se instalan sin compilar nada: no hace falta instalar ningún compilador». Consecuencia: el `Dockerfile` NO instala compiladores (`build-base`, `gcc`, `libffi-dev`, etc.) ni paquetes del sistema salvo que el build real lo pida; si al construir apareciera una compilación (p. ej. `greenlet`), se detiene y se documenta antes de agregar un paquete — no se inventa la necesidad por anticipado. `requirements.txt` actual (`fastapi[standard]>=0.111`, `sqlmodel>=0.0.24`, `sqlalchemy[asyncio]>=2.0`, `asyncpg>=0.30`, `python-dotenv>=1.0`) es el stack verificado por la consigna.

### Orden de capas y `--no-cache-dir`
Justificación: consigna Ejercicio 7 — «Copia y instala requirements.txt antes de copiar el código, con --no-cache-dir: mientras las dependencias no cambien, esa capa sale de la caché y un cambio en el código no reinstala todo». KB 12 §La imagen — «Capas: copiar e instalar requirements.txt antes de copiar el código, con --no-cache-dir (la capa sale de la caché solo si cambian las dependencias)». Secuencia: `WORKDIR /app` → `COPY requirements.txt .` → `RUN pip install --no-cache-dir -r requirements.txt` → `COPY app/ ./app/` → `USER` → `EXPOSE 8000` → `CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]`. Copiá solo el código: `COPY app/ ./app/` (nunca `COPY . .` ni copiar todo el contexto); la app no necesita otros archivos en runtime: solo el paquete `app/` (con `app/main.py`, `app/core/` y `app/modules/*/` según KB 08), las dependencias ya instaladas en el build y el `CMD` uvicorn; ningún otro archivo del repo se requiere en runtime. COPY app/ ./app/ ya deja afuera lo de la raíz (.env, .venv/, .git/ en raíz no se copian); los patrones `**` cubren los __pycache__/*.pyc/*.bak anidados dentro de app/. Por semántica de `COPY` de Docker, `COPY app/ ./app/` sólo copia el directorio `app/`; los archivos de la raíz del contexto no entran. Los patrones `**` del `.dockerignore` cubren los anidados dentro de `app/`, coherente con la intención de exclusión de KB 12 y la consigna.

### Restricción para CH-08 (datos iniciales)
El script de datos iniciales (CH-08) debe vivir dentro de `app/` (p. ej. `app/seed.py`) para ejecutarse con `docker exec libreria python -m app.seed`, porque `COPY app/ ./app/` no copia nada fuera de `app/` (scripts de raíz, `scripts/` u otros dirs quedarían fuera de la imagen en runtime). Esta es una restricción para CH-08, no se implementa en CH-03.

### Usuario no root con `USER`
Justificación: consigna Ejercicio 7 — «La aplicación no corre como root: se crea un usuario sin privilegios y se lo activa con USER … Si alguien vulnera la aplicación, no es dueño del contenedor». KB 12 §La imagen — «se crea un usuario y se activa con USER; la app no corre como root (caso D-06)». Decisión: usuario dedicado (p. ej. creado con `adduser` en Alpine) con permisos de lectura/ejecución sobre `/app`; no se corre como root ni con `--privileged`. Alternativa rechazada: correr como root (viola D-06).

### Comando uvicorn (no `fastapi run`)
Justificación: restricción del usuario para este change — «Arranque con uvicorn app.main:app --host 0.0.0.0 (no fastapi run)». Consigna Ejercicio 7 — «el contenedor levanta uvicorn con app.main:app escuchando en 0.0.0.0». KB 12 §Cómo se corre — «La app escucha en 0.0.0.0 dentro del contenedor (con 127.0.0.1 el puerto publicado nunca respondería)». Se usa instrucción `CMD` en forma de arreglo JSON (sin shell).

### HEALTHCHECK sobre `/health/ready` con `127.0.0.1` y `wget`
Justificación: consigna Ejercicio 7 — «Declara un HEALTHCHECK sobre GET /health/ready». KB 12 §Cómo se corre — «HEALTHCHECK declarado en la imagen sobre GET /health/ready; docker ps lo muestra». Direccionamiento: consigna Ejercicio 7 §EL HEALTHCHECK Y LOCALHOST y KB 12 §El HEALTHCHECK y localhost — en Alpine no hay `curl`; `wget` resuelve `localhost` primero a `::1` (IPv6) y uvicorn con `--host 0.0.0.0` escucha sólo IPv4; «la dirección que sirve es 127.0.0.1». Por eso: `HEALTHCHECK --interval=10s --timeout=3s --start-period=10s --retries=3 CMD wget -qO- http://127.0.0.1:8000/health/ready || exit 1`. No se usa `localhost` ni `curl`. La comprobación manual documentada es `docker exec libreria wget -qO- http://127.0.0.1:8000/health/live` (KB 12 / consigna).

### Timings del HEALTHCHECK (decisión propia)
Decisión propia justificada: `interval=10s`, `timeout=3s`, `start-period=10s`, `retries=3`. Justificación: el `start-period=10s` evita un `unhealthy` falso mientras el lifespan de CH-01 hace `create_all` + el primer `SELECT 1` de `/health/ready`; el `timeout=3s` es suficiente para `wget` local sin bloquear el chequeo; el `interval=10s` con `retries=3` exige tres fallos seguidos (≈30 s) para marcar `unhealthy`, lo que da margen a un pico de base sin rotar el contenedor al primer tropezón, pero a la vez detecta una base inalcanzable con rapidez. Es decisión propia para que `docker ps` muestre `healthy` en D-02 sin esperar hasta 30 s de intervalo.

### `.dockerignore` sin secretos
Justificación: consigna Ejercicio 7 — «El .dockerignore excluye .env, .venv, .git y los _pycache_, y ni la dirección de la base ni su contraseña aparecen en el Dockerfile». KB 12 §La imagen — «.dockerignore excluye .env, .venv, .git y __pycache__; ni la dirección de la base ni su contraseña están en el Dockerfile». Decisión: `.dockerignore` excluye exactamente `.env`, `.venv/`, `.git/`, `**/__pycache__/`, `**/*.pyc`, `**/*.bak` (los patrones sin `**` sólo valen en la raíz del contexto; `**` cubre `__pycache__`/`*.pyc`/`*.bak` anidados dentro de `app/`); el `Dockerfile` no define `DATABASE_URL` ni secretos (la config entra por `--env-file` al correr, KB 12 §Cómo se corre). Extras no excluidos por la consigna (p. ej. `evidencia/`, `test/`) quedan dentro salvo justificación en apply — no se inventan exclusiones.

### Sin Docker Compose; prueba con `docker run` + `--env-file`
Justificación: consigna Ejercicio 7 — «No se usa Docker Compose: la base de datos no forma parte del paquete, porque el servidor ya tiene PostgreSQL» y §Cómo se corre con `docker run -d --name libreria -p <puerto>:8000 --restart unless-stopped --env-file <archivo-de-variables> libreria`. KB `09_decisiones_y_supuestos.md` DD-03 — despliegue de una imagen con `docker run` + `--env-file`; KB 12 §Cómo se corre — `--env-file` entrega la config desde un archivo fuera del repo y de la imagen. Regla de prueba: hay dos archivos de variables de prueba fuera del repo — `$env:TEMP\libreria-test.env` con `DATABASE_URL` que contiene `host.docker.internal` y `SQL_ECHO=false` (tareas 3.1 y 4.3) y `$env:TEMP\libreria-localhost.env` con `localhost` y `SQL_ECHO=false` (tarea 4.2) — nunca dentro del repo, y ambos se borran una sola vez al terminar (5.1 y Migration Plan). Sugerencia (no requisito): usar una base de prueba desechable distinta de `libreria_dev` para estas pruebas, p. ej. `libreria_test_docker` creada para estas pruebas y eliminada después. Alternativa rechazada: Compose (prohibido por consigna y hards).

### `host.docker.internal` y «la base no está en localhost»
Justificación: descripción del change — «Desde el contenedor no sirve localhost para llegar a la base: considerá host.docker.internal». Consigna Ejercicio 7 §LA BASE NO ESTÁ EN LOCALHOST — «Dentro de un contenedor, localhost es el propio contenedor … Si la base corre directamente en el servidor, el contenedor la alcanza por el nombre host.docker.internal, que en Linux hay que habilitar con --add-host=host.docker.internal:host-gateway en el docker run. Si la cátedra entrega otra dirección, se usa esa». KB 12 §La base no está en localhost y §Cómo se corre — mismo tratamiento. Consecuencia para CH-03: el `Dockerfile` no fija `DATABASE_URL`; sólo se deja documentada la forma de pasarla. La detección temprana de red es de CH-10 (CH-03 depende de CH-01; CH-10 depende de CH-02 + CH-03).

### Puertos y variables (`EXPOSE`, puerto publicado)
Justificación: consigna Ejercicio 7 — `-p <puerto>:8000 publica sólo la aplicación, en el puerto que asigna la cátedra`; KB 12 §Cómo se corre — `-p <puerto>:8000`. Decisión: `EXPOSE 8000` en la imagen; el mapeo `-p <puerto>:8000` se decide en cada `docker run` (CH-10 lo hace en el VPS). No se hardcodea el puerto público.

## UI Mockups

Decision: no (no UI)

## Risks / Trade-offs

- [Riesgo] Alpine/musl obliga a recompilar una dependencia futura (p. ej. `greenlet`, `asyncpg` en otra plataforma) → Mitigación: la consigna ya verificó que el stack actual instala sin compilar; si `docker build` lo exige en apply, se frena y se justifica el paquete antes de instalarlo (ver Open Questions).
- [Fallo de diagnóstico] HEALTHCHECK con `localhost` da `unhealthy` espurio → Mitigación: `127.0.0.1` + `wget` (consigna y KB 12).
- [Fallo de diagnóstico] `HEALTHCHECK` sobre `/health/ready` depende del código que define Q2 pendiente → Mitigación: se sigue la propuesta del equipo documentada en CH-01 (503 con cuerpo propio si `SELECT 1` falla) y queda configurable; ver Open Questions.
- [Red] `DATABASE_URL` con `localhost` dentro del contenedor da «Connection refused» → Mitigación: `host.docker.internal` con `--add-host=host.docker.internal:host-gateway` en Linux o dirección de la cátedra (consigna, KB 12); la validación formal es de CH-10.
- [Secretos] Hornear `.env` o `DATABASE_URL` en una capa es irreversible → Mitigación: `.dockerignore` + ningún `ENV` con secretos; `--env-file` fuera de la imagen, fuera del repo en prueba y borrado una sola vez al terminar (5.1 y Migration Plan).
- [Defecto en app/] Si apply detecta un defecto propio de app/ que impide el arranque en contenedor, no se corrige en CH-03: se registra como pregunta abierta para un change aparte y se anota para DEPLOY.md (CH-11). Es prohibición expresa de corrección fuera de alcance en este change.
- [CH-08] El script de datos iniciales depende de esta decisión de almacenamiento: debe vivir dentro de `app/` (p. ej. `app/seed.py`) para ejecutarse con `docker exec libreria python -m app.seed`, porque `COPY app/ ./app/` no copia nada fuera de `app/`.

## Migration Plan

No aplica (sin código previo que migrar). Rollback: basta con no construir la imagen; al revertir, borrar `Dockerfile` y `.dockerignore` no afecta `app/` ni `requirements.txt`. La imagen es aditiva. Limpieza de prueba: antes de cada `docker run --name libreria` se ejecuta `docker rm -f libreria` (ignorar si no existe); al terminar se ejecuta `docker rm -f libreria`, `docker rmi libreria` (imagen de prueba) y, si existen, `Remove-Item "$env:TEMP\libreria-test.env", "$env:TEMP\libreria-localhost.env" -Force`, además de eliminar la base de prueba desechable (p. ej. `libreria_test_docker`) si se creó. Nunca debe quedar un `.env` de prueba dentro del repo.

## Open Questions

- **Q2 — `10_preguntas_abiertas.md` §(2): ¿qué devuelve `GET /health/ready` y con qué código si la base no responde?** La tabla de endpoints del PDF declara sólo 200 para `/health/ready`. El HEALTHCHECK de este change queda sobre `GET /health/ready` con la convención de CH-01 (503 con cuerpo propio si `SELECT 1` falla, a confirmar con cátedra). Si la cátedra define otro código, se ajusta sólo la condición de éxito del `HEALTHCHECK`. No se inventa la regla.
- **Defecto propio de app/ que impide el arranque en contenedor:** si apply detecta un defecto propio de app/ que impide el arranque en contenedor, no se corrige en CH-03: se registra como pregunta abierta para un change aparte y se anota para DEPLOY.md (CH-11).
- **CH-08 depende de esta decisión de almacenamiento:** el script de datos iniciales debe vivir dentro de `app/` (p. ej. `app/seed.py`) para ejecutarse con `docker exec libreria python -m app.seed`, porque `COPY app/ ./app/` no copia nada fuera de `app/`.
- **¿Qué `VOLUME`/permisos necesita el usuario no root para `app/` si la app escribe archivos?** Nada de lo escrito en consigna/KB indica escrituras en el contenedor; no se inventa. Si el build/run de apply lo requiere, se resuelve entonces y se documenta.
- **¿Necesita Alpine de algún paquete (p. ej. `libffi`, `build-base`, `greenlet`) para alguna dependencia?** La consigna y la KB dicen que no hace falta ningún compilador para el stack actual; no se agrega ninguno por anticipado. Si `docker build` lo pide en apply, se agrega sólo lo estrictamente necesario con justificación.
- **¿Si el tamaño en disco supera 100 MB, cuál es el valor que cuenta para D-01?** Consultar a cátedra; no resolver en silencio. La tarea 2.2 registra el encabezado exacto y el valor de cada columna de tamaño de `docker images` en esta máquina, sin asumir cuál de esos valores es el que cuenta para el límite de 100 MB.
