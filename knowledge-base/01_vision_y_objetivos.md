# Visión y Objetivos

## Propósito del sistema
API asincrónica para una librería de barrio que gestione su catálogo (libros, editoriales, géneros, autores) y registre sus ventas con renglones, empaquetada en imagen Docker y desplegada en un VPS con PostgreSQL.

El parcial integra los capítulos 1 a 4 de Programación III (FastAPI, contratos y CRUD, ejecución asincrónica sin bloqueos, persistencia relacional con SQLModel y PostgreSQL con relaciones) y le suma el despliegue en contenedor. El grupo puede partir de su TP entregado.

## Objetivos por actor
| Actor | Objetivo principal | Objetivos secundarios |
|-------|--------------------|------------------------|
| Dueño de la librería / personal de ventas | Registrar ventas con renglones y precios copiados del libro (RN-06) | Mantener el catálogo por editorial, género y autor; verificar el total calculado por el servidor (RN-07) |
| Encargado de catálogo | Cargar libros con ISBN único, precio > 0 y stock ≥ 0 (RN-03) | Gestionar editoriales, géneros y autores; modelar autorías con rol y orden (muchos a muchos con datos) |
| Cliente de la librería | Haber sus datos registrados con email único (RN-02) | Cargar como máximo un perfil con teléfono y dirección (RN-09) |
| Correctores de la cátedra | Verificar el proyecto en línea hasta que se publiquen las notas | Revisar evidencia (caso C-07 y casos D), DEPLOY.md y el .zip de entrega |

## Alcance v1.0 (primer entregable: todo el enunciado)
- API FastAPI asincrónica con parámetros tipados, dependencias con `Depends()` y recursos creados en el ciclo de vida (lifespan, `app.state`).
- Separación modelos de tabla / DTO de entrada (`Create`/`Update`) y salida (`Read`); códigos HTTP correctos (201/200/404/409/422).
- Modelo relacional con agregación, agregación opcional, muchos a muchos con datos, uno a uno, asociación y composición, con navegación bilateral y carga anticipada (`joinedload`/`selectinload`), nunca perezosa.
- Delegación a la base de unicidad, claves foráneas y CHECK; dinero con `Decimal`; paginación `limit` 1–100 (defecto 20) y `offset` ≥ 0; filtro de libros por título case-insensitive con parámetros ligados.
- Empaquetado Docker (`python:3.12-alpine`, usuario sin privilegios, `HEALTHCHECK`, sin secretos) y despliegue en VPS con `docker run` + `--env-file`, sin Docker Compose.
- `test/*.http` con los casos C-01 a C-08, `evidencia/` con C-07 y casos D, DEPLOY.md y README.md de levantada.

## Fuera de alcance
- Autenticación y autorización (capítulo 5).
- Repositorios y Unit of Work (capítulo 6).
- Colas de tareas con Redis (capítulos 7 y 8); el aviso del comprobante se simula con `BackgroundTasks`.
- Docker Compose: despliegue de una sola imagen; la base la provee el servidor.
- Migraciones: el esquema se crea con `create_all` en el lifespan.
- Endpoints DELETE / bajas (no existe en el enunciado — ver 10_preguntas_abiertas.md).

## Métricas de éxito
- Los 8 criterios de evaluación suman 100 % (proyecto y ciclo de vida 8 %, modelos y relaciones 22 %, contratos y CRUD 12 %, altas con relaciones 17 %, lecturas sin N+1 8 %, asincronía 8 %, contenedor 15 %, despliegue VPS 10 %).
- Casos C-01 a C-08 y D-01 a D-07 verificables con salidas guardadas en `evidencia/`.
- Imagen base por debajo de 100 MB según `docker images`, contenedor `healthy`, datos sobreviven a `docker rm -f` y recreación.
