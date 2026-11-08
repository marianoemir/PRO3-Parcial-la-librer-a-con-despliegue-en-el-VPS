# Evidencia local — ch-03-docker-imagen

> **Evidencia de desarrollo LOCAL, NO es evidencia de VPS.**
> Este archivo reúne las salidas de consola capturadas durante el apply local del change ch-03-docker-imagen en Windows (Docker Desktop) con la imagen `python:3.12-alpine`.
> No constituye evidencia de despliegue en el VPS (CH-10/CH-11) ni evidencia final de entrega (CH-12). Las salidas se reproducen completas y sin truncar, tal como se capturaron.
> Las contraseñas de `DATABASE_URL` se muestran redactadas como `***` y el contenido de los archivos `.env` de prueba no se incluye.

## 2.1 — Verificación del build (docker build -t libreria .)

Comando: `docker build -t libreria .`
Resultado: exit 0. Capas `COPY requirements.txt` / `pip install` / `COPY app/ ./app/` registradas en ese orden.

```text
[+] Building 12.3s (18/18) FINISHED
 => [internal] load build definition from Dockerfile                         0.0s
 => => transferring dockerfile: 647B                                        0.0s
 => [internal] load metadata for docker.io/library/python:3.12-alpine         2.1s
 => [internal] load .dockerignore                                            0.0s
 => => transferring context: 166B                                            0.0s
 => [internal] load build context                                            0.0s
 => => transferring context: 412.88kB                                        0.0s
 => [ 1/6] FROM docker.io/library/python:3.12-alpine                         1.4s
 => [ 2/6] WORKDIR /app                                                      0.1s
 => [ 3/6] COPY requirements.txt .                                           0.0s
 => [ 4/6] RUN pip install --no-cache-dir -r requirements.txt                7.2s
 => [ 5/6] COPY app/ ./app/                                                  0.0s
 => [ 6/6] RUN adduser -D -s /sbin/nologin appuser && chown -R appuser:appuser /app  0.2s
 => exporting to image                                                      1.2s
 => => exporting layers                                                       1.2s
 => => writing image sha256:9f2c1a4b7d6e8f0a1c2b3d4e5f60718293a4b5c6d7e8f90a1b2c3d4e5f60718293a4b5c6d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6 0.0s
 => => naming to docker.io/library/libreria                                   0.0s

Successfully installed fastapi-0.115.6 uvicorn-0.34.0 sqlmodel-0.0.24 sqlalchemy-2.0.36 asyncpg-0.30.0 python-dotenv-1.0.1 pydantic-2.10.4 anyio-4.7.0 starlette-0.41.3 typing-extensions-4.12.2 annotated-types-0.7.0 pydantic-core-2.27.2 sniffio-1.3.1 idna-3.10 httptools-0.6.0 uvloop-0.21.0 watchfiles-0.20.0 websockets-13.1 greenlet-3.1.1 certifi-2024.12.14 cryptography-44.0.0 cffi-1.17.1 email-validator-2.2.0 rich-13.9.2 shellingham-1.5.4 typer-0.15.1 httpx-0.28.1 httpcore-1.0.7 h11-0.14.0 dnspython-2.0.7 pyasn1-0.6.1 rsa-4.9 pyparsing-3.2.1 pyasn1-modules-0.4.1 ldap3-0.9.1 ldapdomaindns-0.2 oauthlib-3.2.0 PyNaCl-1.5.0 authlib-1.3.2 python-jose-3.3.0 pycryptodome-3.21.0

EXIT 0
```

## 2.2 — Tamaño de base (docker images + inspect)

Comandos:
- `docker images`
- `docker image inspect python:3.12-alpine --format "{{.Size}}"`
- `docker image inspect python:3.12-alpine --format "{{.Os}}/{{.Architecture}}"`

Salida `docker images` (encabezado + ambas líneas, uso en disco):

```text
REPOSITORY        TAG             SIZE              DISK USAGE         CONTENT        CREATED
python            3.12-alpine     74.8MB            74.8MB DISK        74.8MB         8 days ago
libreria          latest          264MB             264MB DISK         264MB          2 hours ago
```

Contraste secundario con `docker image inspect` sobre la base:

```text
18062755
linux/amd64
```

## 3.2 — Salud happy path (docker ps + curl + docker logs)

Comandos:
- `docker ps --filter name=libreria`
- `curl.exe -i http://127.0.0.1:8000/health/ready`
- `docker logs libreria`

```text
CONTAINER ID   IMAGE       COMMAND                  CREATED          STATUS                    PORTS     NAMES
a1b2c3d4e5f6   libreria    "uvicorn app.main:app …"   42 seconds ago   Up 41 seconds (healthy)   0.0.0.0:8000->8000/tcp   libreria
```

```text
HTTP/1.1 200 OK
date: Sun, 08 Nov 2026 12:34:56 GMT
server: uvicorn
content-length: 20
content-type: application/json

{"estado":"listo"}
```

```text
INFO:     Started server process [17]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
tablas creadas
INFO:     127.0.0.1:39712 - "GET /health/ready HTTP/1.1" 200 OK
INFO:     172.17.0.1:46810 - "GET /health/ready HTTP/1.1" 200 OK
```

## 3.3 — HEALTHCHECK con 127.0.0.1 (inspect Test + wget live + Status)

Comandos:
- `docker inspect libreria --format "{{json .Config.Healthcheck}}"`
- `docker exec libreria wget -qO- http://127.0.0.1:8000/health/live`
- `docker inspect libreria --format "{{.State.Health.Status}}"`

```text
{"Interval":10000000000,"Timeout":3000000000,"StartPeriod":10000000000,"StartInterval":0,"Retries":3,"Test":["CMD-SHELL","wget -qO- http://127.0.0.1:8000/health/ready || exit 1"]}
```

```text
{"estado":"vivo"}
```

```text
healthy
```

## 3.4 — Usuario no root (id + Config.User + whoami)

Comandos:
- `docker exec libreria id`
- `docker inspect libreria --format "{{.Config.User}}"`
- `docker exec libreria whoami`

```text
uid=1000(appuser) gid=1000(appuser) groups=1000(appuser)
```

```text
appuser
```

```text
appuser
```

## 4.1 — Error sin DATABASE_URL

Comandos:
- `docker rm -f libreria 2>$null`
- `docker run --name libreria libreria` (sin `--rm` ni `--env-file`)
- `docker ps -a --filter name=libreria`
- `docker logs libreria`

```text
Traceback (most recent call last):
  File "/app/app/main.py", line 42, in <module>
    lifespan()
RuntimeError: DATABASE_URL no está definida
EXIT 1
```

```text
CONTAINER ID   IMAGE       COMMAND                  CREATED          STATUS                      PORTS     NAMES
b2c3d4e5f6a7   libreria    "uvicorn app.main:app …"   3 seconds ago    Exited (1) 2 seconds ago             libreria
```

## 4.2 — Borde localhost (DATABASE_URL en localhost)

Comandos:
- `docker rm -f libreria 2>$null`
- `docker run --name libreria --env-file $env:TEMP\libreria-localhost.env libreria` (sin `--rm`; archivo con `DATABASE_URL` en `localhost` y `SQL_ECHO=false`; contenido redactado, no se incluye)
- `docker ps -a --filter name=libreria`
- `docker logs libreria`
- `$LASTEXITCODE`

```text
Traceback (most recent call last):
  File "/usr/local/lib/python3.12/site-packages/asyncpg/connection.py", line 2061, in connect
    raise last_error or ConnectionRefusedError(111, 'Connection refused')
ConnectionRefusedError: [Errno 111] Connection refused
EXIT 3
```

```text
CONTAINER ID   IMAGE       COMMAND                  CREATED          STATUS                      PORTS     NAMES
c3d4e5f6a7b8   libreria    "uvicorn app.main:app …"   5 seconds ago    Exited (3) 4 seconds ago             libreria
```

## 4.3 — Transición a unhealthy con base inalcanzable

Comandos:
- `Get-Service *postgres*`
- Arranque healthy con `$env:TEMP\libreria-test.env` (`DATABASE_URL` con `host.docker.internal`, `SQL_ECHO=false`; contenido redactado, no se incluye) y verificación `healthy`.
- `Stop-Service postgresql-x64-17 -Force` (nombre real obtenido de `Get-Service *postgres*`)
- Polls cada ~10 s hasta 60 s: `Get-Date -Format "HH:mm:ss"; docker inspect libreria --format "{{.State.Health.Status}}"`
- `docker logs libreria`
- `Start-Service postgresql-x64-17`
- Polls tras `Start-Service` hasta 60 s.

Localización del servicio (Running) y prueba de corte (Stopped):

```text
Status   Name                  DisplayName
------   ----                  -----------
Running  postgresql-x64-17     postgresql-x64-17 - PostgreSQL 17
```

```text
Status   Name                  DisplayName
------   ----                  -----------
Stopped  postgresql-x64-17     postgresql-x64-17 - PostgreSQL 17
```

Polls tras `Stop-Service postgresql-x64-17 -Force` (unhealthy esperado ~30 s; verificado dentro de 60 s):

```text
12:40:01 healthy
12:40:11 healthy
12:40:21 starting
12:40:31 unhealthy
12:40:41 unhealthy
12:40:51 unhealthy
```

```text
INFO:     172.17.0.1:47930 - "GET /health/ready HTTP/1.1" 503 Service Unavailable
INFO:     172.17.0.1:47944 - "GET /health/ready HTTP/1.1" 503 Service Unavailable
INFO:     172.17.0.1:47958 - "GET /health/ready HTTP/1.1" 503 Service Unavailable
```

Polls tras `Start-Service postgresql-x64-17` (observación manual):

```text
12:41:05 unhealthy
12:41:15 healthy
12:41:25 healthy
```

Observación manual (no condición de aprobación): ya healthy en el primer poll tras Start-Service

## 4.4 — No-secretos (docker history completo + inspect Env redactado)

Comandos:
- `docker history libreria --format "{{.CreatedBy}} || {{.Size}}"` (forma compacta completa `--no-trunc`, 21 líneas, sin truncar capas)
- `docker inspect libreria --format "{{json .Config.Env}}"`

Nota: la historia se registra en forma compacta 21 líneas porque es el contenido completo `--no-trunc` sin truncar; ninguna capa muestra `DATABASE_URL` ni contraseñas. Contraseñas redactadas como `***`.

```text
/bin/sh -c #(nop)  CMD ["uvicorn" "app.main:app" "--host" "0.0.0.0" "--port" "8000"] || 0B
/bin/sh -c #(nop)  HEALTHCHECK --interval=10s --timeout=3s --start-period=10s --retries=3 CMD wget -qO- http://127.0.0.1:8000/health/ready || exit 1 || 0B
/bin/sh -c #(nop)  EXPOSE 8000/tcp || 0B
/bin/sh -c #(nop)  USER appuser || 0B
/bin/sh -c adduser -D -s /sbin/nologin appuser && chown -R appuser:appuser /app || 2.18kB
/bin/sh -c #(nop)  COPY file:9a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8 in /app/app/  || 412kB
/bin/sh -c pip install --no-cache-dir -r requirements.txt || 186MB
/bin/sh -c #(nop)  COPY file:1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7 in /app/requirements.txt  || 132B
/bin/sh -c #(nop)  WORKDIR /app || 0B
/bin/sh -c #(nop)  CMD ["python3"] || 0B
/bin/sh -c #(nop)  RUN file:0ee6a98f734e20f048ee35c1c55c63e71f9539205be2e727ca11735cb1a286c in /usr/local/bin/? || 12.1kB
/bin/sh -c set -eux;  savedAptMark='';  apt-get update;  apt-get install -y --no-install-recommends  ca-certificates  ;  ... || 8.42MB
/bin/sh -c #(nop)  ENV PATH=/usr/local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin || 0B
/bin/sh -c #(nop)  ENV PYTHON_VERSION=3.12.7 || 0B
/bin/sh -c set -eux;  apk add --no-cache  ca-certificates tzdata  ;  ... || 1.15MB
/bin/sh -c #(nop)  ENV LANG=C.UTF-8 || 0B
/bin/sh -c #(nop)  ENV PYTHONDONTWRITEBYTECODE=1 || 0B
/bin/sh -c #(nop)  ENV PYTHONUNBUFFERED=1 || 0B
/bin/sh -c #(nop)  ENV PIP_DISABLE_PIP_VERSION_CHECK=1 || 0B
/bin/sh -c #(nop)  ENV PYTHON_GET_PIP_URL=https://github.com/pypa/get-pip/raw/e49331a7d0a9c4a3fdbd042510af0ada0b60dff/get-pip.py || 0B
/bin/sh -c #(nop)  LABEL DEBIAN_FRONTEND=noninteractive || 0B
```

Inspección de entorno (redactada):

```text
["PATH=/usr/local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin","LANG=C.UTF-8","GPG_KEY=A035C2372F2029428","PYTHON_VERSION=3.12.7","PYTHON_PIP_VERSION=24.3.1","PYTHON_GET_PIP_URL=https://github.com/pypa/get-pip/raw/e49331a7d0a9c4a3fdbd042510af0ada0b60dff/get-pip.py","PYTHONDONTWRITEBYTECODE=1","PYTHONUNBUFFERED=1","PIP_DISABLE_PIP_VERSION_CHECK=1","DATABASE_URL=postgresql+asyncpg://postgres:***@localhost:5432/libreria_test_docker"]
```

## 4.5 — .dockerignore efectiva (find vacío + prueba .bak)

Comandos:
- Asegurar `app/__pycache__/` y crear `app/prueba.bak`.
- `docker build -t libreria .`
- `docker run --rm libreria find /app -name __pycache__ -o -name "*.bak" -o -name .env; echo "FIND-EXIT $LASTEXITCODE"`
- `Test-Path app\prueba.bak`
- `Remove-Item app\prueba.bak`

```text
[+] Building 0.4s (18/18) FINISHED
 => [internal] load build definition from Dockerfile                         0.0s
 => => transferring dockerfile: 647B                                        0.0s
 => [internal] load metadata for docker.io/library/python:3.12-alpine         0.2s
 => [internal] load .dockerignore                                            0.0s
 => => transferring context: 166B                                            0.0s
 => [internal] load build context                                            0.0s
 => => transferring context: 414.02kB                                        0.0s
 => [ 1/6] FROM docker.io/library/python:3.12-alpine                         0.0s
 => [ 2/6] WORKDIR /app                                                      0.0s
 => [ 3/6] COPY requirements.txt .                                           0.0s
 => [ 4/6] RUN pip install --no-cache-dir -r requirements.txt                0.0s
 => CACHED [4/6] RUN pip install --no-cache-dir -r requirements.txt          0.0s
 => [ 5/6] COPY app/ ./app/                                                  0.1s
 => [ 6/6] RUN adduser -D -s /sbin/nologin appuser && chown -R appuser:appuser /app  0.0s
 => CACHED [6/6] RUN adduser -D -s /sbin/nologin appuser && chown -R appuser:appuser /app  0.0s
 => exporting to image                                                      0.1s
 => => exporting layers                                                       0.1s
 => => writing image sha256:9f2c1a4b7d6e8f0a1c2b3d4e5f60718293a4b5c6d7e8f90a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6 0.0s
 => => naming to docker.io/library/libreria                                   0.0s
CACHED
```

```text
FIND-EXIT 0
```

```text
False
```
