# Design: ch-10-despliegue-vps-inicial

## Context

CH-01 define lifespan/health y obliga `DATABASE_URL` sin valor por defecto; CH-03 empaqueta la imagen `python:3.12-alpine` con `uvicorn --host 0.0.0.0 --port 8000`, usuario no root, `HEALTHCHECK` a `http://127.0.0.1:8000/health/ready` con `wget`, y `.dockerignore` sin secretos (spec `openspec/specs/docker-imagen/spec.md`). CH-10 lleva esa imagen al VPS **sin seed** para detectar temprano problemas de red y configuración (`red Docker de la base`, `--env-file`, `DATABASE_URL`, reinicio, puerto). Restricciones duras: sin Docker Compose, sin secretos en repo/imagen/artefactos, sin cambios de app, y la base de datos vive fuera del contenedor (PostgreSQL provisto por el servidor/cátedra, KB 02/KB 12).

## Goals / Non-Goals

**Goals:**

- Desplegar la imagen `libreria` en el VPS con `docker run` y dejar el contenedor `healthy` (D-02).
- Verificar usuario de proceso no root en el contenedor desplegado (D-06).
- Verificar que sin `DATABASE_URL` el contenedor no queda sirviendo (D-05), según contrato de CH-01/CH-03.
- Verificar que el contenedor vuelve a `healthy` tras `docker rm -f libreria` seguido del mismo `docker run` de despliegue.
- Resolver en diseño el contrato de ejecución: `--network <RED_DOCKER>`, `DATABASE_URL` con host `<HOST_BASE>` (nunca `localhost`), `--restart unless-stopped`, puerto publicado y procedimiento de actualización, sin `--add-host` ni `host.docker.internal` como camino principal.
- Separar tareas **ejecutadas manualmente por Mariano en el VPS** de tareas **preparadas por el agente en el repo**; ninguna task escribe ni solicita contraseñas, IPs o credenciales reales (solo nombres de variables y `env.example`).

**Non-Goals:**

- No cargar seed ni validar D-03/D-04 con datos (CH-11, depende de CH-08).
- No generar evidencia final ni carpeta `evidencia/` de entrega (CH-12).
- No escribir `DEPLOY.md` completo (CH-11 lo documenta mientras se despliega con datos); CH-10 solo deja definido el procedimiento y los datos que deberán registrarse luego sin exponer secretos.
- No modificar `app/`, endpoints, modelos, `Dockerfile` ni dependencias.
- No usar Docker Compose ni migraciones.

## Decisions

### 1) Ejecución con `docker run` + `--env-file` (sin Compose)
- **Decisión:** el build es siempre en el VPS (`git pull` + `docker build -t libreria .`); D-02 exige `docker build` y `docker run` en el servidor. El despliegue inicial se realiza con `docker run -d --name libreria --network <RED_DOCKER> -p <PUERTO_PUBLICO>:8000 --restart unless-stopped --env-file <ARCHIVO_ENV_SERVIDOR> libreria` (la red une el contenedor con la base EasyPanel; `--add-host=host.docker.internal:host-gateway` queda como alternativa solo para una base instalada en el host).
- **Justificación:** DD-03, KB 12 §Cómo se corre y §Despliegue en el VPS, consigna/KB: sin Docker Compose; `--env-file` entrega configuración desde archivo del servidor fuera del repo e imagen; D-02 exige build y run en el servidor.
- **Alternativa rechazada:** Compose, variables inline con secretos en historial de shell, `DATABASE_URL` en `Dockerfile`/repo, o llevar la imagen construida fuera del VPS.

### 2) Base en contenedor de EasyPanel unida por red Docker (nunca `localhost`)
- **Decisión:** la base corre como contenedor de EasyPanel (Postgres), no en el host. El despliegue une el contenedor `libreria` a la red de Docker de la base con `--network <RED_DOCKER>` (red overlay attachable; valor real en el VPS: `easypanel-grupo10`) y `DATABASE_URL` usa como host el nombre del servicio de la base `<HOST_BASE>` (valor real verificado: `grupo10_db`) con driver `postgresql+asyncpg` (ej. forma `postgresql+asyncpg://<usuario>:<contraseña>@<HOST_BASE>:5432/<base>`). `--add-host=host.docker.internal:host-gateway` queda como alternativa solo para una base instalada en el host, y no se publica el puerto 5432 de la base. El escenario borde sigue siendo `localhost` en `DATABASE_URL` (falla, `localhost` es el propio contenedor) y su corrección es `<HOST_BASE>` + `--network <RED_DOCKER>`. En todo el change, el `docker run` de la app incluye `--network <RED_DOCKER>`. Los valores reales no se escriben en el repo, solo placeholders.
- **Justificación:** dentro del contenedor `localhost` es el propio contenedor; la conexión por nombre de servicio en la red compartida alcanza el contenedor Postgres de EasyPanel sin exponer su puerto. `--add-host=host.docker.internal:host-gateway` solo aplica si la base corre instalada en el host Linux.
- **Alternativa rechazada:** `localhost`/`127.0.0.1` en `DATABASE_URL` (inaccesible desde el contenedor), publicar el puerto 5432 de la base, o usar valores reales de red/host/credenciales en el repo.

### 3) Ubicación y contenido del archivo de variables (sin secretos en repo)
- **Decisión:** `<ARCHIVO_ENV_SERVIDOR>` vive en el servidor, fuera del repositorio y fuera de la imagen. Contiene al menos `DATABASE_URL` y `SQL_ECHO` (según `env.example`). El agente no crea ni lee ese archivo con valores reales; solo referencia nombres de variables y la forma documentada en `env.example` (sin valores reales, **SU-03** y requisito **"Credenciales"** de la consigna). Ninguna tarea pide IP, usuario, contraseña ni URL real.
- **Justificación:** KB 12, SU-03, regla dura de secretos. `env.example` ya existe como plantilla sin secretos.

### 4) Puerto publicado y escucha interna
- **Decisión:** la app escucha en `0.0.0.0:8000` dentro del contenedor (contrato CH-01/CH-03). Se publica como `-p <PUERTO_PUBLICO>:8000`, donde `<PUERTO_PUBLICO>` es el puerto asignado por la cátedra/infraestructura del VPS (no se inventa ni hardcodea un valor real en repo).
- **Justificación:** KB 12 §Cómo se corre; con `127.0.0.1` interno el puerto publicado no respondería.

### 5) Reinicio y recuperación operativa
- **Decisión:** se usa `--restart unless-stopped` para que el contenedor se levante tras reinicios del servidor/base no lista (KB 12). La recuperación manual verificada en este change es: `docker rm -f libreria` y re-ejecución del mismo `docker run` de despliegue; el contenedor debe volver a `healthy` (con base alcanzable y configuración correcta).
- **Justificación:** KB 12 §Cómo se corre y §Casos D (D-02/D-04 patrón de re-run); este change valida la recuperación inicial sin depender de datos/seed.
- **Actualización del despliegue:** obtener cambios del código en el servidor (`git pull`), ejecutar `docker build -t libreria .` en el VPS, luego `docker rm -f libreria` y repetir el `docker run` con el mismo contrato (`--network <RED_DOCKER>`, `-p <PUERTO_PUBLICO>:8000`, `--restart unless-stopped`, `--env-file <ARCHIVO_ENV_SERVIDOR>`; `--add-host=host.docker.internal:host-gateway` solo como alternativa para base instalada en el host). No se pierden datos por eliminar el contenedor porque la base vive fuera del contenedor; la persistencia con datos se comprueba en CH-11 con seed.

### 6) Comportamiento de salud y D-05 (pendiente de cátedra)
- **Decisión:** se siguen los contratos implementados en CH-01/CH-03: `GET /health/live` no toca base; `GET /health/ready` ejecuta `SELECT 1`; el `HEALTHCHECK` de la imagen consulta `/health/ready` en `127.0.0.1`. La propuesta documentada en CH-01 (no regla) es responder 503 con cuerpo propio si `SELECT 1` falla; sin embargo `knowledge-base/10_preguntas_abiertas.md` §(2) permanece **pendiente** y define la interpretación final del `HEALTHCHECK` y D-05. En CH-10 se verifica observacionalmente con salida real: sin `DATABASE_URL` el contenedor no queda sirviendo (`Exited`/no `running`/no `healthy`), y con configuración/base válida queda `healthy`.
- **Justificación:** KB 10 §(2), design CH-01/CH-03, KB 12 §Casos D. No se inventa regla cerrada.

### 7) Separación de responsabilidades (VPS vs repo)
- **Decisión:** tareas de **VPS (Mariano, manual)**: preparar `<ARCHIVO_ENV_SERVIDOR>` con valores reales provistos por cátedra, ejecutar build/run/rm, inspecciones y curls desde dentro/fuera según acceso. Tareas de **agente (repo)**: preparar/verificar artefactos y documentación del change sin secretos, confirmar que `env.example` documenta los nombres requeridos (`DATABASE_URL`, `SQL_ECHO`) y que el procedimiento no expone valores reales. Si se detectara falta de una variable nombrada en `env.example`, la corrección tocaría repo y queda fuera salvo instrucción explícita; en este change se registra como hallazgo, no se modifica app/código base.
- **Justificación:** requerimiento explícito del usuario y SU-03.

## UI Mockups

Decision: no (no UI)

## Risks / Trade-offs

- [Red base EasyPanel] No unir el contenedor a `<RED_DOCKER>` o usar `localhost` en `DATABASE_URL` → el contenedor no alcanza la base / no queda `healthy`. Mitigación: comando explícito (`--network <RED_DOCKER>`, host `<HOST_BASE>`) y escenario de borde verificable (corrección `localhost` → `<HOST_BASE>` + `--network <RED_DOCKER>`).
- [Red overlay attachable y recreación en EasyPanel] La red overlay attachable fue verificada; si el servicio de base se recrea en EasyPanel, el nombre del servicio `<HOST_BASE>` o la red `<RED_DOCKER>` pueden cambiar y romper la conexión. Mitigación: verificar nombres/red antes de desplegar y registrar como pendiente si cambian (riesgo, no regla).
- [Versión de Postgres] La base es Postgres 18 y la consigna indica 16; se debe confirmar compatibilidad con el arranque del D-02 (riesgo, no regla).
- [Puerto publicado y firewall] `<PUERTO_PUBLICO>` lo define el grupo/cátedra y el puerto publicado puede estar bloqueado por el firewall del VPS; verificar acceso desde afuera (riesgo, no regla).
- [Acceso/Credenciales] El agente no puede ejecutar en el VPS ni conocer `<PUERTO_PUBLICO>`, `<RED_DOCKER>`, `<HOST_BASE>`, `<ARCHIVO_ENV_SERVIDOR>` real ni `DATABASE_URL` real → tareas VPS quedan manuales con placeholders, evidencia real debe ser provista por Mariano.
- [Q2 pendiente] El código exacto de `/health/ready` ante fallo de base no está cerrado por cátedra → D-05/`HEALTHCHECK` se interpretan por comportamiento observado (no queda sirviendo/no healthy) y se cita KB 10 §(2).

## Migration Plan

No aplica (no hay migración de datos/esquema en este change; `create_all` es responsabilidad de CH-01 y no se modifica). Despliegue inicial: `git pull` y `docker build -t libreria .` en el VPS → preparar `<ARCHIVO_ENV_SERVIDOR>` en VPS → `docker rm -f libreria` (si existe) → `docker run ... --network <RED_DOCKER> ...` → verificar `healthy`/endpoints. Rollback operativo: `docker rm -f libreria` y, si es necesario, volver a una imagen/tag anterior disponible en el VPS repitiendo el mismo `docker run` con el archivo de variables del servidor (sin exponer su contenido). Actualización: `git pull` + rebuild en VPS + `docker rm -f` + `docker run` con el mismo contrato.

## Open Questions

- **`knowledge-base/10_preguntas_abiertas.md` §(2) (Media, PENDIENTE):** ¿qué devuelve `GET /health/ready` y con qué código si la base no responde? Impacta la interpretación final del `HEALTHCHECK` y el caso D-05; se sigue la respuesta de CH-01/CH-03 y lo que responda la cátedra. No se resuelve en este change.
- **`<RED_DOCKER>` y `<HOST_BASE>` reales:** la red overlay attachable fue verificada (valores reales en el VPS: `easypanel-grupo10` / `grupo10_db`, no se escriben en el repo); si el servicio de base se recrea en EasyPanel, el nombre del servicio o la red pueden cambiar (pendiente operativo, no regla).
- **Compatibilidad Postgres 18 vs 16:** la base es Postgres 18 y la consigna indica 16; confirmar con el arranque del D-02 (pendiente, no regla).
- **`<PUERTO_PUBLICO>` y firewall:** `<PUERTO_PUBLICO>` lo define el grupo/cátedra y el puerto publicado puede estar bloqueado por el firewall del VPS; verificar acceso desde afuera (pendiente, no regla).
- **Base instalada en el host (alternativa):** si la cátedra provee una base instalada en el host, se usaría `host.docker.internal` + `--add-host=host.docker.internal:host-gateway` en lugar de `<HOST_BASE>` + `--network <RED_DOCKER>`; el valor/escenario concreto no se registra en repo.
