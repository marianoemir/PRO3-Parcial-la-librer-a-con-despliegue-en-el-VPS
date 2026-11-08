# Proposal

## Why

La API ya dispone del modelo relacional de clientes, perfiles y ventas, pero todavía no expone los contratos ni las operaciones para registrar y mantener clientes ni consultar su perfil o sus compras. Este change habilita la parte de clientes de US-003 y deja a CH-07 una dependencia funcional resuelta para registrar ventas.

## What Changes

- Incorporar el comportamiento HTTP de clientes: alta, consulta individual y actualización parcial con contratos `Create`, `Update` y `Read` separados.
- Incorporar la creación de un perfil uno a uno usando el `cliente_id` de la ruta y las respuestas propias para duplicados de email (RN-02) y segundo perfil (RN-09), sin filtrar internals de la base (RN-12).
- Exponer la consulta de ventas de un cliente con un resumen que no incluya renglones y con paginación de RN-10.
- Precargar explícitamente el perfil del cliente y aplicar la estrategia de carga anticipada correspondiente a las ventas, sin carga perezosa (RT-04).
- Mantener todos los handlers asíncronos, delegar SQL y errores de base al service, y usar parámetros ligados (RT-02, RT-05).

## Capabilities

### New Capabilities
- `clientes-perfil`: gestión de clientes, su perfil uno a uno y el resumen paginado de sus ventas mediante las rutas de referencia.

### Modified Capabilities
- Ninguna.

## Impact

- **Código afectado:** `app/modules/clientes/schemas.py`, `service.py` y `router.py`; los modelos `Cliente` y `PerfilCliente` ya fueron publicados por CH-02 y no se modifican en este change. La incorporación del router en `app/main.py` se limita a su línea de registro, según la coordinación del equipo.
- **API:** `POST /clientes/`, `GET` y `PATCH /clientes/{id}`, `POST /clientes/{id}/perfil` y `GET /clientes/{id}/ventas`.
- **Reglas y casos cubiertos:** RN-02, RN-09, RN-12; RT-02, RT-04 y RT-05; casos C-02 (email repetido) y C-03 (segundo perfil). Los archivos de prueba `.http` pertenecen exclusivamente a CH-09.
- **Fuera de alcance:** no se crean DELETE de clientes o perfiles (pendiente Q5 de `knowledge-base/10_preguntas_abiertas.md`), no se alteran modelos/tablas, no se crean renglones ni rutas de ventas, y no se agrega PATCH o DELETE de ventas.
