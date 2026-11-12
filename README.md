# PRO3-Parcial-la-librer-a-con-despliegue-en-el-VPS
Parcial de Programación 3 Backend: Una librería de barrio necesita una API para su catálogo y sus ventas.

**Programación III · Entrega Parcial 2 · Comisión 1**
**Grupo 10 (Lobos Solitarios)**

Integrantes:
- Mariano Chirino (usuario de GitHub: marianoemir) - Legajo 41031
- Andrés Fabre (usuario de GitHub: andresfabre27) - Legajo 53885
- Facundo Quiroga (usuario de GitHub: Buhonero009) - Legajo 52737

**API en línea:** http://libreria.marianochirino.me:8000
- Documentación (Swagger): http://libreria.marianochirino.me:8000/docs
- Estado: http://libreria.marianochirino.me:8000/health/ready
- Abrir con `http://` (no `https://`): la API sirve HTTP plano en el puerto 8000. Si el navegador redirige a https, probar con `http://179.199.129.73:8000/docs`. La raíz `/` y `/health` dan 404, es lo esperado.

## Pasos para levantar el proyecto desde cero en local

Para poner en marcha la aplicación en una máquina local desde un clon limpio del repositorio:

1. **Crear y activar el entorno virtual (venv)**:
   ```bash
   python -m venv .venv
   # En Windows PowerShell:
   .\.venv\Scripts\Activate.ps1
   # En Linux/macOS:
   source .venv/bin/activate
   ```

2. **Instalar dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configurar variables de entorno desde env.example**:
   Copiar el archivo de plantilla a `.env` (el archivo `.env` nunca se versiona):
   ```bash
   # En Windows PowerShell:
   Copy-Item env.example .env
   # En Linux/macOS:
   cp env.example .env
   ```
   Editar `.env` indicando la `DATABASE_URL` correspondiente a una base PostgreSQL vacía (driver `postgresql+asyncpg`, ej: `postgresql+asyncpg://postgres:tu_password@localhost:5432/libreria`).

4. **Crear las tablas arrancando el servidor**:
   Al arrancar la aplicación, el lifespan ejecuta `SQLModel.metadata.create_all` creando automáticamente las 9 tablas requeridas:
   ```bash
   uvicorn app.main:app --host 127.0.0.1 --port 8000
   ```
   Verificar en consola el mensaje `Application startup complete` y detener con `Ctrl+C` (o dejarlo corriendo en otra terminal).

5. **Cargar los datos iniciales (seed)**:
   Con el esquema ya creado, ejecutar el comando de carga inicial (ver sección [Datos iniciales (seed)](#datos-iniciales-seed)):
   ```bash
   python -m app.seed
   ```
   Esto dejará la base en el estado determinista documentado de 27 filas.

## Entorno
- Según lo indicado por el profesor, la aplicación usa el PostgreSQL de la calculadora del grupo (`grupo10_db`); no se pidieron datos de acceso adicionales. La base propia es `libreria`, con rol `libreria_app`.
- En el VPS la base no forma parte de la imagen y no se usa Docker Compose. Toda la configuración de despliegue se encuentra documentada en [DEPLOY.md](DEPLOY.md).

## Casos de prueba

A continuación se detalla la correspondencia entre los casos de prueba de la consigna (`C-01` a `C-08`), su archivo ejecutable en `test/` y el rótulo exacto de la petición:

| Caso | Archivo | Rótulo exacto de request |
|------|---------|--------------------------|
| C-01 | `test/ch09-casos-http-c.http` | `### C-01 — path no entero: FastAPI debe rechazar antes del handler` |
| C-02a | `test/ch09-casos-http-c.http` | `### C-02a — ISBN del libro 1 repetido con el resto del cuerpo válido` |
| C-02b | `test/ch09-casos-http-c.http` | `### C-02b — email de cliente ya existente en el seed (cliente 2 Tomás Ríos)` |
| C-03 | `test/ch09-casos-http-c.http` | `### C-03 — segundo perfil para el cliente 1, que ya lo tiene en el seed` |
| C-04a | `test/ch09-casos-http-c.http` | `### C-04a — editorial inexistente dentro de int4` |
| C-04b | `test/ch09-casos-http-c.http` | `### C-04b — autor inexistente dentro de int4` |
| C-05 (1) | `test/ch07-ventas-errores.http` | `### 409 - POST venta con cliente_id inexistente (C-05 / Task 2.3)` |
| C-05 (2) | `test/ch07-ventas-errores.http` | `### 409 - POST venta con libro_id inexistente en renglones (C-05 / Task 2.1)` |
| C-06 | `test/ch08-seed-datos-iniciales.http` | `### Ejemplo enunciado / C-06 — POST /ventas/ produce id 2 y total 77000.00` |
| C-07-prep | `test/ch09-c07-consultas-fijas.http` | `### C-07-prep — crear libro con varias autorías (ejemplo del enunciado)` |
| C-07a | `test/ch09-c07-consultas-fijas.http` | `### C-07a — libro 1 del seed (una autoría)` |
| C-07b | `test/ch09-c07-consultas-fijas.http` | `### C-07b — libro con varias autorías creado en C-07-prep` |
| C-07c | `test/ch09-c07-consultas-fijas.http` | `### C-07c — detalle venta con dos renglones (venta 1 del seed)` |
| C-07d | `test/ch09-c07-consultas-fijas.http` | `### C-07d — venta auxiliar válida (un renglón)` |
| C-07e | `test/ch09-c07-consultas-fijas.http` | `### C-07e — detalle venta auxiliar con un renglón` |
| C-08 | `test/ch09-casos-http-c.http` | `### C-08 — intento de inyección en filtro de título` |

### Notas operativas sobre orden de ejecución y seed

- **Prerrequisito obligatorio**: Usar una base local dedicada, vacía y autorizada para pruebas. Iniciar la API una vez para que el lifespan cree el esquema; después ejecutar `python -m app.seed` (reinicia las 9 tablas al dataset de 27 filas) y volver a dejar la API en escucha.
- **Orden del ciclo limpio**: `C-01`, `C-02`, `C-03`, `C-04`, `C-08`, `C-05` (desde `test/ch07-ventas-errores.http`).
- **Reinicio del seed antes de C-06 y C-07**: Antes de ejecutar C-06 (en `test/ch08-seed-datos-iniciales.http`) y antes de C-07 (en `test/ch09-c07-consultas-fijas.http`), correr `python -m app.seed` (es repetible), porque los INSERT fallidos de las pruebas previas (C-02a, C-04a, C-04b, C-05) consumen valores de secuencia (`nextval`) en PostgreSQL aun cuando la transacción hace rollback.
- **Comparación de consultas fijas (C-07)**: Reiniciar localmente la API con diagnóstico SQL habilitado (`SQL_ECHO=true`) y comparar en consola las consultas de cada par:
  - Libro 1 (1 autoría, del seed) vs libro creado por el ejemplo (2 autorías) -> 3 SELECT fijos.
  - Venta con dos renglones vs venta auxiliar con un renglón -> 2 SELECT fijos.
- **Casos de despliegue en VPS (D-01 a D-07)**: Su ejecución, evidencias y trazabilidad en servidor están documentadas en [evidencia/LEEME.md](evidencia/LEEME.md) y [DEPLOY.md](DEPLOY.md).

## Evidencia de pruebas y despliegue
Las evidencias requeridas de consultas y despliegue se organizan en dos ubicaciones principales:
- `evidencia/`: contiene la evidencia vigente de consultas SQL sin N+1 (`C-07-consola-sql.log` y `C-07-conteo.txt`), y los casos D probados contra la URL pública y el VPS (`D-03-url-publica.txt`, `D-04-persistencia.txt` y `D-07-aviso-comprobante.txt`).
- `evidencia/ch-10-vps/`: contiene la evidencia del despliegue inicial en el servidor (`D-01-imagenes.txt`, `D-02-despliegue-limpio.txt`, `D-02-acceso-externo.txt`, `D-05-sin-database-url.txt`, `D-06-usuario-no-root.txt`, `recuperacion-healthy.txt` y `prueba-localhost.txt`).
Para más detalles sobre la estructura y trazabilidad histórica, consultar [evidencia/LEEME.md](evidencia/LEEME.md).

## Datos iniciales (seed)

`app/seed.py` carga un dataset **fijo, mínimo y documentado** de 27 filas para que los casos
C-06 y D-03 sean reproducibles tanto en local como en el VPS. Es un comando de
línea de comandos, independiente de la API: no expone endpoints, no define
routers ni schemas y **no crea ni modifica el esquema** (las tablas las crea
`SQLModel.metadata.create_all` en el lifespan de `app/main.py`). Tampoco aplica
reglas de negocio no definidas: en particular, **no descuenta stock** por la
venta que incluye el dataset (ver *Pendientes*).

> **ADVERTENCIA: Reejecutar el seed reinicia los datos.** El comando ejecuta
> un vaciado (`TRUNCATE TABLE ... RESTART IDENTITY CASCADE`) y recarga de las 9
> tablas del proyecto en una única transacción sin confirmación previa, dejando
> siempre el mismo estado inicial conocido y secuencias coherentes.

Los valores monetarios del dataset son `Decimal` (nunca `float`) y la fecha de
la venta es fija y con zona horaria (`2026-01-15T12:00:00+00:00`), de modo que
cada ejecución deja la base en el mismo estado.

### Contenido del dataset

| Tabla | id | Contenido |
|-------|----|-----------|
| `editorial` | 1 | Sudamericana — Argentina |
| `editorial` | 2 | Anagrama — España |
| `genero` | 1 | Novela |
| `genero` | 2 | Cuento |
| `autor` | 1 | Julio Cortázar — Argentina |
| `autor` | 2 | Ricardo Piglia — Argentina |
| `autor` | 3 | Adolfo Bioy Casares — Argentina |
| `autor` | 4 | Silvina Ocampo — Argentina |
| `autor` | 5 | Ernesto Sabato — Argentina |
| `libro` | 1 | ISBN `978-950-00-0001-1` — "Rayuela" — 25000.00 — stock 10 — editorial 1 — género 1 |
| `libro` | 2 | ISBN `978-950-00-0002-8` — "Bestiario" — 18000.00 — stock 6 — editorial 1 — género 2 |
| `libro` | 3 | ISBN `978-950-00-0003-5` — "La invención de Morel" — 20000.00 — stock 5 — editorial 1 — género 1 |
| `libro` | 4 | ISBN `978-950-00-0004-2` — "Respiración artificial" — 27000.00 — stock 7 — editorial 2 — género 1 |
| `libro` | 5 | ISBN `978-950-00-0005-9` — "El túnel" — 19500.00 — stock 3 — editorial 1 — género 1 |
| `libro_autor` | (libro 1, autor 1) | rol `autor`, orden 1 |
| `libro_autor` | (libro 2, autor 1) | rol `autor`, orden 1 |
| `libro_autor` | (libro 3, autor 3) | rol `autor`, orden 1 |
| `libro_autor` | (libro 4, autor 2) | rol `autor`, orden 1 |
| `libro_autor` | (libro 5, autor 5) | rol `autor`, orden 1 |
| `cliente` | 1 | Ana Gómez — `ana.gomez@example.com` |
| `cliente` | 2 | Tomás Ríos — `tomas@example.com` |
| `cliente` | 3 | Carla Fernández — `carla.fernandez@example.com` |
| `perfil_cliente` | 1 | cliente 1 — `+54 11 5555-0001` — Av. Corrientes 1234, CABA |
| `perfil_cliente` | 2 | cliente 3 — `+54 11 5555-0003` — Calle 50 456, La Plata |
| `venta` | 1 | cliente 2 — fecha `2026-01-15T12:00:00+00:00` — total 77000.00 |
| `renglon_venta` | 1 | venta 1 — libro 1 — cantidad 2 — precio_unitario 25000.00 |
| `renglon_venta` | 2 | venta 1 — libro 4 — cantidad 1 — precio_unitario 27000.00 |

Totales por tabla: 2 editoriales, 2 géneros, 5 autores, 5 libros, 5 autorías,
3 clientes, 2 perfiles, 1 venta y 2 renglones (27 filas). El ISBN
`978-950-00-0006-6` no está precargado en el seed para quedar disponible para el
ejemplo de alta de libro del enunciado. El total de la venta 1 es la suma de
`cantidad × precio_unitario` de sus renglones (77000.00) y cada renglón copia el
precio del libro.

Los datos son **de ejemplo del implementador**, no una regla de negocio: los
mails usan el dominio reservado `@example.com`. La lista cerrada definitiva de
filas base está pendiente de la cátedra (ver *Pendientes*).

### Cómo se ejecuta en local

El seed exige que el esquema ya exista; por eso se arranca la aplicación al
menos una vez antes de cargar los datos:

```bash
# 1) Crear el esquema: arrancar la app y detenerla
uvicorn app.main:app --host 127.0.0.1 --port 8000
# (Ctrl+C cuando aparezca "Application startup complete")

# 2) Cargar el dataset (usa DATABASE_URL del entorno o de .env)
python -m app.seed
```

El comando imprime un resumen del estado inicial cargado con los conteos por
tabla y los ids del dataset, y termina con código de salida `0`. No
levanta la API ni abre puertos, y nunca imprime `DATABASE_URL` ni credenciales.
En Windows, si el resumen muestra mal los acentos, ejecutar con
`$env:PYTHONIOENCODING="utf-8"` (o usar Windows Terminal con UTF-8).

### Cómo se ejecuta en el VPS (contenedor)

El `Dockerfile` copia `app/` completo a la imagen, así que el módulo viaja con
ella y se ejecuta dentro del contenedor sin pasos extra:

```bash
docker exec libreria python -m app.seed
```

Usa la `DATABASE_URL` que el contenedor recibió por `--env-file` y reinicia las 9
tablas al mismo dataset documentado arriba.

### Repetibilidad por reinicio, atomicidad y secuencias

- **Reiniciable / Repetible**: cada ejecución vacía las 9 tablas del proyecto
  (`TRUNCATE TABLE ... RESTART IDENTITY CASCADE`) y recarga el dataset completo,
  restableciendo siempre el mismo estado inicial conocido incluso si existían datos
  creados posteriormente vía API.
- **Atómica**: vaciado, inserciones y alineación de secuencias ocurren en una
  única transacción. Si la base rechaza una fila o se interrumpe la carga, se revierte
  toda la transacción completa (incluido el vaciado) y el comando termina con
  código `1`, conservando la base intacta en su estado previo.
- **Secuencias alineadas**: insertar ids explícitos no avanza las secuencias en
  PostgreSQL, por eso el seed ejecuta `setval` al máximo id cargado de
  `editorial`, `genero`, `autor`, `libro`, `cliente`, `perfil_cliente`, `venta`
  y `renglon_venta`. Un alta posterior por API obtiene el id siguiente
  (por ejemplo, el siguiente libro disponible o `POST /ventas/` con `id: 2`) en
  lugar de chocar con el dataset.

### Errores y códigos de salida

| Situación | Mensaje | Código |
|-----------|---------|--------|
| Éxito (carga o reinicio de estado) | Resumen del estado inicial cargado (27 filas) + ids | `0` |
| `DATABASE_URL` ausente o vacía | "Falta la variable de entorno DATABASE_URL…" | `1` |
| Base inalcanzable | "No se pudo conectar con la base de datos…" | `1` |
| Esquema ausente | "El esquema no existe… Iniciá la aplicación al menos una vez…" | `1` |
| Conflicto de integridad / fallo de carga | "No se pudieron cargar los datos iniciales debido a un conflicto de integridad. Se revirtió toda la carga..." | `1` |

Los mensajes son propios: no incluyen SQL, trazas internas, nombres de
constraints, `DATABASE_URL` ni credenciales. El seed no ejecuta `create_all` ni
migraciones.

### Pendientes (knowledge-base/10_preguntas_abiertas.md)

- **§(1) Descuento de stock**: el enunciado no define si una venta descuenta
  stock. La venta 1 del dataset vende 2 unidades del libro 1 y 1 del libro 4,
  pero el stock cargado queda en **10** y **7** respectivamente, sin descuento.
  Si la cátedra lo pide, se ajusta el dataset en un change propio.
- **§(6) Lista cerrada de filas base**: el enunciado no fija el contenido del
  seed. Hasta la respuesta de la cátedra, el dataset de esta sección es el
  documentado y determinista; cualquier cambio se aplica como change propio.

### Verificación

Los casos verificables tras el seed están en
`test/ch08-seed-datos-iniciales.http`: `GET /health/ready`, `GET /libros/`
(5 libros; el libro 6 del ejemplo del enunciado se crea con `POST /libros/`),
`GET /clientes/2` (Tomás Ríos), `GET /ventas/1` (total `"77000.00"` con sus dos
renglones) y `POST /ventas/` del caso C-06 (201 con `id: 2`, precios copiados,
subtotales 50000.00/27000.00 y total `"77000.00"`).
