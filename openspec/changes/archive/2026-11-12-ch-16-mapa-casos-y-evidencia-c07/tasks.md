# Tasks: ch-16-mapa-casos-y-evidencia-c07

> **Nota:** Orden del apply: primero los grupos 1, 2 y 5. La tarea 3.1 la ejecuta Mariano en su terminal (el agente no la ejecuta ni la tilda). Las tareas 3.2, 4.1 y 4.2 se ejecutan recién cuando Mariano confirme que los archivos de evidencia existen; hasta entonces quedan [ ].

## 1. Encabezado histórico en test/ch07-ventas-exito.http

- [x] 1.1 Agregar el bloque de comentarios de advertencia histórica al inicio de `test/ch07-ventas-exito.http` (indicando que es un archivo histórico de desarrollo de CH-07 que requiere una base con IDs específicos y no corre contra el seed final, y referenciando a `test/ch08-seed-datos-iniciales.http` para C-06 y `test/ch09-c07-consultas-fijas.http` para C-07) sin alterar peticiones existentes, y verificar con:
  ```powershell
  [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
  Get-Content -Encoding UTF8 test\ch07-ventas-exito.http -Head 15
  ```
  Esperado: las primeras líneas muestran la advertencia histórica y referencias a los archivos vigentes.

## 2. Mapa de casos de prueba en README.md

- [x] 2.1 Agregar en `README.md`, justo debajo de la URL pública, esta línea: «Abrir con `http://` (no `https://`): la API sirve HTTP plano en el puerto 8000. Si el navegador redirige a https, probar con `http://179.199.129.73:8000/docs`.». Agregar además la sección «Casos de prueba» en `README.md` con la tabla Caso (C-01, C-02a, C-02b, C-03, C-04a, C-04b, C-05 [los dos requests de ch07-ventas-errores.http], C-06, C-07 [C-07-prep y C-07a a C-07e] y C-08) -> Archivo -> Rótulo del request, con los rótulos copiados textualmente de los .http (no de memoria). El orden y la nota del seed se copian de las notas operativas de `test/ch09-casos-http-c.http` y `test/ch09-c07-consultas-fijas.http`. Remitir los casos D hacia `evidencia/LEEME.md`.
- [x] 2.2 Verificar que cada rótulo de request referenciado exista textualmente en su archivo correspondiente y que `README.md` contenga cada nombre de archivo y cada rótulo de la tabla:
  ```powershell
  [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
  $mapa = @(
      @{ Caso = "C-01";      File = "test\ch09-casos-http-c.http";         Pattern = "C-01 — path no entero: FastAPI debe rechazar antes del handler" },
      @{ Caso = "C-02a";     File = "test\ch09-casos-http-c.http";         Pattern = "C-02a — ISBN del libro 1 repetido con el resto del cuerpo válido" },
      @{ Caso = "C-02b";     File = "test\ch09-casos-http-c.http";         Pattern = "C-02b — email de cliente ya existente en el seed (cliente 2 Tomás Ríos)" },
      @{ Caso = "C-03";      File = "test\ch09-casos-http-c.http";         Pattern = "C-03 — segundo perfil para el cliente 1, que ya lo tiene en el seed" },
      @{ Caso = "C-04a";     File = "test\ch09-casos-http-c.http";         Pattern = "C-04a — editorial inexistente dentro de int4" },
      @{ Caso = "C-04b";     File = "test\ch09-casos-http-c.http";         Pattern = "C-04b — autor inexistente dentro de int4" },
      @{ Caso = "C-05 (1)";  File = "test\ch07-ventas-errores.http";       Pattern = "409 - POST venta con cliente_id inexistente (C-05 / Task 2.3)" },
      @{ Caso = "C-05 (2)";  File = "test\ch07-ventas-errores.http";       Pattern = "409 - POST venta con libro_id inexistente en renglones (C-05 / Task 2.1)" },
      @{ Caso = "C-06";      File = "test\ch08-seed-datos-iniciales.http"; Pattern = "Ejemplo enunciado / C-06 — POST /ventas/ produce id 2 y total 77000.00" },
      @{ Caso = "C-07-prep"; File = "test\ch09-c07-consultas-fijas.http";  Pattern = "C-07-prep — crear libro con varias autorías (ejemplo del enunciado)" },
      @{ Caso = "C-07a";     File = "test\ch09-c07-consultas-fijas.http";  Pattern = "C-07a — libro 1 del seed (una autoría)" },
      @{ Caso = "C-07b";     File = "test\ch09-c07-consultas-fijas.http";  Pattern = "C-07b — libro con varias autorías creado en C-07-prep" },
      @{ Caso = "C-07c";     File = "test\ch09-c07-consultas-fijas.http";  Pattern = "C-07c — detalle venta con dos renglones (creada en ch08 o venta 1 del seed)" },
      @{ Caso = "C-07d";     File = "test\ch09-c07-consultas-fijas.http";  Pattern = "C-07d — venta auxiliar válida (un renglón)" },
      @{ Caso = "C-07e";     File = "test\ch09-c07-consultas-fijas.http";  Pattern = "C-07e — detalle venta auxiliar con un renglón" },
      @{ Caso = "C-08";      File = "test\ch09-casos-http-c.http";         Pattern = "C-08 — intento de inyección en filtro de título" }
  )
  $fallos = 0
  foreach ($item in $mapa) {
      $matchFile = Select-String -Path $item.File -Pattern $item.Pattern -SimpleMatch -Encoding UTF8
      $matchReadmeRotulo = Select-String -Path README.md -Pattern $item.Pattern -SimpleMatch -Encoding UTF8
      $fileName = Split-Path $item.File -Leaf
      $matchReadmeFile = Select-String -Path README.md -Pattern $fileName -SimpleMatch -Encoding UTF8
      $ok = ($matchFile -ne $null) -and ($matchReadmeRotulo -ne $null) -and ($matchReadmeFile -ne $null)
      if (-not $ok) { $fallos++ }
      [PSCustomObject]@{
          Caso = $item.Caso
          EnArchivo = ($matchFile -ne $null)
          EnReadmeRotulo = ($matchReadmeRotulo -ne $null)
          EnReadmeArchivo = ($matchReadmeFile -ne $null)
      }
  }
  Write-Output "Total fallos: $fallos"
  ```
  Esperado: todos los checks en `$true` y `Total fallos: 0`.

## 3. Captura y registro de evidencia de C-07 (venta de 1 renglón)

- [x] 3.1 **(Ejecuta Mariano en su terminal — el agente no la ejecuta ni la tilda)**:
  0) Mariano crea la base vacía `libreria_c16` en pgAdmin y edita el `.env` a mano para apuntar a ella (el agente no lo lee ni lo edita).
  1) Activar el venv y `$env:SQL_ECHO="true"`.
  2) Iniciar uvicorn con la salida a un archivo en `%TEMP%` (esto crea el esquema).
  3) En otra terminal, `python -m app.seed` (debe mostrar el resumen de 27 filas).
  4) Sin ningún otro pedido en el medio, POST /ventas/ con el cuerpo de C-07d (esperado: 201, id 2, total 18000.00).
  5) GET /ventas/1 (2 renglones) y GET /ventas/2 (1 renglón).
  6) Detener uvicorn, copiar el log a `evidencia/C-07-ventas-un-renglon.log` y generar `evidencia/C-07-ventas-un-renglon-conteo.txt` contando las líneas `Engine SELECT ` entre el pedido anterior y cada pedido (mismo formato que `evidencia/C-07-conteo.txt`).
  7) Devolver el `.env` a `libreria_dev` y quitar `SQL_ECHO`. Si el POST no da id 2, repetir todo desde el paso 2. Sin scripts que alineen secuencias.
- [x] 3.2 Verificar la existencia y consistencia de los nuevos archivos de evidencia de C-07:
  ```powershell
  [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
  $pathLog = Test-Path evidencia\C-07-ventas-un-renglon.log
  $pathConteo = Test-Path evidencia\C-07-ventas-un-renglon-conteo.txt
  if (-not ($pathLog -and $pathConteo)) {
      throw "Faltan archivos de evidencia: log=$pathLog, conteo=$pathConteo"
  }
  $logContent = Get-Content -Encoding UTF8 evidencia\C-07-ventas-un-renglon.log
  $hasPost = ($logContent | Select-String -Pattern '"POST /ventas/ HTTP/1.1" 201' -SimpleMatch -Encoding UTF8) -ne $null
  $hasGet1 = ($logContent | Select-String -Pattern '"GET /ventas/1 HTTP/1.1" 200' -SimpleMatch -Encoding UTF8) -ne $null
  $hasGet2 = ($logContent | Select-String -Pattern '"GET /ventas/2 HTTP/1.1" 200' -SimpleMatch -Encoding UTF8) -ne $null
  $hasPassword = ($logContent | Select-String -Pattern 'password' -Encoding UTF8) -ne $null
  $hasConnString = ($logContent | Select-String -Pattern 'postgresql+asyncpg://' -SimpleMatch -Encoding UTF8) -ne $null

  $conteoContent = Get-Content -Encoding UTF8 evidencia\C-07-ventas-un-renglon-conteo.txt
  # Verificar que GET /ventas/1 y GET /ventas/2 tienen el mismo SELECT (esperado 2 y 2)
  Write-Output "Post OK: $hasPost | Get1 OK: $hasGet1 | Get2 OK: $hasGet2 | Sin password: $(-not $hasPassword) | Sin connString: $(-not $hasConnString)"
  Get-Content -Encoding UTF8 evidencia\C-07-ventas-un-renglon-conteo.txt
  ```
  Esperado: requests 201/200 presentes en log, sin credenciales, y conteos de SELECT exactamente iguales a 2 para GET /ventas/1 y GET /ventas/2. Si difieren, frenar y reportar sin editar la evidencia.

## 4. Actualización de evidencia/LEEME.md

- [x] 4.1 Incorporar en `evidencia/LEEME.md` la referencia a `C-07-ventas-un-renglon.log` y `C-07-ventas-un-renglon-conteo.txt` en el bloque de evidencia vigente, explicando que contiene la comparación de una venta de 1 renglón frente a una de 2 renglones.
- [x] 4.2 Verificar que `evidencia/LEEME.md` contenga las nuevas referencias con:
  ```powershell
  [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
  Get-Content -Encoding UTF8 evidencia\LEEME.md | Select-String -Pattern "C-07-ventas-un-renglon" -Encoding UTF8
  ```
  Esperado: menciones presentes en `LEEME.md`.

## 5. Actualización de CHANGES.md y Estado de Orquestación

- [x] 5.1 Agregar la entrada `[CH-16]` en `CHANGES.md` declarando dependencias: CH-12 tanda a (rama encadenada, README y LEEME editados ahí), CH-15 (seed) y CH-09 (casos C-07), y actualizar el árbol de dependencias, conservando finales de línea CRLF, y verificar con:
  ```powershell
  git diff -U1 CHANGES.md
  & .\.venv\Scripts\python.exe -c "
  with open('CHANGES.md', 'rb') as f:
      content = f.read()
  lines = content.split(b'\n')
  bad = [i+1 for i, l in enumerate(lines[:-1]) if not l.endswith(b'\r')]
  print(f'Lineas sin CRLF: {len(bad)}')
  "
  ```
  Esperado: diff acotado a CH-16 y `Lineas sin CRLF: 0`.
- [x] 5.2 Leer primero el valor actual de `roadmap.revision` (esperado 4; si no, actual + 1) y agregar CH-16 en `roadmap.changes` copiando la forma exacta de la entrada de CH-15 (no como string suelto). Conservar los finales de línea del archivo (.active-orchestrator-state.json), verificando con:
  ```powershell
  [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
  Get-Content -Encoding UTF8 .active-orchestrator-state.json | Select-String "CH-16", "revision"
  ```
  Esperado: `"CH-16"` presente y `revision` incrementada a 5.
