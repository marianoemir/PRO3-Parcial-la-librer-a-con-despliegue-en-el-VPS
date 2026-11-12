# Preguntas Abiertas

> Las dudas de esta sección **no son reglas**: son lo que el enunciado no resuelve. Se registran acá para consultar con la cátedra antes de codificar el comportamiento correspondiente. Ver también `[DISCOVERY] scale` en la parte inferior.

## Inconsistencias detectadas
### IN-01 (resuelta) — Símbolos de los CHECK truncados en la extracción del PDF
**Documento A dice**: en las tablas del PDF, los CHECK de `stock`, `orden` y `total` se leen como `CHECK stock = 0`, `CHECK orden = 1` y `CHECK total = 0`.
**Documento B dice**: RN-03 del mismo enunciado ("el stock nunca es negativo") implica `stock ≥ 0`.
**Impacto**: si se implementara literalmente `= 0`/`= 1`, solo se aceptaría stock 0 u orden 1, y ventas con total 0.
**Resolución**: resuelta — los CHECK son `stock >= 0`, `orden >= 1` y `total >= 0`, verificados en página 4 del PDF original `docs/Parcial_Cap1a4_Consigna.pdf` donde aparece `≥` (la extracción de texto los truncaba como `= 0` / `= 1`). Ver SU-01 (confirmada) en 09_decisiones_y_supuestos.md.

## Preguntas abiertas (priorizadas)
| Prioridad | Pregunta | Bloquea | Decisor |
|-----------|----------|---------|---------|
| Alta | (1) ¿La venta descuenta stock del libro? | El alta de ventas y el seed | Cátedra |
| Media | (2) ¿Qué devuelve `GET /health/ready` y con qué código si la base no responde? | El healthcheck y el despliegue | Cátedra |
| Media | (4) ¿`orden` es único dentro de un libro? | El alta de libros con autorías | Cátedra |
| Media | (3) `POST /autores/` solo declara 201 y 422 (§ endpoints de referencia): ¿no tiene 409? | El contrato de autores | Cátedra |
| Baja | (5) DELETE no existe en el enunciado: confirmar que no se crean endpoints de baja | El alcance de los routers | Cátedra |
| Baja | (6) ¿Qué contiene exactamente el seed? (ejemplos del enunciado: venta cliente 2, libros 1 y 4, precios 25000.00/27000.00; libro con autores 3 y 4, editorial 1, género 1) | La reproducibilidad de los casos C-06/D-03 | Cátedra |
| Baja | (7) ¿`autor_id` en `libro_autor` lleva índice propio? (`libro_id` cubierto por la PK compuesta (`libro_id`, `autor_id`)) | El modelo de datos (índices en FK) | Cátedra |
| Media | (8) ¿Cómo regularizar la brecha de proceso CH-11/CH-12? CH-11 figura completado en `CHANGES.md` (2026-11-11) como hecho a mano en el VPS sin propose/apply y no tiene carpeta en `openspec/changes/archive/`, mientras CH-12 depende de CH-11 y el flujo indica archivar antes de avanzar (CHANGES.md "Cómo usar este documento" y checklist 4.4). Recomendación propuesta en CH-14 (`design.md`): O3 + nota de evidencia O1, pendiente de confirmar con Facundo y Andrés; es una duda interna de proceso, no de la cátedra. | Cierre formal de CH-12 y trazabilidad SDD | Equipo |

Detalle de cada duda:

1. **¿La venta descuenta stock?** El enunciado no dice que registrar una venta modifique `libro.stock`. No implementar descuento hasta la respuesta; documentar la decisión en este archivo.
2. **`GET /health/ready` sin base**: la tabla de endpoints declara solo 200 ("Estado de la base"). ¿Qué devuelve exactamente `GET /health/ready` y con qué código si la base no responde (`SELECT 1` falla: 503, 500 u otro código)? Define el comportamiento del `HEALTHCHECK`. **Propuesta del equipo (NO regla)**: responder 503 con cuerpo propio, igual que en TP anterior de veterinaria; a confirmar con cátedra.
3. **`POST /autores/` sin 409**: la tabla declara solo 201 y 422 para el alta de autores, pero `autor` podría colisionar por otras vías (FK o UNIQUE futuros). ¿La ausencia de 409 es intencional (nunca puede colisionar) o una omisión?
4. **Unicidad de `orden` dentro de un libro**: `libro_autor` tiene PK (`libro_id`, `autor_id`) y CHECK `orden ≥ 1`, pero nada impide dos autorías con el mismo `orden` para el mismo libro. ¿Se agrega una UNIQUE (`libro_id`, `orden`)?
5. **Sin endpoints de baja**: no existe DELETE en ninguna tabla de endpoints. Confirmar que no se crea ninguno (los listados y detalles nunca verán bajas). Si la cátedra espera bajas, agregarlas como changes separados.
6. **Contenido del seed**: los ejemplos del enunciado (venta `cliente_id: 2` con libros 1 y 4, precios 25000.00 y 27000.00; libro con autores 3 y 4, editorial 1, género 1, "Los que aman, odian") parecen ejemplos de forma. Falta la lista cerrada de filas base. Hasta tenerla, el seed debe ser determinista y documentado en el README para que C-06/D-03 sean reproducibles. Nota (pregunta abierta, no regla): el ejemplo del enunciado devuelve id 2 en POST /ventas/ y sugiere seed con venta id 1.
7. **Índice de `autor_id` en `libro_autor`**: el enunciado pide índice en cada clave foránea. En `libro_autor`, `libro_id` está cubierto por la PK compuesta (`libro_id`, `autor_id`); ver anotación en 04_modelo_de_datos.md (`autor_id` con índice propio y justificación como `turno_practica.turno_id` en el TP anterior). A confirmar con cátedra si corresponde índice propio para `autor_id`.
8. **Regularización de CH-11/CH-12 (brecha de proceso interna, detectada en CH-14 2026-11-11):** CH-11 está marcado completado hecho a mano en VPS sin propose/apply y sin carpeta archivada, pero CH-12 depende de CH-11 y el flujo esperado requiere archivado. Recomendación: O3 + nota de evidencia O1, pendiente de confirmar con Facundo y Andrés. Es una duda interna de proceso, no de la cátedra. No se inventa historial ni archivado retroactivo. Ver `openspec/changes/ch-14-rectificacion-active-stack/design.md`.

## [DISCOVERY] scale — low confidence
`scale` pudo inferirse como `public_multi_user` desde el despliegue en VPS accesible desde afuera, pero el uso real es de corrección por grupo. No bloquea la KB; se deja como valor a confirmar por el equipo.
