# Proposal: ch-12-evidencia-entrega

## Why

El proyecto tiene el backend completo desplegado en el VPS, con el dataset de datos iniciales alineado a los ejemplos del enunciado (CH-15 completado) y la evidencia técnica de despliegue y consultas capturada. Para cerrar la entrega formal del parcial de Programación III se requiere consolidar la documentación operativa (`README.md` con pasos de despliegue desde cero, integrantes, endpoints y URL pública; `DEPLOY.md` con detalles de infraestructura y base compartida), organizar el índice y archivo histórico de la evidencia (`evidencia/`), y auditar exhaustivamente el historial de Git para certificar la ausencia absoluta de contraseñas o credenciales reales.

Esta propuesta organiza el change CH-12 en dos tandas:
- **Tanda a (alcance inmediato de este change)**: Actualización de `README.md`, `DEPLOY.md`, organización/reubicación documentada de evidencia local histórica vs vigente (`evidencia/`), actualización de una línea de comentario en `test/ch07-ventas-exito.http` hacia la ruta reubicada, auditoría de secretos en historial Git listando y clasificando cada coincidencia, actualización de notas en `CHANGES.md` (con alcance de tanda a y aclaración CH-14) y alineación de `AGENTS.md` y `CLAUDE.md`.
- **Tanda b (alcance diferido antes del archivo final de CH-12)**: Verificación del paquete `.zip` de entrega con `git archive` y `tar -tf` garantizando la exclusión de `.env`, `.venv` y `__pycache__`.

## What Changes

1. **`README.md`**:
   - Incorporación de nombres y apellidos de los integrantes: Mariano Chirino, Facundo Quiroga y Andrés Fabre.
   - Procedimiento paso a paso para levantar el proyecto desde cero en local (entorno virtual, instalación de dependencias desde `requirements.txt`, configuración de `.env` a partir de `env.example`, base PostgreSQL vacía, arranque con uvicorn que crea las tablas automáticamente, y carga de datos iniciales con `python -m app.seed`). Sin tocar la sección «Datos iniciales (seed)» salvo para enlazarla.
   - Declaración de la URL pública `http://libreria.marianochirino.me:8000` con enlaces a `/docs` y `/health/ready`, aclarando explícitamente que la raíz `/` y `/health` responden `404 Not Found` (comportamiento normal y esperado, ya que los endpoints inician en `/health/live`, `/health/ready`, etc.).
   - Sección «Entorno» aclarando que, según lo indicado por el profesor, la aplicación usa el PostgreSQL de la calculadora del grupo (`grupo10_db`) y no se requirieron datos de acceso adicionales.
   - Lista referencial de las dos ubicaciones de evidencia (`evidencia/` y `evidencia/ch-10-vps/`).
2. **`DEPLOY.md`**:
   - Completitud de la sección «Entorno» con la información de la base compartida (`grupo10_db`) según lo indicado por el profesor.
   - Actualización de la sección «Evidencia» para listar y detallar las dos ubicaciones vigentes (`evidencia/` y `evidencia/ch-10-vps/`) referenciando `evidencia/LEEME.md`.
   - Conservación deliberada de la marca `[A COMPLETAR: VPS asignado por la cátedra / propio del grupo]`, al no disponerse de dicha confirmación.
3. **`evidencia/` y suite de prueba**:
   - Traslado mediante `git mv` de los archivos `evidencia/C-07-libros-consultas.txt` y `evidencia/C-07-ventas-consultas.txt` (que registran consultas sobre libros 45 y 48, y ventas 11 y 12 en una base de desarrollo de CH-07) a la carpeta histórica `evidencia/ch-07-local/`.
   - Edición de una línea de comentario en `test/ch07-ventas-exito.http` (línea 41) para que apunte a `evidencia/ch-07-local/C-07-ventas-consultas.txt`, sin alterar ningún request ni aserción HTTP. Se preserva el archivo `tasks.md` archivado de CH-07 intacto (cita las rutas viejas) y `LEEME.md` aclara dicha referencia histórica.
   - Creación de `evidencia/LEEME.md` como índice explicativo y canónico que discrimine evidencia vigente (C-07 en `C-07-consola-sql.log` + `C-07-conteo.txt`; D-03, D-04, D-07 en raíz de `evidencia/`; D-01, D-02, D-05, D-06 en `evidencia/ch-10-vps/`) de la evidencia histórica de desarrollo local (`ch-03-local/` y `ch-07-local/`).
   - Verificación de existencia de los siete casos D y el caso C-07 sin tocar el VPS ni regenerar evidencia.
4. **Historial Git**:
   - Auditoría con `git log --all -p` exportado a `$env:TEMP\hist.txt` listando y clasificando cada coincidencia encontrada, certificando que no existen contraseñas reales.
5. **`CHANGES.md`**:
   - Incorporación de nota fechada `12/11/2026` en `[CH-12]` detallando el alcance de la tanda a (README, evidencia, historial) y tanda b (zip), manteniendo intactas las líneas originales de Scope.
   - Ajuste en la nota de CH-14 en `## Rectificaciones` aclarando la fecha de documentación (`2026-11-11`) vs fecha de archivo (`2026-11-12`).
   - Estado de CH-12 permanece `[ ]` pendiente.
   - Preservación estricta de finales de línea CRLF.
6. **`AGENTS.md` y `CLAUDE.md`**:
   - Actualización del párrafo de las líneas 47–52 para incluir CH-14 y CH-15 archivados y establecer a CH-12 como el único change pendiente del roadmap.
   - Mantenimiento de identidad binaria estricta entre ambos archivos (mismo hash SHA256).

## Capabilities

### New Capabilities
- Ninguna.

### Modified Capabilities
- Ninguna.

*(No se agregan ni modifican specs porque este change no modifica el comportamiento de la API).*

## Impact

- **Código de aplicación (`app/`)**: Ninguno (fuera de alcance).
- **Infraestructura y VPS**: Ninguno (fuera de alcance, no se altera el contenedor ni la base).
- **Tests y suites HTTP (`test/`)**: Actualización de una sola línea de comentario en `test/ch07-ventas-exito.http` (línea 41) actualizando la ruta referencial a `evidencia/ch-07-local/C-07-ventas-consultas.txt`; ningún request ni prueba funcional se modifica.
- **Documentación y metadatos**: `README.md`, `DEPLOY.md`, `evidencia/`, `CHANGES.md`, `AGENTS.md`, `CLAUDE.md`.
