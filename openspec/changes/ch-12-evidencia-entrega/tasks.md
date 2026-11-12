# Tasks: ch-12-evidencia-entrega

> **Nota de ejecución**: Este apply ejecuta solo los grupos 1 a 5. El grupo 6 (tanda b) NO se ejecuta ni se tilda; CH-12 no se archiva en este apply.

## 1. Actualización de README.md (Tanda a)

- [ ] 1.1 Incorporar en `README.md` la nómina de integrantes (Mariano Chirino, Facundo Quiroga, Andrés Fabre) y verificar mediante:
  ```powershell
  [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
  Get-Content -Encoding UTF8 README.md | Select-String "Mariano Chirino", "Facundo Quiroga", "Andrés Fabre"
  ```
  Esperado: las 3 líneas/nombres aparecen.
- [ ] 1.2 Agregar la guía paso a paso para levantar el proyecto desde cero en local (venv, `pip install -r requirements.txt`, copiar `env.example` a `.env`, base vacía, arranque con `uvicorn app.main:app` para crear tablas y seed con `python -m app.seed`), manteniendo intacta la sección «Datos iniciales (seed)» salvo enlaces, y verificar mediante:
  ```powershell
  [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
  @("venv", "pip install -r requirements.txt", "env.example", "uvicorn app.main:app", "python -m app.seed") | ForEach-Object {
      $term = $_
      $found = (Get-Content -Encoding UTF8 README.md | Select-String -SimpleMatch $term)
      [PSCustomObject]@{ Termino = $term; Encontrado = ($found -ne $null) }
  }
  ```
  Esperado: las 5 expresiones aparecen (`Encontrado = True` para todas).
- [ ] 1.3 Incorporar la URL pública `http://libreria.marianochirino.me:8000` con enlaces a `/docs` y `/health/ready`, aclarando explícitamente que la raíz `/` y `/health` devuelven `404 Not Found`, y verificar con:
  ```powershell
  [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
  Get-Content -Encoding UTF8 README.md | Select-String "http://libreria.marianochirino.me:8000", "/docs", "/health/ready", "404"
  ```
  Esperado: los términos de la URL pública y aclaración de 404 aparecen.
- [ ] 1.4 Agregar la sección «Entorno» con la descripción de la base compartida (`grupo10_db`) según lo indicado por el profesor y listar las dos ubicaciones de evidencia (`evidencia/` y `evidencia/ch-10-vps/`), verificando con:
  ```powershell
  [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
  Get-Content -Encoding UTF8 README.md | Select-String "indicado por el profesor", "grupo10_db", "ch-10-vps"
  ```
  Esperado: las referencias a «indicado por el profesor», «grupo10_db» y «ch-10-vps» aparecen en `README.md`.

## 2. Actualización de DEPLOY.md (Tanda a)

- [ ] 2.1 Completar en `DEPLOY.md` la sección «Entorno» con los detalles de la base compartida (`grupo10_db`) según lo indicado por el profesor, preservando la marca `[A COMPLETAR: VPS asignado por la cátedra / propio del grupo]`, y verificar con:
  ```powershell
  [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
  Get-Content -Encoding UTF8 DEPLOY.md | Select-String "indicado por el profesor", "\[A COMPLETAR: VPS asignado"
  ```
  Esperado: ambas cadenas aparecen en `DEPLOY.md`.
- [ ] 2.2 Actualizar la sección «Evidencia» de `DEPLOY.md` para describir con exactitud las dos ubicaciones (`evidencia/` y `evidencia/ch-10-vps/`) mencionando `LEEME.md`, y verificar con:
  ```powershell
  [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
  Get-Content -Encoding UTF8 DEPLOY.md | Select-String "LEEME.md"
  ```
  Esperado: la mención de «LEEME.md» aparece en la sección Evidencia de `DEPLOY.md`.

## 3. Organización y Documentación de evidencia/ (Tanda a)

- [ ] 3.1 Mover los archivos de consultas locales de CH-07 (`C-07-libros-consultas.txt` y `C-07-ventas-consultas.txt`) a la carpeta `evidencia/ch-07-local/` mediante `git mv` y verificar que no queden en la raíz de `evidencia/` mediante:
  ```powershell
  Test-Path evidencia\C-07-libros-consultas.txt, evidencia\C-07-ventas-consultas.txt
  Test-Path evidencia\ch-07-local\C-07-libros-consultas.txt, evidencia\ch-07-local\C-07-ventas-consultas.txt
  ```
  Esperado: `False, False` para la raíz y `True, True` para la subcarpeta histórica.
- [ ] 3.2 Crear `evidencia/LEEME.md` documentando el índice completo de evidencia (vigente: C-07 en `C-07-consola-sql.log` + `C-07-conteo.txt`; D-03, D-04, D-07 en raíz; D-01, D-02 en dos archivos, D-05, D-06 en `ch-10-vps/`; e histórico en `ch-03-local/` y `ch-07-local/`), incluyendo nota explícita de que el `tasks.md` archivado de CH-07 (tarea 4.5) cita las rutas anteriores `evidencia/C-07-*-consultas.txt` y que hoy se ubican en `evidencia/ch-07-local/`, y verificar con:
  ```powershell
  Test-Path evidencia\LEEME.md
  ```
  Esperado: `True`.
- [ ] 3.3 Confirmar mediante listado real que los 7 casos D y el caso C-07 están completos y accesibles sin tocar el VPS ni regenerar archivos, ejecutando:
  ```powershell
  [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
  Get-ChildItem -Recurse evidencia -Name
  ```
  Esperado:
  - En la raíz: `C-07-consola-sql.log`, `C-07-conteo.txt`, `D-03-url-publica.txt`, `D-04-persistencia.txt`, `D-07-aviso-comprobante.txt`, `LEEME.md`.
  - En `ch-10-vps/`: `D-01-imagenes.txt`, `D-02-acceso-externo.txt`, `D-02-despliegue-limpio.txt`, `D-05-sin-database-url.txt`, `D-06-usuario-no-root.txt`, `prueba-localhost.txt`, `recuperacion-healthy.txt`.
  - En `ch-07-local/`: `C-07-libros-consultas.txt`, `C-07-ventas-consultas.txt`.
  - En `ch-03-local/`: `ch03-evidencia.md`.
- [ ] 3.4 Verificar ocurrencias de «Los que aman» y «Bruno» en los archivos vigentes de `evidencia/` (excluyendo `ch-07-local/`):
  ```powershell
  [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
  $archivosVigentes = Get-ChildItem -Recurse evidencia | Where-Object { -not $_.PSIsContainer -and $_.FullName -notmatch "ch-07-local" }
  $losQueAman = $archivosVigentes | Select-String "Los que aman"
  Write-Host "Coincidencias 'Los que aman': $($losQueAman.Count)"
  $losQueAman | ForEach-Object { "$($_.Filename):$($_.LineNumber): $($_.Line)" }
  $bruno = $archivosVigentes | Select-String "Bruno"
  Write-Host "Coincidencias 'Bruno': $($bruno.Count)"
  ```
  Esperado: `Coincidencias 'Los que aman': 1` en `C-07-consola-sql.log` correspondiente a la tupla de parámetros del INSERT del libro 6; y `Coincidencias 'Bruno': 0`.
- [ ] 3.5 Editar la línea 41 de `test/ch07-ventas-exito.http` para que apunte a `evidencia/ch-07-local/C-07-ventas-consultas.txt` y verificar con:
  ```powershell
  git grep -n -e "C-07-libros-consultas" -e "C-07-ventas-consultas"
  ```
  Esperado: solo el `tasks.md` archivado de CH-07 y las rutas nuevas `evidencia/ch-07-local/`; ninguna ruta vieja fuera de lo archivado.

## 4. Auditoría de Historial Git y No-Secretos (Tanda a)

- [ ] 4.1 Exportar el historial completo de Git con diffs a un archivo fuera del repositorio y buscar patrones regex de contraseñas y credenciales:
  ```powershell
  [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
  git log --all -p | Out-File -Encoding utf8 "$env:TEMP\hist.txt"
  $patterns = @(
      'password',
      'passwd',
      'pwd',
      'secret',
      'token',
      'contrase',
      'postgresql\+asyncpg://[^:]+:[^@]+@',
      '\b[0-9a-fA-F]{32}\b'
  )
  foreach ($p in $patterns) {
      $hits = Select-String -Path "$env:TEMP\hist.txt" -Pattern $p
      $count = ($hits | Measure-Object).Count
      Write-Host "=== Patron: '$p' - Total coincidencias: $count ==="
      $hits | ForEach-Object {
          $lineTrimmed = $_.Line.Trim()
          if ($lineTrimmed.Length -gt 200) { $lineTrimmed = $lineTrimmed.Substring(0, 200) + "..." }
          "$($_.LineNumber): $lineTrimmed"
      }
  }
  ```
  Esperado: Mostrar la salida cruda y clasificar cada coincidencia (placeholder, falsa, enmascarada o real); ninguna contraseña real.
- [ ] 4.2 Revisar todo el árbol de archivos versionados con `git ls-files` para comprobar que no existan secretos ni `.env` versionado:
  ```powershell
  [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
  git ls-files .env
  git check-ignore .env
  Get-Content -Encoding UTF8 env.example | Select-String "DATABASE_URL"
  git ls-files | ForEach-Object {
      if (Test-Path $_ -PathType Leaf) {
          Select-String -Path $_ -Pattern 'postgresql\+asyncpg://[^:]+:[^@]+@'
      }
  }
  ```
  Esperado: `git ls-files .env` vacío; `git check-ignore .env` devuelve `.env`; la línea `DATABASE_URL` de `env.example` muestra formato de ejemplo sin valor real; y la búsqueda sobre `git ls-files` arroja cero cadenas de conexión con contraseña real.
- [ ] 4.3 (Solo verificación, sin editar): Buscar la IP `138.117.19.105` en `README.md`, `DEPLOY.md`, `evidencia/` y `openspec/` (sin tocar archivados) y reportar coincidencias:
  ```powershell
  [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
  Select-String -Path README.md, DEPLOY.md -Pattern '138\.117\.19\.105'
  Get-ChildItem -Recurse evidencia | Where-Object { -not $_.PSIsContainer } | Select-String '138\.117\.19\.105'
  Get-ChildItem -Recurse openspec | Where-Object { -not $_.PSIsContainer -and $_.FullName -notmatch "archive" } | Select-String '138\.117\.19\.105'
  ```
  Esperado: Listar coincidencias crudas en el informe final.

## 5. Actualización de CHANGES.md, AGENTS.md y CLAUDE.md (Tanda a)

- [ ] 5.1 En `CHANGES.md`, agregar en la entrada `[CH-12]` la nota fechada `12/11/2026` con el alcance de la tanda a y la tanda b sin alterar las líneas originales de Scope, y en `## Rectificaciones` aclarar las fechas de CH-14 (documentado 2026-11-11, archivado 2026-11-12), manteniendo CRLF y verificando con:
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
  Esperado: diff acotado a las líneas editadas y `Lineas sin CRLF: 0`.
- [ ] 5.2 Actualizar el párrafo de las líneas 47–52 de `AGENTS.md` y `CLAUDE.md` para quitar «CH-01 a CH-13» (decir «CH-01 a CH-15»), incluir CH-15 (seed fiel al enunciado, archivado 2026-11-12) junto a CH-14 y CH-12 como único pendiente, verificando identidad y términos con:
  ```powershell
  [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
  Get-FileHash AGENTS.md, CLAUDE.md
  Select-String -Path AGENTS.md, CLAUDE.md -Pattern "CH-01 a CH-13"
  Select-String -Path AGENTS.md, CLAUDE.md -Pattern "CH-15"
  ```
  Esperado: mismo hash SHA256 exacto para ambos archivos; `CH-01 a CH-13` arroja 0 coincidencias; y `CH-15` aparece presente en ambos.

## 6. Verificación de Entrega en Archivo .zip (Tanda b — Diferida para cierre de CH-12)

- [ ] 6.1 Generar archivo de empaquetado de prueba fuera del repositorio usando `git archive`:
  ```powershell
  git archive --format=zip --prefix=libreria/ -o "$env:TEMP\test-entrega.zip" HEAD
  ```
  Esperado: archivo `$env:TEMP\test-entrega.zip` generado fuera del workspace.
- [ ] 6.2 Certificar que el archivo empaquetado no incluya `.env`, `.venv` ni `__pycache__`:
  ```powershell
  tar -tf "$env:TEMP\test-entrega.zip" | Select-String '(^|/)\.env$', '\.venv', '__pycache__'
  ```
  Esperado: ninguna coincidencia (salida vacía).
- [ ] 6.3 Eliminar el archivo temporal `$env:TEMP\test-entrega.zip` tras la verificación sin dejar residuos en el repositorio:
  ```powershell
  Remove-Item "$env:TEMP\test-entrega.zip" -Force
  Test-Path "$env:TEMP\test-entrega.zip"
  ```
  Esperado: `False`.
