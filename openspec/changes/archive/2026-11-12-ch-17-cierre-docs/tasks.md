# Tasks: ch-17-cierre-docs

## 1. Limpieza de marcas provisionales en DEPLOY.md

- [x] 1.1 En `DEPLOY.md`, eliminar la nota de la línea 5 (`> Lo marcado **[A COMPLETAR]** se confirma al cerrar el despliegue final.`); en la sección «Día y hora del despliegue» («Despliegue vigente») reemplazar `**[A COMPLETAR: actualizar si se vuelve a recrear el contenedor]**` por `Si se vuelve a recrear el contenedor, esta hora se actualiza.`; y en «Entorno» (línea «Servidor») reemplazar `**[A COMPLETAR: VPS asignado por la cátedra / propio del grupo]**` por `propio de un integrante del grupo (no lo asignó la cátedra). Ya se usaba para el proyecto de Frontend del grupo (la calculadora) y las dos materias comparten el servidor.`. Verificar con:
  ```powershell
  git diff -U1 DEPLOY.md
  Select-String -Path DEPLOY.md, README.md -Pattern "A COMPLETAR" -Encoding UTF8
  ```
  Esperado: diff acotado a los tres puntos indicados y 0 coincidencias de "A COMPLETAR" en ambos archivos.

## 2. Unificación del rótulo C-07c en test HTTP y README.md

- [x] 2.1 En `test/ch09-c07-consultas-fijas.http`, modificar el encabezado de la línea 54 reemplazando `(creada en ch08 o venta 1 del seed)` por `(venta 1 del seed)`. En `README.md`, modificar la fila C-07c de la tabla «Casos de prueba» (línea 81) con idéntica sustitución, de modo que ambos archivos contengan carácter por carácter `### C-07c — detalle venta con dos renglones (venta 1 del seed)`. Verificar con:
  ```powershell
  git diff -U1 test/ch09-c07-consultas-fijas.http README.md
  $r1 = (Select-String -Path test/ch09-c07-consultas-fijas.http -Pattern "### C-07c" -Encoding UTF8).Line.Trim()
  $r2 = (Select-String -Path README.md -Pattern "C-07c" -Encoding UTF8).Line
  $expected = "### C-07c — detalle venta con dos renglones (venta 1 del seed)"
  [PSCustomObject]@{
      HttpCoincide = ($r1 -eq $expected)
      ReadmeContiene = ($r2 -like "*$expected*")
  }
  ```
  Esperado: `HttpCoincide = True` y `ReadmeContiene = True`. Los artefactos archivados de CH-16 permanecen inalterados.

## 3. Actualización y sincronización de AGENTS.md y CLAUDE.md

- [x] 3.1 En `AGENTS.md` y `CLAUDE.md`, dentro de la sección «Roadmap de Changes», cambiar `CH-01 a CH-15` por `CH-01 a CH-16`, y reemplazar la mención `CH-14 ... y CH-15 ... figuran archivados el 2026-11-12. Primer y único change pendiente: CH-12 evidencia-entrega (...)` por una redacción que indique que CH-14, CH-15 y CH-16 figuran archivados el 2026-11-12 y que el único change abierto es CH-12 (tanda a mergeada; falta la tanda b, el zip), manteniendo el resto de la frase intacta. Verificar con:
  ```powershell
  git diff -U2 AGENTS.md CLAUDE.md
  Get-FileHash AGENTS.md, CLAUDE.md
  Select-String -Path AGENTS.md, CLAUDE.md -Pattern "CH-16", "tanda a mergeada", "CH-01 a CH-16" -Encoding UTF8
  ```
  Esperado: hashes SHA256 idénticos para ambos archivos y presencia de todos los términos clave esperados.

## 4. Registro en CHANGES.md y .active-orchestrator-state.json

- [x] 4.1 En `CHANGES.md`:
  - Agregar `CH-17` a la lista de la nota de convención de códigos (`CH-01`–`CH-12`, `CH-15`, `CH-16` y `CH-17`).
  - Agregar `CH-17` en el árbol de dependencias descendiendo de CH-16 y CH-12 tanda a.
  - Incorporar la entrada `### [CH-17] cierre-docs` con Estado `[ ]` pendiente, dependencias, scope documental y punteros de lectura previa.
  Verificar con:
  ```powershell
  git diff -U2 CHANGES.md
  & .\.venv\Scripts\python.exe -c "
  with open('CHANGES.md', 'rb') as f:
      content = f.read()
  lines = content.split(b'\n')
  bad = [i+1 for i, l in enumerate(lines[:-1]) if not l.endswith(b'\r')]
  print(f'Lineas sin CRLF en CHANGES.md: {len(bad)}')
  "
  ```
  Esperado: diff acotado y `Lineas sin CRLF en CHANGES.md: 0`.

- [x] 4.2 En `.active-orchestrator-state.json`:
  - Incrementar `roadmap.revision` de 5 a 6.
  - Agregar `"CH-17"` al arreglo `roadmap.changes`.
  Verificar con:
  ```powershell
  git diff -U1 .active-orchestrator-state.json
  & .\.venv\Scripts\python.exe -c "
  with open('.active-orchestrator-state.json', 'rb') as f:
      content = f.read()
  lines = content.split(b'\n')
  bad = [i+1 for i, l in enumerate(lines[:-1]) if not l.endswith(b'\r')]
  print(f'Lineas sin CRLF en .active-orchestrator-state.json: {len(bad)}')
  "
  ```
  Esperado: diff exacto y `Lineas sin CRLF en .active-orchestrator-state.json: 0`.
