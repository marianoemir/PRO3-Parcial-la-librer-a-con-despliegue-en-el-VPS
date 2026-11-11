# Tasks

> Propose-only: este change entrega artefactos (proposal, design, specs, tasks). **No** ejecutar apply, **no** commitear, **no** modificar `openspec/changes/archive/`. La verificación de implementación corresponde al apply futuro; cada tarea abajo indica cómo se verificará.
>
> **Alcance corregido:** `ventas` (CH-07, stubs no implementados) queda excluido de este change. El change propio de ventas debe nacer con los límites `int4` desde su origen (ver constancia en `proposal.md`, `design.md` y nota en `CHANGES.md`).

## 1. Constante compartida y adopción en módulos (≤ 2 h)

- [x] 1.1 Crear `app/core/constants.py` con `INT4_MAX = 2147483647` (documentar que corresponde a PostgreSQL `integer` int4) y exportar para uso en routers/schemas. **Verificación:** `python -c "from app.core.constants import INT4_MAX; print(INT4_MAX)"` imprime `2147483647`; `rg "INT4_MAX" app/core/constants.py` muestra definición única.
- [x] 1.2 En `app/modules/libros/router.py` y `app/modules/clientes/router.py`, aplicar `Path(le=INT4_MAX)` a todos los path ids (`/libros/{id}` GET/PATCH, `/clientes/{id}` GET/PATCH, `/clientes/{id}/perfil` POST, `/clientes/{id}/ventas` GET), `Query(ge=0, le=INT4_MAX)` a `offset` en listados (`GET /libros/`, `GET /clientes/{id}/ventas`) y `Query(le=INT4_MAX)` al filtro opcional `genero_id` de `GET /libros/`, importando desde `app.core.constants`. Mantener `id == 0` → 404 (sin `ge=1` en path). **Verificación:** `.http` `GET /libros/99999999999`, `GET /libros/?offset=99999999999`, `GET /libros/?genero_id=99999999999`, `GET /clientes/99999999999` responden 422 sin cuerpo con `Traceback`/`DataError`/SQL; `GET /libros/0` (o id 0 equivalente) responde 404.
- [x] 1.3 (Opcional recomendado) Reemplazar `_INT4_MAX` local en `app/modules/{editoriales,generos,autores}/router.py` por import de `INT4_MAX` sin cambiar valores ni constraints. **Verificación:** `rg "_INT4_MAX" app/modules` vacío o solo usos justificados; smoke `.http` existente de CH-04 sigue devolviendo 422 en overflow.

## 2. Body ids en schemas (≤ 2 h)

- [x] 2.1 Normalizar `app/modules/libros/schemas.py` para usar `INT4_MAX` en `Field(ge=1, le=INT4_MAX)` de `editorial_id`, `genero_id`, `autor_id` y en `orden` (`LibroCreate`, `LibroUpdate`, DTO de autoría anidada) sin alterar semántica actual (ya validada a 422 por HTTP en propose). **Verificación:** `POST /libros/` y `PATCH /libros/{id}` con cualquier body id u `autores[0].orden` `99999999999` responden 422 antes de tocar DB; FK inexistente dentro de rango sigue siendo 409 (RT-02).

## 3. Casos `.http` planificados (≤ 1.5 h, definición en change / ejecución en apply)

- [x] 3.1 Crear `test/ch13-libros-rango-int4.http` con casos: `GET /libros/99999999999`→422, `PATCH /libros/99999999999`→422, `GET /libros/?offset=99999999999`→422, `GET /libros/?genero_id=99999999999`→422, body overflow en POST/PATCH (`editorial_id/genero_id/autor_id/autores[0].orden`)→422, y control `GET /libros/0`→404. **Verificación:** ejecución manual en VS Code/REST client o herramienta equivalente; códigos y cuerpos sin internals.
- [x] 3.2 Crear `test/ch13-clientes-rango-int4.http` con: `GET/PATCH /clientes/99999999999`→422, `POST /clientes/99999999999/perfil`→422, `GET /clientes/99999999999/ventas`→422, `GET /clientes/1/ventas?offset=99999999999`→422, control `GET /clientes/0`→404. **Verificación:** idem.

## 4. Specs, CHANGES.md y cierre documental (≤ 1 h)

- [x] 4.1 Actualizar deltas de spec en `openspec/changes/ch-13-validacion-rango-int4/specs/` para `libros-autorias` y `clientes-perfil` con el escenario “id u offset fuera de rango” (422, RN-12). `ventas-renglones` queda excluido de este change (CH-07 debe nacer con límites int4 desde su propio change). **Verificación (propose):** archivos presentes y consistentes con design/proposal; `openspec validate ch-13-validacion-rango-int4 --strict` si el tooling está disponible (en apply/archive).
- [x] 4.2 Nota de rectificación actualizada en `CHANGES.md`: CH-13 corrige el bug transversal de validación `int4` en CH-05/CH-06 y deja constancia explícita de que CH-07 (`ventas-renglones`) debe incorporar estos límites desde su propio change. **Verificación:** `git diff -- CHANGES.md` muestra solo la nota de rectificación acordada; no se marcan `[x]` de otros changes ni se altera archivo archivado.
- [x] 4.3 En apply: revisar respuestas 4xx para confirmar ausencia de `uq_`, `DataError`, `Traceback`, `asyncpg`, SQL o nombres de tabla (RN-12). **Verificación:** búsqueda textual sobre cuerpos de respuesta capturados de `.http`.

## Notas de verificación cruzada

- **Curl (propose, 2026-11-11):** `GET http://127.0.0.1:8000/health/live` → 200. `POST /libros/` y `PATCH /libros/1` con `editorial_id: 99999999999` → 422 (body ids de libros ya acotados en schemas actuales). No se pudo demostrar 500 por path/offset en la instancia activa; el análisis de código fuente respalda la corrección propuesta.
- **Exclusión ventas (corrección de alcance):** `app/modules/ventas/` son stubs y CH-07 está pendiente; no se incluyen `specs/ventas-renglones`, tareas de router/schema ni `test/ch13-ventas-rango-int4.http` en este change. CH-07 debe incluir path ids, `offset`/`limit` (RN-10), body ids (`cliente_id`, `renglones[].libro_id`), `id==0`→404, 422 sin internals y sin pre-check (RN-12, RT-02) desde su nacimiento.
- **No ejecutar:** apply, commit, ni edición de `openspec/changes/archive/**`.
