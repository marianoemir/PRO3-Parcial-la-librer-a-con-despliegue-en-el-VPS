# Design: ch-17-cierre-docs

## Context

Faltan 4 horas para la entrega formal del trabajo práctico integrador (Parcial Programación III). Tras la revisión del 12/11/2026 y la aprobación y archivo de los changes CH-14, CH-15 y CH-16, se revisaron los documentos de entrega. Se detectaron marcas provisionales pendientes (`[A COMPLETAR]`) en `DEPLOY.md`, una discordancia en el rótulo de la prueba C-07c entre `test/ch09-c07-consultas-fijas.http` y `README.md`, y la necesidad de sincronizar el estado del roadmap en `AGENTS.md`, `CLAUDE.md`, `CHANGES.md` y `.active-orchestrator-state.json`.

Ver motivación detallada en `proposal.md`.

## Goals / Non-Goals

**Goals:**
- Eliminar de forma completa y definitiva todas las marcas `[A COMPLETAR]` en `DEPLOY.md` y verificar que tampoco existan en `README.md`.
- Documentar en `DEPLOY.md` que el servidor VPS es propio de un integrante del grupo (no asignado por la cátedra), compartido con el proyecto de Frontend (la calculadora).
- Actualizar el encabezado de la prueba C-07c en `test/ch09-c07-consultas-fijas.http` a `### C-07c — detalle venta con dos renglones (venta 1 del seed)` y reflejar idéntica cadena en la tabla «Casos de prueba» de `README.md`.
- Actualizar `AGENTS.md` y `CLAUDE.md` manteniendo identidad estricta de hash SHA256 (`Get-FileHash`), incorporando CH-16 como archivado junto a CH-14 y CH-15 el 2026-11-12, y aclarando que CH-12 es el único change abierto (tanda a mergeada, tanda b del zip pendiente).
- Registrar formalmente `[CH-17]` en `CHANGES.md` y actualizar `.active-orchestrator-state.json` (revisión 5 → 6), conservando terminación de línea CRLF estricta en ambos archivos.

**Non-Goals:**
- Tocar el código fuente de la aplicación en `app/` (fuera de alcance).
- Modificar el archivo `Dockerfile`, `.dockerignore` o la configuración de despliegue real en el VPS.
- Reescribir o modificar artefactos de changes previamente archivados (CH-14, CH-15, CH-16 o anteriores). En particular, no modificar el `tasks.md` archivado de CH-16 que cita el rótulo histórico de C-07c.
- Leer o editar el archivo local `.env` (regla estricta de seguridad SU-03).
- Ejecutar la fase de aplicación (`/opsx:apply`).

## Decisions

### 1) Justificación de un change específico (CH-17) en lugar de enmendar changes archivados
- **Decisión**: Crear un change independiente de cierre documental (`ch-17-cierre-docs`) en vez de reabrir o editar los artefactos archivados de CH-16 o anticipar la tanda b de CH-12.
- **Justificación**:
  1. *Regla de inmutabilidad de artefactos archivados*: En la metodología Active Stack / OPSX, una vez que un change ha sido verificado y archivado (`openspec/changes/archive/`), su contenido queda congelado como registro histórico inmutable de auditoría. CH-16 cumplió su alcance de trazabilidad de C-07 y mapa de casos y fue archivado formalmente.
  2. *Separación de responsabilidades con CH-12*: CH-12 («evidencia-entrega») tiene dividida su ejecución en dos tandas; la tanda a ya fue mergeada y la tanda b está reservada para la verificación final del empaquetado `.zip` justo antes de subir a la plataforma. Mezclar ajustes de texto en `DEPLOY.md`, sincronización de rótulos de tests y actualización de instrucciones de agentes dentro de CH-12 oscurecería el propósito de cada change y diluiría la trazabilidad a pocas horas de la entrega.
  3. *Trazabilidad de decisiones de entrega*: Registrar los detalles finales de entrega en su propio change proporciona evidencia explícita de revisión previa a la entrega final.
- **Alternativas consideradas**:
  - *Editar retrospectivamente los archivos archivados de CH-16*: Rechazada de plano por violar el principio de inmutabilidad y falsear la historia de auditoría de Git y OpenSpec.
  - *Incluirlo como parte no planificada de la tanda b de CH-12*: Rechazada porque la tanda b está acotada estrictamente a la verificación y empaquetado del archivo comprimido (`.zip`), sin secretos y sin dependencias espurias.

### 2) Unificación y simplificación del rótulo C-07c
- **Decisión**: Sustituir `(creada en ch08 o venta 1 del seed)` por `(venta 1 del seed)` en `test/ch09-c07-consultas-fijas.http` (línea 54) y en la tabla de `README.md` (línea 81).
- **Justificación**: Tras la aplicación de CH-15, el seed oficial genera deterministamente la venta 1 con 2 renglones en la base de datos. La mención a «creada en ch08» correspondía a etapas tempranas de desarrollo donde el seed se ejecutaba desde ch08 de forma incremental. Mantener una referencia dual genera confusión al corrector docente. La nueva cadena es unívoca y exacta.
- **Alternativas consideradas**:
  - *Conservar el rótulo histórico*: Rechazada porque mantiene ambigüedad respecto al origen del registro evaluado.

### 3) Eliminación total de marcas provisionales en DEPLOY.md
- **Decisión**: Retirar la nota de la línea 5 y sustituir las marcas `[A COMPLETAR]` por los datos definitivos confirmados: la propiedad del VPS (servidor propio de Mariano Chirino, compartido con el proyecto de la calculadora de Frontend) y la política de actualización horaria del contenedor si se recrea.
- **Justificación**: Los documentos de entrega final no deben contener marcas de trabajo en progreso (`TODO`, `A COMPLETAR`, etc.), ya que denotan entrega incompleta ante la evaluación docente.
- **Alternativas consideradas**:
  - *Dejar las marcas hasta el momento exacto de empaquetar el zip*: Rechazada por riesgo de olvido a 4 horas de la entrega.

### 4) Mantenimiento de identidad binaria entre AGENTS.md y CLAUDE.md
- **Decisión**: Modificar ambos archivos de forma estrictamente idéntica, verificando mediante `Get-FileHash` que sus sumas de verificación SHA256 coincidan exactamente.
- **Justificación**: Es una regla dura del proyecto documentada en las reglas duras de `AGENTS.md` y `CLAUDE.md`: «AGENTS.md y CLAUDE.md idénticos; si se cambia uno, se actualiza el otro.»

## Verifiable Scenarios

### Escenario 1 (Esperado — Ausencia total de marcas provisionales en DEPLOY.md y README.md)
- **DADO** los archivos `DEPLOY.md` y `README.md` tras aplicar el change
- **CUANDO** se busca la cadena "A COMPLETAR" con `Select-String` en ambos archivos
- **ENTONCES** no se encuentra ninguna coincidencia (0 ocurrencias) y el texto de `DEPLOY.md` describe con precisión el servidor propio compartido y la indicación de actualización horaria.

### Escenario 2 (Borde / Consistencia — Coincidencia estricta de rótulo C-07c)
- **DADO** la suite `test/ch09-c07-consultas-fijas.http` y la sección «Casos de prueba» de `README.md`
- **CUANDO** se extrae el encabezado de `C-07c` en ambos archivos
- **ENTONCES** ambos contienen exactamente el texto `### C-07c — detalle venta con dos renglones (venta 1 del seed)` carácter por carácter, sin diferencias, y los archivos archivados de CH-16 permanecen inalterados.

### Escenario 3 (Error si falla — Identidad estricta y sincronización de AGENTS.md y CLAUDE.md)
- **DADO** los archivos `AGENTS.md` y `CLAUDE.md`
- **CUANDO** se computa `Get-FileHash` sobre ambos y se busca la mención de "CH-16"
- **ENTONCES**:
  1. El hash SHA256 de `AGENTS.md` es exactamente idéntico al de `CLAUDE.md`.
  2. Ambos archivos mencionan «CH-01 a CH-16».
  3. Ambos archivos señalan que CH-14, CH-15 y CH-16 están archivados el 2026-11-12 y que CH-12 es el único change abierto (tanda a mergeada; falta la tanda b, el zip).
  4. Si los hashes difieren o alguno no menciona CH-16, la verificación falla.

## Risks / Trade-offs

- **[Riesgo de terminación de línea LF accidental en Windows]** → Mitigación: Los scripts y tareas de verificación incluyen chequeo explícito en Python para certificar 0 líneas sin CRLF tanto en `CHANGES.md` como en `.active-orchestrator-state.json`.
- **[Riesgo de divergencia entre AGENTS.md y CLAUDE.md]** → Mitigación: Verificación obligatoria con `Get-FileHash` tras la edición.
