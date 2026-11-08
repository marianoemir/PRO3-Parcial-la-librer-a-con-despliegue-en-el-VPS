# Spec Delta

## Purpose

Define el contrato observable de la fundación de la API: arranque asíncrono con creación de tablas, endpoints de salud, configuración por entorno sin secretos y sesiones por petición.

## ADDED Requirements

### Requirement: Arranque con creación de tablas y log
Al arrancar, el sistema SHALL crear el motor asíncrono y la fábrica de sesiones, guardarlos en el estado de la aplicación, ejecutar la creación de tablas que falten con todos los modelos importados y escribir una línea de log de arranque tras la creación, aunque el diagnóstico de consultas esté desactivado. Si la base no responde, el arranque SHALL fallar y el proceso no SHALL quedar sirviendo.

#### Scenario: Arranque exitoso con log visible (lista de tablas vacía hasta CH-02)
- **WHEN** se inicia la aplicación con `DATABASE_URL` válida y la base responde
- **THEN** el proceso queda sirviendo en `0.0.0.0` y el log muestra una línea de arranque con la lista de tablas creadas (vacía en CH-01, porque los modelos de dominio llegan recién en CH-02). La verificación completa de "tablas creadas sobre base vacía" se completa en CH-02, cuando exista al menos un modelo registrado.
- **Note**: el log de arranque no imprime `DATABASE_URL` ni credenciales

#### Scenario: Base sin respuesta bloquea el arranque
- **WHEN** la base no responde durante la creación de tablas
- **THEN** el arranque falla, el proceso termina con error y no queda sirviendo

### Requirement: Endpoint de salud del proceso
`GET /health/live` SHALL responder 200 con el cuerpo exacto `{"estado": "vivo"}` y SHALL NOT consultar la base de datos.

#### Scenario: Proceso vivo sin tocar la base
- **WHEN** la aplicación se arrancó con la base viva, luego la base se detiene y se solicita `GET /health/live`
- **THEN** el sistema responde 200 con el cuerpo exacto `{"estado": "vivo"}`
- **Note**: con la base caída desde antes del arranque, el lifespan falla y no hay servicio que responder (ver "Base sin respuesta bloquea el arranque"); este escenario cubre la base caída en ejecución, con la app ya sirviendo

### Requirement: Endpoint de salud de la base
`GET /health/ready` SHALL ejecutar `SELECT 1` sobre la base y responder 200 con el cuerpo exacto `{"estado": "listo"}` cuando la base responde, y 503 con el cuerpo exacto `{"estado": "no listo"}` sin texto interno de la base cuando `SELECT 1` falla.

#### Scenario: Base disponible responde 200
- **WHEN** se solicita `GET /health/ready` y `SELECT 1` se ejecuta sin error
- **THEN** el sistema responde 200 con el cuerpo exacto `{"estado": "listo"}`

#### Scenario: Base no disponible responde según decisión del equipo pendiente
- **WHEN** la aplicación se arrancó con la base viva, luego la base se detiene y se solicita `GET /health/ready` (`SELECT 1` falla por base no disponible en ejecución)
- **THEN** el sistema responde 503 con el cuerpo exacto `{"estado": "no listo"}`, con cuerpo propio sin texto interno de la base (RN-12)
- **Note**: con la base caída desde antes del arranque, el lifespan falla y no hay servicio que responder (ver "Base sin respuesta bloquea el arranque"); este escenario cubre la base caída en ejecución, con la app ya sirviendo
- **Note**: **PENDIENTE — decisión del equipo pendiente de confirmación con cátedra (Q2, `knowledge-base/10_preguntas_abiertas.md` §(2)) — NO es regla del enunciado**; ese código solo condicionará el `HEALTHCHECK` de CH-03
- **Note**: El caso D-05 (sin `DATABASE_URL`) es independiente del 503 y no depende de él

### Requirement: Configuración por entorno sin secretos
Si `DATABASE_URL` no está definida o está vacía, el proceso SHALL terminar con un error claro y SHALL NOT usar valor por defecto, y SHALL NOT imprimir credenciales en el log. `env.example` SHALL incluir `DATABASE_URL` con forma `postgresql+asyncpg://` sin valores reales y `SQL_ECHO=false`, y la activación de diagnóstico de consultas SHALL leer `SQL_ECHO` con valor `false` por defecto.

#### Scenario: Arranque sin DATABASE_URL termina con error claro
- **WHEN** se inicia la aplicación sin la variable `DATABASE_URL`, o con `DATABASE_URL` vacía, o sin `.env` que la provea
- **THEN** el proceso termina con un error claro que nombra la variable faltante y no queda sirviendo, sin imprimir credenciales
- **Note**: `DATABASE_URL=` cuenta como ausente
- **Note**: `.env` SHALL estar excluido de versionado junto con `.venv/`, `__pycache__/`, `*.bak` y `.atl/` (vía el `.gitignore` preexistente, que se verifica y completa sin recrearse)
- **Note**: El log de arranque SHALL NOT imprimir `DATABASE_URL` ni credenciales

#### Scenario: Ejemplo de entorno sin secretos
- **WHEN** se revisa `env.example`
- **THEN** contiene `DATABASE_URL` con forma `postgresql+asyncpg://` sin credenciales reales y `SQL_ECHO=false`
- **Note**: `.env` SHALL estar excluido de versionado junto con `.venv/`, `__pycache__/`, `*.bak` y `.atl/` (vía el `.gitignore` preexistente, que se verifica y completa sin recrearse)

### Requirement: Sesiones por petición y cierre del motor
Cada petición que requiera base SHALL recibir una sesión propia con `expire_on_commit=False` provista por `get_session`. Al apagarse la aplicación, el motor SHALL cerrarse. Todos los handlers SHALL ser `async def` y la escucha SHALL realizarse en `0.0.0.0`.

#### Scenario: Sesión y cierre del motor
- **WHEN** se procesa una petición que usa la base y luego se apaga la aplicación
- **THEN** cada petición usa una sesión propia con `expire_on_commit=False` y el motor queda cerrado tras el apagado
