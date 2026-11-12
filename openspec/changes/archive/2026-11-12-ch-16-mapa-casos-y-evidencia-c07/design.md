# Design: ch-16-mapa-casos-y-evidencia-c07

## Context

El proyecto cuenta con la implementación completa de endpoints, pruebas automáticas `.http` y despliegue en VPS. Durante la revisión final previa a la entrega se detectaron aspectos que facilitan la evaluación docente y perfeccionan el cumplimiento estricto del enunciado:
1. El enunciado del parcial en el caso C-07 exige verificar que las consultas no presenten problema de N+1 y mantengan una cantidad fija tanto con uno como con varios autores o renglones. El log consolidado en CH-15 verificó autores (1 vs 2 autorías en libros) y ventas de 2 renglones (venta 1 del seed y venta 2 creada con 2 renglones), pero carecía de una venta de 1 renglón bajo el dataset final.
2. `test/ch07-ventas-exito.http` fue un archivo de trabajo local de CH-07 y depende de IDs que no coinciden con el seed final de 27 filas.
3. El `README.md` no contaba con un índice directo que guíe al corrector sobre qué archivo `.http` y qué request corresponde a cada caso C-01 a C-08.

## Goals / Non-Goals

**Goals:**
- Agregar un encabezado de advertencia histórica claro en `test/ch07-ventas-exito.http` sin alterar ninguna petición existente.
- Proveer en `README.md` una tabla exhaustiva Caso -> Archivo -> Rótulo exacto de request para C-01 a C-08, con notas de precondiciones (`app.seed`) y remisión de los casos D hacia `evidencia/LEEME.md`.
- Generar y registrar evidencia nueva complementaria de C-07 (`evidencia/C-07-ventas-un-renglon.log` y `evidencia/C-07-ventas-un-renglon-conteo.txt`) comparando una venta de 1 renglón frente a una de 2 renglones sobre una base local limpia, sin alterar los archivos de evidencia existentes de CH-15.
- Documentar en `evidencia/LEEME.md` la existencia y propósito de la nueva evidencia complementaria.
- Registrar el change en `CHANGES.md` (respetando CRLF) y en `.active-orchestrator-state.json`.

**Non-Goals:**
- Modificar el código fuente en `app/`.
- Reescribir o mover `test/ch07-ventas-exito.http` (rompería referencias en el `tasks.md` archivado de CH-07).
- Sobrescribir o alterar los archivos de evidencia consolidados de CH-15 (`C-07-consola-sql.log` y `C-07-conteo.txt`).
- Tocar el contenedor o la base de datos de producción en el VPS.

## Decisions

### 1) Creación de archivos nuevos para la evidencia de 1 renglón (sin editar CH-15)
- **Decisión**: Crear `evidencia/C-07-ventas-un-renglon.log` y `evidencia/C-07-ventas-un-renglon-conteo.txt` en lugar de sobrescribir `C-07-consola-sql.log` y `C-07-conteo.txt`.
- **Justificación**:
  1. *Inmutabilidad de evidencia aprobada*: Los archivos `C-07-consola-sql.log` y `C-07-conteo.txt` corresponden a la corrida integral de verificación del change CH-15, debidamente auditada y referenciada en la documentación de entrega de CH-12. Modificarlos invalidaría los timestamps y la correspondencia con los commits previos.
  2. *Claridad acumulativa*: Mantener ambos conjuntos de archivos permite al docente observar tanto la verificación integral de libros y ventas del seed (`C-07-consola-sql.log`), como la prueba focalizada complementaria de 1 renglón vs 2 renglones (`C-07-ventas-un-renglon.log`).
- **Alternativas rechazadas**:
  - *Sobrescribir los archivos de CH-15*: Destruiría la evidencia integral previa de libros (1 vs 2 autorías) y altas de venta de 2 renglones.
  - *No generar evidencia de 1 renglón*: Dejaría abierta la observación formal de que ambas ventas evaluadas en CH-15 tenían 2 renglones.

### 2) Encabezado en `test/ch07-ventas-exito.http` sin renombrar ni mover el archivo
- **Decisión**: Incorporar un bloque de comentarios inicial de advertencia en `test/ch07-ventas-exito.http`, dejando intacto el nombre, la ruta y todas las peticiones del archivo.
- **Justificación**:
  1. *Trazabilidad de artefactos archivados*: El archivo `tasks.md` archivado de CH-07 (`openspec/changes/archive/2026-11-11-ch-07-ventas-renglones/tasks.md:27`) cita textualmente `test/ch07-ventas-exito.http`. Moverlo o renombrarlo rompería los enlaces de auditoría histórica del repositorio.
  2. *Prevención de errores en evaluación*: Al abrir el archivo, cualquier evaluador verá de inmediato que se trata de una suite histórica de desarrollo y encontrará la referencia explícita hacia los archivos vigentes (`ch08-seed-datos-iniciales.http` para C-06 y `ch09-c07-consultas-fijas.http` para C-07).
- **Alternativas rechazadas**:
  - *Mover a una subcarpeta histórica*: Rompería la ruta fija citada en el change archivado CH-07.
  - *Reescribir las peticiones para adaptarlas al seed final*: Destruiría el registro de cómo se probó originalmente el módulo de ventas en CH-07.

### 3) Ejecución de la captura de evidencia por Mariano
- **Decisión**: Las tareas de captura de consola de uvicorn y conteo SQL las ejecuta Mariano en su terminal local sobre una base de prueba aislada (`libreria_c16`), y el agente las integra y verifica en los artefactos.
- **Justificación**: Cumple con la regla dura de que el agente no arranca servidores en background ni manipula bases de datos locales por fuera de las herramientas autorizadas, garantizando salidas de consola 100% reales.

## Verifiable Scenarios

### Escenario 1 (Esperado — Consultas fijas en venta de 1 renglón vs 2 renglones)
- **DADO** una base de datos recién sembrada con `python -m app.seed` y una venta auxiliar creada con 1 renglón (C-07d de `test/ch09-c07-consultas-fijas.http`)
- **CUANDO** se consulta el detalle de la venta de 2 renglones (`GET /ventas/1`) y el detalle de la venta de 1 renglón (`GET /ventas/2`)
- **ENTONCES** ambas peticiones generan exactamente 2 consultas SELECT cada una (`SELECT=2`), y la evidencia queda registrada íntegra en `evidencia/C-07-ventas-un-renglon.log` y `evidencia/C-07-ventas-un-renglon-conteo.txt`.

### Escenario 2 (Error — Prevención de confusión en test/ch07-ventas-exito.http)
- **DADO** el archivo `test/ch07-ventas-exito.http`
- **CUANDO** un usuario o evaluador abre el archivo
- **ENTONCES** las primeras líneas contienen un aviso explícito de que el archivo es histórico de desarrollo y no corre sobre el seed final, redirigiendo a los archivos ejecutables vigentes y previniendo ejecuciones fallidas con 404/409.

### Escenario 3 (Borde / Consistencia — Integridad del mapa en README.md)
- **DADO** la tabla de «Casos de prueba» incorporada en `README.md`
- **CUANDO** se verifican los rótulos documentados contra los archivos `.http` del repositorio
- **ENTONCES**:
  1. C-05 apunta a `test/ch07-ventas-errores.http`.
  2. C-06 apunta a `test/ch08-seed-datos-iniciales.http` (sin duplicar con ch07).
  3. C-07 apunta a `test/ch09-c07-consultas-fijas.http`.
  4. Ningún rótulo de la tabla apunta a un request inexistente en `test/`.

## Risks / Trade-offs

- **[Riesgo de arranque de base/seed]** → Mitigación: El seed exige el esquema creado: uvicorn arranca primero.
- **[Riesgo de divergencia en conteo de consultas]** → Mitigación: El procedimiento de captura exige ejecutar `python -m app.seed` inmediatamente antes del alta auxiliar, asegurando que la venta de 1 renglón obtenga `id: 2` de forma limpia y determinista.
