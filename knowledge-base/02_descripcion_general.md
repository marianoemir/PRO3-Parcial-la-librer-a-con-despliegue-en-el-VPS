# Descripción General

## Stack tecnológico
| Capa | Tecnología | Versión mínima |
|------|------------|----------------|
| Lenguaje | Python | 3.12 |
| Framework web | FastAPI (todos los handlers `async def`) | ≥ 0.111 |
| Modelos y contratos | SQLModel | ≥ 0.0.24 |
| ORM asíncrono, sesión, carga anticipada | SQLAlchemy 2.0 | 2.0 |
| Driver PostgreSQL asíncrono | asyncpg | ≥ 0.30 |
| Base de datos | PostgreSQL | 16 |
| Configuración | python-dotenv | 1.0 |
| Servidor ASGI | uvicorn (vía `fastapi[standard]`) | el que instala `fastapi[standard]` |
| Contenedores | Docker | ≥ 20.10 |

La dirección de la base se lee de la variable de entorno `DATABASE_URL`, definida en un archivo `.env` que no se versiona. El repositorio incluye `env.example` con la forma del valor y sin ningún secreto (con driver `postgresql+asyncpg`, host, usuario, contraseña y nombre de base provistos por la cátedra, más `SQL_ECHO=false` en el ejemplo).

## Arquitectura general
API monolítica en una sola imagen Docker. Organización por módulo funcional con estructura idéntica en cada módulo: `app/main.py` (aplicación, lifespan y registro de routers), `app/core/config.py` (lectura de `DATABASE_URL` desde el entorno), `app/core/database.py` (motor, fábrica de sesiones y dependencia `get_session`), y por módulo `app/modules/<módulo>/{models,schemas,service,router}.py`. La lógica vive en el `service` de cada módulo, que recibe la sesión como parámetro.

Módulos mínimos: `health`, `editoriales`, `generos`, `autores`, `libros`, `clientes`, `ventas`. `LibroAutor` vive en `libros`, `PerfilCliente` en `clientes`, `RenglonVenta` en `ventas`.

El motor asíncrono y la fábrica de sesiones se crean en el lifespan, se guardan en `app.state` y el motor se cierra al apagar. La sesión llega a cada handler con `Depends(get_session)`, una por petición, creada con `expire_on_commit=False`. Al arrancar, el lifespan crea las tablas que falten con `SQLModel.metadata.create_all`, con todos los modelos ya importados. Si la base no responde, el arranque falla y el contenedor termina con error.

## Integraciones externas
| Servicio | Propósito | Tipo |
|----------|-----------|------|
| PostgreSQL 16 (provista por el servidor/VPS) | Persistencia relacional; la base no forma parte del paquete Docker | Conexión ASGI async vía asyncpg |
| Docker Engine en la máquina del grupo y en el VPS | Construir la imagen y correr el contenedor con `docker run` | CLI |

Sin repositorios, Unit of Work, colas, Docker Compose ni migraciones.

## API REST (resumen de endpoints)
- Salud: `GET /health/live` (no toca la base), `GET /health/ready` (`SELECT 1`).
- Referencia con CRUD: `/editoriales/`, `/generos/`, `/autores/`, `/libros/`, `/clientes/` (POST/GET/PATCH según corresponda; ver `06_funcionalidades.md`).
- Relaciones: `GET /editoriales/{id}/libros`, `GET /generos/{id}/libros`, `GET /autores/{id}/libros` (con rol y orden), `POST /clientes/{id}/perfil`, `GET /clientes/{id}/ventas`.
- Ventas: `POST /ventas/` (con renglones anidados), `GET /ventas/`, `GET /ventas/{id}`; sin PATCH de ventas (RN-08).

Ver el detalle completo de métodos, rutas, cuerpos, respuestas y códigos en `06_funcionalidades.md` (tabla de endpoints de referencia) y `07_flujos_principales.md`.
