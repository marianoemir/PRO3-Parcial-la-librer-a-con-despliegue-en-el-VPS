# División del equipo — Parcial Librería con despliegue en el VPS (SDD con Active Stack)

**Equipo**: Mariano · Facundo · Andrés
**Estado al**: 07/11/2026 · fundación completa (KB, roadmap, skills y reglas del agente); los changes `CH-01` a `CH-12` están pendientes.
**Fecha y hora de entrega**: la publica la cátedra en el campus (a confirmar).
**Fuente de verdad**: `docs/Parcial_Cap1a4_Consigna.pdf`. Roadmap y detalle de cada change: `CHANGES.md`. Reglas del agente: `AGENTS.md` / `CLAUDE.md`.

> **Reparto acordado**: Mariano lleva lo más pesado (el camino crítico del código) y todo lo de Docker y el VPS. Facundo y Andrés se reparten los CRUD de referencia, clientes, el seed y los casos `.http`. Los roles A/B/C de `CHANGES.md` y `AGENTS.md` son **roles de trabajo**, no personas: Mariano cumple los roles A y C, y el rol B se divide entre Facundo y Andrés.

| Persona | Roles de `CHANGES.md` | Changes |
|---|---|---|
| **Mariano** | A (Backend Core) + C (Infra/DevOps) | `CH-01`, `CH-02`, `CH-03`, `CH-05`, `CH-07`, `CH-10`, `CH-11`, `CH-12` |
| **Facundo** | B (Backend Aux) | `CH-04`, `CH-08` |
| **Andrés** | B (Backend Aux) | `CH-06`, `CH-09` |

---

## 0. Dónde estamos y qué hace cada uno ahora

**Ya está hecho**: la fundación (OpenSpec, knowledge base `01`–`10` y `12`, `CHANGES.md`, skills `fastapi` y `sqlmodel`, `AGENTS.md` y `CLAUDE.md`). Hacé `git pull` antes de empezar.

**Antes de arrancar, una consulta a la cátedra** (no bloquea el inicio pero sí `CH-07`): ¿la venta descuenta stock del libro? Es la duda de prioridad alta de `knowledge-base/10_preguntas_abiertas.md` (§1). Que la mande una sola persona y registre la respuesta ahí. Las demás dudas (§2 a §7) se pueden consultar en el mismo mensaje.

| Persona | Empieza ya con | Después | Qué lo frena |
|---|---|---|---|
| **Mariano** | `CH-01` foundation-setup → `CH-02` core-models | `CH-05`, `CH-03` + `CH-10` (primer despliegue en el VPS), `CH-07`, y al final `CH-11` y `CH-12` | Nada al inicio. Destraba a los otros dos: sin `CH-02` mergeado, nadie arranca los módulos. |
| **Facundo** | Leer la KB y revisar `CH-01` y `CH-02` | `CH-04` apenas esté `CH-02`; luego `CH-08` (seed) cuando estén `CH-04` y `CH-07` | `CH-04` espera a `CH-02`; `CH-08` espera a `CH-07`. |
| **Andrés** | Leer la KB y revisar `CH-01` y `CH-02` | `CH-06` apenas esté `CH-02`; luego `CH-09` (casos `.http`) cuando esté `CH-08` | `CH-06` espera a `CH-02`; `CH-09` espera a `CH-08`. |

**Orden sugerido para Mariano** (es una sola persona con ocho changes, y el orden importa):

1. `CH-01` → `CH-02`: destraban a todos.
2. `CH-05` libros-autorias: está en el camino crítico y solo necesita `CH-02`.
3. `CH-03` docker-imagen → `CH-10` despliegue-vps-inicial: **no los dejes para el final**. El despliegue vale el 25 % de la nota (imagen 15 % + VPS 10 %) y tiene trampas (`localhost` vs `host.docker.internal`, `HEALTHCHECK`). Conviene que los problemas aparezcan con tiempo.
4. `CH-07` ventas-renglones (necesita `CH-05` y `CH-06`).
5. `CH-11` despliegue-vps-datos + `DEPLOY.md` (necesita `CH-08`) → `CH-12` evidencia-entrega (necesita `CH-09` y `CH-11`).

**Cómo se revisa**: ver la política de revisión en la sección 1.

---

## 1. De un vistazo

| # | Change | Dueño | Depende de | Lo revisa | Estimación* | Estado |
|---|---|---|---|---|---|---|
| CH-01 | `foundation-setup` | Mariano | — | Facundo | 5–6 h | ⬜ pendiente |
| CH-02 | `core-models` | Mariano | CH-01 | Facundo **y** Andrés | 6–8 h | ⬜ pendiente |
| CH-03 | `docker-imagen` | Mariano | CH-01 | Andrés | 3–4 h | ⬜ pendiente |
| CH-04 | `crud-editoriales-generos-autores` | Facundo | CH-02 | Mariano | 5–7 h | ⬜ pendiente |
| CH-05 | `libros-autorias` | Mariano | CH-02 | Andrés | 6–8 h | ⬜ pendiente |
| CH-06 | `clientes-perfil` | Andrés | CH-02 | Facundo | 3–4 h | ⬜ pendiente |
| CH-07 | `ventas-renglones` | Mariano | CH-05, CH-06 | Facundo **y** Andrés | 6–8 h | ⬜ pendiente |
| CH-08 | `seed-datos-iniciales` | Facundo | CH-04, CH-07 | Mariano | 3–4 h | ⬜ pendiente |
| CH-09 | `casos-http-C` | Andrés | CH-08 | Facundo | 3–4 h | ⬜ pendiente |
| CH-10 | `despliegue-vps-inicial` | Mariano | CH-02, CH-03 | Andrés | 4–6 h | ⬜ pendiente |
| CH-11 | `despliegue-vps-datos` (+ `DEPLOY.md`) | Mariano | CH-10, CH-08 | Facundo | 4–5 h | ⬜ pendiente |
| CH-12 | `evidencia-entrega` | Mariano | CH-09, CH-11 | Facundo **y** Andrés | 3–4 h | ⬜ pendiente |

\* Estimación orientativa de esta propuesta, no de `CHANGES.md` (que solo dice 4–6 h por change). Ajustala según cómo vaya avanzando cada uno.

Carga total estimada: Mariano ≈ 37–47 h · Facundo ≈ 8–11 h · Andrés ≈ 6–8 h.

### Camino crítico y paralelismo

Camino crítico: `CH-01 → CH-02 → CH-05 → CH-07 → CH-08 → CH-11 → CH-12`.

Los puntos de sincronización (gates) son los de `CHANGES.md`:

| Gate | Se libera cuando… | Se puede avanzar en paralelo |
|---|---|---|
| 1 | `CH-01` ✓ | `CH-02` y `CH-03` (ambos de Mariano: en serie) |
| 2 | `CH-02` ✓ | `CH-04` (Facundo), `CH-06` (Andrés) y `CH-05` (Mariano); luego `CH-10` (Mariano) cuando esté `CH-03` |
| 3 | `CH-05` ✓ y `CH-06` ✓ | `CH-07` (Mariano) |
| 4 | `CH-07` ✓ y `CH-04` ✓ | `CH-08` (Facundo) |
| 5 | `CH-08` ✓ | `CH-09` (Andrés) y `CH-11` (Mariano, si `CH-10` ✓) |
| 6 | `CH-09` ✓ y `CH-11` ✓ | `CH-12` (Mariano) |

> **Cuello de botella**: Mariano concentra el camino crítico del código y todo el despliegue, así que sus changes se hacen **en serie**, mientras que en el plan original corrían en paralelo con otro agente. Facundo y Andrés van a tener tiempo libre en los gates 2 a 4; ese tiempo conviene usarlo en revisar los PRs de Mariano apenas se abren. Si Mariano se atrasa, `CH-05` (solo necesita `CH-02`) y `CH-07` pueden pasar a Facundo o Andrés.

### Política de revisión

- Cada change lo revisa **otra persona**, nunca su dueño (columna "Lo revisa"). Los de `Governance: CRITICO` o que bloquean a otros (`CH-02`, `CH-07`) los revisan los dos restantes. Como casi todo lo de Docker y VPS es de Mariano, lo revisan Andrés o Facundo.
- Los PRs que **bloquean a otro** (`CH-01`, `CH-02`, `CH-05`, `CH-06`, `CH-07`, `CH-08`) se revisan apenas se abren. El resto se junta en **rondas** (dos PRs a la vez).
- La revisión usa el checklist de la guía: dependencias archivadas, cada regla citada existe en la KB, lo ambiguo quedó como pregunta abierta, al menos tres escenarios por spec y evidencia real (salida de la herramienta, no la explicación del agente).

---

## 2. Reglas de coordinación

- **Un change, un dueño.** Los archivos compartidos tienen dueño único (tabla de abajo). Si necesitás un cambio en un archivo ajeno, se lo pedís al dueño.
- **No se hace `propose` de un change hasta que sus dependencias estén archivadas y mergeadas en `main`**, y cada uno haya hecho `git pull`.
- **Modelos antes que CRUD**: ningún `service` ni `router` se propone antes de que `CH-02` esté archivado.
- **No inventar reglas de negocio.** Lo que el enunciado no dice es pregunta abierta (`knowledge-base/10_preguntas_abiertas.md`); toda decisión de dominio se justifica en `design.md`.
- **No crear endpoints que no estén listados** (no hay DELETE ni PATCH de ventas).
- **Los tests no parchean código**: si un caso falla, se reporta al dueño del módulo y se corrige en una rama suya.
- **Si un change crece más de una jornada, se parte antes de empezar**, no a mitad de camino.
- **Un commit por fase o change archivado**; commits convencionales (`feat:`, `fix:`, `docs:`, `chore:`). Nada de `.env`, `.venv`, `__pycache__` ni `*.bak`.

### Archivos compartidos y su dueño

| Archivo | Dueño | Cómo se cambia |
|---|---|---|
| `app/main.py` | Mariano (`CH-01`) | Cada dueño agrega solo su línea `include_router` del módulo. En un conflicto de merge se conservan ambas líneas. |
| `app/core/config.py`, `app/core/database.py` | Mariano (`CH-01`) | Pedido al dueño. |
| `models.py` de los siete módulos | Mariano (`CH-02`) | Todos los modelos de tabla se publican juntos en `CH-02`; si un módulo necesita otra columna, se pide a Mariano. |
| `schemas.py`, `service.py`, `router.py` de cada módulo | El dueño del change del módulo | — |
| `requirements.txt`, `env.example`, `.gitignore` | Mariano (`CH-01`) | Pedido al dueño. |
| `Dockerfile`, `.dockerignore` | Mariano (`CH-03`) | Pedido al dueño. |
| Script del seed | Facundo (`CH-08`) | Lo ejecuta Mariano en el VPS (`CH-11`). |
| `test/*.http` | Andrés (`CH-09`) | — |
| `DEPLOY.md`, `evidencia/`, `README.md` final | Mariano (`CH-11` y `CH-12`) | Facundo y Andrés completan lo que les toca (ver sección 4). |

> **Convención heredada de la veterinaria (a confirmar):** ningún módulo importa DTO de otro; cada `schemas.py` define sus propias vistas resumidas.

---

## 3. Riesgos y cosas a cuidar

| Riesgo | Por qué importa | Qué hacer |
|---|---|---|
| Mariano concentra ocho changes | Si se atrasa, se atrasa casi todo el camino crítico y el despliegue. | Orden sugerido de la sección 0; Facundo y Andrés revisan sus PRs apenas se abren; `CH-05` o `CH-07` pueden reasignarse. |
| `CH-02` se atrasa | Nadie puede arrancar los módulos sin los modelos. | Es lo primero después de `CH-01`; los otros dos revisan el PR en cuanto se abre. |
| Despliegue en el VPS al final | Es el 25 % de la nota (imagen 15 % + despliegue 10 %) y tiene trampas (`localhost` vs `host.docker.internal`, `HEALTHCHECK`). | `CH-03` y `CH-10` justo después de `CH-05`, sin esperar el seed. |
| Descuento de stock sin respuesta | Afecta `CH-07` y el seed (`CH-08`). | Consultar a la cátedra ya; mientras tanto, no implementar descuento. |
| `/health/ready` sin base | El enunciado solo declara 200; el 503 es decisión del equipo. | Se implementa en `CH-01` como decisión propia (a documentar en `design.md`) y se confirma con la cátedra. |
| Secretos en el repo, la imagen o el zip | Un proyecto con credenciales reales no se corrige hasta que se subsane. | `.gitignore` desde `CH-01`; revisar el diff antes de cada commit y el historial antes de armar el `.zip`. |
| Estado del VPS al momento de la corrección | El despliegue tiene que seguir en línea hasta que se publiquen las notas. | `--restart unless-stopped` y cómo actualizar documentados en `DEPLOY.md`. |

---

## 4. Entrega

Un único `Parcial_Cap1a4_<NombreDelGrupo>.zip`, que sube **un solo integrante** al campus. Lo arma Mariano en `CH-12` y lo revisan Facundo y Andrés antes de subirlo.

Contenido: código fuente, `requirements.txt`, `env.example` (sin valores reales), `test/`, `Dockerfile`, `.dockerignore`, `README.md` (con nombres y apellidos de los integrantes y los pasos para levantar desde cero), `DEPLOY.md` y `evidencia/` (caso C-07 y casos D-01 a D-07). **Sin** `.venv`, `__pycache__` ni `.env`.

Para el `README.md`: Mariano arma la estructura y los pasos de entorno, arranque y contenedor; Facundo completa los pasos del seed y Andrés los de los casos `.http`.
