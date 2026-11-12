# DEPLOY.md — Cómo se construyó y se corrió la imagen en el VPS

> BORRADOR (CH-10). Lo marcado **[A COMPLETAR]** se llena con lo que se haga en CH-11 (datos iniciales, D-03/D-04/D-07) y al cerrar el despliegue final.

## URL pública
- `http://179.199.129.73:8000` (verificado desde afuera del VPS el 11/11/2026 a las 21:58, hora de Argentina, después del último `docker run`: `GET /health/ready` devuelve 200 con `{"estado":"listo"}`).
- Salud: `GET /health/live` y `GET /health/ready`. Documentación interactiva: `/docs`.

## Día y hora del despliegue
- Primer despliegue: miércoles 11/11/2026, 21:24 (hora de Argentina, UTC−3). El servidor lo registró como `Thu Nov 12 00:24:12 UTC 2026`.
- Despliegue vigente (contenedor recreado después de las pruebas D-05 y de `localhost`): miércoles 11/11/2026, alrededor de las 21:57 (hora de Argentina). Quedó `healthy` y respondió 200 desde afuera a las 21:58. **[A COMPLETAR: actualizar si se vuelve a recrear el contenedor, por ejemplo al cargar los datos iniciales o al actualizar la aplicación]**

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
- **[A COMPLETAR]** `docker exec libreria <comando de datos iniciales del proyecto>` (tomarlo del README de CH-08).

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
Salidas de los casos D en `evidencia/`. Las de CH-10 están en `evidencia/ch-10-vps/`:
- `D-01-imagenes.txt`: imagen base y imagen del proyecto, con el tamaño en disco.
- `D-02-despliegue-limpio.txt`: `docker build`, `docker run`, `docker ps` en estado `healthy`, `docker logs` con el arranque y las tablas creadas.
- `D-02-acceso-externo.txt`: `GET /health/ready` desde afuera del servidor.
- `D-05-sin-database-url.txt`: la imagen sin `DATABASE_URL` termina con error y no queda sirviendo.
- `D-06-usuario-no-root.txt`: el proceso corre como `appuser`, no como root.
- `recuperacion-healthy.txt`: `docker rm -f` y el mismo `docker run` vuelven a `healthy`.
- `prueba-localhost.txt`: `DATABASE_URL` con `localhost` falla con «Connection refused».

Pendientes de CH-11: D-03, D-04 y D-07 (**[A COMPLETAR]**).
