# Tasks

## 1. Preparación y verificación de contexto

- [x] 1.1 Confirmar contexto del change y ausencia de la guía en el workspace. **Cómo se verifica:** ejecutar `openspec status --change ch-14-rectificacion-active-stack --json` (o equivalente) y confirmar schema `spec-driven` con artefactos `proposal/design/specs/tasks`; ejecutar `Get-ChildItem -Recurse -Filter "*GUIA*active*stack*" -ErrorAction SilentlyContinue` y registrar salida vacía (la guía no está dentro del repo; referencias de sección verificadas por el equipo contra su copia). Evidencia en `design.md`.

- [x] 1.2 Confirmar fuentes y precondiciones antes de aplicar cambios documentales. **Cómo se verifica:** revisar `CHANGES.md`, `AGENTS.md`, `CLAUDE.md`, `knowledge-base/10_preguntas_abiertas.md`, `.active-orchestrator-state.json`, artefactos del change y `.http`/specs relevantes (`test/ch09-casos-http-c.http`, `test/ch09-c07-consultas-fijas.http`, `test/ch07-ventas-errores.http`, `test/ch08-seed-datos-iniciales.http`, deltas/`openspec/specs` CH-13); `design.md` y `specs/casos-http-c/spec.md` citan evidencia directa y marcan `[VERIFICAR]` donde corresponda.

## 2. Spec `casos-http-c` (artefacto del change)

- [x] 2.1 Mantener `specs/casos-http-c/spec.md` con `## Purpose`, `## ADDED Requirements` y un requirement por caso C-01 a C-08, referenciando C-05 en `test/ch07-ventas-errores.http` y C-06 en `test/ch08-seed-datos-iniciales.http` sin duplicarlos. **Cómo se verifica:** el archivo contiene headings `### Requirement: C-01` a `C-08`, menciona los `.http` propietarios y no duplica cuerpos HTTP de C-05/C-06.

- [x] 2.2 Mantener escenarios verificables y atemporales respaldados por evidencia: sin escenarios de descuento de stock, C-02 con huérfano respaldado por título `CH09` en C-02a y C-04 con huérfano, C-07 con conteos 3/3 y 2/2 SELECT observados el 11/11/2026 por Mariano con `SQL_ECHO` (captura formal en CH-12), C-08 fusionado, y `detail` de C-05 alineado a `test/ch07-ventas-errores.http`. **Cómo se verifica:** revisión del spec + tabla escenario→evidencia en `design.md` sin escenarios huérfanos ni `[VERIFICAR]` en THEN de C-07.

- [x] 2.3 Mantener en `design.md` la justificación de capability `casos-http-c`, convención WHEN/THEN adaptada al repo (referencias de guía verificadas por el equipo contra su copia) y decisiones de diseño. **Cómo se verifica:** `design.md` contiene decisión/rationale y mapeo coherente con la spec.

## 3. Auditoría y mapeos (re-ejecución y actualización en `design.md`)

- [x] 3.1 Re-ejecutar B.1 (inventario de artefactos archivados) y B.2 (Purpose, ADDED/MODIFIED, conteo `#### Scenario`) y actualizar `design.md` con comandos y salidas relevantes. **Cómo se verifica:** `design.md` incluye comandos + salidas reales y conclusiones.

- [x] 3.2 Re-ejecutar B.3 con comparación por encabezados `### Requirement:` del delta MODIFIED de CH-13 contra `openspec/specs/clientes-perfil/spec.md` y `openspec/specs/libros-autorias/spec.md` (además de hashes), y concluir sincronización/contenido reflejado. **Cómo se verifica:** `design.md` incluye el comando real de comparación, salida/conteos de encabezados faltantes y conclusión explícita (buscar "int4" no alcanza).

- [x] 3.3 Re-ejecutar B.4 (`tasks.md`: tildes, mención de verificación, citas a `openspec validate` como `[VERIFICAR]` sin evidencia conservada) y B.5 (estados `CHANGES.md` vs carpetas archivadas y formatos). **Cómo se verifica:** `design.md` incluye conteos/flags, estados observados y hallazgos.

- [x] 3.4 Re-ejecutar B.6 (hashes `AGENTS.md`/`CLAUDE.md` e identidad) y B.7 (`.active-orchestrator-state.json` vs `CHANGES.md`). **Cómo se verifica:** `design.md` registra hash final `4AEAB80F26D0B5E46F65DB65BA917DD1A604B89D8F07D90DC91D3C641B18C376` para ambos (cuando aplique) y `git status --short` observado, y estado de consistencia de state/roadmap.

- [x] 3.5 Re-ejecutar B.8 con búsqueda puntual de DSN con credencial y clasificar cada resultado. **Cómo se verifica:** `design.md` incluye el comando `Get-ChildItem openspec\changes\archive -Recurse -File | Select-String -Pattern '://[^/\s:@]+:[^@\s]+@'` (o equivalente), lista cada match clasificado como placeholder/ejemplo o valor real sin copiar el valor si fuera real.

- [x] 3.6 Actualizar mapeo escenario→evidencia y nota de cierre checklist 4.5. **Cómo se verifica:** `design.md` incluye tabla escenario→evidencia sin huérfanos y nota de cierre documental con `git status --short`, `git diff --stat` y confirmación de que `archive/`, `app/`, `test/` no cambiaron.

## 4. Actualizaciones documentales acotadas (`/opsx:apply`)

- [x] 4.1 Resincronizar `CHANGES.md` (ubicar por título de sección, conservar CRLF). **Cómo se verifica:** (a) la nota de CH-14 en "Rectificaciones" no afirma "divergencias archive↔openspec/specs" como conclusión principal y refleja que **CH-13 está reflejado en `openspec/specs`** (`cli_missing=0` y `lib_missing=0`: los requisitos del delta están en `openspec/specs`; el hash distinto es esperable entre delta y spec consolidada) y la recomendación O3+O1 pendiente de Facundo y Andrés; (b) la entrada `[CH-14]` corrige "Leer antes" sin ruta inexistente a la guía y no incluye "con resultados observados el 11/11/2026" en el scope de la spec.

- [x] 4.2 Actualizar `knowledge-base/10_preguntas_abiertas.md`, pregunta (8). **Cómo se verifica:** responsable "Equipo", incluye recomendación O3+O1 pendiente de confirmar con Facundo y Andrés, y aclara que es una duda interna de proceso, no de la cátedra.

- [x] 4.3 Verificar identidad de `AGENTS.md` y `CLAUDE.md`. **Cómo se verifica:** `Get-FileHash AGENTS.md,CLAUDE.md` devuelve el mismo hash para ambos.

- [x] 4.4 Al archivar CH-14, reemplazar "rectificación metodológica en curso (sin apply)" por el estado real en `AGENTS.md` y `CLAUDE.md`, de forma idéntica. **Cómo se verifica:** `Select-String` muestra el texto actualizado en ambos archivos y `Get-FileHash AGENTS.md,CLAUDE.md` devuelve el mismo hash para ambos.

## 5. Comprobaciones de alcance y cierre

- [x] 5.1 Confirmar que `openspec/changes/archive/`, `app/` y `test/` no fueron modificados por el change. **Cómo se verifica:** `git diff --name-only -- "openspec/changes/archive" app test` y `git status --short -- "openspec/changes/archive" app test` sin resultados nuevos atribuibles al change.

- [x] 5.2 Revisar coherencia final de los artefactos del change. **Cómo se verifica:** lectura de `proposal.md`, `design.md`, `tasks.md` y `specs/casos-http-c/spec.md` confirma redacción atemporal, mapeo consistente con la spec, auditoría con comandos/conclusiones corregidas, recomendación CH-11/CH-12 pendiente y tareas con "Cómo se verifica".
