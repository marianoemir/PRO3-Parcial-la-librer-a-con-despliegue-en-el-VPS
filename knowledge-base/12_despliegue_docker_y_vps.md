# Despliegue: Docker y VPS (extra)

Archivo extra (no canónico): detalla los Ejercicios 7 y 8 de la consigna. Los 10 archivos canónicos son 01–10.

## La imagen
- Base `python:3.12-alpine`: el límite de 100 MB es sobre la base (python:3.12-alpine ocupa 74,7 MB en disco con Docker 29.2, frente a 180 MB de `python:3.12-slim`). La imagen del proyecto con dependencias puede ser mayor; es lo esperado. Alpine usa musl y suele traer problemas con paquetes que se compilan, pero se verificó que las dependencias de este stack (asyncpg, pydantic-core y el resto del `requirements.txt`) se instalan sin compilar nada: no hace falta instalar ningún compilador.
- Capas: copiar e instalar `requirements.txt` **antes** de copiar el código, con `--no-cache-dir` (la capa sale de la caché solo si cambian las dependencias).
- Usuario sin privilegios: se crea un usuario y se activa con `USER`; la app no corre como root (caso D-06: `docker exec libreria id` no es root).
- Sin secretos: `.dockerignore` excluye `.env`, `.venv`, `.git` y `__pycache__`; ni la dirección de la base ni su contraseña están en el `Dockerfile` (entran por variables de entorno al correr).

## Cómo se corre
```bash
docker run -d --name libreria -p <puerto>:8000 --restart unless-stopped \
  --env-file <archivo-de-variables> libreria
```
- `-p <puerto>:8000` publica solo la aplicación, en el puerto que asigna la cátedra.
- `--restart unless-stopped` levanta el contenedor si termina (reinicio del servidor, base aún no lista).
- `--env-file` entrega la configuración desde un archivo que vive en el servidor, fuera del repositorio y de la imagen: `DATABASE_URL` (driver `postgresql+asyncpg`, host, usuario, contraseña y base provistos por la cátedra) y `SQL_ECHO=false`.
- La app escucha en `0.0.0.0` dentro del contenedor (con `127.0.0.1` el puerto publicado nunca respondería). Crea sus tablas al arrancar; si la base no responde, el contenedor termina con error.
- `HEALTHCHECK` declarado en la imagen sobre `GET /health/ready`; `docker ps` lo muestra.

## La base no está en localhost
Dentro de un contenedor, `localhost` es el propio contenedor: una `DATABASE_URL` con localhost falla con "Connection refused" aunque PostgreSQL funcione. Si la base corre directamente en el servidor, el contenedor la alcanza con `--add-host=host.docker.internal:host-gateway` en el `docker run` (en Linux hay que habilitarlo así); si la cátedra entrega otra dirección, se usa esa.

## El HEALTHCHECK y localhost
En Alpine no hay `curl`; `wget` (que sí viene) resuelve `localhost` primero a `::1` (IPv6), y uvicorn con `--host 0.0.0.0` escucha solo en IPv4. Un `HEALTHCHECK` con `http://localhost:8000/` falla con "Connection refused" aunque el servidor responda desde afuera, y el contenedor queda `unhealthy` sin nada roto. Se comprueba con `docker exec libreria wget -qO- http://127.0.0.1:8000/health/live`; la dirección que sirve es `127.0.0.1`.

## Despliegue en el VPS y DEPLOY.md
- El grupo construye la imagen en el servidor (o la construye en otro lado y la lleva) y la corre con `docker run`; la elección se documenta en `DEPLOY.md`.
- Una vez arriba, la base se carga ejecutando dentro del contenedor el comando de datos iniciales del proyecto (`docker exec libreria …`).
- Queda accesible desde afuera en la URL que se declara en `DEPLOY.md` y **sigue en línea hasta que se publiquen las notas** (la corrección lo prueba).
- `DEPLOY.md` incluye: URL pública, día y hora del despliegue, comandos `docker build` y `docker run` completos (con el nombre del archivo de variables, sin su contenido), cualquier cambio hecho al proyecto para que corra en el contenedor, y cómo actualizar (construir la imagen de nuevo, eliminar el contenedor y volver a correrlo). Los datos no se pierden: viven en la base del servidor, no en el contenedor.
- Si el proyecto no arranca en el contenedor por un defecto propio (p. ej., una ruta de salud que no responde como pide el documento), se corrige y se anota en `DEPLOY.md`.

## Casos D (evidencia en `evidencia/`)
D-01: `docker images` — base por debajo de 100 MB y el `Dockerfile` parte de ella. D-02: servidor limpio: `docker build` + `docker run`, `docker ps` muestra `healthy`, `docker logs` muestra el arranque con las tablas creadas. D-03: desde afuera del VPS: `GET /health/ready` (200), `GET /libros/` con los datos iniciales (200), `POST /ventas/` con el cuerpo del caso C-06 (201, precios copiados, total calculado). D-04: `docker rm -f libreria` y el mismo `docker run` → vuelve a `healthy` y los datos siguen (la base no vive en el contenedor; `create_all` solo crea las tablas que faltan). D-05: correr sin `DATABASE_URL` → el contenedor no queda sirviendo (termina con error: no hay dirección por defecto). D-06: usuario del proceso no root. D-07: el aviso del comprobante aparece en `docker logs libreria` después de la línea de la respuesta.

## Entrega (cátedra)
Un único `.zip` llamado `Parcial_Cap1a4_<NombreDelGrupo>.zip`, subido por **un solo integrante** al campus, con: código fuente completo, `requirements.txt`, `env.example` (forma de `DATABASE_URL`, sin valores reales), `test/`, `Dockerfile`, `.dockerignore`, `README.md` (nombres y apellidos de los integrantes + pasos para levantar desde cero: entorno virtual, dependencias, `.env`, arranque del servidor que crea las tablas y carga de datos iniciales), `DEPLOY.md` y `evidencia/` (captura o fragmento del caso C-07 y salida de cada caso D). El `.zip` **no** contiene `.venv`, `__pycache__` ni `.env`. Si incluye `.git`, también se revisa su historial: una contraseña que alguna vez se subió y se borró después sigue estando en el historial y exige cambiarla.

Grupo/integrantes:
- Mariano Chirino
- Andrés Fabre
- Facundo Quiroga
