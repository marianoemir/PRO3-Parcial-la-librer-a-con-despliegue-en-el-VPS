# Design

## Context

Rectificación metodológica (Active Stack + SDD) para el change `ch-14-rectificacion-active-stack` (schema `spec-driven`). El change incorpora la spec faltante de `casos-http-c` (C-01 a C-08) y documenta una auditoría basada en evidencia de herramienta y en artefactos del repositorio, sin modificar código de la app, archivos `.http` ni `openspec/changes/archive/`.

`GUIA-active-stack-sdd.md` no está dentro del repo. Las referencias a sus secciones (§0.5, §4.1, §4.2, §4.4, §4.5, §6, §10.4) citadas en este documento fueron verificadas por el equipo contra su copia y se usan como criterio de mapeo/auditoría.

## Goals / Non-Goals

**Goals:**
- Incorporar `specs/casos-http-c/spec.md` con `## Purpose`, `## ADDED Requirements`, escenarios verificables atemporales y respaldados por `.http`/seed/observaciones documentadas, referencias a C-05/C-06 sin duplicarlos, y observaciones C-07 documentadas.
- Documentar auditoría con comandos y salidas reales: inventario de artefactos archivados, conteo de `#### Scenario` y secciones, sincronización `archive specs` vs `openspec/specs`, comparación de CH-13 por encabezados `### Requirement:` (delta MODIFIED vs specs principales), revisión de `tasks.md`, coherencia de estados, hashes de `AGENTS.md`/`CLAUDE.md`, estado de `.active-orchestrator-state.json` y búsqueda puntual de DSN con credencial en archivados.
- Registrar tabla hallazgo→sección de guía, mapeo escenario→evidencia, opciones CH-11/CH-12 con recomendación pendiente, y nota de cierre documental del checklist 4.5 (sin suite de tests automatizada).
- Definir en `tasks.md` el trabajo para `/opsx:apply`: resincronización acotada de `CHANGES.md` y KB 10, verificación/actualización de estado CH-14 en `AGENTS.md` y `CLAUDE.md` al archivar (idénticos), y re-ejecución de auditoría/mapeos/comprobaciones.

**Non-Goals:**
- No modificar `openspec/changes/archive/`, `app/` ni `test/`.
- No sincronizar `openspec/specs/` masivamente ni crear `.openspec.yaml` faltantes en archivados.
- No inventar resultados no respaldados por evidencia; registrar `[VERIFICAR]` donde falte evidencia histórica/formal.
- No ejecutar `/opsx:apply` ni realizar commits como parte de la planificación del change.

## Decisions

### 1. Capability `casos-http-c`
- **Decisión:** mantener capability `casos-http-c` en `openspec/changes/ch-14-rectificacion-active-stack/specs/casos-http-c/spec.md`.
- **Rationale:** agrupa C-01 a C-08 (KB 06 §Casos de prueba mínimos) como contrato observable de verificación HTTP, separado de capabilities de dominio y despliegue; evita colisión con `openspec/specs/` existentes y permite sincronización futura.
- **Alternativas:** una capability por caso (fragmentado), reusar capability de dominio (mezcla responsabilidades).

### 2. Tratamiento de C-01 a C-08 en la spec
- **Decisión:** C-05 y C-06 se referencian en artefactos existentes (`test/ch07-ventas-errores.http`, `test/ch08-seed-datos-iniciales.http`) sin duplicarlos. C-01 se limita a 422/error de validación pública según `.http`. C-03 usa el id del `.http` (`/clientes/1/perfil`) respaldado por seed (`app/seed.py` define perfil para cliente 1). C-02/C-03/C-04/C-05 citan `detail` observados en `.http`. C-06 mantiene total/precios observados en `.http` CH-08. C-07 registra conteos observados 3/3 y 2/2 SELECT (11/11/2026, Mariano, `SQL_ECHO`) y la captura formal de evidencia queda para CH-12. C-08 se fusiona en un escenario que cubre patrón de inyección, respuesta `[]` y ausencia de catálogo completo/error SQL, respaldado por RN-11/RT-05 en KB 05. No se especifica descuento de stock en ventas porque el enunciado no lo pide y la consulta a la cátedra está pendiente (KB 10).
- **Rationale:** refleja el contrato observable respaldado por artefactos existentes y evita fijar comportamiento en un punto ambiguo.
- **Alternativas:** incluir escenarios no respaldados o de ambigüedades pendientes (incorrecto), omitir observaciones C-07 documentadas (pierde evidencia útil).

### 3. Convención de escenarios WHEN/THEN
- **Decisión:** la spec usa `- **WHEN**` / `- **THEN**`, consistente con las specs archivadas y consolidadas del repo.
- **Rationale:** la guía §4.2 contempla Dado/Cuando/Entonces pero §0.5 indica adaptar a la convención del repo; las referencias de guía fueron verificadas por el equipo contra su copia y la convención observada en el repo es WHEN/THEN.
- **Alternativas:** migrar a Dado/Cuando/Entonces (rompe consistencia sin necesidad).

### 4. Auditoría como evidencia re-ejecutable
- **Decisión:** los hallazgos de auditoría se documentan con comandos, salidas reales o conclusiones derivadas de herramientas, y comparación con el estado del repositorio. B.3 compara por encabezados `### Requirement:` de los deltas MODIFIED de CH-13 contra `openspec/specs/clientes-perfil/spec.md` y `openspec/specs/libros-autorias/spec.md` (además de hashes/contenido característico). B.8 ejecuta búsqueda puntual de DSN con credencial y clasifica cada resultado sin copiar valores reales si aparecieran.
- **Rationale:** evidencia = salida de herramienta/artefacto verificable; evita inferencias no respaldadas.

### 5. Alcance documental de `/opsx:apply`
- **Decisión:** `proposal.md` y `tasks.md` describen el trabajo que realizará `/opsx:apply`: mantener la spec/auditoría del change, resincronizar ediciones acotadas en `CHANGES.md`, actualizar KB 10 pregunta (8), verificar identidad `AGENTS.md`/`CLAUDE.md` y actualizar su estado CH-14 al archivar, y re-ejecutar auditoría/mapeos/comprobaciones. Este documento no ejecuta apply ni modifica esos archivos externos al directorio del change.
- **Rationale:** separa planificación (artefactos del change) de aplicación (tareas operativas), respetando las restricciones del flujo.

### 6. Brecha CH-11/CH-12 (opciones y recomendación, sin decisión)
- **Decisión tomada:** ninguna (pendiente de confirmar con Facundo y Andrés).
- **Recomendación:** **O3 + nota de evidencia O1**. O3: excepción formal fechada al checklist 4.4 para CH-11, aceptada por el equipo, sin consultar cátedra porque la regla es interna del equipo y el enunciado no evalúa artefactos OpenSpec; documentar evidencia existente (DEPLOY.md, evidencia/D-03,D-04,D-07, estado manual en `CHANGES.md`). O1: registrar nota de evidencia/trazabilidad sin inventar propose/archive retroactivo. CH-12 debe cerrarse solo con evidencia verificable.
- **Alternativas:** O1 sola (trazabilidad más débil), O2 change de regularización prospectivo (mayor costo, útil si se exige trazabilidad formal adicional).

## Auditoría (B) — Evidencia

### B.0 — Guía fuera del repo

**Comando:**
```powershell
Get-ChildItem -Recurse -Filter "*GUIA*active*stack*" -ErrorAction SilentlyContinue | Select-Object -ExpandProperty FullName
```
**Salida:** *(sin resultados)*

**Conclusión:** `GUIA-active-stack-sdd.md` no está dentro del repo. Las referencias de sección citadas fueron verificadas por el equipo contra su copia.

### B.1 — Inventario de artefactos por change archivado

**Comando:**
```powershell
Get-ChildItem "openspec\changes\archive" -Directory | Sort-Object Name | ForEach-Object {
  $files = (Get-ChildItem $_.FullName -Force -File -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Name | Sort-Object) -join ', '
  $hasSpecsDir = Test-Path (Join-Path $_.FullName 'specs')
  $specCaps = if ($hasSpecsDir) { (Get-ChildItem (Join-Path $_.FullName 'specs') -Directory -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Name) -join ', ' } else { '' }
  [PSCustomObject]@{change=$_.Name; files=$files; specs_dir=$hasSpecsDir; capabilities=$specCaps}
} | Format-List
```
**Salida relevante:** CH-01..CH-04, CH-06..CH-08 con `.openspec.yaml`, `design.md`, `proposal.md`, `tasks.md` y `specs_dir=True`; CH-05 con `README.md` extra; CH-09 sin `specs/` (`skip_specs: true` en `.openspec.yaml`); CH-10 sin `.openspec.yaml` y con `specs/despliegue-vps-inicial`; CH-13 sin `.openspec.yaml` y con `specs/clientes-perfil, libros-autorias`.

**Conclusión:** confirmados CH-09 sin `specs/`, CH-10 sin `.openspec.yaml`, CH-13 sin `.openspec.yaml`, CH-05 con `README.md` extra.

### B.2 — Purpose, ADDED/MODIFIED y escenarios

**Comando:**
```powershell
Get-ChildItem "openspec\changes\archive" -Recurse -Filter "spec.md" | ForEach-Object {
  $c = Get-Content $_.FullName -Raw
  [PSCustomObject]@{
    path=$_.FullName.Replace((Get-Location).Path+'\','')
    scenarios=([regex]::Matches($c,'#### Scenario')).Count
    purpose=[bool]($c -match '(?m)^## Purpose')
    added=[bool]($c -match '(?m)^## ADDED Requirements')
    modified=[bool]($c -match '(?m)^## MODIFIED Requirements')
  }
} | Format-Table -AutoSize -Wrap
```
**Salida relevante:** 11 specs; todas con `purpose=True`, `scenarios >= 3`. CH-13 usa `modified=True, added=False` (y ADDED en clientes-perfil según contenido) en sus deltas; los demás deltas usan `added=True`. Formato de escenarios observado: `- **WHEN**` / `- **THEN**`.

### B.3 — Sincronización archive specs vs `openspec/specs` y comparación CH-13 por encabezados

**Comando (hashes):**
```powershell
Get-ChildItem "openspec\changes\archive" -Directory | ForEach-Object {
  $change = $_.Name; $specDir = Join-Path $_.FullName 'specs'
  if (Test-Path $specDir) {
    Get-ChildItem $specDir -Directory | ForEach-Object {
      $cap = $_.Name; $arch = Join-Path $_.FullName 'spec.md'; $main = Join-Path "openspec\specs\$cap" 'spec.md'
      $mainExists = Test-Path $main
      $cmp = 'N/A'; if ($mainExists) { $cmp = if ((Get-FileHash $arch).Hash -eq (Get-FileHash $main).Hash) {'IDENTICAL'} else {'DIFFERENT'} }
      [PSCustomObject]@{archive_change=$change; capability=$cap; main_exists=$mainExists; compare=$cmp}
    }
  }
} | Format-Table -AutoSize
```
**Salida relevante (re-ejecutada):**
```text
archive_change                                    capability                  main_exists compare
--------------                                    ----------                  ----------- -------
2026-11-08-ch-01-foundation-setup                 foundation                         True DIFFERENT
2026-11-08-ch-02-core-models                      core-models                        True DIFFERENT
2026-11-08-ch-03-docker-imagen                    docker-imagen                      True DIFFERENT
2026-11-08-ch-04-crud-editoriales-generos-autores editoriales-generos-autores        True DIFFERENT
2026-11-08-ch-05-libros-autorias                  libros-autorias                    True DIFFERENT
2026-11-08-ch-06-clientes-perfil                  clientes-perfil                    True DIFFERENT
2026-11-11-ch-07-ventas-renglones                 ventas-renglones                   True IDENTICAL
2026-11-11-ch-08-seed-datos-iniciales             datos-iniciales                    True DIFFERENT
2026-11-11-ch-10-despliegue-vps-inicial           despliegue-vps-inicial             True DIFFERENT
2026-11-11-ch-13-validacion-rango-int4            clientes-perfil                    True DIFFERENT
2026-11-11-ch-13-validacion-rango-int4            libros-autorias                    True DIFFERENT
```

**Comando (comparación CH-13 por encabezados `### Requirement:` del delta MODIFIED vs specs principales):**
```powershell
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$ch13Cli = Get-Content "openspec\changes\archive\2026-11-11-ch-13-validacion-rango-int4\specs\clientes-perfil\spec.md" -Raw -Encoding UTF8
$mainCli = Get-Content "openspec\specs\clientes-perfil\spec.md" -Raw -Encoding UTF8
$ch13Lib = Get-Content "openspec\changes\archive\2026-11-11-ch-13-validacion-rango-int4\specs\libros-autorias\spec.md" -Raw -Encoding UTF8
$mainLib = Get-Content "openspec\specs\libros-autorias\spec.md" -Raw -Encoding UTF8
function ReqHeaders($text){ [regex]::Matches($text,'(?m)^### Requirement:.*$') | ForEach-Object { $_.Value.Trim() } }
$hChCli=@(ReqHeaders $ch13Cli); $hMainCli=@(ReqHeaders $mainCli)
$hChLib=@(ReqHeaders $ch13Lib); $hMainLib=@(ReqHeaders $mainLib)
"cli_missing=$(@($hChCli | Where-Object { $hMainCli -notcontains $_ }).Count)"; "lib_missing=$(@($hChLib | Where-Object { $hMainLib -notcontains $_ }).Count)"
```
**Salida relevante (re-ejecutada, con lectura UTF-8 explícita):**
```text
cli_missing=0
lib_missing=0
```
Encabezados del delta CH-13 presentes en specs principales:
- clientes-perfil: `Perfil único asociado al cliente de la ruta`, `Detalle de cliente con perfil singular`, `Ventas resumidas y paginadas de un cliente`, `Rango int4 en id de ruta para actualización de cliente`.
- libros-autorias: `Listado paginado y búsqueda por título y género`, `Detalle de libro precargado`, `Actualización parcial de libro`, `Errores del alta de libro sin exponer la base`.

**Nota:** leer las specs con `-Encoding UTF8`; sin eso, PowerShell 5.1 compara mal los encabezados con tildes (`único`, `actualización`) y da `cli_missing=2` en falso. Con lectura UTF-8 el resultado correcto es `cli_missing=0`: los encabezados del delta CH-13 están presentes en `openspec/specs`.

**Comando (comprobación de texto de un requisito MODIFICADO, no solo encabezado):**
```powershell
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$pattern = 'rango `int4` soportado; si está fuera de rango responderá 422 sin ejecutar el handler'
$delta = Select-String -Path "openspec/changes/archive/2026-11-11-ch-13-validacion-rango-int4/specs/clientes-perfil/spec.md" -Pattern $pattern -SimpleMatch
$main = Select-String -Path "openspec/specs/clientes-perfil/spec.md" -Pattern $pattern -SimpleMatch
"pattern=$pattern"
"delta_match=$([bool]$delta) line=$($delta.LineNumber)"
"main_match=$([bool]$main) line=$($main.LineNumber)"
if($delta){$delta.Line.Trim()}
if($main){$main.Line.Trim()}
```
**Salida (re-ejecutada):**
```text
pattern=rango `int4` soportado; si está fuera de rango responderá 422 sin ejecutar el handler
delta_match=True line=7
main_match=True line=33
El sistema SHALL crear un perfil con `POST /clientes/{id}/perfil` usando exclusivamente el id de la ruta como `cliente_id`. El `cliente_id` de ruta SHALL cumplir el rango `int4` soportado; si está fuera de rango responderá 422 sin ejecutar el handler. `PerfilCreate` SHALL incluir únicamente `telefono` y `direccion`, SHALL rechazar todo campo no declarado, incluido `id` o `cliente_id`, y la respuesta SHALL ser `PerfilRead` con `id`, `cliente_id`, `telefono` y `direccion`.
El sistema SHALL crear un perfil con `POST /clientes/{id}/perfil` usando exclusivamente el id de la ruta como `cliente_id`. El `cliente_id` de ruta SHALL cumplir el rango `int4` soportado; si está fuera de rango responderá 422 sin ejecutar el handler. `PerfilCreate` SHALL incluir únicamente `telefono` y `direccion`, SHALL rechazar todo campo no declarado, incluido `id` o `cliente_id`, y la respuesta SHALL ser `PerfilRead` con `id`, `cliente_id`, `telefono` y `direccion`.
```

**Conclusión:** **CH-13 está reflejado en `openspec/specs`**. `cli_missing=0` y `lib_missing=0` indican que los requisitos del delta están en `openspec/specs`; el hash distinto es esperable (delta vs spec consolidada). La comprobación de texto de un requisito MODIFICADO confirma que el contenido está presente en las specs principales (no solo los encabezados). Solo `ventas-renglones` es IDENTICAL por hash. `casos-http-c` no existe en `openspec/specs/`. No se sincroniza en este change.

### B.4 — `tasks.md`: tildes, verificación y comandos

**Comando:**
```powershell
Get-ChildItem "openspec\changes\archive" -Directory | ForEach-Object {
  $t = Join-Path $_.FullName 'tasks.md'
  if (Test-Path $t) {
    $c = Get-Content $t -Raw
    [PSCustomObject]@{change=$_.Name; checked=([regex]::Matches($c,'(?m)^\s*- \[x\]')).Count; unchecked=([regex]::Matches($c,'(?m)^\s*- \[ \]')).Count; mentions_verify=($c -match 'cómo se verifica|como se verifica|verificar|verificación|verificacion'); cites_openspec_validate=($c -match 'openspec validate')}
  }
} | Format-Table -AutoSize
```
**Salida relevante:** CH-01..CH-09 y CH-13 con todas las tareas tildadas; CH-10 con `checked=2`, `unchecked=10`. CH-04, CH-09 y CH-13 citan `openspec validate`.

**Conclusión:** CH-10 presenta incoherencia de cierre formal (carpeta archivada con tareas sin tildar). La ejecución histórica real de `openspec validate` en CH-04/CH-09/CH-13 no tiene evidencia conservada en artefactos/outputs archivados: **[VERIFICAR]**.

### B.5 — Estados CHANGES.md vs carpetas archivadas y formato

**Comando:**
```powershell
git status --porcelain -- "openspec/changes/archive"
git diff --name-only -- "openspec/changes/archive"
Select-String -Path CHANGES.md -Pattern '### \[CH-|^- \*\*Estado\*\*:' | Select-Object LineNumber, Line
```
**Salida relevante:** sin cambios git en `openspec/changes/archive/`. `CHANGES.md` muestra CH-01..CH-09 completados, CH-10 archivado, CH-11 completado hecho a mano en el VPS sin propose/apply (sin carpeta archivada), CH-12 pendiente, CH-13 completado (aplicado), CH-14 documentado.

**Comandos de existencia:** CH-10 sin `.openspec.yaml`, CH-13 sin `.openspec.yaml`, CH-05 con `README.md`, CH-09 sin `specs/`.

**Conclusión:** formatos de estado mixtos y brechas formales: CH-10 archivado sin `.openspec.yaml` y con tareas sin tildar; CH-13 archivado/aplicado sin `.openspec.yaml` (su contenido sí está reflejado en `openspec/specs`; hash distinto esperable, ver B.3); CH-11 manual sin carpeta archivada con dependencia CH-12.

### B.6 — AGENTS.md y CLAUDE.md (identidad y estado observado)

**Comando (identidad y estado actual, re-ejecutado):**
```powershell
Get-FileHash AGENTS.md,CLAUDE.md | Format-List Path,Hash
git status --short -- AGENTS.md CLAUDE.md
```
**Salida relevante (re-ejecutada):**
```text
Path : C:\Users\Mariano_Chirino\Documents\GitHub\PRO3-Parcial-la-librer-a-con-despliegue-en-el-VPS\AGENTS.md
Hash : 4AEAB80F26D0B5E46F65DB65BA917DD1A604B89D8F07D90DC91D3C641B18C376

Path : C:\Users\Mariano_Chirino\Documents\GitHub\PRO3-Parcial-la-librer-a-con-despliegue-en-el-VPS\CLAUDE.md
Hash : 4AEAB80F26D0B5E46F65DB65BA917DD1A604B89D8F07D90DC91D3C641B18C376

 M AGENTS.md
 M CLAUDE.md
```

**Hallazgo: AGENTS.md y CLAUDE.md desactualizados (Primer change pendiente: CH-09)** — **Confirmado y corregido en el working tree** (evidencia histórica de `HEAD` conservada abajo).

Antes de ejecutar los comandos siguientes se fijó `[Console]::OutputEncoding = [System.Text.Encoding]::UTF8` para que la salida no salga con caracteres rotos.

**Comando (estado anterior en `HEAD`):**
```powershell
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
git show HEAD:AGENTS.md | Select-String 'Primer change pendiente'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
git show HEAD:CLAUDE.md | Select-String 'Primer change pendiente'
```
**Salida:**
```text
Ver `CHANGES.md` (CH-01 a CH-13, 4–6 h por change; CH-13 es rectificación aplicada). Camino crítico pendiente: **CH-10 
→ CH-11 → CH-12** (CH-09 corre en paralelo y también bloquea CH-12). Primer change pendiente: **CH-09 casos-http-C** 
(CH-01 a CH-08 y CH-13 ya completados). Los modelos/esquema (CH-02) van antes de cualquier service/router. 
Docker/VPS/evidencia son changes propios (CH-03, CH-10, CH-11, CH-12).

Ver `CHANGES.md` (CH-01 a CH-13, 4–6 h por change; CH-13 es rectificación aplicada). Camino crítico pendiente: **CH-10 
→ CH-11 → CH-12** (CH-09 corre en paralelo y también bloquea CH-12). Primer change pendiente: **CH-09 casos-http-C** 
(CH-01 a CH-08 y CH-13 ya completados). Los modelos/esquema (CH-02) van antes de cualquier service/router. 
Docker/VPS/evidencia son changes propios (CH-03, CH-10, CH-11, CH-12).
```

**Conclusión:** `AGENTS.md` y `CLAUDE.md` son idénticos entre sí (hash final `4AEAB80F26D0B5E46F65DB65BA917DD1A604B89D8F07D90DC91D3C641B18C376`). `git status --short` observado en esta re-ejecución: `M AGENTS.md` y `M CLAUDE.md`. No se modifica su contenido en este apply; el texto "rectificación metodológica en curso (sin apply)" solo debe actualizarse al estado real al archivar CH-14, en ambos archivos de forma idéntica.

### B.7 — `.active-orchestrator-state.json` vs `CHANGES.md`

**Comando:**
```powershell
Get-Content .active-orchestrator-state.json -Raw
```
**Salida relevante:** `roadmap.changes` incluye CH-01..CH-14 y `roadmap.revision` = 3.

**Conclusión:** consistente con `CHANGES.md` en cuanto a inclusión de CH-14.

### B.8 — Búsqueda puntual de DSN con credencial en archivados

**Comando:**
```powershell
Get-ChildItem openspec\changes\archive -Recurse -File | Select-String -Pattern '://[^/\s:@]+:[^@\s]+@'
```
**Salida relevante (re-ejecutada):** 3 coincidencias.
- `openspec/changes/archive/2026-11-08-ch-01-foundation-setup/tasks.md:8` — **placeholder/documentación de forma** (`usuario:clave@host:5432/base` en `env.example`).
- `openspec/changes/archive/2026-11-08-ch-01-foundation-setup/tasks.md:18` — **placeholder/ejemplo de prueba** (`usuario:contraseña@localhost:1/base` en comando de verificación).
- `openspec/changes/archive/2026-11-11-ch-10-despliegue-vps-inicial/design.md:34` — **placeholder/documentación de forma** (`<usuario>:<contraseña>@<HOST_BASE>:5432/<base>`).

**Clasificación:** no se identificaron valores reales de credenciales; todos los resultados son placeholders/ejemplos con variables o texto genérico. Si apareciera un valor real, se advertiría sin copiarlo (no aplica). **[VERIFICAR]** búsqueda exhaustiva para otros formatos sensibles no cubiertos por el patrón.

## Hallazgos

| Hallazgo | Resultado | Evidencia |
|---|---|---|
| CH-09 archivado sin `specs/` | Confirmado | B.1 (`specs_dir False`). Rectificado por delta `specs/casos-http-c/spec.md`. |
| CH-13 sin `.openspec.yaml` | Confirmado | B.1/B.5. |
| CH-13 reflejado en `openspec/specs` | Confirmado (reflejado; hash distinto esperable delta vs spec consolidada) | B.3: hashes DIFFERENT, pero `cli_missing=0`, `lib_missing=0` y comprobación de texto de requisito MODIFIED presente en specs principales. |
| CH-05 con `README.md` extra | Confirmado | B.1. |
| CH-10 sin `.openspec.yaml` y con tareas sin tildar | Confirmado | B.1/B.4/B.5. |
| Nota CH-13 en `CHANGES.md` cita ruta no archivada | Confirmado (texto histórico) | B.5 y revisión de `CHANGES.md`. |
| CH-11 hecho a mano, no archivado, dependencia CH-12 | Confirmado (brecha de proceso) | B.1/B.5 y `CHANGES.md`. |
| `AGENTS.md`/`CLAUDE.md` idénticos | Confirmado | B.6: hash `4AEAB80F26D0B5E46F65DB65BA917DD1A604B89D8F07D90DC91D3C641B18C376`. |
| AGENTS.md y CLAUDE.md desactualizados (Primer change pendiente: CH-09) | Confirmado y corregido en el working tree | B.6: estado anterior en `HEAD` evidenciado con `git show` (UTF-8 fijado antes de ejecutar). |
| Ejecución histórica real de `openspec validate` (CH-04, CH-09, CH-13) | `[VERIFICAR]` | B.4: citado en `tasks.md`, sin salida conservada. |

## Tabla hallazgo → sección de guía (referencias verificadas por el equipo contra su copia)

> `GUIA-active-stack-sdd.md` no está dentro del repo; las referencias fueron verificadas por el equipo contra su copia.

| Hallazgo / tema | Sección de guía | Aplicación en este change |
|---|---|---|
| CH-11 marcado completado sin carpeta archivada; formatos de estado | **§6** (marcar `[x]` solo cuando el change está archivado) | Documenta brecha de estado/formato y define tarea de resincronización acotada en `CHANGES.md` sin alterar historial archivado. |
| CH-10 y CH-13 sin `.openspec.yaml` en archivados | **§4.1** (propose genera `.openspec.yaml`) | Evidencia de artefacto faltante en archivados; no se crea retroactivamente. |
| CH-12 depende de CH-11 no archivado formalmente | **§4.4** (dependencias archivadas) | Brecha de gate/dependencia formal; recomendación O3+O1 pendiente de confirmación, sin inventar archivado retroactivo. |
| AGENTS.md/CLAUDE.md idénticos y comparación contra evidencia | **§10.4** (rectificación actualiza AGENTS.md y CLAUDE.md idénticos y compara lo archivado contra git) | Hash verificado y `git status/diff` usados para confirmar que `archive/`, `app/`, `test/` no tienen cambios; tareas definen verificación/actualización al archivar. |
| Convención de escenarios y adaptación al repo | **§4.2**, **§0.5** | Se mantiene WHEN/THEN coherente con el repo. |
| Cierre documental sin suite de tests | **§4.5** | Nota de cierre documental basada en alcance y evidencia git (sin suite automatizada). |

## Mapeo escenario → evidencia (spec `casos-http-c`)

| Requirement / Escenario | Evidencia (`.http` o fuente) | Respaldo observado/documentado | Nota |
|---|---|---|---|
| C-01 / ruta no entero → 422 | `test/ch09-casos-http-c.http` (GET `/libros/no-es-entero`) | 422, validación pública, sin detalle BD | Según artefacto `.http` |
| C-01 / ruta válida no confundida | `test/ch09-c07-consultas-fijas.http` (GET `/libros/1`) | 200 fixture libro 1 | Borde operativo |
| C-02 / ISBN repetido → 409 | `test/ch09-casos-http-c.http` C-02a | `detail: "Ya existe un libro con ese ISBN"` | Título C-02a contiene `CH09` |
| C-02 / email repetido → 409 | `test/ch09-casos-http-c.http` C-02b | `detail: "El email ya está registrado."` | Cita texto observado |
| C-02 / sin huérfano | `test/ch09-casos-http-c.http` (GET `/libros/?titulo=CH09` tras rechazos) | 200 `[]` | Integridad |
| C-03 / segundo perfil → 409 | `test/ch09-casos-http-c.http` C-03; `app/seed.py` cliente 1 | `detail: "El cliente ya tiene un perfil."` | Id respaldado por seed |
| C-04 / editorial inexistente → 409 | `test/ch09-casos-http-c.http` C-04a | `detail: "La referencia indicada no existe"` | Cita texto observado |
| C-04 / autor inexistente → 409 | `test/ch09-casos-http-c.http` C-04b | `detail: "La referencia indicada no existe"` | Cita texto observado |
| C-04 / sin huérfanos | `test/ch09-casos-http-c.http` (GET `/libros/?titulo=CH09`) | 200 `[]` | Integridad |
| C-05 / cliente inexistente (ref) | `test/ch07-ventas-errores.http` | 409 `detail: "La referencia indicada no existe o hay un conflicto de datos"` | documentado en el .http (comentario Esperado) |
| C-05 / libro inexistente (ref) | `test/ch07-ventas-errores.http` | 409 `detail: "El libro indicado no existe"` | Referencia |
| C-06 / venta válida total correcto (ref) | `test/ch08-seed-datos-iniciales.http` | 201, `total: "77000.00"`, precios/subtotales copiados | Referencia |
| C-07 / libros consultas fijas | `test/ch09-c07-consultas-fijas.http` (GET `/libros/1`, `/libros/6`) | 200; 3/3 SELECT observados 11/11/2026 por Mariano con `SQL_ECHO` | Captura formal en CH-12 |
| C-07 / ventas consultas fijas | `test/ch09-c07-consultas-fijas.http` (GET `/ventas/2`, `/ventas/3`, POST auxiliar) | 200/201 fixture; 2/2 SELECT observados 11/11/2026 por Mariano con `SQL_ECHO` | Captura formal en CH-12 |
| C-08 / patrón inyección seguro | `test/ch09-casos-http-c.http` C-08; RN-11/RT-05 (KB 05) | 200 `[]`, sin catálogo completo ni error SQL | Escenario fusionado |

**Sin escenarios huérfanos:** todos los escenarios de la spec aparecen en la tabla anterior.

## Opciones CH-11/CH-12 (sin decisión tomada)

| Opción | Descripción | Costo / riesgo | Efecto |
|---|---|---|---|
| O1 — Evidencia documental sin archivado formal | Mantener CH-11 como completado manual, exigir evidencia verificable en CH-12 sin crear carpeta archivada retroactiva. | Bajo costo; trazabilidad SDD incompleta. | Preserva historial; documenta deuda. |
| O2 — Change de regularización prospectivo | Crear change futuro que documente/regularice evidencia y decisiones de CH-11 sin afirmar propose/apply original. | Costo medio; menor riesgo que inventar historial. | Mejora trazabilidad formal. |
| O3 — Excepción formal fechada (checklist 4.4) | Registrar excepción explícita al gate/archivo de CH-11 con responsable/fecha y evidencia mínima aceptada, y continuar CH-12 bajo esa excepción. | Bajo-medio; depende de aceptación interna. | Desbloquea flujo con trazabilidad explícita de la excepción. |

**Recomendación (pendiente de confirmar con Facundo y Andrés):** **O3 + nota de evidencia O1**. Excepción formal fechada al checklist 4.4 aceptada por el equipo (sin consultar cátedra: regla interna del equipo, no evaluada por el enunciado) combinada con registro de evidencia existente de CH-11 y sin inventar propose/archive retroactivo. CH-12 debe cerrarse solo con evidencia verificable.

## Nota de cierre checklist 4.5 (change sin cambios de código)

Este change no modifica `app/` ni `test/` ni ejecuta comportamiento de runtime; el repositorio no tiene suite de tests automatizada (tests son `.http`). El checklist 4.5 (“tests en verde”) se cierra documentalmente con evidencia de alcance/ausencia de cambios de código y salidas reales de git, no con ejecución de tests.

**Comando (re-ejecutado al cierre del apply):**
```powershell
git status --short
git diff --stat
git diff --name-only -- "openspec/changes/archive" app test
git status --short -- "openspec/changes/archive" app test
```
**Salida `git status --short` (re-ejecutada):**
```text
 M .active-orchestrator-state.json
 M AGENTS.md
 M CHANGES.md
 M CLAUDE.md
 M knowledge-base/10_preguntas_abiertas.md
?? openspec/changes/ch-14-rectificacion-active-stack/
```

**Salida `git diff --stat` (re-ejecutada):**
```text
 .active-orchestrator-state.json         |  4 ++--
 AGENTS.md                               |  2 +-
 CHANGES.md                              | 16 +++++++++++++++-
 CLAUDE.md                               |  2 +-
 knowledge-base/10_preguntas_abiertas.md |  2 ++
 5 files changed, 21 insertions(+), 5 deletions(-)
```

`git diff --name-only -- "openspec/changes/archive" app test` y `git status --short -- "openspec/changes/archive" app test` sin resultados (código de salida 0). **Confirmación:** `openspec/changes/archive/`, `app/` y `test/` no cambiaron.

**Hashes de identidad AGENTS/CLAUDE (re-ejecutado):** `4AEAB80F26D0B5E46F65DB65BA917DD1A604B89D8F07D90DC91D3C641B18C376` (ambos). No se cambió el texto "rectificación metodológica en curso" hasta archivar CH-14.

## Plan de trabajo del change (`/opsx:apply`)

- Mantener y aplicar los artefactos del change: `proposal.md`, `design.md`, `specs/casos-http-c/spec.md`, `tasks.md`.
- Resincronizar en `CHANGES.md` (ubicando por título de sección, conservando CRLF) la nota de CH-14 en “Rectificaciones” y la entrada `[CH-14]` según `tasks.md`.
- Actualizar `knowledge-base/10_preguntas_abiertas.md` pregunta (8) según `tasks.md`.
- Verificar que `AGENTS.md` y `CLAUDE.md` sigan idénticos (hash) y, al archivar CH-14, actualizar el estado CH-14 en ambos al estado real.
- Re-ejecutar la auditoría (B.1–B.8), actualizar el mapeo escenario→evidencia y comprobar que `archive/`, `app/` y `test/` no cambiaron.

## Risks / Trade-offs

- **[Riesgo] Guía ausente en repo** → referencias verificadas por el equipo contra su copia, no contra un archivo local.
- **[Riesgo] Sincronización futura de openspec/specs** → CH-13 está reflejado (B.3); el hash distinto entre delta y spec consolidada es esperable, no se detectó divergencia de contenido.
- **[Riesgo] Captura formal de C-07 pendiente** → conteos observados documentados; evidencia formal corresponde a CH-12.
- **[Riesgo] Brechas formales CH-10/CH-11** → recomendación registrada, decisión pendiente de Facundo y Andrés.
- **[Verificar] Ejecución histórica de `openspec validate`** (CH-04, CH-09, CH-13) sin salida conservada.
- **[Verificar] Cobertura de búsqueda de secretos** limitada al patrón de DSN con credencial usado.

## Open Questions

- **Pendiente de confirmar con Facundo y Andrés:** adopción de recomendación **O3 + nota O1** para brecha CH-11/CH-12.
- **[VERIFICAR]** Ejecución histórica real de `openspec validate` en CH-04, CH-09, CH-13.
- **[VERIFICAR]** Captura formal de consola para conteos C-07 (evidencia CH-12).
- **[VERIFICAR]** Búsqueda exhaustiva de secretos en archivados para formatos no cubiertos por el patrón usado.
- ¿Sincronizar `openspec/specs/clientes-perfil` y `libros-autorias` al contenido exacto/resultante esperado tras CH-13 en un change futuro? (fuera de alcance).
