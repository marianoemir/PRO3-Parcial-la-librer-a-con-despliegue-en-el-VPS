# Tasks

## 1. Preparación reproducible y mapa de cobertura

- [x] 1.1 Crear `test/ch09-casos-http-c.http` con `@base` configurable, prerequisitos de base dedicada/vacía, arranque que crea el esquema y `python -m app.seed`; verificar que el archivo no contiene `DATABASE_URL`, contraseñas ni comandos destructivos y que referencia el orden C-01..C-08.
- [x] 1.2 Documentar en el encabezado del archivo la reutilización sin edición de `test/ch07-ventas-errores.http` (C-05), `test/ch08-seed-datos-iniciales.http` (C-06) y el nuevo archivo C-07; verificar por inspección que no se duplica una solicitud ya propiedad de CH-07/CH-08/CH-13.

## 2. Casos faltantes de contratos y restricciones

- [x] 2.1 Agregar C-01 en `test/ch09-casos-http-c.http`: `GET /libros/no-es-entero`, esperado 422 antes del handler; verificarlo contra la API local recién iniciada y guardar solo el código/cuerpo público observado en el comentario, sin salida interna.
- [x] 2.2 Agregar C-02 para ISBN de libro 1 y email de cliente 2 repetidos, con cuerpos por lo demás válidos; esperado 409 con `detail` propio y sin SQL/constraint/traceback; verificar ambas respuestas después del seed.
- [x] 2.3 Agregar C-03 para segundo `POST /clientes/1/perfil` con cuerpo válido y C-04 en dos solicitudes de `POST /libros/` (editorial inexistente y autor inexistente, ids dentro de int4); verificar 409 en cada caso y que ninguna respuesta exponga internals de base (RN-09, RN-12, RT-01/RT-02).
- [x] 2.4 Agregar C-08 con `GET /libros/?titulo=%27%20OR%20%271%27%3D%271`; esperado 200 y lista vacía; verificar la respuesta con el seed cargado, sin interpolar texto de usuario en instrucciones SQL (RN-11, RT-05).

## 3. C-07 portable y verificación integrada

- [x] 3.1 Crear `test/ch09-c07-consultas-fijas.http` con los GET de libro 1 frente a libro 6, `GET /ventas/2` tras C-06 y una alta auxiliar válida de una línea seguida de `GET /ventas/3` en base limpia; verificar que los comentarios distinguen ids de fixture de contratos públicos y que los detalles contienen las relaciones esperadas.
- [x] 3.2 Ejecutar el ciclo completo en una base local dedicada: esquema por lifespan → seed → C-01/C-02/C-03/C-04/C-08 → C-05 existente → C-06 existente → C-07; verificar códigos/valores esperados, incluido C-06 con total `"77000.00"`, precios `"25000.00"`/`"27000.00"` y subtotales `"50000.00"`/`"27000.00"`.
- [x] 3.3 Reiniciar localmente con `SQL_ECHO=true` solo para C-07 y comparar en consola la cantidad de consultas de detalle uno/varios autores y uno/varios renglones; verificar igualdad/fijeza sin añadir la captura a `evidencia/` (la evidencia real es responsabilidad de CH-12).
- [x] 3.4 Revisar `git diff --check`, `git status --short` y `openspec validate ch-09-casos-http-c --strict`; verificar que solo cambian los `.http` CH-09 y sus artefactos OpenSpec, sin código, tests existentes, secretos, commit ni push.

## Workflow follow-up

- Solicitar revisión de Facundo (revisor asignado) antes de archivar.
- Archivar el change solo después de que todas las solicitudes y escenarios anteriores estén verificados con salida real.
