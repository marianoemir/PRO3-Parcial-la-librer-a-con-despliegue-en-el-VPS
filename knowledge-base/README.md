# Parcial Programación III — La Librería con Despliegue en el VPS · Base de Conocimiento

Base de conocimiento generada por ingest desde `docs/Parcial_Cap1a4_Consigna.pdf` (fuente de verdad, 16 páginas). Los nombres de tablas y columnas del modelo de dominio son obligatorios: se pueden agregar, no quitar ni renombrar.

Grupo:
- Mariano Chirino
- Andrés Fabre
- Facundo Quiroga

## Índice de Archivos
| Archivo | Contenido |
|---------|-----------|
| [01_vision_y_objetivos.md](01_vision_y_objetivos.md) | Propósito, objetivos por actor, alcance y fuera de alcance, métricas de éxito |
| [02_descripcion_general.md](02_descripcion_general.md) | Stack imponeado (Python 3.12, FastAPI ≥ 0.111, SQLModel ≥ 0.0.24, PostgreSQL 16, Docker), arquitectura y módulos |
| [03_actores_y_roles.md](03_actores_y_roles.md) | Actores, ausencia de RBAC (sin autenticación) y lista de rutas públicas |
| [04_modelo_de_datos.md](04_modelo_de_datos.md) | Tablas y columnas obligatorias, relaciones (agregación, muchos a muchos con datos, uno a uno, composición), seed |
| [05_reglas_de_negocio.md](05_reglas_de_negocio.md) | Reglas RN-01 a RN-12 del enunciado más reglas transversales (códigos HTTP, escritura delegada, asincronía, carga anticipada) |
| [06_funcionalidades.md](06_funcionalidades.md) | Épicas US-001 a US-006 con criterios de aceptación y tabla de endpoints de referencia |
| [07_flujos_principales.md](07_flujos_principales.md) | Arranque, alta de libro, alta de venta, lecturas sin N+1, perfil de cliente, contenedor y despliegue |
| [08_arquitectura_propuesta.md](08_arquitectura_propuesta.md) | Patrones, estructura obligatoria `app/main.py` + `app/core/` + `app/modules/*`, seguridad y variables de entorno |
| [09_decisiones_y_supuestos.md](09_decisiones_y_supuestos.md) | Decisiones DD-01 a DD-06 (entidad intermedia, ventas inmutables, un contenedor, garantías delegadas, precios del servidor, roadmap Docker/VPS) y supuestos |
| [10_preguntas_abiertas.md](10_preguntas_abiertas.md) | Las 6 dudas abiertas del enunciado (no son reglas), la inconsistencia de los CHECK y el marcador `[DISCOVERY] scale` |
| [12_despliegue_docker_y_vps.md](12_despliegue_docker_y_vps.md) | Extra: Dockerfile python:3.12-alpine, `docker run` + `--env-file`, `host.docker.internal`, HEALTHCHECK con `127.0.0.1`, DEPLOY.md, casos D y formato de entrega |

## Quick Start para Desarrolladores
1. Entender el dominio → [01](01_vision_y_objetivos.md), [03](03_actores_y_roles.md)
2. Entender los datos → [04](04_modelo_de_datos.md)
3. Entender las reglas → [05](05_reglas_de_negocio.md)
4. Entender la arquitectura → [02](02_descripcion_general.md), [08](08_arquitectura_propuesta.md)
5. Implementar → [07](07_flujos_principales.md), [06](06_funcionalidades.md)
6. Antes de codificar → [10](10_preguntas_abiertas.md)

## Resumen Ejecutivo
La librería expone una API asincrónica FastAPI + SQLModel + PostgreSQL 16 con siete módulos, DTO separados de los modelos, garantías delegadas a la base con traducción a 409 propios, lecturas precargadas sin N+1, y ventas inmutables con precios y total calculados por el servidor. El proyecto se empaqueta en una imagen `python:3.12-alpine` sin secretos y se despliega en el VPS con un único `docker run` + `--env-file`, quedando en línea hasta que se publiquen las notas.
