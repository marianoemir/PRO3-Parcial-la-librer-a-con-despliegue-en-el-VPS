# DEPLOY.md — Cómo se construyó y se corrió la imagen en el VPS

> Lo marcado **[A COMPLETAR]** se confirma al cerrar el despliegue final.

## URL pública
- `http://libreria.marianochirino.me:8000` (IP del VPS: 179.199.129.73; verificado desde afuera del VPS el 12/11/2026 a las 17:30, hora de Argentina, después del último `docker run`: `GET /libros/` y `GET /ventas/2` responden 200 con los datos cargados).
- Salud: `GET /health/live` y `GET /health/ready`. Documentación interactiva: `/docs`.

## Día y hora del despliegue
- Primer despliegue: miércoles 11/11/2026, 21:24 (hora de Argentina, UTC−3). El servidor lo registró como `Thu Nov 12 00:24:12 UTC 2026`.
- Despliegue vigente (contenedor recreado en la prueba D-04, con los datos iniciales ya cargados): jueves 12/11/2026, 17:30 (hora de Argentina), con el seed nuevo (27 filas). Quedó `healthy` y respondió 200 desde afuera. **[A COMPLETAR: actualizar si se vuelve a recrear el contenedor]**

## Entorno
- Servidor: VPS con Ubuntu y Docker 29.8.0. **[A COMPLETAR: VPS asignado por la cátedra / propio del grupo]**
- Base de datos: PostgreSQL 18 que ya corre en el servidor como contenedor (servicio `grupo10_db`), base `libreria` con usuario propio (`libreria_app`). La consigna indica PostgreSQL 16: con la 18 el arranque completo funciona, `create_all` crea las 9 tablas y asyncpg conecta sin problemas (ver `evidencia/ch-10-vps/D-02-despliegue-limpio.txt`).
- La base no forma parte de la imagen y no se usa Docker Compose.
- Imagen base `python:3.12-alpine` (74,8 MB en disco, medido en el VPS; ver `evidencia/ch-10-vps/D-01-imagenes.txt`). La imagen `libreria` ocupa 264 MB en disco.

## Archivo de variables
- Ruta en el servidor: `/root/libreria.env` (fuera del repositorio y de la imagen, permisos 600).
- Contiene `DATABASE_URL` (driver `postgresql+asyncpg`, host `grupo10_db`, puerto 5432, base `libreria`, con usuario y contraseña) y `SQL_ECHO=false`. El contenido no se publica; la forma está en `env.example`.

## Comandos
Obtener el código (primera vez) y construir la imagen en el servidor (el repositorio queda en `/root/libreria`):

```bash
cd /root
git clone https://github.com/marianoemir/PRO3-Parcial-la-librer-a-con-despliegue-en-el-VPS.git libreria
cd libreria
docker build -t libreria .
```

Correr el contenedor:

```bash
docker run -d --name libreria --network easypanel-grupo10 -p 8000:8000 \
  --restart unless-stopped --env-file /root/libreria.env libreria
```

- `--network easypanel-grupo10`: une el contenedor a la red de Docker de la base. Dentro de un contenedor `localhost` es el propio contenedor, así que la base se alcanza por el nombre del servicio (`grupo10_db`). Por eso no hace falta `--add-host=host.docker.internal:host-gateway`, que solo aplica a una base instalada directamente en el host. Con `localhost` en `DATABASE_URL` el arranque falla con «Connection refused» (ver `evidencia/ch-10-vps/prueba-localhost.txt`).
- `-p 8000:8000`: publica solo la aplicación. El puerto 5432 de la base no se publica.
- `--restart unless-stopped`: Docker vuelve a levantar el contenedor si el servidor se reinicia o si la base no respondía al arrancar.
- `--env-file /root/libreria.env`: configuración desde el servidor, sin secretos en la imagen.

## Datos iniciales
Con el contenedor arriba y las tablas creadas, se cargan con el comando de datos iniciales del proyecto:

```bash
docker exec libreria python -m app.seed
```

Carga el dataset documentado de 27 filas (2 editoriales, 2 géneros, 5 autores, 5 libros, 5 autorías, 3 clientes, 2 perfiles, 1 venta y 2 renglones). **ADVERTENCIA: Reejecutar el seed reinicia los datos**: vacía y recarga las 9 tablas del proyecto en una única transacción sin confirmación previa (con secuencias/ids coherentes), dejando siempre el mismo estado inicial conocido. La salida está en `evidencia/D-03-url-publica.txt`. El script vive en `app/seed.py`, que la imagen ya incluye: si se modifica `app/seed.py`, debe reconstruirse la imagen (`docker build -t libreria .`) antes de ejecutar el seed en el contenedor.

## Cambios hechos al proyecto para que corra en el contenedor
- Ninguno: el build y el arranque funcionaron sin modificar el código (confirmado con D-02, D-05 y D-06). Lo que se agregó al proyecto fue solo el `Dockerfile` y el `.dockerignore`.

## Cómo se actualiza la aplicación
```bash
cd /root/libreria
git pull
docker build -t libreria .
docker rm -f libreria
docker run -d --name libreria --network easypanel-grupo10 -p 8000:8000 \
  --restart unless-stopped --env-file /root/libreria.env libreria
```
Los datos no se pierden: viven en la base del servidor y no en el contenedor. Eliminar y volver a correr el contenedor lo deja otra vez `healthy` (ver `evidencia/ch-10-vps/recuperacion-healthy.txt`).

## Evidencia
Salidas de los casos D en `evidencia/`. Las de CH-11 están directamente en `evidencia/`:
- `D-03-url-publica.txt`: seed, `GET /health/ready`, `GET /libros/` y `POST /ventas/` desde afuera, en la URL pública.
- `D-04-persistencia.txt`: `docker rm -f` y el mismo `docker run`; vuelve a `healthy` y los datos siguen.
- `D-07-aviso-comprobante.txt`: el aviso del comprobante en `docker logs`, después de la línea de la respuesta.

Las de CH-10 están en `evidencia/ch-10-vps/`:
- `D-01-imagenes.txt`: imagen base y imagen del proyecto, con el tamaño en disco.
- `D-02-despliegue-limpio.txt`: `docker build`, `docker run`, `docker ps` en estado `healthy`, `docker logs` con el arranque y las tablas creadas.
- `D-02-acceso-externo.txt`: `GET /health/ready` desde afuera del servidor.
- `D-05-sin-database-url.txt`: la imagen sin `DATABASE_URL` termina con error y no queda sirviendo.
- `D-06-usuario-no-root.txt`: el proceso corre como `appuser`, no como root.
- `recuperacion-healthy.txt`: `docker rm -f` y el mismo `docker run` vuelven a `healthy`.
- `prueba-localhost.txt`: `DATABASE_URL` con `localhost` falla con «Connection refused».
