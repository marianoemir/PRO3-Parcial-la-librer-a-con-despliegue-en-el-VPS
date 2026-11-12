# Proposal

## Why

El seed actual (`app/seed.py`) deja el ISBN `978-950-00-0006-6` ocupado por el libro 6 y al cliente 2 como "Bruno Díaz" (`bruno.diaz@example.com`), por lo que los ejemplos JSON del enunciado (`POST /libros/` con ese ISBN y `POST /ventas/` con cliente 2 "Tomás Ríos" `tomas@example.com`, libros 1×2 y 4×1, respuesta esperada id 2 y total `"77000.00"`) chocan con el estado sembrado (409/conflicto de identidad). Además, el mecanismo idempotente basado en `INSERT ... ON CONFLICT DO NOTHING` no garantiza un estado conocido cuando ya existen datos posteriores: una venta o un libro creados después sobreviven a la reejecución. Este change alinea el dataset con los ejemplos del enunciado y hace que el seed deje siempre el mismo estado inicial reproducible. CH-08 está archivado y no se reescribe.

## What Changes

- Actualiza el dataset determinista del seed para que sea fiel a los ejemplos del enunciado: se elimina el libro 6 y sus dos autorías; el cliente 2 pasa a "Tomás Ríos" (`tomas@example.com`); la venta 1 y sus renglones se conservan para que el alta de venta del ejemplo reciba el id 2. El estado esperado queda en 27 filas (2 editoriales, 2 géneros, 5 autores, 5 libros, 5 autorías, 3 clientes, 2 perfiles, 1 venta, 2 renglones). Son datos del implementador, no reglas.
- Cambia la estrategia de carga para garantizar estado conocido y reiniciable: vaciado y recarga en una misma transacción (`TRUNCATE` de las 9 tablas del proyecto nombradas explícitamente con `RESTART IDENTITY CASCADE`, seguido de inserción y alineación de secuencias). Si falla cualquier paso, se revierte toda la transacción, incluido el vaciado.
- Resuelve el choque de creación del libro del ejemplo (ISBN `978-950-00-0006-6`) estableciendo que se crea una sola vez dentro del ciclo limpio (en `test/ch09-c07-consultas-fijas.http`), mientras que `test/ch08-seed-datos-iniciales.http` verifica el estado sembrado y ejecuta la venta del ejemplo (201, id 2, total "77000.00").
- Ajusta los contratos de spec `datos-iniciales` y `casos-http-c` (deltas ADDED, MODIFIED y REMOVED) para reflejar el nuevo dataset, la repetibilidad por reinicio y los escenarios mínimos requeridos.
- Ajusta solo los artefactos `.http` que dependen del libro 6 o de "Bruno Díaz" (`test/ch07-ventas-errores.http`, `test/ch08-seed-datos-iniciales.http`, `test/ch09-casos-http-c.http`, `test/ch09-c07-consultas-fijas.http`), preservando el orden obligatorio de los casos y asegurando que C-02b use `tomas@example.com` para provocar 409 por email duplicado.
- Actualiza la sección "Datos iniciales (seed)" de `README.md` y las menciones relevantes del seed en `DEPLOY.md` (nuevo dataset, comando, y advertencia visible de que el seed borra las 9 tablas sin confirmación previa y resetea lo que haya en la base).
- Define los pasos manuales de actualización en el VPS en orden: `git pull`, `docker build`, recrear contenedor con `docker run` (con la misma red y `.env`), esperar `healthy`, ejecutar `docker exec libreria python -m app.seed`, actualizar hora en `DEPLOY.md` y rehacer D-03, D-04 y D-07.
- Actualiza el roadmap/estado documental: agrega `[CH-15]` en `CHANGES.md` (estado, scope, dependencias CH-08 y CH-09, governance MEDIO, "Leer antes"), ajusta la línea de convención (CH-15 es change propio, no rectificación), actualiza el árbol para que CH-12 dependa también de CH-15, agrega nota fechada, conserva CRLF editando solo las líneas necesarias; sube `roadmap.revision` de 3 a 4 y agrega CH-15 en `.active-orchestrator-state.json`. `AGENTS.md` y `CLAUDE.md` permanecen idénticos (sin corregir el arranque "CH-01 a CH-13", responsabilidad de CH-12).
- Registra en `knowledge-base/10_preguntas_abiertas.md` que "el ejemplo de `POST /libros/` crea el sexto libro" es una inferencia del equipo y no algo afirmado por el PDF (responsable: Equipo). El seed sigue sin descontar stock.

## Capabilities

### New Capabilities

_(ninguna — el change modifica capacidades existentes)_

### Modified Capabilities

- `datos-iniciales`: cambia el dataset (5 libros/5 autorías, cliente 2 "Tomás Ríos", 27 filas), el criterio de repetibilidad (vaciar y recargar en transacción para estado conocido) y las expectativas de resumen/errores asociadas al nuevo comportamiento.
- `casos-http-c`: actualiza precondiciones/fixtures y expectativas que dependían del libro 6 o de "Bruno Díaz" (C-02a, C-02b y C-07), manteniendo la cobertura C-01..C-08 y la verificación de conteos fijos en C-07.

## Impact

- Código de seed: `app/seed.py` (dataset, estrategia de carga atómica por `TRUNCATE` + inserción, alineación de secuencias y mensajes de consola propios sin secretos/internals).
- Verificación HTTP: `test/ch07-ventas-errores.http`, `test/ch08-seed-datos-iniciales.http`, `test/ch09-casos-http-c.http`, `test/ch09-c07-consultas-fijas.http` (solo lo dependiente del libro 6 o de Bruno Díaz; orden de C-01..C-08 preservado).
- Documentación: `README.md` (solo sección "Datos iniciales (seed)"), `DEPLOY.md`, `CHANGES.md`, `.active-orchestrator-state.json`, `knowledge-base/10_preguntas_abiertas.md`.
- Specs del change: `openspec/changes/ch-15-seed-fiel-enunciado/specs/datos-iniciales/spec.md`, `openspec/changes/ch-15-seed-fiel-enunciado/specs/casos-http-c/spec.md`.
- Fuera de alcance: routers, services y models de la API; `Dockerfile`; el VPS. El reseteo del VPS y rehacer D-03, D-04 y D-07 quedan como tareas manuales finales en `tasks.md` (responsable Mariano, con verificación indicada).
- Referencias cubiertas (RN/RT/C/D): RN-06, RN-07, RN-11, RN-12, RT-02, RT-04, RT-05; casos C-01 a C-08 (regresión, con C-07 de consultas fijas); D-03/D-04/D-07 como pasos manuales posteriores en VPS (no ejecutados en este change). Las dudas no resueltas por el enunciado (descuento de stock, lista cerrada de seed, y la inferencia del "sexto libro" del ejemplo de `POST /libros/`) se registran/citan como preguntas abiertas, no como reglas.
