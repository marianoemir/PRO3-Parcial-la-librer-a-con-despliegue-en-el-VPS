# Proposal: ch-17-cierre-docs

## Why

A 4 horas de la entrega formal del parcial, tras la revisión exhaustiva del 12/11/2026 y la incorporación de los changes CH-14, CH-15 y CH-16, se identificaron cuatro detalles estrictamente documentales que requieren cierre para dejar la entrega lista y sin marcas provisionales:
1. `DEPLOY.md` aún conserva la nota de la línea 5 y marcas provisionales `[A COMPLETAR]` en las secciones «Día y hora del despliegue» y «Entorno». Con el servidor ya confirmado (propio de un integrante del grupo, compartido con la materia Frontend para la calculadora) y el despliegue final estabilizado, estas marcas deben ser reemplazadas por texto definitivo para que no quede ninguna marca `[A COMPLETAR]` en `DEPLOY.md` ni en `README.md`.
2. En la suite de pruebas `test/ch09-c07-consultas-fijas.http` (encabezado `### C-07c`) y en la tabla de «Casos de prueba» de `README.md`, el rótulo de la petición C-07c conserva la referencia histórica `(creada en ch08 o venta 1 del seed)`. Dado que tras CH-15 y CH-16 la venta con dos renglones evaluada es unívocamente la venta 1 del seed determinista, el rótulo debe simplificarse a `(venta 1 del seed)` y coincidir carácter por carácter entre ambos archivos.
3. `AGENTS.md` y `CLAUDE.md` deben mantenerse idénticos (verificable con `Get-FileHash`), reflejando la evolución del roadmap de CH-01 a CH-16, consignando que CH-14, CH-15 y CH-16 están archivados el 2026-11-12 y que el único change abierto es CH-12 (con la tanda a mergeada y pendiente la tanda b del empaquetado zip).
4. El registro del ciclo de vida del proyecto requiere incorporar la entrada `[CH-17]` en `CHANGES.md`, actualizar el árbol de dependencias, la convención de códigos y elevar la revisión del roadmap en `.active-orchestrator-state.json` de 5 a 6 conservando terminaciones de línea CRLF estrictas (0 líneas sin CRLF).

Este change no modifica código de aplicación (`app/`), `Dockerfile`, la lógica de negocio ni reescribe artefactos archivados.

## What Changes

1. **`DEPLOY.md`**:
   - Eliminación de la nota inicial de la línea 5: `> Lo marcado **[A COMPLETAR]** se confirma al cerrar el despliegue final.`.
   - En «Día y hora del despliegue» («Despliegue vigente»), reemplazo de la marca provisional `**[A COMPLETAR: actualizar si se vuelve a recrear el contenedor]**` por la frase definitiva: `Si se vuelve a recrear el contenedor, esta hora se actualiza.`.
   - En «Entorno» (línea «Servidor»), reemplazo de la marca `**[A COMPLETAR: VPS asignado por la cátedra / propio del grupo]**` por la aclaración definitiva: `propio de un integrante del grupo (no lo asignó la cátedra). Ya se usaba para el proyecto de Frontend del grupo (la calculadora) y las dos materias comparten el servidor.`.
   - Verificación de que no quede ningún `A COMPLETAR` en `DEPLOY.md` ni en `README.md`.
2. **Rótulo de C-07c en `test/ch09-c07-consultas-fijas.http` y `README.md`**:
   - En `test/ch09-c07-consultas-fijas.http`, actualización del encabezado `### C-07c` para que diga textualmente: `### C-07c — detalle venta con dos renglones (venta 1 del seed)`.
   - En `README.md`, actualización de la fila correspondiente a C-07c en la tabla «Casos de prueba» con la misma cadena exacta: `### C-07c — detalle venta con dos renglones (venta 1 del seed)`.
   - Preservación sin modificación de los artefactos archivados de CH-16 que citan el rótulo histórico.
3. **Instrucciones para agentes (`AGENTS.md` y `CLAUDE.md`)**:
   - En el párrafo de «Roadmap de Changes», cambiar `CH-01 a CH-15` por `CH-01 a CH-16`.
   - Reemplazar la mención a los changes archivados y pendientes para declarar que CH-14, CH-15 y CH-16 están archivados el 2026-11-12 y que el único change abierto es CH-12 (tanda a mergeada; falta la tanda b, el zip), manteniendo el resto de la frase.
   - Asegurar que `AGENTS.md` y `CLAUDE.md` queden con hash SHA256 idéntico.
4. **Registro de gobernanza y trazabilidad (`CHANGES.md` y `.active-orchestrator-state.json`)**:
   - Agregar la entrada `[CH-17]` en `CHANGES.md` con Estado `[ ]` pendiente, dependencias (CH-16 ✓, CH-12 tanda a ✓), scope documental y enlaces de lectura previa.
   - Agregar `CH-17` en el árbol de dependencias y en la nota de convención de códigos.
   - En `.active-orchestrator-state.json`, actualizar `roadmap.revision` de 5 a 6 y agregar `"CH-17"` a la lista de `roadmap.changes`.
   - Mantener terminaciones CRLF estrictas en ambos archivos (0 líneas sin CRLF).

## Capabilities

### New Capabilities
- Ninguna.

### Modified Capabilities
- Ninguna.

*(Change estrictamente documental y de metadatos de entrega; `skip_specs: true` configurado en `.openspec.yaml` al no alterar requerimientos funcionales ni contratos de la API).*

## Impact

- **Código de aplicación (`app/`)**: Ninguno (fuera de alcance).
- **Contenedores y Docker (`Dockerfile`, `.dockerignore`)**: Ninguno.
- **Servidor y VPS**: Ninguno (se documenta el estado real existente del servidor).
- **Tests HTTP (`test/`)**: Actualización exclusiva de la línea de encabezado del caso C-07c en `test/ch09-c07-consultas-fijas.http`. No se modifican URLs, métodos, cuerpos ni aserciones.
- **Documentación y metadatos**: `DEPLOY.md`, `README.md`, `AGENTS.md`, `CLAUDE.md`, `CHANGES.md`, `.active-orchestrator-state.json`.
- **Artefactos archivados**: Ninguno (se respeta la regla de inmutabilidad de changes archivados).
