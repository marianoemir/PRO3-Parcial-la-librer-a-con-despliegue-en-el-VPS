# Proposal: ch-16-mapa-casos-y-evidencia-c07

## Why

Durante la revisión de cierre de la entrega del parcial contra las consignas oficiales, se identificaron tres brechas documentales y operativas:
1. El archivo `test/ch07-ventas-exito.http` fue concebido durante el desarrollo temprano del módulo de ventas (CH-07) sobre una base auxiliar local con identificadores prefijados (`cliente_id=11`, libros 45–47, ventas 9, 11 y 12). Si un evaluador ejecuta ese archivo contra el dataset determinista final de 27 filas (CH-15), las peticiones fallan con errores 404 o 409, ya que dichos IDs no existen en el seed oficial. Se requiere un encabezado explicativo prominente que aclare su carácter histórico sin alterar sus peticiones.
2. El `README.md` carece de un mapa centralizado que relacione cada caso de prueba de la cátedra (C-01 a C-08) con su archivo `.http` ejecutable correspondiente y el rótulo exacto del request, indicando las precondiciones de ejecución (`python -m app.seed`).
3. El enunciado exige explícitamente para el caso C-07 demostrar una «cantidad fija de consultas, la misma con uno o con varios autores o renglones». La evidencia vigente (`evidencia/C-07-conteo.txt` de CH-15) compara dos ventas de 2 renglones cada una (`GET /ventas/1` y `GET /ventas/2`), pues la venta 1 del seed y la venta 2 creada por el POST del C-06 poseen ambas 2 renglones. No existe en la evidencia vigente una comparación directa entre una venta de 1 renglón y una de varios renglones (la única comparación 1 vs 3 renglones residía en la carpeta histórica `evidencia/ch-07-local/`).

Este change resuelve de forma no destructiva estas tres necesidades sin modificar los archivos de evidencia preexistentes de CH-15 ni la suite funcional.

## What Changes

1. **`test/ch07-ventas-exito.http`**:
   - Incorporación de un bloque de comentarios en el encabezado indicando que es un archivo HISTÓRICO de desarrollo de CH-07, que requiere una base con IDs específicos y no debe correrse contra el seed final.
   - Referenciación a los archivos vigentes donde se ejecutan los casos C-06 (`test/ch08-seed-datos-iniciales.http`) y C-07 (`test/ch09-c07-consultas-fijas.http`).
   - Sin alterar ningún request, URL, body ni aserción existente.
2. **`README.md`**:
   - Incorporación de una nueva sección «Casos de prueba» con una tabla mapeando cada caso (C-01 a C-08) hacia su archivo `.http` y rótulo exacto del request.
   - Incorporación del aviso de abrir con `http://` (no `https://`) justo debajo de la URL pública.
   - Notas operativas sobre el orden de ejecución y la necesidad de ejecutar `python -m app.seed` antes de los casos dependientes del dataset inicial.
   - Referenciación de los casos de despliegue D-01 a D-07 hacia `evidencia/LEEME.md`.
3. **Nueva evidencia de C-07 (venta de 1 renglón vs 2 renglones)**:
   - Creación de dos archivos nuevos en `evidencia/`: `C-07-ventas-un-renglon.log` (captura de consola de uvicorn con `SQL_ECHO=true`) y `C-07-ventas-un-renglon-conteo.txt` (resumen de conteo de SELECTs).
   - La captura la realiza Mariano en su entorno local sobre una base limpia `libreria_c16`, ejecutando el seed, el alta de una venta de 1 renglón (caso C-07d de `test/ch09-c07-consultas-fijas.http`, id 2) y consultando `GET /ventas/1` (2 renglones) y `GET /ventas/2` (1 renglón).
   - Se preservan intactos los archivos de CH-15 (`C-07-consola-sql.log` y `C-07-conteo.txt`).
4. **`evidencia/LEEME.md`**:
   - Actualización del índice para registrar los dos nuevos archivos de evidencia y explicar que allí se documenta la comparación de 1 renglón contra 2 renglones.
5. **`CHANGES.md` y gobernanza**:
   - Registro de la entrada `[CH-16]` con estado `[ ]` y actualización del árbol de dependencias.
   - Actualización de `.active-orchestrator-state.json` incrementando la revisión del roadmap e incorporando CH-16.

## Capabilities

### New Capabilities
- Ninguna.

### Modified Capabilities
- Ninguna.

*(Change estrictamente documental y de evidencia técnica; `skip_specs: true` configurado en `.openspec.yaml` al no alterar contratos de la API).*

## Impact

- **Código de aplicación (`app/`)**: Ninguno (fuera de alcance).
- **Contenedores y Docker (`Dockerfile`, `.dockerignore`)**: Ninguno.
- **Servidor y VPS**: Ninguno (la captura de evidencia se realiza en base local de prueba).
- **Tests y suites HTTP (`test/`)**: Modificación exclusiva de comentarios en el encabezado de `test/ch07-ventas-exito.http`.
- **Documentación y metadatos**: `README.md`, `evidencia/LEEME.md`, `evidencia/C-07-ventas-un-renglon*`, `CHANGES.md`, `.active-orchestrator-state.json`.
