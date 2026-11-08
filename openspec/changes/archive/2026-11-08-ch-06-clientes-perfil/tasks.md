# Tasks

## 1. Contratos del módulo (≤ 1 hora)

- [x] 1.1 Definir en `app/modules/clientes/schemas.py` los DTO `ClienteCreate`, `ClienteUpdate`, `ClienteRead`, `PerfilCreate`, `PerfilRead` y `VentaResumenRead` con el contrato exacto de `design.md`: todos los Create/Update rechazan extras, `ClienteCreate` rechaza `id`, `PerfilCreate` rechaza `cliente_id`, PATCH rechaza `{}` y `null` explícito para sus campos, y el resumen declara `fecha: datetime`, `total: Decimal` y no renglones; verificar con el esquema OpenAPI local que cada ruta publica el body y response model previstos.
- [x] 1.2 Aplicar validaciones de cuerpo y de query para el PATCH y el listado de ventas (`limit` 1–100, default 20; `offset >= 0`); verificar con solicitudes manuales inválidas que campos extra, `id`/`cliente_id` prohibidos, `nombre`/`email` nulos y `{}` en PATCH responden 422 sin ejecutar escrituras.

## 2. Servicios de clientes y perfil (≤ 2 horas)

- [x] 2.1 Implementar en `app/modules/clientes/service.py` alta y PATCH de cliente con `exclude_unset`, recarga con `joinedload(Cliente.perfil)`, rollback y traducción propia de `uq_cliente_email`; verificar localmente alta 201, duplicado de email 409 sin texto interno y PATCH inexistente 404.
- [x] 2.2 Implementar la lectura individual con `joinedload(Cliente.perfil)` y el mapeo de perfil singular o nulo; verificar con `SQL_ECHO=true` que obtener un cliente con y sin perfil responde 200 sin una carga perezosa posterior.
- [x] 2.3 Implementar el alta de perfil: comprobar el padre de ruta para 404, tomar `cliente_id` solo del path e insertar sin consulta previa de perfil; traducir `uq_perfil_cliente_cliente_id` a 409 propio y una FK de carrera a 409 propio; verificar localmente 201, 404 de cliente ausente y C-03 (segundo perfil → 409).
- [x] 2.4 Implementar el listado paginado de ventas del cliente mediante una consulta plana de `Venta`, con `ORDER BY Venta.id` antes de offset/limit y sin tocar `renglones`; verificar con `SQL_ECHO=true` respuestas 200 estables con lista vacía y con ventas, ausencia de `renglones`, `fecha`/`total` tipados como contrato, límites/offset válidos y 422 fuera de rango.

## 3. Rutas e integración (≤ 1 hora)

- [x] 3.1 Implementar en `app/modules/clientes/router.py` las cinco rutas de referencia como `async def`, con router delgado, sesión por dependencia, response models y códigos 201/200/404/409/422 definidos en la spec; verificar `python -m compileall app/modules/clientes` y la documentación OpenAPI local.
- [x] 3.2 Registrar únicamente el router de clientes en `app/main.py`, sin modificar otros routers o modelos; verificar que la aplicación arranca y que las cinco rutas aparecen en `/openapi.json`.

## 4. Verificación del change (≤ 1 hora)

- [x] 4.1 Ejecutar contra una base local los escenarios de `specs/clientes-perfil/spec.md` y guardar las salidas reales de consola/curl para la revisión: alta, campos extra prohibidos sin escritura, email repetido, PATCH parcial y `{}` → 422 sin cambio, perfil 201/404/409, detalle con perfil/null y ventas paginadas por `Venta.id` sin renglones; no crear archivos `test/*.http`, porque CH-09 es su dueño.
- [x] 4.2 Revisar el diff del módulo contra RN-02, RN-09, RN-12 y RT-02/RT-04/RT-05: confirmar que no hay DELETE, SQL en router, lazy loading, texto interno de base ni cambios de modelos; verificar el checklist antes de solicitar revisión de Facundo.

## Workflow follow-up

- Solicitar la revisión de Facundo según `docs/DIVISION-DEL-EQUIPO (1).md`; no commitear ni archivar sin pedido explícito y sin que cada escenario de la spec esté verificado.
- Tras la implementación y revisión, ejecutar `/openspec-archive-change` para `ch-06-clientes-perfil` y recién entonces actualizar el estado de CH-06 en `CHANGES.md`.
