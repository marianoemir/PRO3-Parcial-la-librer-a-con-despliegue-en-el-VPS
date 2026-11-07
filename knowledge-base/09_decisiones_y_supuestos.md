# Decisiones y Supuestos

## Decisiones documentadas
### DD-01 — `libro_autor` como entidad intermedia con clase propia
**Decisión**: modelar `libro_autor` como objeto de asociación (`LibroAutor`) con `rol` y `orden`, no como `link_model` simple.
**Contexto**: la relación Libro–Autor es muchos a muchos con datos propios (rol y orden en la tapa) que no pertenecen ni al libro ni al autor.
**Alternativas consideradas**: una tabla intermedia sin clase (ocultaría los datos); columnas de autoría dentro del libro (no escala a varios autores).
**Justificación**: el enunciado lo impone explícitamente (sección "La tabla intermedia es una entidad").
**Trade-offs aceptados**: navegación en dos saltos (`libro.autorias[i].autor`) y una clase más que mantener.

### DD-02 — Las ventas no se modifican ni se dan de baja
**Decisión**: no hay PATCH de ventas (RN-08) ni endpoints DELETE de ningún recurso.
**Contexto**: la venta registra un hecho y el enunciado no define baja de ningún recurso.
**Justificación**: ventas registran un hecho; no modificarlas evita inconsistencias con precios ya copiados.
**Trade-offs aceptados**: las correcciones de errores de carga requieren intervención manual sobre la base.

### DD-03 — Un solo contenedor, sin Docker Compose
**Decisión**: despliegue de una imagen con `docker run` + `--env-file`; la base es la que ya tiene el servidor.
**Contexto**: el enunciado excluye Docker Compose y el `HEALTHCHECK` lo declara la propia imagen.
**Justificación**: reduce superficie de ataque y disco en el VPS; los datos viven en la base del servidor, no en el contenedor.
**Trade-offs aceptados**: la orquestación (reinicio, puertos, red) se gestiona manualmente con `docker run`/`docker ps`/`docker logs`.

### DD-04 — Garantías delegadas a la base, con traducción a 409 propio
**Decisión**: no consultar antes si un id existe; escribir y traducir el `IntegrityError` a un mensaje propio (RN-12, RT-02).
**Contexto**: delegar en la base las garantías que la base puede dar (unicidad, FK, CHECK).
**Justificación**: evita TOCTOU y, sobre todo, satisface RN-12 (ningún error revela texto interno).
**Trade-offs aceptados**: mensajes de error propios redactados por el service en lugar de los detalles de la base.

### DD-05 — Precio de renglón y total calculados por el servidor
**Decisión**: RN-06 y RN-07: `precio_unitario` se copia del libro y `total` se calcula en el servidor; ninguno viaja en el DTO.
**Contexto**: el cliente no debe poder falsificar precios.
**Justificación**: invariante del dominio; el snapshot del precio queda congelado aunque cambie el precio del libro.
**Trade-offs aceptados**: cambios de precio del libro no afectan ventas ya registradas (es el comportamiento deseado).

### DD-06 — Roadmap con el tramo Docker/VPS separado como changes propios
**Decisión**: separar el tramo Docker/VPS en changes propios para empezarlos temprano (indicación del equipo en el brief inicial, fuera del enunciado; no del orquestador).
**Contexto**: el despliegue en línea debe existir hasta que se publiquen las notas; empezar tarde arriesga el criterio del 10 %.
**Justificación**: el contenedor y el VPS son independientes del código del dominio y pueden desarrollarse en paralelo.
**Trade-offs aceptados**: coordinar los hitos del primer entregable (código + contenedor + despliegue) con changes separados.

## Supuestos inferidos
### SU-01 (confirmada) — Los símbolos de los CHECK de la consigna son `≥`
**Confirmada**: los CHECK de `stock`, `orden` y `total` son `stock >= 0`, `orden >= 1` y `total >= 0` (verificado en página 4 del PDF original `docs/Parcial_Cap1a4_Consigna.pdf`, donde aparece `≥`; la extracción de texto los truncaba como `= 0` / `= 1`).
**Origen**: tablas del modelo de dominio (página 4 del PDF original) + RN-03 ("stock nunca es negativo").
**Riesgo si es falso**: constraints incorrectos que impidan insertar datos válidos.
**Cómo validar**: validado contra página 4 del PDF original; los casos C-06/D-03 con datos típicos lo confirmarían en la implementación.

### SU-02 — `sale de expire_on_commit=False` y una sesión por petición
**Supuesto**: la sesión se crea por petición con `expire_on_commit=False` (impuesto por el enunciado, sección 4.5).
**Origen**: Ejercicio 1 de la consigna.
**Riesgo si es falso**: objetos expirados tras el commit que fuerzan cargas perezosas prohibidas.
**Cómo validar**: cualquier lectura con relaciones en tests de casos C-07.

### SU-03 — La entrega la sube un solo integrante y el zip va sin .venv, __pycache__, .env ni contraseñas en el historial
**Supuesto**: el historial de `.git`, si se incluye, está limpio de credenciales reales.
**Origen**: formato de entrega del enunciado.
**Riesgo si es falso**: si alguna vez se subió una contraseña y se borró después, sigue en el historial y hay que cambiarla además.
**Cómo validar**: revisión de `git log`/historial antes de empaquetar; verificar que `env.example` no tenga valores reales.
