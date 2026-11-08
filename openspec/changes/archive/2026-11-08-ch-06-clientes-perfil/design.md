# Design

## Context

CH-02 ya publica `Cliente`, `PerfilCliente` y sus constraints nombrados; los tres archivos del módulo `clientes` son stubs. Esta propuesta implementa la capacidad definida en `specs/clientes-perfil/spec.md`; su motivación está en `proposal.md`.

El módulo sigue la estructura obligatoria: el router declara rutas, DTO y códigos; el service recibe la sesión asíncrona, ejecuta las consultas/escrituras y traduce errores. No se modifican tablas ni modelos. `app/main.py` recibe solamente el registro del router por parte del dueño del change, conforme a `docs/DIVISION-DEL-EQUIPO (1).md`.

## Goals / Non-Goals

**Goals:**
- Mantener contratos de entrada y salida explícitos, sin exponer modelos de tabla ni campos que el cliente no debe enviar.
- Resolver 404, 409 y 422 de forma predecible y sin texto interno de PostgreSQL.
- No acceder a relaciones sin una estrategia de carga anticipada declarada.

**Non-Goals:**
- No crear ni alterar `models.py`, constraints, migraciones, datos de seed o archivos `test/*.http`.
- No crear bajas, renglones, ni rutas PATCH/DELETE para ventas; CH-07 posee la creación y detalle de ventas con renglones, y CH-09 los casos HTTP.
- No resolver ni ampliar la pregunta Q5; se mantiene como limitación pendiente/confirmable de la cátedra.

## Decisions

### D1 — Contratos de respuesta y PATCH parcial

`ClienteCreate` contiene `nombre` y `email`; `ClienteUpdate` declara esos mismos campos como omitibles y el service aplica solo `exclude_unset`. Todo DTO de entrada `Create` o `Update` del módulo configura el equivalente compatible de Pydantic a `extra="forbid"`: rechaza con 422 cualquier campo no declarado. Así, `ClienteCreate` rechaza expresamente un `id` suministrado y `PerfilCreate` rechaza un `cliente_id` suministrado. Además, el PATCH requiere al menos un campo declarado: un cuerpo `{}` se rechaza con 422 antes de llegar al service y no escribe cambios. Si `nombre` o `email` se incluyen explícitamente, su valor debe ser un string; `null` se rechaza con 422 en el DTO antes de alcanzar el service o escribir. `PerfilCreate` contiene `telefono` y `direccion`, sin `id` ni `cliente_id`. `PerfilRead` expone `id`, `cliente_id`, `telefono` y `direccion`; `ClienteRead` expone `id`, `nombre`, `email` y `perfil: PerfilRead | None`. `VentaResumenRead` expone exactamente `id`, `cliente_id`, `fecha: datetime` y `total: Decimal`; deliberadamente excluye `renglones`, libros y relaciones anidadas, y nunca representa dinero como `float`.

**Justificación:** satisface el PDF/Ejercicio 3, evita que el cuerpo asigne la relación de perfil y evita aceptar silenciosamente entradas no contractuales. La validación de PATCH vacío preserva la semántica de actualización parcial como cambio efectivo; distinguir un campo omitido de `null` explícito evita que un valor inválido alcance la escritura. El resumen de ventas evita invadir el detalle de CH-07, conserva `fecha` tipada y el dinero exacto con `Decimal`, y no activa relaciones no necesarias.

**Alternativas descartadas:** reutilizar los modelos de tabla como DTO (acopla persistencia y expone campos); permitir extras por el comportamiento predeterminado del validador (acepta silenciosamente entradas prohibidas); interpretar `{}` como PATCH sin efecto (oculta un body inválido); incluir `cliente_id` en `PerfilCreate` (permite contradicción con la ruta); representar `total` como `float` (pierde exactitud monetaria); devolver renglones en ventas (fuera de alcance y carga innecesaria).

### D2 — Cliente inexistente al crear perfil: 404 por lectura de padre, 409 para rechazos de escritura

El service verificará que el cliente del path exista antes de crear su perfil y devolverá 404 propio si no existe. Esta es una excepción estrecha y justificada a la regla general RT-02/DD-04: la tabla de endpoints prescribe explícitamente 404 para `POST /clientes/{id}/perfil`, por lo que no se puede distinguir públicamente el padre ausente con un único `INSERT` que produciría una FK/`IntegrityError` traducida a 409.

La lectura se limita a identificar el recurso de ruta que define el contrato 404; no consulta si el email o el perfil ya existen. Tras confirmar el padre, el service intenta el `INSERT` directamente y traduce `uq_perfil_cliente_cliente_id` a 409 propio para RN-09. Si el cliente se elimina entre esa lectura y el commit, la FK se traduce a 409 propio por la regla de rechazo de escritura, sin filtrar el error interno; no se inventa reintento ni semántica adicional.

**Alternativas descartadas:** insertar sin leer y devolver 409 para FK ausente (contradice 404 declarado); inspeccionar el texto de la excepción para convertir FK a 404 (acopla al motor y arriesga RN-12); consultar previamente el perfil (contradice RT-02 y agrega una carrera innecesaria).

### D3 — Paginación en ventas del cliente

`GET /clientes/{id}/ventas` acepta `limit` entre 1 y 100, con 20 por defecto, y `offset >= 0`; los valores inválidos producen 422. La consulta aplica siempre `ORDER BY Venta.id` antes de `offset` y `limit`, para que las páginas sean estables y repetibles. Aunque la fila de la tabla de rutas no enumera query params, RN-10 y el Ejercicio 3 dicen que **todo listado** se pagina, por lo que la regla transversal prevalece sobre la omisión de la fila.

**Alternativas descartadas:** devolver todas las ventas (infringe RN-10); paginar sin orden explícito (la base no garantiza un orden estable); no implementar la ruta hasta que se aclare (la regla ya define contrato suficiente).

### D4 — Carga anticipada explícita sin renglones

La lectura individual de cliente, y la recarga posterior a alta o PATCH cuando se devuelve `ClienteRead`, usa una consulta con `joinedload(Cliente.perfil)` porque el perfil es una relación a uno. La consulta de ventas confirma primero la existencia del cliente y luego selecciona `Venta` filtrada y paginada sin acceder a `Venta.renglones` ni a otras relaciones: no hay relación incluida en `VentaResumenRead`, por lo que no requiere `selectinload`. Si el contrato futuro añadiera una colección, deberá usar `selectinload` en la misma consulta.

**Justificación:** cumple RT-04 y el PDF: toda relación leída se precarga; ninguna relación omitida se toca de forma perezosa. La respuesta de ventas queda intencionalmente plana.

**Alternativas descartadas:** devolver `cliente.ventas` por navegación (riesgo de lazy loading); cargar renglones preventivamente (incrementa consultas/datos y viola el alcance del resumen).

### D5 — Integridad y traducción de errores

Altas y cambios de email intentan escribir sin consulta previa de unicidad. El service realiza rollback tras `IntegrityError`, reconoce los constraints nombrados que le pertenecen y devuelve 409 con mensajes propios, sin propagar texto, tabla, constraint ni traza de base (RN-02, RN-09, RN-12). Los routers no contienen SQL ni `try/except` de base y todos sus handlers son `async def`; las consultas usan la API parametrizada del ORM (RT-05).

### D6 — Sin DELETE como limitación pendiente, no decisión implícita

No se expondrán DELETE para clientes, perfiles ni ventas. Esto implementa la limitación vigente de DD-02 y se cita como pendiente Q5 de `knowledge-base/10_preguntas_abiertas.md`: la cátedra debe confirmar que no espera bajas. Si la respuesta exige bajas, se propondrá un change separado; CH-06 no las introduce silenciosamente.

## Risks / Trade-offs

- **Carrera entre comprobar cliente y crear perfil** → La ventana se acepta para respetar el 404 de la ruta; una FK posterior se traduce a 409 propio y no filtra internals.
- **Omisión de paginación en la fila del endpoint** → Se aplica RN-10, de alcance universal; la especificación deja explícito el contrato para evitar interpretaciones diferentes.
- **Cambios futuros en el DTO de ventas de CH-07** → `VentaResumenRead` es local al módulo clientes y plano; cualquier ampliación debe hacerse como cambio de especificación y revisar cargas.
- **Q5 permanece sin respuesta de cátedra** → No se amplía el dominio: se conserva la limitación y se consulta antes de crear rutas de baja.

## Migration Plan

No hay migración de datos ni de esquema: CH-02 ya publica las tablas y constraints. Al aplicar, se reemplazan los stubs del módulo, se registra su router y se verifica el contrato manualmente; el rollback consiste en revertir esas implementaciones, ya que este change no modifica datos estructurales.

## Open Questions

- **Q5, `knowledge-base/10_preguntas_abiertas.md`:** confirmar con cátedra que no se esperan endpoints DELETE. No bloquea este scope porque la tabla actual no declara ninguno.
