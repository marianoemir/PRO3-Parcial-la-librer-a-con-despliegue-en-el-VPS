# Proposal

## Why

CH-09 (`2026-11-11-ch-09-casos-http-c`) se archivó como change de verificación con `skip_specs: true` y sin carpeta `specs/`, por lo que la capability de los casos HTTP C-01 a C-08 no quedó especificada ni sincronizada en `openspec/specs/`. Además, la aplicación de la guía Active Stack/SDD quedó con evidencias parciales en artefactos archivados y en documentación del proyecto, sin una auditoría formal que distinguiera lo ya ocurrido (no corregible sin modificar historial archivado) de lo que puede rectificarse documentalmente.

Este change de rectificación metodológica agrega la spec faltante de CH-09 y deja trazada una auditoría basada en evidencia de herramienta y en los artefactos del repositorio, sin modificar código de la app, archivos `.http` ni contenido/estado de changes archivados.

## What Changes

- Agrega `specs/casos-http-c/spec.md` para la capability de los casos HTTP C-01 a C-08: `## Purpose`, `## ADDED Requirements`, escenarios verificables y atemporales con evidencias en `.http`/seed, referencias a artefactos existentes para C-05 y C-06 sin duplicarlos, y observaciones documentadas para C-07.
- Documenta en `design.md` la auditoría metodológica (B): inventario de artefactos archivados, conteo de escenarios y secciones de specs, sincronización y comparación por encabezados `### Requirement:` entre deltas CH-13 y `openspec/specs`, revisión de `tasks.md`, coherencia de estados, identidad de `AGENTS.md`/`CLAUDE.md`, estado de `.active-orchestrator-state.json` y búsqueda puntual de DSN con credencial en archivados; incluye tabla hallazgo→sección de guía, mapeo escenario→evidencia y opciones CH-11/CH-12.
- Define como trabajo del change (a ejecutar en `/opsx:apply` según `tasks.md`): resincronización acotada de `CHANGES.md`, actualización de `knowledge-base/10_preguntas_abiertas.md` pregunta (8), verificación de identidad `AGENTS.md`/`CLAUDE.md` y actualización de su estado CH-14 al archivar, y re-ejecución de la auditoría/mapeos/comprobaciones de no modificación de `archive/`, `app/` y `test/`.
- Registra la recomendación **O3 + nota de evidencia O1** para la brecha CH-11/CH-12 como propuesta pendiente de confirmación con Facundo y Andrés (regla interna de proceso, no del enunciado).

## Capabilities

### New Capabilities

- `casos-http-c`: especifica los casos de prueba HTTP C-01 a C-08 como requisitos verificables del contrato observable (validación, conflictos 409 propios, búsqueda segura y lectura con cantidad fija de consultas observable), referenciando artefactos `.http` existentes donde corresponde (C-05, C-06) y sin duplicarlos.

### Modified Capabilities

Ninguna. Este change no altera el comportamiento de la aplicación ni los contratos ya implementados; incorpora la spec faltante de CH-09 y documentación de auditoría/rectificación.

## Impact

- **Artefactos OpenSpec del change:** `openspec/changes/ch-14-rectificacion-active-stack/proposal.md`, `design.md`, `specs/casos-http-c/spec.md`, `tasks.md`.
- **Trabajo documentado para `/opsx:apply` (no aplicado en este change de planificación):** ediciones acotadas en `CHANGES.md`, `knowledge-base/10_preguntas_abiertas.md` y actualización de estado CH-14 en `AGENTS.md`/`CLAUDE.md` al archivar (manteniéndolos idénticos), según `tasks.md`.
- **Sin impacto en runtime:** no modifica `app/`, `Dockerfile`, `.dockerignore`, `requirements.txt`, `test/*.http`, ni changes archivados.
- **Evidencia y referencias:** auditoría basada en salida real de herramientas y en artefactos del repositorio. `GUIA-active-stack-sdd.md` no está dentro del repo; las referencias a sus secciones fueron verificadas por el equipo contra su copia.
- **Fuera de alcance:** `/opsx:apply`, corrección retroactiva de artefactos archivados, creación de `.openspec.yaml` faltantes en archivados, sincronización masiva de `openspec/specs/`, y cualquier cambio de código o datos.
