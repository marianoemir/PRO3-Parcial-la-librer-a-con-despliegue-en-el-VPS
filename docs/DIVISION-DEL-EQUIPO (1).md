# División del equipo — Parcial Librería con despliegue en el VPS (SDD con Active Stack)

**Equipo**: Mariano · Facundo · Andrés
**Estado al**: 08/11/2026 · fundación completa; **`CH-01`, `CH-02` y `CH-05` terminados, archivados y mergeados en `main`**; **`CH-03` terminado y archivado en su rama `feat/ch-03-docker-imagen` (PR pendiente, todavía no mergeado en `main`)**; sigue `CH-10` (Mariano); el resto está pendiente.
**Fecha y hora de entrega**: la publica la cátedra en el campus (a confirmar).
**Fuente de verdad**: `docs/Parcial_Cap1a4_Consigna.pdf`. Roadmap y detalle de cada change: `CHANGES.md`. Reglas del agente: `AGENTS.md` / `CLAUDE.md`. Contexto completo para pegar en una IA: `CONTEXTO-TRASPASO.md`.

> **Reparto acordado**: Mariano lleva lo más pesado (el camino crítico del código) y todo lo de Docker y el VPS. Facundo y Andrés se reparten los CRUD de referencia, clientes, el seed y los casos `.http`. Los roles A/B/C de `CHANGES.md` y `AGENTS.md` son **roles de trabajo**, no personas: Mariano cumple los roles A y C, y el rol B se divide entre Facundo y Andrés.

| Persona | Roles de `CHANGES.md` | Changes | Hechos |
|---|---|---|---|
| **Mariano** | A (Backend Core) + C (Infra/DevOps) | `CH-01`, `CH-02`, `CH-03`, `CH-05`, `CH-07`, `CH-10`, `CH-11`, `CH-12` | `CH-01`, `CH-02`, `CH-05`, `CH-03` (PR pendiente) |
| **Facundo** | B (Backend Aux) | `CH-04`, `CH-08` | — |
| **Andrés** | B (Backend Aux) | `CH-06`, `CH-09` | — |

---

## 0. Dónde estamos y qué hace cada uno ahora

**Ya está hecho**:

- La fundación (OpenSpec, knowledge base `01`–`10` y `12`, `CHANGES.md`, skills `fastapi` y `sqlmodel`, `AGENTS.md` y `CLAUDE.md`).
- `CH-01` `foundation-setup`: `app/main.py`, `core/config.py`, `core/database.py`, lifespan con `create_all`, módulo `health`, `requirements.txt`, `env.example`. Archivado y mergeado en `main`.
- `CH-02` `core-models`: los **9** modelos de tabla con restricciones nombradas, índices y relaciones bilaterales, más los stubs de `schemas.py`, `service.py` y `router.py` en los módulos nuevos. Archivado y mergeado en `main` (PR #3).
- `CH-05` `ch-05-libros-autorias`: módulo `libros` completo (`POST`, `GET` con `limit`, `offset` y `titulo`, `GET /{id}`, `PATCH`), sin N+1, con traducción de `IntegrityError` a 409 y spec `libros-autorias` en `openspec/specs/`. Archivado y mergeado en `main` (PR #5, merge commit `9bcd2d9`), sin revisión cruzada de Andrés.
- `CH-03` `ch-03-docker-imagen`: `Dockerfile` (`python:3.12-alpine`, usuario `appuser` uid 1000, `HEALTHCHECK` con `wget` a `http://127.0.0.1:8000/health/ready`, intervalo 10 s, timeout 3 s, start-period 10 s, 3 reintentos) y `.dockerignore` (6 líneas de la consigna). Archivado en `openspec/changes/archive/2026-11-08-ch-03-docker-imagen/`, spec en `openspec/specs/docker-imagen/`. Verificado en local (Docker Desktop): build 0, base `python:3.12-alpine` 74,8 MB, caché de `pip install`, `healthy`, `/health/ready` 200, sin `DATABASE_URL` sale `Exited (1)`, con `localhost` sale `Exited (3)`, con `Stop-Service postgresql-x64-17` real pasa a `unhealthy` y al volver Postgres recupera `healthy`, sin secretos en la imagen, `.dockerignore` efectivo. Evidencia local (no del VPS) en `evidencia/ch-03-local/ch03-evidencia.md`. **PR pendiente; la revisión de Andrés también.**

**Antes de arrancar tu change**: `git checkout main`, `git pull`, y comprobá que existen `openspec/specs/core-models/` y los `models.py` de los siete módulos (ya están en `main`: `CH-02` está mergeado, así que `CH-04` y `CH-06` están habilitados). No se hace `propose` hasta tener la dependencia archivada y mergeada.

**Una consulta a la cátedra sigue pendiente** (no bloquea `CH-04` ni `CH-06`, pero sí `CH-07`): ¿la venta descuenta stock del libro? Es la duda de prioridad alta de `knowledge-base/10_preguntas_abiertas.md` (§1). Que la mande una sola persona y registre la respuesta ahí. En el mismo mensaje conviene consultar: el código y cuerpo de `/health/ready` sin base (el equipo decidió 503 `{"estado":"no listo"}`), si el índice propio de `libro_autor.autor_id` alcanza y si `libro_id` necesita uno propio, y las demás dudas abiertas.

| Persona | Empieza ya con | Después | Qué lo frena |
|---|---|---|---|
| **Mariano** | `CH-10` despliegue-vps-inicial (`CH-03` ya terminado, falta el PR) | `CH-07`, y al final `CH-11` y `CH-12` | Nada ahora. `CH-07` espera a `CH-06` (Andrés). |
| **Facundo** | `CH-04` crud-editoriales-generos-autores (ya habilitado) y la revisión del PR de `CH-02` | `CH-08` (seed) cuando estén `CH-04` y `CH-07` | `CH-08` espera a `CH-07`. |
| **Andrés** | `CH-06` clientes-perfil (ya habilitado) y la revisión del PR de `CH-02` | `CH-09` (casos `.http`) cuando esté `CH-08` | `CH-09` espera a `CH-08`. |

**Orden de Mariano** (una sola persona con los changes restantes en serie; el orden importa):

1. ✅ `CH-01` → ✅ `CH-02`.
2. ✅ `CH-05` libros-autorias.
3. ✅ `CH-03` docker-imagen (archivado, PR pendiente) → `CH-10` despliegue-vps-inicial: **no lo dejes para el final**. El despliegue vale el 25 % de la nota (imagen 15 % + VPS 10 %) y tiene trampas (`localhost` vs `host.docker.internal`, `HEALTHCHECK`, `greenlet` en Alpine). Conviene que los problemas aparezcan con tiempo.
4. `CH-07` ventas-renglones (necesita `CH-05` y `CH-06`).
5. `CH-11` despliegue-vps-datos + `DEPLOY.md` (necesita `CH-08`) → `CH-12` evidencia-entrega (necesita `CH-09` y `CH-11`).

**Cómo se revisa**: ver la política de revisión en la sección 1.

---

## 1. De un vistazo

| # | Change | Dueño | Depende de | Lo revisa | Estimación* | Estado |
|---|---|---|---|---|---|---|
| CH-01 | `foundation-setup` | Mariano | — | Facundo | 5–6 h | ✅ archivado y mergeado (revisión cruzada pendiente) |
| CH-02 | `core-models` | Mariano | CH-01 | Facundo **y** Andrés | 6–8 h | ✅ archivado y mergeado (PR #3; revisión cruzada pendiente) |
| CH-03 | `docker-imagen` | Mariano | CH-01 | Andrés | 3–4 h | ✅ archivado en su rama (PR pendiente; revisión de Andrés pendiente) |
| CH-04 | `crud-editoriales-generos-autores` | Facundo | CH-02 | Mariano | 5–7 h | ⬜ habilitado |
| CH-05 | `ch-05-libros-autorias` | Mariano | CH-02 | Andrés | 6–8 h | ✅ archivado y mergeado (PR #5; revisión de Andrés pendiente) |
| CH-06 | `clientes-perfil` | Andrés | CH-02 | Facundo | 3–4 h | ⬜ habilitado |
| CH-07 | `ventas-renglones` | Mariano | CH-05, CH-06 | Facundo **y** Andrés | 6–8 h | ⬜ pendiente |
| CH-08 | `seed-datos-iniciales` | Facundo | CH-04, CH-07 | Mariano | 3–4 h | ⬜ pendiente |
| CH-09 | `casos-http-C` | Andrés | CH-08 | Facundo | 3–4 h | ⬜ pendiente |
| CH-10 | `despliegue-vps-inicial` | Mariano | CH-02, CH-03 | Andrés | 4–6 h | ⬜ pendiente |
| CH-11 | `despliegue-vps-datos` (+ `DEPLOY.md`) | Mariano | CH-10, CH-08 | Facundo | 4–5 h | ⬜ pendiente |
| CH-12 | `evidencia-entrega` | Mariano | CH-09, CH-11 | Facundo **y** Andrés | 3–4 h | ⬜ pendiente |

\* Estimación orientativa de esta propuesta, no de `CHANGES.md` (que solo dice 4–6 h por change). Ajustala según cómo vaya avanzando cada uno.

Carga total estimada: Mariano ≈ 37–47 h (restan ≈ 20–27 h) · Facundo ≈ 8–11 h · Andrés ≈ 6–8 h.

### Camino crítico y paralelismo

Camino crítico: `CH-01 → CH-02 → CH-05 → CH-07 → CH-08 → CH-11 → CH-12`.

Los puntos de sincronización (gates) son los de `CHANGES.md`, ordenados según el orden de Mariano:

| Gate | Se libera cuando… | Se puede avanzar en paralelo |
|---|---|---|
| 1 ✅ | `CH-01` ✓ | `CH-02` (Mariano) |
| 2 ✅ | `CH-02` ✓ | `CH-04` (Facundo), `CH-06` (Andrés) y `CH-05` (Mariano, ✅). Después de `CH-05`, Mariano sigue con `CH-03` y `CH-10`. |
| 3 | `CH-05` ✅ y `CH-06` ⬜ (falta Andrés) | `CH-07` (Mariano) cuando esté `CH-06`; mientras tanto, `CH-03` y `CH-10` |
| 4 | `CH-07` ✓ y `CH-04` ✓ | `CH-08` (Facundo) |
| 5 | `CH-08` ✓ | `CH-09` (Andrés) y `CH-11` (Mariano, si `CH-10` ✓) |
| 6 | `CH-09` ✓ y `CH-11` ✓ | `CH-12` (Mariano) |

> **Cuello de botella**: Mariano concentra el camino crítico del código y todo el despliegue, así que sus changes se hacen **en serie**. Facundo y Andrés van a tener tiempo libre en los gates 3 y 4; ese tiempo conviene usarlo en revisar los PRs de Mariano apenas se abren. Si Mariano se atrasa, `CH-07` puede pasar a Facundo o Andrés.

### Política de revisión

- Cada change lo revisa **otra persona**, nunca su dueño (columna "Lo revisa"). Los de `Governance: CRITICO` o que bloquean a otros (`CH-02`, `CH-07`) los revisan los dos restantes. Como casi todo lo de Docker y VPS es de Mariano, lo revisan Andrés o Facundo.
- Los PRs que **bloquean a otro** (`CH-01`, `CH-02`, `CH-05`, `CH-06`, `CH-07`, `CH-08`) se revisan apenas se abren. El resto se junta en **rondas** (dos PRs a la vez).
- La revisión usa el checklist de la guía: dependencias archivadas, cada regla citada existe en la KB, lo ambiguo quedó como pregunta abierta, al menos tres escenarios por spec y evidencia real (salida de la herramienta, no la explicación del agente).
- **`CH-03`**: al abrir el PR, avisar a Andrés (revisor). En la descripción aclarar que `evidencia/ch-03-local/` es evidencia local y no del VPS, y que la prueba de `unhealthy` se hizo con `Stop-Service` real.
- **Pendiente de acordar**: los PRs de `CH-01` y de `CH-05` los mergeó Mariano (administra el repo) sin la revisión cruzada de Facundo y de Andrés respectivamente. Los tres definen si la política se mantiene tal cual (y se avisa a los revisores cuando se abre un PR) o se acuerda otra cosa. Facundo y Andrés pueden revisar `CH-01`, `CH-02` y `CH-05` igual, sin bloquear nada.

---

## 2. Reglas de coordinación

- **Un change, un dueño.** Los archivos compartidos tienen dueño único (tabla de abajo). Si necesitás un cambio en un archivo ajeno, se lo pedís al dueño.
- **No se hace `propose` de un change hasta que sus dependencias estén archivadas y mergeadas en `main`**, y cada uno haya hecho `git pull`.
- **Una rama por change** (por ejemplo `feat/ch-04-crud-editoriales-generos-autores`). El PR se abre en GitHub contra `main` y se mergea con **"Create a merge commit"** (no Squash).
- **Modelos antes que CRUD**: ningún `service` ni `router` se propone antes de que `CH-02` esté archivado (ya cumplido).
- **No inventar reglas de negocio.** Lo que el enunciado no dice es pregunta abierta (`knowledge-base/10_preguntas_abiertas.md`); toda decisión de dominio se justifica en `design.md`.
- **No crear endpoints que no estén listados** (no hay DELETE ni PATCH de ventas).
- **Cada módulo lleva `models.py`, `schemas.py`, `service.py` y `router.py`**: la lógica va en el `service` (recibe la sesión como parámetro y traduce errores) y el router solo recibe, delega y declara la respuesta.
- **Los tests no parchean código**: si un caso falla, se reporta al dueño del módulo y se corrige en una rama suya.
- **Si un change crece más de una jornada, se parte antes de empezar**, no a mitad de camino.
- **Un commit por fase o change archivado**; commits convencionales (`feat:`, `fix:`, `docs:`, `chore:`). Nada de `.env`, `.venv`, `__pycache__` ni `*.bak`. No se commitea ni se pushea sin decidirlo explícitamente.

### Archivos compartidos y su dueño

| Archivo | Dueño | Cómo se cambia |
|---|---|---|
| `app/main.py` | Mariano (`CH-01`) | Cada dueño agrega solo su línea `include_router` del módulo. En un conflicto de merge se conservan ambas líneas. Los modelos ya se importan todos en `CH-02`. |
| `app/core/config.py`, `app/core/database.py` | Mariano (`CH-01`) | Pedido al dueño. |
| `models.py` de los siete módulos | Mariano (`CH-02`, **terminado**) | Si un módulo necesita otra columna o restricción, se pide a Mariano. No se renombran tablas ni columnas. |
| `schemas.py`, `service.py`, `router.py` de cada módulo | El dueño del change del módulo | Los stubs de `CH-02` (solo docstring) se reemplazan en el change del módulo. |
| `requirements.txt`, `env.example`, `.gitignore` | Mariano (`CH-01`) | Pedido al dueño. |
| `Dockerfile`, `.dockerignore` | Mariano (`CH-03`) | Pedido al dueño. |
| Script del seed | Facundo (`CH-08`) | Lo ejecuta Mariano en el VPS (`CH-11`). |
| `test/*.http` | Andrés (`CH-09`) | — |
| `DEPLOY.md`, `evidencia/`, `README.md` final | Mariano (`CH-11` y `CH-12`) | Facundo y Andrés completan lo que les toca (ver sección 4). |

> **Convención heredada de la veterinaria (a confirmar):** ningún módulo importa DTO de otro; cada `schemas.py` define sus propias vistas resumidas. Los DTO se nombran `Create`, `Update`, `Read`.

---

## 3. Riesgos y cosas a cuidar

| Riesgo | Por qué importa | Qué hacer |
|---|---|---|
| Mariano concentra los changes restantes | Si se atrasa, se atrasa casi todo el camino crítico y el despliegue. | Orden de la sección 0; Facundo y Andrés revisan sus PRs apenas se abren; `CH-07` puede reasignarse. |
| Revisiones cruzadas pendientes (`CH-01`, `CH-02`, `CH-05`) | Los PRs ya están mergeados en `main` sin que los revisen los dueños de revisión; un error de modelo o de contrato se propagaría a los demás changes. | Facundo y Andrés los revisan sobre `main` en sus tiempos libres; lo que encuentren se corrige en una rama del dueño. |
| Despliegue en el VPS al final | Es el 25 % de la nota (imagen 15 % + despliegue 10 %) y tiene trampas (`localhost` vs `host.docker.internal`, `HEALTHCHECK`). | `CH-03` ya está hecho (falta el PR); sigue `CH-10` sin esperar el seed. |
| Descuento de stock sin respuesta | Afecta `CH-07` y el seed (`CH-08`). | Consultar a la cátedra ya; mientras tanto, no implementar descuento. |
| `/health/ready` sin base | El enunciado solo declara 200; el 503 es decisión del equipo. | Ya implementado y verificado en `CH-01` (503 `{"estado":"no listo"}`); falta confirmarlo con la cátedra. |
| Secretos en el repo, la imagen o el zip | Un proyecto con credenciales reales no se corrige hasta que se subsane. | `.gitignore` desde `CH-01`; revisar el diff antes de cada commit y el historial antes de armar el `.zip`. |
| Estado del VPS al momento de la corrección | El despliegue tiene que seguir en línea hasta que se publiquen las notas. | `--restart unless-stopped` y cómo actualizar documentados en `DEPLOY.md`. |

---

## 4. Entrega

Un único `Parcial_Cap1a4_<NombreDelGrupo>.zip` (el nombre del grupo todavía hay que definirlo), que sube **un solo integrante** al campus. Lo arma Mariano en `CH-12` y lo revisan Facundo y Andrés antes de subirlo.

Contenido: código fuente, `requirements.txt`, `env.example` (sin valores reales), `test/`, `Dockerfile`, `.dockerignore`, `README.md` (con nombres y apellidos de los integrantes y los pasos para levantar desde cero), `DEPLOY.md` y `evidencia/` (caso C-07 y casos D-01 a D-07). **Sin** `.venv`, `__pycache__` ni `.env`.

Para el `README.md`: Mariano arma la estructura y los pasos de entorno, arranque y contenedor; Facundo completa los pasos del seed y Andrés los de los casos `.http`.
