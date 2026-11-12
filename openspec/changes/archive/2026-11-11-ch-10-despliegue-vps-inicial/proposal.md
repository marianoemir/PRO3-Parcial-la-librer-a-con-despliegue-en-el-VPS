# Proposal: ch-10-despliegue-vps-inicial

## Why

CH-02 (modelos/esquema) y CH-03 (imagen Docker) ya están archivados y en `main`, pero la aplicación aún no fue llevada a producción en el VPS. CH-10 realiza el **despliegue inicial sin seed** para validar temprano la infraestructura real: build y ejecución limpia en el VPS con `docker run` + `--env-file` + `--network <RED_DOCKER>`, publicación de puerto, reinicio automático, usuario no root, comportamiento sin `DATABASE_URL` (D-05), conexión a la base en contenedor de EasyPanel por nombre de servicio `<HOST_BASE>` (nunca `localhost`) y recuperación del contenedor a estado `healthy` tras `docker rm -f` + nuevo `docker run`. Esto detecta problemas de red/configuración antes de cargar datos (CH-11).

## What Changes

- Define y documenta el procedimiento de **despliegue inicial en el VPS** (ejecutado manualmente por Mariano) usando la imagen `libreria` construida siempre en el VPS (`git pull` + `docker build -t libreria .`), sin Docker Compose.
- Establece el contrato operativo del `docker run` inicial: `-d --name libreria --network <RED_DOCKER> -p <PUERTO_PUBLICO>:8000 --restart unless-stopped --env-file <ARCHIVO_ENV_SERVIDOR>`; `--add-host=host.docker.internal:host-gateway` queda como alternativa solo para una base instalada en el host.
- Exige que el archivo de variables viva **en el servidor, fuera del repo y de la imagen**, y que `DATABASE_URL` use driver `postgresql+asyncpg` con host `<HOST_BASE>` (nombre del servicio de la base en contenedor EasyPanel, nunca `localhost`) en la red `<RED_DOCKER>`, sin publicar el puerto 5432 de la base.
- Define cómo se **actualiza** el despliegue inicial: `git pull`, reconstruir imagen en el VPS, eliminar contenedor y volver a correrlo con el mismo contrato (los datos no aplican en este change porque no hay seed; la persistencia con datos se valida en CH-11).
- Separa explícitamente tareas **preparadas por el agente en el repo** (documentación/verificación de forma, sin secretos) de tareas **ejecutadas manualmente por Mariano en el VPS** con salida real de herramientas.
- No crea ni ejecuta seed (eso es CH-11/CH-08), no produce la evidencia final de entrega (CH-12) y no modifica código de aplicación.

## Capabilities

### New Capabilities

- `despliegue-vps-inicial`: despliegue inicial en el VPS sin datos semilla, con contenedor publicado, reinicio automático, configuración por `--env-file`, conexión a base fuera del contenedor mediante host correcto y verificación de salud/errores esperados.

### Modified Capabilities

Ninguna. No cambia requisitos de `foundation`, `core-models` ni `docker-imagen`; consume sus contratos (imagen, healthchecks, arranque y comportamiento sin `DATABASE_URL`).

## Impact

- **Código/archivos afectados**: únicamente artefactos OpenSpec de este change (`openspec/changes/ch-10-despliegue-vps-inicial/`). No se modifica `app/`, `Dockerfile`, `.dockerignore`, `requirements.txt`, `AGENTS.md`, `CLAUDE.md`, `CHANGES.md` ni otros changes.
- **Casos cubiertos**: D-02 (build + run limpio, contenedor `healthy`), D-05 (sin `DATABASE_URL` el contenedor no queda sirviendo), D-06 (`docker exec libreria id` no es root), y el contenedor vuelve a `healthy` tras `docker rm -f` + `docker run`. Cubre también la restricción operativa D-02/D-05 de KB 12 (base en contenedor EasyPanel alcanzada por `--network <RED_DOCKER>` y host `<HOST_BASE>`, nunca `localhost`).
- **Reglas/códigos que la gobiernan**: DD-03, DD-06, SU-03 y requisito **"Credenciales"** de la consigna para secretos (`knowledge-base/09_decisiones_y_supuestos.md`); `/health/ready` según `knowledge-base/07_flujos_principales.md` (Flujo 6) y contrato de **CH-01/CH-03**; KB 12 §§ Cómo se corre, La base no está en localhost, El HEALTHCHECK y localhost, Despliegue en el VPS y DEPLOY.md, Casos D; KB 02 §Integraciones externas. **Pendiente citado (no resuelto):** `knowledge-base/10_preguntas_abiertas.md` §(2) — qué devuelve `GET /health/ready` y con qué código si la base no responde; condiciona la lectura final del `HEALTHCHECK`/D-05 y se sigue lo definido por CH-01/CH-03 y lo que responda la cátedra.
- **Fuera de alcance**: carga de datos iniciales/seed y casos D-03/D-04 con datos (CH-11), aviso D-07, evidencia C-07/D-x final y `evidencia/` (CH-12), redacción del `DEPLOY.md` completo (CH-11 lo escribe mientras se despliega con datos), cambios de endpoints o lógica de aplicación, Docker Compose, migraciones, y resolución de dudas abiertas del enunciado.
- **Riesgos / dependencias**: depende de CH-02 y CH-03 (ya archivados). Requiere acceso al VPS, archivo de variables real en el servidor y datos de conexión provistos por la cátedra (no disponibles en repo). Omitir `--network <RED_DOCKER>` o usar `localhost` en `DATABASE_URL` produce fallo de conexión desde el contenedor; si el servicio de base se recrea en EasyPanel, `<RED_DOCKER>`/`<HOST_BASE>` pueden cambiar. La base es Postgres 18 (consigna indica 16) y el puerto publicado puede estar bloqueado por firewall (riesgos/pendientes operativos, no reglas).
