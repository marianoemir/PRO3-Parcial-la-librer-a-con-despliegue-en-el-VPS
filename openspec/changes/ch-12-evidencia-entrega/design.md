# Design: ch-12-evidencia-entrega

## Context

El proyecto se encuentra en su fase final de entrega para el parcial de Programación III. Todos los módulos del backend (`health`, `editoriales`, `generos`, `autores`, `libros`, `clientes`, `ventas`), la imagen Docker (`python:3.12-alpine`), el despliegue en VPS (CH-10 y CH-11 manual/ejecutado con evidencia verificada) y el dataset determinista alineado al enunciado (CH-15 completado) están listos.

Restricciones y estado actual:
- Mariano aprobó formalmente el 12/11/2026 la excepción O3+O1 documentada en CHANGES.md (entrada `[CH-15]`): CH-11 no cuenta con carpeta archivada en `openspec/changes/archive/`, pero su ejecución está acreditada por `DEPLOY.md` y las capturas reales de `evidencia/D-03-url-publica.txt`, `evidencia/D-04-persistencia.txt` y `evidencia/D-07-aviso-comprobante.txt`.
- No se deben inventar datos ausentes: ni el nombre del grupo ni la fecha límite están confirmados; tampoco si el VPS fue provisto por la cátedra o es propio del grupo.
- La URL pública `http://libreria.marianochirino.me:8000` responde 404 en `/` y `/health`, lo cual es el comportamiento normal y correcto del proyecto, pues los routers montados exponen `/health/live`, `/health/ready`, `/docs`, etc.
- No se tocan archivos de aplicación en `app/`, ni las peticiones ni respuestas funcionales en `test/` (solo una línea de comentario en `test/ch07-ventas-exito.http`), ni la infraestructura del VPS, ni se empaqueta el zip de entrega en esta tanda.

## Goals / Non-Goals

**Goals:**
- Estructurar e integrar en `README.md` toda la información de entrega: integrantes, guía de arranque desde cero (con comandos reales y existentes), URL pública y aclaración de endpoints 404, notas de entorno sobre la base compartida `grupo10_db` según lo indicado por el profesor, e índice de evidencia.
- Consolidar en `DEPLOY.md` los detalles de la base compartida según lo indicado por el profesor y el mapa de evidencias (`evidencia/` y `evidencia/ch-10-vps/`) referenciando `evidencia/LEEME.md`, preservando la marca `[A COMPLETAR: VPS asignado por la cátedra / propio del grupo]`.
- Organizar el directorio `evidencia/`: reubicar los archivos de prueba locales de CH-07 (`C-07-libros-consultas.txt` y `C-07-ventas-consultas.txt`) a `evidencia/ch-07-local/` preservando su trazabilidad histórica sin contaminar la evidencia vigente (`C-07-consola-sql.log` y `C-07-conteo.txt`), actualizar el comentario de `test/ch07-ventas-exito.http` (línea 41) a la ruta nueva, y redactar un `LEEME.md` exhaustivo aclarando la referencia histórica del `tasks.md` archivado de CH-07.
- Auditar y documentar que el historial Git está completamente libre de contraseñas reales.
- Registrar con precisión en `CHANGES.md` el alcance de tanda a y tanda b, y la aclaración de fechas de CH-14, conservando CRLF.
- Mantener `AGENTS.md` y `CLAUDE.md` perfectamente sincronizados (idénticos, mismo hash SHA256) reflejando a CH-12 como el único pendiente.

**Non-Goals:**
- Generar o verificar el `.zip` en esta tanda a (queda como Grupo 6 en tasks.md para la tanda b, sin cerrar CH-12 hasta entonces).
- Modificar el código fuente de `app/`, `Dockerfile` o `.dockerignore`.
- Modificar archivos en `openspec/changes/archive/`.
- Conectarse al VPS, regenerar evidencia o alterar el contenedor en producción.

## Decisions

### 1) Tratamiento y destino de los archivos C-07 locales de desarrollo
- **Decisión**: Mover mediante `git mv` los archivos `evidencia/C-07-libros-consultas.txt` y `evidencia/C-07-ventas-consultas.txt` a la carpeta histórica `evidencia/ch-07-local/`, actualizar el comentario de la línea 41 en `test/ch07-ventas-exito.http` hacia la ruta nueva, y crear `evidencia/LEEME.md` documentando la estructura completa.
- **Justificación**:
  1. *Patrón establecido de evidencia local de desarrollo*: La carpeta `evidencia/ch-07-local/` sigue exactamente el patrón de `evidencia/ch-03-local/`, reuniendo evidencia de desarrollo local para distinguirla de la evidencia de entrega y de VPS.
  2. *Contenido real de los archivos a mover*:
     - `C-07-libros-consultas.txt`: Registra consultas `GET /libros/45` (1 autor, autor_id=5) y `GET /libros/48` (3 autores, autor_ids=5,6,7) tomadas durante la verificación local de CH-07 en una base de desarrollo.
     - `C-07-ventas-consultas.txt`: Registra consultas `GET /ventas/11` (1 renglón, libro_id=45) y `GET /ventas/12` (3 renglones, libros_ids=45,46,47) ejecutadas contra un uvicorn en puerto 8010 durante el desarrollo de CH-07.
     - *(Separado de estos dos archivos: en el dataset de seed inicial de CH-08, antes de CH-15, el libro 6 estaba sembrado; en el seed actual de CH-15 no está sembrado y se crea con el POST del enunciado).*
  3. *Trazabilidad sin pérdida de información*: Eliminar los archivos destruiría la constatación histórica del trabajo del Agente A durante CH-07. Moverlos a `evidencia/ch-07-local/` preserva el historial de Git y aísla la evidencia histórica del entregable principal. El `tasks.md` archivado de CH-07 cita las rutas originales en su tarea 4.5; al estar archivado no se modifica y `evidencia/LEEME.md` documenta la equivalencia.
- **Alternativas rechazadas**:
  - *Dejarlos en la raíz de `evidencia/`*: Rechazado porque genera confusión con los conteos y datos vigentes de C-07 (`C-07-consola-sql.log` y `C-07-conteo.txt`).
  - *Eliminarlos (`git rm`)*: Rechazado porque se perdería el registro de cómo se validó inicialmente el caso C-07 durante el desarrollo del módulo de ventas.

### 2) Estructura de `evidencia/LEEME.md`
- **Decisión**: El archivo `evidencia/LEEME.md` se estructurará en tres bloques claros:
  1. **Evidencia vigente de entrega (en raíz `evidencia/`)**:
     - `C-07-consola-sql.log` y `C-07-conteo.txt`: Consultas capturadas de consola con `SQL_ECHO=true` demostrando la ausencia de N+1 (3 consultas para `POST /libros/`, `GET /libros/1` y `GET /libros/6`; 2 consultas para `GET /ventas/1` y `GET /ventas/2`; 3 consultas para `POST /ventas/`, exactamente como registra `C-07-conteo.txt`).
     - `D-03-url-publica.txt`: Ejecución del seed, `GET /health/ready`, `GET /libros/` y `POST /ventas/` desde afuera del VPS, en la URL pública.
     - `D-04-persistencia.txt`: Prueba de destrucción (`docker rm -f`) y recreación del contenedor manteniendo los datos persistidos en PostgreSQL.
     - `D-07-aviso-comprobante.txt`: Tarea en segundo plano (`BackgroundTasks`) que emite el aviso del comprobante con retraso simulado.
  2. **Evidencia del despliegue inicial en VPS (`evidencia/ch-10-vps/`)**:
     - `D-01-imagenes.txt`: Tamaños de imagen en el VPS (`python:3.12-alpine` y `libreria`).
     - `D-02-despliegue-limpio.txt` y `D-02-acceso-externo.txt`: Build y arranque inicial en el servidor, salud y tablas creadas.
     - `D-05-sin-database-url.txt`: Verificación de que sin variable de base de datos el contenedor termina con EXIT=1 (según el archivo).
     - `D-06-usuario-no-root.txt`: Ejecución con usuario sin privilegios `appuser`.
     - `recuperacion-healthy.txt`: Reanudación limpia de estado `healthy`.
     - `prueba-localhost.txt`: Verificación de fallo controlado por `Connection refused` al usar `localhost` en lugar del nombre de servicio `grupo10_db`.
  3. **Evidencia histórica local (`evidencia/ch-03-local/` y `evidencia/ch-07-local/`)**:
     - `ch-03-local/ch03-evidencia.md`: Evidencia de desarrollo capturada durante el apply local del change ch-03-docker-imagen en Windows (Docker Desktop) con la imagen `python:3.12-alpine`.
     - `ch-07-local/C-07-libros-consultas.txt` y `C-07-ventas-consultas.txt`: Consultas de la verificación local de CH-07 en base de desarrollo (libros 45, 48; ventas 11, 12). Incluye nota explícita aclarando que el `tasks.md` archivado de CH-07 (tarea 4.5) cita las rutas anteriores `evidencia/C-07-*-consultas.txt` y que hoy se ubican en esta subcarpeta histórica.

### 3) Alcance por tandas (Tanda a vs Tanda b)
- **Decisión**: Dividir formalmente el change en dos tandas de ejecución:
  - **Tanda a**:
    - Grupo 1: Edición y complementación de `README.md` (integrantes, pasos desde cero, URL pública, endpoints 404, base compartida `grupo10_db`, ubicaciones de evidencia).
    - Grupo 2: Edición de `DEPLOY.md` (entorno con base compartida, ubicaciones de evidencia referenciando `evidencia/LEEME.md`, preservación de `[A COMPLETAR: VPS asignado por la cátedra / propio del grupo]`).
    - Grupo 3: Reubicación de C-07 locales a `evidencia/ch-07-local/`, actualización de comentario en `test/ch07-ventas-exito.http` (línea 41) y creación de `evidencia/LEEME.md`.
    - Grupo 4: Auditoría del historial Git y verificación de no-secretos (búsqueda regex de patrones sobre `$env:TEMP\hist.txt`, clasificación de coincidencias y búsqueda de la IP 138.117.19.105).
    - Grupo 5: Actualización de notas de `CHANGES.md` (respetando CRLF y validando con script Python binario), y alineación idéntica de `AGENTS.md` y `CLAUDE.md`.
  - **Tanda b (Diferida)**:
    - Grupo 6: Generación y verificación del archivo `.zip` en `$env:TEMP\test-entrega.zip` mediante `git archive` y `tar -tf`, certificando que no contenga `(^|/)\.env$`, `.venv` ni `__pycache__`. Se ejecutará cuando se decida cerrar y archivar CH-12.

### 4) Tratamiento de especificaciones (Sin specs delta)
- **Decisión**: No se agregan specs en este change porque no modifica el comportamiento ni los contratos de la API.
- **Justificación**: CH-12 es un change estrictamente documental, de ordenamiento de evidencia y auditoría de seguridad del repositorio. No introduce nuevas funcionalidades a la API ni altera los requisitos ni contratos de comportamiento de los endpoints ya consolidados en `openspec/specs/`.

### 5) Registro formal de la situación de CH-11 y CH-14
- En el roadmap y en la documentación técnica queda explícito que CH-11 fue realizado manualmente en el VPS y no posee carpeta en `openspec/changes/archive/`. La recomendación O3 y nota O1 fue aprobada por Mariano el 12/11/2026.
- En `CHANGES.md`, la nota de CH-14 aclara que fue documentado el 11/11/2026 y formalmente archivado el 12/11/2026 tras la auditoría y specs correspondientes.

## Verifiable Scenarios

### Escenario 1 (Esperado — Documentación completa y accesible)
- **DADO** el archivo `README.md` actualizado
- **CUANDO** se inspecciona su contenido
- **ENTONCES** contiene:
  1. Los tres integrantes: Mariano Chirino, Facundo Quiroga y Andrés Fabre.
  2. Los pasos completos para levantar desde cero (venv, requirements.txt, .env desde env.example, base vacía, arranque con uvicorn que crea tablas, seed con `python -m app.seed`).
  3. La URL `http://libreria.marianochirino.me:8000` con enlaces a `/docs` y `/health/ready`.
  4. La aclaración explícita de que `/` y `/health` devuelven `404 Not Found`.
  5. La nota de entorno indicando el uso de `grupo10_db` según lo indicado por el profesor.
  6. La mención de las dos ubicaciones de evidencia (`evidencia/` y `evidencia/ch-10-vps/`).

### Escenario 2 (Error / Seguridad — Ausencia total de credenciales reales)
- **DADO** el repositorio en su estado de trabajo y en todo su historial Git (`git log --all -p`)
- **CUANDO** se auditan las coincidencias contra patrones regex de credenciales y contraseñas
- **ENTONCES** la auditoría lista y clasifica cada coincidencia (placeholder, falsa, enmascarada o real), y confirma que no existe ninguna contraseña real expuesta en ningún commit del historial ni en los archivos del árbol.

### Escenario 3 (Borde / Consistencia — Evidencia y archivos canónicos)
- **DADO** el directorio `evidencia/`, el repositorio y los archivos de instrucciones de agentes
- **CUANDO** se inspecciona el contenido de los archivos vigentes de evidencia, las rutas de referencias cruzadas y los hashes de `AGENTS.md` y `CLAUDE.md`
- **ENTONCES**:
  1. Ningún archivo en `evidencia/` (fuera de `ch-07-local/`) menciona "Bruno".
  2. «Los que aman» aparece en los archivos vigentes de `evidencia/` (excluida `ch-07-local/`) en una única línea en `C-07-consola-sql.log`, correspondiente a los parámetros del `INSERT INTO libro` generado por el `POST /libros/` del ejemplo del PDF, sin ninguna otra mención ni resultados de SELECT de dicho libro en el log.
  3. Los archivos `C-07-libros-consultas.txt` y `C-07-ventas-consultas.txt` residen en `evidencia/ch-07-local/`.
  4. `evidencia/LEEME.md` existe y mapea con precisión los 7 casos D y el caso C-07.
  5. `AGENTS.md` y `CLAUDE.md` son idénticos bit a bit (`Get-FileHash` arroja el mismo SHA256), no contienen la frase obsoleta "CH-01 a CH-13", y contienen "CH-15", indicando que CH-12 es el único pendiente.
  6. `git grep -n -e "C-07-libros-consultas" -e "C-07-ventas-consultas"` devuelve solo el `tasks.md` archivado de CH-07 y las rutas nuevas `evidencia/ch-07-local/` (ninguna ruta vieja huérfana en el árbol de trabajo).

## Risks / Trade-offs

- **[Riesgo de divergencia entre AGENTS.md y CLAUDE.md]** → Mitigación: Toda modificación se aplica en espejo y se valida mediante comparación estricta de hash SHA256 antes de dar por concluida la tarea.
- **[Riesgo de alteración de finales de línea en CHANGES.md]** → Mitigación: Se respeta estrictamente CRLF y se verifica mediante script de Python en modo binario (`'rb'`) asegurando cero líneas con salto simple `\n` huérfano.
- **[Riesgo de confusión sobre endpoints 404]** → Mitigación: El `README.md` documenta explícitamente que la raíz y `/health` no forman parte de los paths definidos por la consigna y devuelven 404, dirigiendo al corrector a `/docs` y `/health/ready`.
