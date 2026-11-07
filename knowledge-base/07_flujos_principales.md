# Flujos Principales

## Flujo 1: Arranque y ciclo de vida
**Disparador**: inicio de la aplicación (local con uvicorn o contenedor).
**Actor**: sistema (lifespan de FastAPI).

**Pasos**:
1. `app/main.py` entra al lifespan: crea el motor asíncrono y la fábrica de sesiones, los guarda en `app.state`.
2. `SQLModel.metadata.create_all` crea las tablas que faltan (con todos los modelos ya importados).
3. Registra los routers de los módulos y deja la app atendiendo.
4. Al apagar, cierra el motor.

**Casos de error**:
- Base no responde → el arranque falla y el contenedor termina con error (no queda atendiendo).
- `DATABASE_URL` ausente → el contenedor no queda sirviendo (caso D-05).

## Flujo 2: Alta de un libro con autorías
**Disparador**: `POST /libros/` con ISBN, título, precio, stock, `editorial_id`, `genero_id` y lista `autores` (`autor_id`, `rol`, `orden`).
**Actor**: encargado de catálogo.

**Pasos**:
1. El router recibe el DTO `LibroCreate` y lo delega al `service` con la sesión de `Depends(get_session)`.
2. El `service` construye el libro y sus `LibroAutor` y escribe **sin consultar antes** la existencia de los ids (RT-02).
3. La base valida FK, `isbn` UNIQUE, CHECK de precio/stock, PK de `libro_autor` y CHECK de rol/orden.
4. Si la base acepta → 201 con el detalle del libro (precargado con `joinedload`/`selectinload`). Si rechaza → la traducción del `IntegrityError` a 409 con mensaje propio (RN-12).

**Diagrama de secuencia**:
```
Cliente → Router (libros) → Service → Session → PostgreSQL
                              ← 201 detalle / 409 mensaje propio ←
```

**Casos de error**: editorial o autor inexistente → 409 (C-04); ISBN repetido → 409 (C-02); cuerpo inválido → 422.

## Flujo 3: Alta de una venta con renglones
**Disparador**: `POST /ventas/` con `cliente_id` y lista `renglones` (`libro_id`, `cantidad`).
**Actor**: personal de ventas.

**Pasos**:
1. El DTO anidado garantiza al menos un renglón y ningún libro repetido (RN-04, RN-05), si no → 422.
2. El `service` carga los libros, copia cada `precio_unitario` desde el libro (RN-06) y calcula `total` como suma de `cantidad × precio_unitario` (RN-07).
3. Escribe la venta con sus renglones (composición); FK inválida (cliente o libro inexistente) → 409 (C-05).
4. Responde 201 con la venta (cliente y renglones precargados) y agenda con `BackgroundTasks` el aviso simulado (`await asyncio.sleep(0.5)` + mensaje en el log) **después** de la respuesta.

**Casos de error**: sin renglones o con libro repetido → 422; cliente/libro inexistente → 409; nunca viajan precio, total ni fecha en el cuerpo.

## Flujo 4: Lectura sin N+1, listado paginado y búsqueda
**Disparador**: `GET /libros/{id}`, `GET /ventas/{id}`, `GET /libros/`.
**Actor**: cualquier llamador.

**Pasos**:
1. El `service` arma la consulta declarando `joinedload` (a uno) o `selectinload` (colecciones) para editorial, género, autorías y renglones.
2. El detalle se resuelve con un número fijo de consultas, independiente de la cantidad de autores o renglones (caso C-07, evidencia en consola).
3. En listados, `limit` (1–100, defecto 20) y `offset` (≥ 0) validados por `Query` (RN-10); el filtro por título usa parámetros ligados case-insensitive (RN-11); `' OR '1'='1` produce 200 con lista vacía (C-08).

**Casos de error**: id no entero → 422 sin ejecutar el handler (C-01); id inexistente → 404; paginación fuera de rango → 422.

## Flujo 5: Alta y lectura de perfil de cliente
**Disparador**: `POST /clientes/{id}/perfil`, `GET /clientes/{id}`.
**Pasos**:
1. Al crear, el `service` escribe el perfil con `cliente_id` del path; la base rechaza el segundo perfil por `cliente.cliente_id` UNIQUE → 409 (C-03); cliente inexistente → 409 o 404 según la tabla de códigos (POST declara 201/404/409).
2. Al leer un cliente, se precarga su perfil (objeto único, no lista) y sus ventas en endpoints dedicados.

## Flujo 6: Contenedor y despliegue en el VPS
**Disparador**: `docker build` y `docker run` en el VPS.
**Pasos**:
1. Se construye la imagen desde `python:3.12-alpine` (ver `12_despliegue_docker_y_vps.md`).
2. Se corre con `docker run -d --name libreria -p <puerto>:8000 --restart unless-stopped --env-file <archivo> libreria`.
3. Docker detecta salud vía `HEALTHCHECK` sobre `GET /health/ready` (con `127.0.0.1`, no `localhost`).
4. Se cargan los datos iniciales con `docker exec libreria …`; el despliegue queda en línea en la URL de `DEPLOY.md` hasta que se publiquen las notas.

**Casos de error**: `DATABASE_URL` con localhost dentro del contenedor → "Connection refused" (usar `host.docker.internal` con `--add-host=host.docker.internal:host-gateway` en Linux, o la dirección provista por la cátedra); `HEALTHCHECK` con `localhost` → `unhealthy` espurio (Alpine/`wget` resuelve IPv6 primero; usar `127.0.0.1`).
