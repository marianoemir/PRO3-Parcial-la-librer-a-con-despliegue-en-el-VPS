# Arquitectura Propuesta

## Patrones aplicados
| Patrón | Dónde se usa | Por qué |
|--------|--------------|---------|
| Organización por módulo funcional | `app/modules/<módulo>/{models,schemas,service,router}.py` | Misma estructura en todos los módulos; cada módulo modela su dominio (LibroAutor en `libros`, PerfilCliente en `clientes`, RenglonVenta en `ventas`) |
| Separación modelo de tabla / DTO | `models.py` (tabla, restricciones, relaciones) vs `schemas.py` (`Create`/`Update` entrada, `Read` salida) | Contratos independientes de la persistencia; los DTO de alta no llevan `id` |
| Lógica en el service | `service.py` recibe la sesión como parámetro | La lógica vive en el service (no en el router); traduce `IntegrityError` a mensajes propios |
| Router delgado | `router.py` recibe, delega y declara la respuesta HTTP | Códigos 201/404/409/422 según la tabla de endpoints |
| Carga anticipada obligatoria | `service.py` con `joinedload` (a uno) / `selectinload` (colecciones) | Ninguna lectura depende de la carga perezosa; evita N+1 (caso C-07) |
| Delegación de garantías a la base | UNIQUE, FK y CHECK ejecutados por PostgreSQL | El service escribe y traduce; sin consultas previas de existencia (RT-02) |
| Ciclo de vida con lifespan | `app/main.py` + `app.state` + `Depends(get_session)` con `expire_on_commit=False` | Recursos creados al arrancar y compartidos por petición; motor cerrado al apagar |
| Tarea en segundo plano | `BackgroundTasks` + `await asyncio.sleep(0.5)` al registrar una venta | Aviso del comprobante sin bloquear la respuesta |

## Estructura de directorios
```
app/
├── main.py                     # Aplicación, lifespan, registro de routers
├── core/
│   ├── config.py               # Lectura de DATABASE_URL desde el entorno
│   └── database.py             # Motor, fábrica de sesiones, get_session
└── modules/
    ├── health/
    ├── editoriales/
    ├── generos/
    ├── autores/
    ├── libros/                 # incluye LibroAutor
    ├── clientes/               # incluye PerfilCliente
    └── ventas/                 # incluye RenglonVenta
        └── {models,schemas,service,router}.py
test/                           # archivos .http con los casos de prueba
Dockerfile, .dockerignore
DEPLOY.md, README.md, env.example, requirements.txt
evidencia/                      # caso C-07 y casos D
```

## Seguridad
- Autenticación: ninguna (fuera de alcance, capítulo 5).
- Autorización: ninguna; todas las rutas son públicas.
- Validación de input: DTO de entrada separados de los modelos; PATCH con `exclude_unset`; paginación con restricciones en `Query` (422); SQL siempre con parámetros ligados (nunca concatenación con datos del usuario).
- Secrets management: `.env` no versionado (ni en repo, ni en imagen, ni en zip); `env.example` con la forma de `DATABASE_URL` y sin valores reales; `DATABASE_URL` entregada al contenedor vía `--env-file`. La app no corre como root en el contenedor. Ningún error devuelve texto interno de la base (RN-12).

## Variables de entorno
| Variable | Descripción | Ejemplo | Sensible |
|----------|-------------|---------|----------|
| `DATABASE_URL` | Dirección de la base PostgreSQL con driver `postgresql+asyncpg` | `postgresql+asyncpg://usuario:contraseña@host:5432/base` | Sí (no versionar; en VPS dentro del archivo de variables, fuera del repo y de la imagen) |
| `SQL_ECHO` | Diagnóstico de consultas en consola (`echo=True` configurable); en despliegue en `false` | `false` | No |

Detalle completo del empaquetado y despliegue (capas, HEALTHCHECK, `host.docker.internal`, DEPLOY.md): `12_despliegue_docker_y_vps.md`.
