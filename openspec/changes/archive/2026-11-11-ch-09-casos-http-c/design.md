# Design

## Context

Ver `proposal.md` para la motivación. El PDF exige archivos `.http` con C-01 a C-08 y comentarios de respuesta esperada. CH-08 dejó un seed idempotente, pero los casos HTTP deben ejecutarse contra una **base dedicada y recreada**: el esquema lo crea el lifespan y luego `python -m app.seed` inserta cliente 2, libros 1 y 4, cliente 1 con perfil, libro 6 con dos autorías y venta 1 con dos renglones.

El árbol actual ya contiene evidencias HTTP de cambios de dominio: `test/ch07-ventas-errores.http` (C-05), `test/ch07-ventas-exito.http` (C-06 y notas C-07) y `test/ch08-seed-datos-iniciales.http` (C-06/D-03). Esos archivos pertenecen al alcance histórico de CH-07/CH-08 y no se reescriben ni se duplican. Algunos ids de CH-07 son de una ejecución anterior y no sirven como fixture portátil.

Las rutas y mensajes públicos vigentes se obtienen de los routers/services ya integrados. La batería no cambia contratos: valida los 409 propios exigidos por RN-01, RN-02, RN-09 y RN-12, los errores/éxito de ventas RN-04 a RN-07 y la consulta parametrizada de RN-11/RT-05.

## Goals / Non-Goals

**Goals:**

- Añadir solo los casos HTTP faltantes y un flujo reproducible que componga los casos ya existentes, sin tocar los módulos dueños.
- Fijar un orden de ejecución sobre una base limpia que permita usar ids estables del seed y que no confunda una respuesta 409 de una ejecución previa con la regla que se busca demostrar.
- Para cada caso, exigir código, cuerpo/forma observable y la ausencia de internals de base en los 409 cubiertos por RN-12.
- Convertir C-07 en una verificación portable de solicitudes de detalle (uno frente a varios autores/renglones), dejando el conteo/captura SQL real en CH-12.

**Non-Goals:**

- No cambiar `app/`, `app/seed.py`, contratos, datos del seed, Docker, VPS, `evidencia/` ni código de los módulos si un caso falla.
- No recrear C-05/C-06 existentes ni modificar los archivos CH-07/CH-08/CH-13.
- No automatizar la captura de consola ni declarar una cantidad numérica nueva de `SELECT`: C-07 exige igualdad/fijeza entre detalles, y CH-12 conserva la evidencia.
- No crear pytest, Playwright, credenciales, `.env`, scripts destructivos ni una base de datos de prueba compartida.

## Decisions

### 1. Un archivo de control CH-09 para los cinco casos faltantes y una guía de composición

- **Decisión:** crear `test/ch09-casos-http-c.http` con C-01, C-02, C-03, C-04 y C-08, además de un bloque inicial que indica cómo encadenar C-05/C-06 desde los archivos existentes y C-07 desde el archivo específico de este change. Cada solicitud lleva comentario con método, datos previos, resultado esperado y aserciones observables.
- **Rationale:** los cinco casos no están cubiertos por los `.http` vigentes; C-05/C-06 ya tienen solicitudes propietarias en CH-07/CH-08. Un único archivo nuevo evita duplicación, mantiene el requisito del PDF de `test/` y deja el mapa C-01..C-08 explícito.
- **Alternativas:** crear ocho archivos nuevos (descartado: duplica C-05/C-06/C-07); editar los archivos de CH-07/CH-08 (descartado: invade cambios archivados); no crear un índice (descartado: oculta el orden y el dueño de cada caso).

### 2. Datos de cada caso faltante: seed estable + cuerpos completos y no persistentes

- **Decisión:** C-01 consulta `GET /libros/no-es-entero` y espera 422; C-02 hace dos POST válidos salvo por ISBN del libro 1 y email del cliente 2 repetidos, espera 409 con `detail` propio; C-03 intenta un segundo perfil para cliente 1 y espera 409; C-04 intenta altas de libro por separado con editorial inexistente y autor inexistente dentro de rango, y espera 409 propio; C-08 hace `GET /libros/?titulo=%27%20OR%20%271%27%3D%271` y espera 200 con `[]`.
- **Rationale:** el seed provee todas las referencias válidas y los conflictos seleccionados no crean filas, por lo que no contaminan la secuencia ni dependen de ids generados. Los cuerpos de libro incluyen precio como cadena decimal y autorías válidas, de modo que la respuesta prueba la restricción objetivo y no un 422 previo.
- **Alternativas:** crear fixtures por API antes de cada caso (descartado: agrega mutabilidad, colisiones y orden); usar ids extremos para inexistencia (descartado: puede confundir 409 de negocio con validación/rango); aserciones sobre mensajes PostgreSQL (descartado por RN-12).

### 3. C-05/C-06 se reutilizan; C-07 obtiene una fixture mínima tras C-06

- **Decisión:** la secuencia documentada en base nueva será: iniciar API para crear esquema, detener/reiniciar contra la misma base, ejecutar seed, correr C-01..C-04/C-08, ejecutar la solicitud C-05 de `ch07-ventas-errores.http`, ejecutar la C-06 de `ch08-seed-datos-iniciales.http` (crea venta 2) y, finalmente, `test/ch09-c07-consultas-fijas.http`. Este último compara detalles `GET /libros/1` (un autor) y `GET /libros/6` (dos autores), `GET /ventas/2` (dos renglones de C-06) y crea una venta auxiliar de un renglón, que en una base limpia será id 3, para `GET /ventas/3`.
- **Rationale:** el seed contiene suficiente variación para libros y venta de varios renglones, pero no una venta de un renglón. La fixture auxiliar es una alta válida y aislada; el id 3 solo se usa bajo el ciclo limpio y ordenado declarado, por lo que el contraste C-07 es reproducible sin alterar seed ni depender de ids históricos CH-07.
- **Alternativas:** modificar seed para agregar una venta (descartado: corresponde a CH-08 y excede el caso); usar los ids 11/12 de CH-07 (descartado: no están garantizados); automatizar encadenamiento dependiente del cliente REST (descartado: el enunciado exige `.http`, no una herramienta o sintaxis propietaria).

### 4. Criterios de respuesta y seguridad operativa

- **Decisión:** los `.http` fijarán status, JSON esperado y campos de valor estable: C-06 verifica `total: "77000.00"`, cliente 2, renglones 1×2/4×1, `precio_unitario` y subtotales; C-07 verifica las relaciones serializadas, no el número de consultas en HTTP. Los 409 deben incluir un `detail` propio y nunca mostrar `asyncpg`, `IntegrityError`, SQL, constraint, tabla o traceback. Los ids de venta creados se describen como dependientes de la base limpia, no como contratos de la API.
- **Rationale:** status solo no detecta drift relevante; las respuestas monetarias se serializan como strings de dos decimales y C-07 se observa por consola con `SQL_ECHO=true`, conforme PDF/RN-06/RN-07/RT-04. No se leen ni versionan secretos: `DATABASE_URL` sigue exclusivamente en el entorno local.
- **Alternativas:** exigir el texto exacto completo de todos los errores (descartado: el PDF obliga mensajes propios, no redacción literal); ejecutar contra la base de desarrollo compartida (descartado: no es idempotente ni aislado); registrar `SQL_ECHO=true` en archivos (descartado: es configuración local).

## Risks / Trade-offs

- **[Riesgo] Ejecutar sobre una base ya usada** → Mitigación: los encabezados exigen base dedicada recreada, seed y orden exacto; se advierte que venta 2/3 no debe asumirse fuera de ese ciclo.
- **[Riesgo] Los 409 de C-04/C-05 cambian de detalle público sin filtrar internals** → Mitigación: se verifica código y carácter público/sanitizado, no texto de driver ni constraint; el detalle literal vigente se registra solo como referencia.
- **[Riesgo] El cliente `.http` no soporta aserciones programables** → Mitigación: comentarios completos de esperado, como pide la consigna; la verificación se hace inspeccionando respuesta real, sin introducir otra dependencia.
- **[Riesgo] C-07 se interprete como evidencia final** → Mitigación: el archivo indica que debe arrancarse con `SQL_ECHO=true`, comparar la cantidad de consultas de los cuatro GET y entregar la salida real únicamente en CH-12.
- **[Riesgo] Una falla impulse cambios en módulo ajeno** → Mitigación: CH-09 reporta ruta, cuerpo y respuesta al dueño del módulo; no parchea código ni cambia contrato.

## Migration Plan

1. No hay migraciones ni despliegue. Agregar los dos `.http` planificados y no modificar archivos existentes.
2. Ejecutar localmente contra una base temporal/dedicada configurada fuera del repositorio: arrancar `uvicorn app.main:app --host 127.0.0.1 --port <puerto>`, ejecutar `python -m app.seed`, y reiniciar con `SQL_ECHO=true` solo para C-07 si hace falta capturar consola.
3. Seleccionar solicitudes en el orden de la decisión 3 y registrar respuestas reales sin copiar secretos ni salida SQL a este change.
4. Rollback: eliminar únicamente los dos nuevos archivos CH-09; no hay estado de esquema que revertir. La base temporal se elimina mediante el procedimiento local del operador, nunca por un `.http` ni por una instrucción que apunte al VPS.

## Open Questions

- **KB §(1) (PENDIENTE):** si la cátedra ordena descontar stock al vender, C-06 y la fixture auxiliar de C-07 deberán ajustar únicamente sus comprobaciones de stock en un change posterior; CH-09 no fija esa regla.
- **KB §(6) (PENDIENTE):** si cambia el dataset oficial, deben revisarse los ids/valores documentados (cliente 2, libros 1/4/6 y venta 1); no se reemplazan silenciosamente en CH-09.
