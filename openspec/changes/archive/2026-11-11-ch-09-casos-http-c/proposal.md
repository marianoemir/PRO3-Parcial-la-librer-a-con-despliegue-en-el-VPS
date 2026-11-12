# Proposal

## Why

El enunciado exige que la entrega incluya archivos `test/*.http` que demuestren los casos mínimos C-01 a C-08. Tras CH-08 existe un dataset determinista y una secuencia de alta conocida, por lo que ahora puede consolidarse una batería ejecutable, repetible y atribuida a Andrés sin invadir los módulos de dominio ni la evidencia de despliegue.

## What Changes

- Incorporar archivos `test/ch09-c*.http` que cubran C-01 a C-08 con método, ruta, cuerpo, código esperado y aserciones de forma/valores relevantes.
- Documentar el ciclo seguro de datos: base local dedicada y vacía, arranque para crear el esquema, ejecución de `python -m app.seed` y servidor apuntando a esa base; no se usan credenciales ni se modifica el seed.
- Hacer repetibles las solicitudes de escritura mediante datos del seed y nombres/ISBN/emails exclusivos de CH-09 cuando sean necesarios; las ejecuciones posteriores deben conservar expectativas que no dependan de ids de ventas crecientes.
- Mantener C-07 como solicitudes HTTP de detalle y guía de ejecución con `SQL_ECHO=true`; la captura/conteo real de consola queda para CH-12.
- Verificar los 409 de C-02, C-04 y C-05 sin depender de texto interno de PostgreSQL, conforme RN-12.

## Capabilities

### New Capabilities

Ninguna. Este change agrega artefactos de verificación para contratos ya publicados; no introduce comportamiento del sistema.

### Modified Capabilities

Ninguna. No cambian requisitos ni contratos HTTP de las capacidades existentes.

> Se declara `skip_specs: true` en `.openspec.yaml` porque se trata exclusivamente de batería de pruebas/documentación de ejecución; no corresponde inventar un delta de comportamiento para satisfacer validación.

## Impact

- **Artefactos:** nuevos archivos `.http` bajo `test/`; no se modifica código de `app/`, modelos, routers, schemas, servicios, seed, Dockerfile ni `evidencia/`.
- **Cobertura:** C-01 a C-08 del PDF; RN-01, RN-02, RN-04 a RN-07, RN-09 a RN-12 y RT-01, RT-04, RT-05.
- **Dependencias:** CH-08 archivado y su `app/seed.py`/dataset estable (cliente 2, libros 1 y 4, venta 1, libro 6 con dos autorías).
- **Fuera de alcance:** casos D y despliegue/VPS; generación de evidencia de C-07 (CH-12); tests de borde, contratos adicionales o rangos ya cubiertos por los `.http` de CH-07, CH-08 y CH-13; cambios de código ante una falla (se reportan al dueño del módulo).
