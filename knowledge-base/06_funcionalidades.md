# Funcionalidades

Organizadas por épica y luego por historia de usuario (US-NNN). Las puntuaciones corresponden a los 8 ejercicios de la consigna (fuente: `docs/Parcial_Cap1a4_Consigna.pdf`).

## Épica 1: Proyecto, conexión y ciclo de vida (8 puntos)
### US-001 — Levantar la aplicación con lifespan y crear el esquema
**Como** operador de la librería
**Quiero** que la API cree las tablas que falten al arrancar, sin migraciones
**Para** empezar a operar sobre una base vacía

**Criterios de aceptación**:
- [ ] Motor asíncrono y fábrica de sesiones creados en el lifespan, guardados en `app.state`, motor cerrado al apagar.
- [ ] `SQLModel.metadata.create_all` con todos los modelos importados; la app no queda sirviendo si la base no responde.
- [ ] `GET /health/live` no toca la base; `GET /health/ready` ejecuta `SELECT 1`.
- [ ] `DATABASE_URL` leída de `.env`; `env.example` incluye la forma del valor sin secretos.

**Reglas relacionadas**: RN-12, RT-01.

## Épica 2: Modelos, restricciones y relaciones (22 puntos)
### US-002 — Publicar el modelo relacional completo
**Como** encargado de catálogo
**Quiero** las tablas con sus UNIQUE, CHECK, FK e índices y navegación bilateral
**Para** tener la base como garante de unicidad y consistencia

**Criterios de aceptación**:
- [ ] Tablas y columnas exactas de `04_modelo_de_datos.md` (sin quitar ni renombrar).
- [ ] `Cliente.perfil` devuelve un objeto, no una lista; dinero con `Decimal`, nunca `float`.
- [ ] Cada FK con índice y `Relationship(back_populates=.)` en ambos extremos.
- [ ] `libro_autor` como clase intermedia con `rol` y `orden` (navegación `libro.autorias[i].autor`).

**Reglas relacionadas**: RN-01, RN-02, RN-03, RN-09, RT-04.

## Épica 3: Contratos y CRUD (12 puntos)
### US-003 — Operar los recursos de referencia con DTO separados
**Como** encargado de catálogo
**Quiero** crear, listar, ver y corregir editoriales, géneros, autores, libros y clientes con códigos HTTP correctos
**Para** mantener el catálogo y los clientes con contratos claros

**Criterios de aceptación**:
- [ ] Los DTO de alta no llevan `id`; los PATCH aplican solo los campos enviados (`exclude_unset`).
- [ ] Códigos: 201 al crear, 404 si no existe, 409 si la base rechaza, 422 si el contrato no se cumple.
- [ ] Listados paginados (`limit`/`offset`, RN-10) y búsqueda de libros por título con parámetros ligados (RN-11).

**Reglas relacionadas**: RN-01, RN-02, RN-03, RN-05, RN-09, RN-10, RN-11, RN-12, RT-01, RT-02.

**Endpoints de referencia (método, ruta, códigos)**:
| Método | Ruta | Códigos |
|--------|------|---------|
| GET | `/health/live`, `/health/ready` | 200 |
| POST/GET/PATCH | `/editoriales/`, `/editoriales/{id}` | 201/409/422; 200/422; 200/404/409 |
| GET | `/editoriales/{id}/libros` | 200, 404 |
| POST/GET | `/generos/`, `/generos/{id}` | 201/409; 200 |
| GET | `/generos/{id}/libros` | 200, 404 |
| POST | `/autores/` | 201, 422 (ver 10_preguntas_abiertas.md sobre 409) |
| GET/PATCH | `/autores/{id}` | 200, 404, 422 |
| GET | `/autores/{id}/libros` (con rol y orden) | 200, 404 |
| POST/GET/PATCH | `/libros/`, `/libros/`, `/libros/{id}` | 201/409/422; 200/422; 200/404/409/422 |
| POST | `/clientes/` | 201, 409, 422 |
| GET/PATCH | `/clientes/{id}` | 200/404; 200/404/409/422 |
| POST | `/clientes/{id}/perfil` | 201, 404, 409 |
| GET | `/clientes/{id}/ventas` | 200, 404 |
| POST/GET/GET | `/ventas/`, `/ventas/`, `/ventas/{id}` | 201/409/422; 200/422; 200/404 |

## Épica 4: Altas con relaciones (17 puntos)
### US-004 — Registrar libros con autorías y ventas con renglones
**Como** personal de ventas
**Quiero** dar de alta un libro indicando editorial, género y autores con rol/orden, y registrar una venta con sus renglones sin indicar precios
**Para** que el servidor copie precios y calcule el total, sin falsificación por el cliente

**Criterios de aceptación**:
- [ ] Alta de libro: viajan `editorial_id`, `genero_id` y lista `autores` (`autor_id`, `rol`, `orden`); si la base rechaza un id, 409 sin consulta previa.
- [ ] Alta de venta: viaja `cliente_id` y lista `renglones` (`libro_id`, `cantidad`); el precio se copia del libro y el total lo calcula el servidor (RN-06, RN-07).
- [ ] La venta se crea con sus renglones cumpliendo RN-04 a RN-07; entrada de ejemplo del enunciado (`cliente_id: 2`, renglones `libro_id: 1` ×2 y `libro_id: 4` ×1) produce total `77000.00` con subtotales `50000.00` y `27000.00`.

**Reglas relacionadas**: RN-04, RN-05, RN-06, RN-07, RN-08, RN-12, RT-01, RT-02.

## Épica 5: Lecturas sin N+1, asincronía, contenedor y despliegue (8 + 8 + 15 + 10 puntos)
### US-005 — Leer detalles con número fijo de consultas y sin bloqueos
**Criterios de aceptación**:
- [ ] Detalle de libro (editorial, género, autores) y de venta (cliente, renglones) resueltos con `joinedload`/`selectinload`; número fijo de consultas que no crece con autores o renglones (caso C-07).
- [ ] Todos los handlers `async def`, sin llamadas bloqueantes; aviso del comprobante con `BackgroundTasks` + `await asyncio.sleep(0.5)` y mensaje en el log, después de la respuesta.

### US-006 — Empaquetar la imagen y desplegarla en el VPS
**Criterios de aceptación**:
- [ ] `Dockerfile` desde `python:3.12-alpine` (< 100 MB según `docker images`), requirements antes del código con `--no-cache-dir`, usuario sin privilegios, `HEALTHCHECK` sobre `GET /health/ready`, escucha en `0.0.0.0`, sin secretos.
- [ ] Despliegue con `docker run -d --name libreria -p <puerto>:8000 --restart unless-stopped --env-file <archivo> libreria`; base alcanzable por `host.docker.internal` si aplica; `DEPLOY.md` con URL, comandos y procedimiento de actualización; despliegue en línea hasta que se publiquen las notas.

Ver el detalle completo en `12_despliegue_docker_y_vps.md`.

## Casos de prueba mínimos (test/*.http + evidencia/)
C-01 (parámetro de ruta no entero → 422 sin ejecutar el handler), C-02 (ISBN/email repetido → 409 propio), C-03 (segundo perfil → 409), C-04 (libro con editorial/autor inexistente → 409), C-05 (venta con libro/cliente inexistente → 409), C-06 (venta válida dos renglones → 201, precios copiados, total calculado), C-07 (detalle libro/venta → cantidad fija de consultas, con evidencia en consola), C-08 (búsqueda `' OR '1'='1` → 200 con lista vacía). Casos D-01 a D-07 sobre el VPS con salidas en `evidencia/`.
