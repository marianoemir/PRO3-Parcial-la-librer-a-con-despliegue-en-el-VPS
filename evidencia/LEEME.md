# Índice de Evidencia — Parcial Programación III

Este directorio reúne las evidencias de ejecución de consultas y despliegue en VPS requeridas por la consigna del parcial.

## 1. Evidencia vigente de entrega (en la raíz de `evidencia/`)

Corresponde al estado final del proyecto con el dataset determinista de 27 filas (CH-15):

- **`C-07-consola-sql.log`**: Salida de consola con `SQL_ECHO=true` demostrando la ausencia del problema N+1 en las consultas de libros y ventas con carga anticipada (`joinedload` y `selectinload`). El libro 6 del ejemplo del enunciado se crea con POST /libros/ y no viene precargado en el seed.
- **`C-07-conteo.txt`**: Conteo exacto de consultas por endpoint observado en la prueba:
  ```text
  POST   /libros/       SELECT=3
  GET    /libros/1      SELECT=3
  GET    /libros/6      SELECT=3
  GET    /ventas/1      SELECT=2
  POST   /ventas/       SELECT=3
  GET    /ventas/2      SELECT=2
  ```
- **`D-03-url-publica.txt`**: Carga de datos iniciales con `python -m app.seed` ejecutado en el contenedor y pruebas de los endpoints (`GET /health/ready`, `GET /libros/` y `POST /ventas/`) desde afuera del VPS en la URL pública `http://libreria.marianochirino.me:8000`.
- **`D-04-persistencia.txt`**: Demostración de persistencia tras eliminación forzada (`docker rm -f libreria`) y recreación con el mismo `docker run`; el contenedor vuelve a estado `healthy` y los datos en PostgreSQL se conservan intactos.
- **`D-07-aviso-comprobante.txt`**: Registro en `docker logs` del aviso de comprobante emitido en segundo plano (`BackgroundTasks`) tras registrar una venta con `POST /ventas/`, apareciendo después de la línea de respuesta HTTP.

## 2. Evidencia de despliegue inicial en el VPS (`evidencia/ch-10-vps/`)

Capturas obtenidas durante el despliegue base de la imagen sin datos (CH-10):

- **`D-01-imagenes.txt`**: Inspección y tamaño en disco de la imagen base (`python:3.12-alpine`, 74.8 MB) y de la imagen de la app (`libreria`, 264 MB).
- **`D-02-despliegue-limpio.txt`**: Proceso de `docker build`, `docker run` inicial, contenedor en estado `healthy` y logs de arranque con las 9 tablas creadas por `SQLModel.metadata.create_all`.
- **`D-02-acceso-externo.txt`**: Consulta externa con curl a `GET /health/ready` respondiendo 200 `{"estado":"listo"}`.
- **`D-05-sin-database-url.txt`**: Verificación de que sin la variable `DATABASE_URL` el contenedor termina con EXIT=1 (según el archivo) y no queda sirviendo.
- **`D-06-usuario-no-root.txt`**: Inspección de procesos y usuario comprobando ejecución como usuario no privilegiado `appuser` (UID 1000).
- **`recuperacion-healthy.txt`**: Recreación de contenedor volviendo exitosamente al estado `healthy`.
- **`prueba-localhost.txt`**: Prueba negativa demostrando que apuntar `DATABASE_URL` a `localhost` dentro del contenedor falla con `Connection refused` (EXIT=3) y que la conexión debe ser vía el nombre del servicio `grupo10_db` en la red Docker.

## 3. Evidencia histórica de desarrollo local

Subcarpetas de archivo histórico generadas durante el desarrollo de changes previos:

- **`ch-03-local/`**:
  - `ch03-evidencia.md`: Evidencia de desarrollo capturada durante el apply local del change ch-03-docker-imagen en Windows (Docker Desktop) con la imagen `python:3.12-alpine`.
- **`ch-07-local/`**:
  - `C-07-libros-consultas.txt` y `C-07-ventas-consultas.txt`: Consultas capturadas en una base de desarrollo durante la verificación local de CH-07 (libros 45 y 48; ventas 11 y 12 en uvicorn puerto 8010).
  - *Nota histórica*: El archivo `tasks.md` archivado de CH-07 (tarea 4.5 en `openspec/changes/archive/2026-11-11-ch-07-ventas-renglones/tasks.md`) cita las rutas originales `evidencia/C-07-*-consultas.txt`, las cuales fueron trasladadas a esta carpeta histórica para mantener la raíz de `evidencia/` reservada para la entrega vigente.
