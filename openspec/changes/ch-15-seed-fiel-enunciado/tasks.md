# Tasks

## 1. Dataset y comportamiento del seed (`app/seed.py`)

- [x] 1.1 Actualizar el dataset determinista en `app/seed.py` para reflejar 27 filas: eliminar el libro 6 y sus 2 autorías (quedan libros 1–5 y 5 autorías), cambiar el cliente 2 a "Tomás Ríos" (`tomas@example.com`), conservar autores 3 y 4, editorial 1 y género 1, y mantener la venta 1 (cliente 2, libro 1 ×2 a 25000.00, libro 4 ×1 a 27000.00, total 77000.00, fecha fija) y sus renglones. Verificar leyendo `app/seed.py` y comprobando que no exista el ISBN `978-950-00-0006-6` ni "Bruno Díaz"/`bruno.diaz@example.com`, que los conteos declarados sumen 27 y que el dinero use `Decimal`.
- [x] 1.2 Reemplazar la estrategia `INSERT ... ON CONFLICT DO NOTHING` por carga reiniciable en una única transacción: ejecutar `TRUNCATE` de las 9 tablas del proyecto nombradas explícitamente (`editorial`, `genero`, `autor`, `libro`, `libro_autor`, `cliente`, `perfil_cliente`, `venta`, `renglon_venta`) con `RESTART IDENTITY CASCADE`, insertar el dataset y alinear secuencias para que el siguiente `POST /libros/` del enunciado y el siguiente `POST /ventas/` del enunciado obtengan ids coherentes (venta 2). Verificar revisando el SQL/flujo en `app/seed.py` y que no se use truncado genérico del schema ni otras tablas/bases.
- [x] 1.3 Ajustar la salida de consola y el manejo de errores a la nueva estrategia: resumen propio del estado cargado/reiniciado (sin "insertadas / ya existían"), mensajes propios con código de salida 1 ante `DATABASE_URL` faltante, esquema ausente, base inalcanzable o fallo de carga, sin imprimir credenciales, `DATABASE_URL`, SQL, trazas internas ni nombres de constraints. Verificar revisando `app/seed.py` y ejecutando `python -m app.seed` en un entorno controlado (sin `DATABASE_URL` o con esquema ausente según corresponda) observando exit code 1 y mensaje propio.
- [x] 1.4 Garantizar rollback total: cualquier fallo durante vaciado/carga debe revertir la transacción completa dejando la base exactamente como estaba antes. Verificar en base local dedicada:
  1) Con el seed cargado y una venta y un libro creados por la API, tomar `SELECT count(*)` de las 9 tablas del proyecto.
  2) Agregar una restricción temporal que falle un INSERT del seed: `ALTER TABLE libro ADD CONSTRAINT tmp_falla CHECK (id <> 3) NOT VALID;` (el `NOT VALID` es necesario porque el libro 3 ya existe).
  3) Correr `python -m app.seed` y confirmar código de salida 1, mensaje propio y sin internals de base de datos.
  4) Repetir las consultas de conteo (`SELECT count(*) FROM ...`) sobre las 9 tablas y comprobar que son idénticos a los tomados en el paso 1 (incluidos los datos creados por la API).
  5) Eliminar la restricción temporal: `ALTER TABLE libro DROP CONSTRAINT tmp_falla;`.
  6) Evidencia: registrar la salida real de los comandos SQL y de terminal antes, durante y después del intento.

## 2. Ajustes de artefactos `.http` dependientes

- [x] 2.1 Actualizar `test/ch08-seed-datos-iniciales.http` al nuevo dataset y comportamiento: 27 filas, 5 libros, cliente 2 "Tomás Ríos" (`tomas@example.com`), sin libro 6 en el seed, y nota de que reejecutar el seed reinicia los datos. Ajustar para que NO cree el libro con ISBN `978-950-00-0006-6` (ese libro se crea exclusivamente en `test/ch09-c07-consultas-fijas.http` para evitar 409 por duplicación). Mantener/verificar la inspección del estado sembrado (`GET /libros/` devolviendo 5, `GET /clientes/2` devolviendo Tomás Ríos, `GET /ventas/1`) y la creación de la venta del ejemplo del enunciado con `POST /ventas/` esperando 201, `id: 2`, `total: "77000.00"`, cliente `tomas@example.com` y renglones con título, precio unitario y subtotal. Verificar ejecutando las peticiones con `curl.exe` o el runner `.http` contra base local vacía dedicada con esquema y seed cargados, guardando la salida real.
- [x] 2.2 Actualizar `test/ch09-casos-http-c.http`: C-02a debe usar el ISBN del libro 1 (`978-950-00-0001-1`) ya existente en el seed vigente para seguir provocando 409 (dejando libre el ISBN `978-950-00-0006-6` para C-07); C-02b debe usar explícitamente `tomas@example.com` (email del cliente 2 sembrado en CH-15) reemplazando cualquier mención a `bruno.diaz@example.com` para provocar 409 de unicidad de email de forma reproducible (si se mantuviera un email no sembrado, la solicitud respondería 201 y crearía un cliente no deseado en medio del ciclo). Verificar ejecutando el ciclo limpio documentado con `curl.exe`/`.http` sobre base local vacía dedicada con seed y comprobando códigos/cuerpos esperados (409 propios, 422, 200 `[]` en C-08) sin internals.
- [x] 2.3 Actualizar `test/ch09-c07-consultas-fijas.http`: en este archivo se realiza POR ÚNICA VEZ en todo el ciclo de pruebas la creación del libro con varias autorías mediante el `POST /libros/` del ejemplo del enunciado (ISBN `978-950-00-0006-6`, libro 6, esperando 201), nombrando la petición `# @name crearLibro` y capturando el `id` devuelto dinámicamente vía `{{crearLibro.response.body.$.id}}` para consultar su detalle en lugar de asumir una fixture fija sembrada. El archivo NO crea la venta del ejemplo (la venta 2 se crea una sola vez en ch08): hace el `POST /libros/` del ejemplo, `GET /libros/1` y `GET /libros/{{crearLibro.response.body.$.id}}`, `GET /ventas/2` (o venta 1), el `POST` de la venta auxiliar nombrando `# @name crearVentaAuxiliar` y `GET /ventas/{{crearVentaAuxiliar.response.body.$.id}}`. Se documenta en el encabezado la nota operativa de ejecutar `python -m app.seed` antes de C-07 para evitar desalineación de secuencias por inserts fallidos previos. Asegurar que los archivos `.http` terminen con salto de línea. Verificar con `SQL_ECHO=true` en consola local, ejecutando el ciclo limpio y registrando la salida real que muestre 3 SELECT fijos para libro 1 vs libro con varias autorías y 2 SELECT fijos para las dos ventas comparadas.
- [x] 2.4 Revisar y ajustar mínimamente `test/ch07-ventas-errores.http` solo si depende de "Bruno Díaz", del libro 6 o de supuestos del seed anterior, manteniendo los casos de error 409/422 válidos y sin acoplarlos a datos eliminados. Verificar ejecutando las peticiones del archivo con `curl.exe`/`.http` sobre base local con seed vigente y confirmando los códigos/`detail` propios esperados.

## 3. Documentación, roadmap y preguntas abiertas

- [x] 3.1 Actualizar solo la sección "Datos iniciales (seed)" de `README.md` (sin tocar otras secciones del archivo) con el nuevo dataset (27 filas, tabla de contenido corregida sin libro 6, cliente 2 Tomás Ríos, 5 autorías), el comando y la advertencia explícita y visible de que reejecutar el seed reinicia los datos de las 9 tablas del proyecto sin confirmación previa. Verificar con lectura del archivo y que no se modifiquen otras secciones.
- [x] 3.2 Actualizar `DEPLOY.md` en las menciones del seed para reflejar el nuevo dataset/conteos, el comando, la advertencia destacada de que reejecutar reinicia las 9 tablas, y el orden de reconstrucción del VPS cuando se actualiza `app/seed.py`. Verificar con lectura del archivo y búsqueda de referencias al seed/dataset.
- [x] 3.3 Actualizar `CHANGES.md`: agregar entrada `[CH-15] seed-fiel-enunciado` (estado, scope, dependencias CH-08 y CH-09, governance MEDIO, "Leer antes"), ajustar la línea de convención para indicar que CH-15 es change propio (no rectificación), actualizar el árbol/dependencias para que CH-12 dependa también de CH-15 (aclarando que CH-15 no se marca con ✓ en dependencias ni gates de `CHANGES.md` hasta que esté efectivamente archivado), agregar nota fechada y tocar solo las líneas necesarias preservando CRLF. Verificar con `git diff -- CHANGES.md` (solo líneas editadas) y comprobación de finales de línea CRLF.
- [x] 3.4 Actualizar `.active-orchestrator-state.json` subiendo `roadmap.revision` de 3 a 4 y agregando `CH-15` a `roadmap.changes`. Verificar con lectura del JSON y validación de formato.
- [x] 3.5 Registrar en `knowledge-base/10_preguntas_abiertas.md` que "el ejemplo de `POST /libros/` crea el sexto libro" es una inferencia del equipo y no algo afirmado explícitamente por el PDF (responsable: Equipo), y mantener indicado que el seed sigue sin descontar stock. Verificar con lectura de la sección añadida/modificada. Confirmar que `AGENTS.md` y `CLAUDE.md` permanecen idénticos (sin cambios de contenido) comparando sus hashes SHA256.

## 4. Verificación integral en base local dedicada (nunca VPS)

- [x] 4.1 Verificar estado inicial esperado y alcance del vaciado: en base local vacía y dedicada (p.ej. `libreria_c09`) con esquema creado, ejecutar `python -m app.seed` y comprobar 27 filas con consultas SQL por tabla, `GET /libros/` devuelve 5 y `GET /clientes/2` devuelve "Tomás Ríos" `tomas@example.com`; confirmar que el seed no afecta tablas ajenas a las 9 del proyecto. Evidencia: salida real de consola del seed, de `curl.exe` y de consultas SQL.
- [x] 4.2 Verificar que el ISBN queda libre y la venta coincide con el ejemplo: tras el seed, ejecutar `POST /libros/` con el JSON del enunciado (ISBN `978-950-00-0006-6`) y obtener 201 (no 409); ejecutar `POST /ventas/` con el JSON del enunciado y obtener 201 con id 2, total `"77000.00"`, cliente `tomas@example.com` y renglones con `titulo`, `precio_unitario` y `subtotal`. Evidencia: salida real de `curl.exe`.
- [x] 4.3 Verificar repetibilidad por reinicio y alineación de secuencias: tras el seed, crear una venta y un libro por la API, reejecutar el seed y comprobar mismo estado inicial (27 filas), `GET /ventas/2` 404, `GET /libros/6` 404 y que el siguiente `POST /ventas/` del ejemplo vuelve a dar id 2. Evidencia: salida real de `curl.exe` y consultas SQL de conteos.
- [x] 4.4 Verificar manejo de errores y salida segura: ejecutar el seed sin `DATABASE_URL` y/o con esquema ausente según el caso y confirmar código de salida 1 y mensaje propio sin credenciales ni internals. Evidencia: salida real de consola/terminal mostrando exit code.
- [x] 4.5 Verificar regresión integral C-01..C-08: ejecutar el ciclo limpio documentado sobre base local vacía dedicada con seed de CH-15, preservando el orden obligatorio y la ejecución de `python -m app.seed` previo a C-06 y previo a C-07 tal como indican las notas operativas; confirmar C-01..C-06/C-08 según contratos y C-07 con 3 SELECT fijos (libro 1 vs libro con varias autorías creado por el ejemplo) y 2 SELECT fijos (ventas comparadas) usando `SQL_ECHO=true`. Evidencia: salida real de `curl.exe` y fragmentos reales de consola SQL con conteos/comparación visibles.

## 5. Pasos manuales posteriores en VPS (fuera de este change)

- [ ] 5.1 [VPS] **Responsable: Mariano.** Actualizar código en el servidor:
  ```bash
  cd /root/libreria
  git pull
  ```
- [ ] 5.2 [VPS] **Responsable: Mariano.** Reconstruir la imagen Docker local para incorporar la versión actualizada de `app/seed.py`:
  ```bash
  docker build -t libreria .
  ```
- [ ] 5.3 [VPS] **Responsable: Mariano.** Recrear el contenedor de la aplicación con la misma configuración vigente (sin credenciales expuestas):
  ```bash
  docker rm -f libreria
  docker run -d --name libreria --network easypanel-grupo10 -p 8000:8000 \
    --restart unless-stopped --env-file /root/libreria.env libreria
  ```
- [ ] 5.4 [VPS] **Responsable: Mariano.** Esperar a que el contenedor pase al estado `healthy`:
  ```bash
  docker ps
  curl -s http://127.0.0.1:8000/health/ready
  ```
- [ ] 5.5 [VPS] **Responsable: Mariano.** Ejecutar la carga del seed de CH-15 dentro del contenedor (ADVERTENCIA: reinicia los datos de las 9 tablas del proyecto):
  ```bash
  docker exec libreria python -m app.seed
  ```
- [ ] 5.6 [VPS] **Responsable: Mariano.** Rehacer D-03 y D-07 con el MISMO `POST /ventas/` del ejemplo del enunciado (capturar los logs de Docker antes de eliminar el contenedor):
  1) `GET /health/ready` responde 200 `{"estado":"listo"}` y `GET /libros/` responde 200 con los 5 libros del dataset.
  2) Ejecutar `POST /ventas/` con cliente 2 y libros 1×2 y 4×1, verificando 201 con `id: 2`, `total: "77000.00"`, cliente `tomas@example.com` y subtotales calculados. Guardar salida en `evidencia/D-03-url-publica.txt`.
  3) Inmediatamente tras la respuesta HTTP, capturar `docker logs libreria` para registrar el aviso de emisión de comprobante en diferido y guardar salida en `evidencia/D-07-aviso-comprobante.txt`.
- [ ] 5.7 [VPS] **Responsable: Mariano.** Rehacer D-04 (persistencia/recuperación):
  1) Eliminar el contenedor y volver a levantarlo con el mismo comando:
     ```bash
     docker rm -f libreria
     docker run -d --name libreria --network easypanel-grupo10 -p 8000:8000 \
       --restart unless-stopped --env-file /root/libreria.env libreria
     ```
  2) Esperar a que vuelva al estado `healthy`.
  3) Consultar `GET /health/ready`, `GET /libros/` y `GET /ventas/2` verificando que los datos siguen persistiendo intactos en la base PostgreSQL. Guardar también `docker logs libreria` del contenedor nuevo, mostrando las líneas de los `GET /libros/` y `GET /ventas/2`, dentro de `evidencia/D-04-persistencia.txt`.
- [ ] 5.8 [VPS] **Responsable: Mariano.** Actualizar la sección "Día y hora del despliegue" en `DEPLOY.md` con la fecha y hora exacta del despliegue vigente DESPUÉS del último `docker run`.

## Workflow follow-up

- Ejecutar `/opsx:apply ch-15-seed-fiel-enunciado` para implementar las tareas 1–4 siguiendo estas specs y este diseño, y registrar evidencia real de cada verificación.
- Tras completar y verificar, archivar el change con `/opsx:archive ch-15-seed-fiel-enunciado` según el flujo SDD del proyecto y actualizar el estado en `CHANGES.md` solo cuando corresponda al cierre real.
