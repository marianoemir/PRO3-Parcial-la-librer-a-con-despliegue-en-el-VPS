# Actores y Roles

## Actores del sistema
| Actor | Descripción | Cómo interactúa |
|-------|-------------|-----------------|
| Personal de la librería (operador) | Usuario único que opera la API para catálogo y ventas | Llama los endpoints REST (alta de libros, ventas, listados); no hay identidad ni sesión |
| Cliente final de la librería | Persona que compra libros y puede cargar un perfil | No consume la API directamente; sus datos se registran vía `clientes` |
| Correctores de la cátedra | Verifican el proyecto y el despliegue en línea | Acceden a la URL pública del VPS y leen `evidencia/` y `DEPLOY.md` |

No se evalúan autenticación ni autorización (capítulo 5): la API no tiene usuarios del sistema ni roles de acceso.

## RBAC — Matriz de permisos
No aplica RBAC. Todo endpoint es accesible sin autenticación; cualquier llamador con acceso a la URL pública puede invocar POST/GET/PATCH definidos en el enunciado. Los únicos "roles" del dominio son los de la relación Libro–Autor (autor, coautor, traductor, ilustrador), que son datos de la autoría, no permisos de acceso.

| Rol (acceso) | Recurso | Permisos |
|--------------|---------|----------|
| Sin autenticación (único nivel) | Todos los definidos (`/health/`, `/editoriales/`, `/generos/`, `/autores/`, `/libros/`, `/clientes/`, `/ventas/`) | Los declarados por endpoint: POST (201/409/422), GET (200/404/422), PATCH (200/404/409/422) según la tabla de referencias |
| — | Ventas PATCH | No existe (RN-08) |
| — | DELETE / bajas | No existe — no crear endpoints de baja (ver 10_preguntas_abiertas.md) |

## Rutas públicas
Todas las rutas del sistema son públicas (sin autenticación):
- `GET /health/live`, `GET /health/ready`
- `POST/GET/PATCH /editoriales/`, `GET /editoriales/{id}/libros`
- `POST/GET /generos/`, `GET /generos/{id}/libros`
- `POST/GET/PATCH /autores/`, `GET /autores/{id}/libros`
- `POST/GET/PATCH /libros/`, `GET /libros/{id}`
- `POST/GET/PATCH /clientes/`, `GET /clientes/{id}`, `POST /clientes/{id}/perfil`, `GET /clientes/{id}/ventas`
- `POST/GET /ventas/`, `GET /ventas/{id}`

La URL pública del despliegue se declara en `DEPLOY.md` y debe permanecer en línea hasta que se publiquen las notas.
