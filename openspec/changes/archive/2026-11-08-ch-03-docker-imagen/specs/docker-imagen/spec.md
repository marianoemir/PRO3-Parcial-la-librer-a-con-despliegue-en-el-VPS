# Spec Delta

## Purpose

Empaquetar la API de librería en una imagen Docker reproducible, sin secretos y con diagnóstico de salud, para probarla con `docker run` y desplegarla en el VPS sin Docker Compose.

## ADDED Requirements

### Requirement: Imagen base Alpine y capas en orden de caché
La imagen SHALL partir de `python:3.12-alpine`, copiar e instalar `requirements.txt` con `--no-cache-dir` antes de copiar sólo el código con `COPY app/ ./app/` (nunca `COPY . .` ni copiar todo el contexto), y exponerse en el puerto 8000. En runtime la app sólo necesita el paquete `app/` (más dependencias instaladas en el build y el arranque uvicorn; ningún otro archivo del repo se requiere — ver `app/main.py` y KB 08).

#### Scenario: Evidencia D-01 con uso en disco de base y libreria
- **WHEN** se verifica el tamaño de la base con `docker images` para el caso D-01
- **THEN** la evidencia muestra `docker images` con AMBAS líneas, `python:3.12-alpine` y la imagen `libreria`, con uso en disco registrado (consigna Ejercicio 7: «en disco»): registrar el valor de uso en disco de cada línea (base Python y `libreria`); el encabezado exacto y el valor de cada columna de tamaño mostrada se registran y comparan contra el límite <100 MB para la base

#### Scenario: Build limpio y capa de dependencias reutilizable
- **WHEN** se ejecuta `docker build -t libreria .` sin cambios en `requirements.txt` y luego se reconstruye tras editar sólo código de `app/`
- **THEN** `docker build` sale 0 y en la segunda corrida la capa de `pip install` se reutiliza de caché (no reinstala dependencias)

### Requirement: Arranque con uvicorn sobre 0.0.0.0 y usuario no root
La imagen SHALL arrancar con `uvicorn app.main:app --host 0.0.0.0 --port 8000` (sin `fastapi run`), crear un usuario sin privilegios y activarlo con `USER`; el proceso NO SHALL correr como root.

#### Scenario: Contenedor healthy con base disponible y usuario no root
- **WHEN** antes se ejecutó `docker rm -f libreria` (ignorar si no existe) y se corre `docker run -d --name libreria -p 8000:8000 --env-file $env:TEMP\libreria-test.env libreria` con una `DATABASE_URL` válida y alcanzable que contiene `host.docker.internal` y `SQL_ECHO=false` (el archivo vive fuera del repo, con una base de prueba desechable distinta de `libreria_dev`, p. ej. `libreria_test_docker`; se borra una sola vez en 5.1; nunca dentro del repo)
- **THEN** `docker ps --filter name=libreria` muestra `healthy`, `curl.exe -i http://127.0.0.1:8000/health/ready` devuelve 200, y `docker exec libreria id` muestra un uid distinto de 0 (caso D-06)

### Requirement: HEALTHCHECK sobre /health/ready con 127.0.0.1
La imagen SHALL declarar `HEALTHCHECK` con `wget` a `http://127.0.0.1:8000/health/ready` y NO SHALL usar `localhost` ni `curl`.

#### Scenario: HEALTHCHECK declarado con 127.0.0.1 y /health/ready
- **WHEN** se inspecciona el healthcheck de la imagen con `docker inspect libreria --format "{{json .Config.Healthcheck}}"`
- **THEN** el `Test` contiene `127.0.0.1` y `/health/ready` y NO contiene `localhost` ni `curl`

#### Scenario: HEALTHCHECK marca unhealthy con base inalcanzable
- **WHEN** la aplicación arrancó healthy con una base alcanzable usando `$env:TEMP\libreria-test.env` (`DATABASE_URL` con `host.docker.internal` y `SQL_ECHO=false`), primero se localiza el nombre real del servicio con `Get-Service *postgres*` (p. ej. si la salida es `postgresql-x64-16`, ese es `<thatName>`; no asumir el nombre `postgresql`), luego se corta la base del host (`Stop-Service <thatName> -Force` como administrador) manteniendo el contenedor en ejecución durante ~30 s (interval 10s x retries 3), y después se levanta de nuevo el servicio (`Start-Service <thatName>` como administrador)
- **THEN** `docker inspect libreria --format "{{.State.Health.Status}}"` responde `unhealthy` (o `docker ps` muestra el contenedor como `(unhealthy)`); lo obligatorio es llegar a `unhealthy`. Tras `Start-Service <thatName>`, registrar como observación (no como requisito) si vuelve a `healthy` o no: «observado: vuelve a healthy / no vuelve por pool con conexiones muertas» (el pool puede retener conexiones muertas)

### Requirement: Contexto de build sin secretos
El `.dockerignore` SHALL excluir exactamente `.env`, `.venv/`, `.git/`, `**/__pycache__/`, `**/*.pyc`, `**/*.bak`, y el `Dockerfile` NO SHALL contener `DATABASE_URL` ni contraseñas; la configuración entra sólo por `--env-file` al correr.

#### Scenario: .dockerignore excluye secretos y entorno local
- **WHEN** existen en el contexto `app/__pycache__/` (directorio real) y `app/prueba.bak`, y se ejecuta `docker build -t libreria .` seguido de `docker run --rm libreria find /app -name __pycache__ -o -name "*.bak" -o -name .env` (sin paréntesis porque PowerShell los interpreta)
- **THEN** `docker build` sale 0, el `find` devuelve vacío (sin salida / sin coincidencias — sin `__pycache__`, `*.bak` ni `.env` dentro de `/app`), `docker history libreria --no-trunc` no muestra `DATABASE_URL` ni contraseñas, y `docker inspect libreria --format "{{json .Config.Env}}"` no contiene `DATABASE_URL` real

### Requirement: Arranque sin DATABASE_URL no queda sirviendo
La imagen SHALL fallar al arrancar si falta `DATABASE_URL` y NO SHALL quedar sirviendo (ni `running` ni `healthy`) en ese caso.

#### Scenario: Contenedor sin DATABASE_URL termina Exited y nunca queda sirviendo
- **WHEN** antes se ejecutó `docker rm -f libreria` (ignorar si no existe) y se corre `docker run --name libreria libreria` sin `--rm` ni `--env-file` ni `DATABASE_URL`
- **THEN** el contenedor termina con error (código distinto de 0) y `docker ps -a --filter name=libreria` muestra `Exited (1)` o equivalente, nunca `running`/`healthy` (caso D-05; depende de CH-01 y Q2 pendiente, ver Open Questions)

#### Scenario: Base en localhost es inalcanzable desde el contenedor
- **WHEN** antes se ejecutó `docker rm -f libreria` (ignorar si no existe) y `DATABASE_URL` usa `localhost` como host y `SQL_ECHO=false` desde el archivo externo `$env:TEMP\libreria-localhost.env` mientras la base corre en el host
- **THEN** el contenedor termina en estado `Exited` y `docker logs libreria` muestra un error de conexión (`ConnectionRefusedError` o `Connect call failed` de asyncpg); el fix documentado es `host.docker.internal` con `--add-host=host.docker.internal:host-gateway` en Linux, o la dirección provista por la cátedra (nunca `localhost` dentro del contenedor)
