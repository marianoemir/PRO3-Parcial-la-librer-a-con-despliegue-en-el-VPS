# Decisión find-skill — Parcial Librería (2026-11-07)

## Instaladas en el proyecto (.agents/skills/)

| Skill | Origen global | Motivo |
|---|---|---|
| fastapi | `C:\Users\Mariano_Chirino\.agents\skills\fastapi\SKILL.md` (+ `references/`) | Oficial FastAPI: async handlers, lifespan, router/service fino. Alineada con stack impuesto. |
| sqlmodel | `C:\Users\Mariano_Chirino\.agents\skills\sqlmodel\SKILL.md` | Oficial SQLModel: Field/Relationship, separación models/schemas. |

Copiadas con `Copy-Item` el 2026-11-07. Globales quedan en disco pero fuera del repo.

## Descartadas (NO copiadas al proyecto)

| Skill | Motivo |
|---|---|
| docker-patterns | Centrada en Docker Compose, excluido por el enunciado. La KB `12_despliegue_docker_y_vps.md` ya cubre el contenedor (sin Compose). |
| api-testing | De Supertest/httpx/pytest, no de archivos `.http` (`test/*.http`) que exige la cátedra. |
| fastapi-async-patterns | Genérica; las reglas async ya las fijan RT-03 y RT-04 de la KB (`05_reglas_de_negocio.md`). |
