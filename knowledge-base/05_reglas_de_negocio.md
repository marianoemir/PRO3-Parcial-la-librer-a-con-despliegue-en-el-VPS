# Reglas de Negocio

Códigos RN-01 a RN-12 del enunciado (fuente: `docs/Parcial_Cap1a4_Consigna.pdf`). Garante esperado = quién garantiza la regla.

## Catálogo y clientes
- **RN-01**: El ISBN de un libro es único. Garante: `UNIQUE` en la base; al escribir se traduce el rechazo a 409 con mensaje propio.
- **RN-02**: El email de un cliente es único. Garante: `UNIQUE` en la base; 409.
- **RN-03**: El precio de un libro es mayor que cero y el stock nunca es negativo. Garante: CHECK en la base y validación del DTO.
- **RN-09**: Un cliente tiene como máximo un perfil. Garante: `UNIQUE` en `perfil_cliente.cliente_id`; 409.

## Ventas y renglones
- **RN-04**: Una venta se crea con sus renglones: los datos de cada renglón viajan dentro del cuerpo del alta de la venta, y no existe un alta de renglones por separado. Garante: DTO anidado; los renglones se agregan a `venta.renglones`.
- **RN-05**: Una venta tiene al menos un renglón, y un mismo libro no aparece en dos renglones. Garante: validación del DTO; 422.
- **RN-06**: El precio de cada renglón se copia del libro al registrar la venta y no cambia aunque después cambie el precio del libro. Garante: el servidor lo lee de la base; nunca viaja en el DTO.
- **RN-07**: El total de la venta lo calcula el servidor como suma de cantidad por precio unitario. Garante: no viaja en el DTO.
- **RN-08**: Las ventas no se modifican: registran un hecho. Garante: no hay PATCH de ventas.

## Listados, filtros y errores
- **RN-10**: Todo listado se pagina con `limit` (de 1 a 100, por defecto 20) y `offset` (desde 0). Garante: restricciones en `Query`; 422.
- **RN-11**: El listado de libros se puede filtrar por parte del título, sin distinguir mayúsculas. Garante: parámetro ligado (nunca SQL armado con texto).
- **RN-12**: Ningún error devuelve al cliente texto interno de la base (nombres de tablas, restricciones o trazas). Garante: traducción del `IntegrityError` a un mensaje propio.

## Reglas transversales derivadas del enunciado (NO son reglas del enunciado; RN oficiales son SOLO RN-01 a RN-12)
- **RT-01** (códigos de respuesta): 201 al crear, 404 si el recurso no existe, 409 si la base rechaza la escritura, 422 si el cuerpo o los parámetros no cumplen el contrato.
- **RT-02** (escritura delegada): en el alta del libro ningún `if` consulta antes si un id existe: se escribe, y si la base rechaza la clave foránea se responde 409. Unicidad y FK delegadas a la base; sin consultas previas de existencia.
- **RT-03** (asincronía): todos los handlers son `async def`; ninguna llamada bloqueante dentro de ellos (`time.sleep`, `requests`, acceso síncrono a la base).
- **RT-04** (carga anticipada): toda relación que se lee se precarga en la misma consulta con `joinedload` (relaciones a uno) o `selectinload` (colecciones); ninguna lectura depende de la carga perezosa.
- **RT-05** (SQL): nunca armado por concatenación de texto con datos del usuario; siempre con parámetros ligados.
