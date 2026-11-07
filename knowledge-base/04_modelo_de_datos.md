# Modelo de Datos

> **Fuente de verdad**: `docs/Parcial_Cap1a4_Consigna.pdf` (16 páginas). Los nombres de tablas y columnas son **obligatorios** (los usan los casos de prueba y la corrección); se pueden agregar columnas, pero **no quitar ni renombrar** las indicadas. Denominación de tabla según la consigna: `libro_autor`, `perfil_cliente`, `renglon_venta` (en snake_case, no plural).

## Dominios
Catálogo (editorial, genero, autor, libro, libro_autor), clientes (cliente, perfil_cliente) y ventas (venta, renglon_venta). Ver `08_arquitectura_propuesta.md` para la estructura por módulo.

## ERD (descripción textual)
- `editorial` 1—N `libro` (agregación: el libro incorpora una editorial que ya existe; viaja su id; la misma editorial la comparten muchos libros).
- `genero` 1—N `libro` (agregación opcional: un libro puede no tener género; `genero_id` nulo permitido).
- `libro` N—M `autor` a través de `libro_autor` con datos `rol` y `orden` (muchos a muchos con datos; clase intermedia con su propia clase, no `link_model`; navegación `libro.autorias[i].autor`).
- `cliente` 1—0/1 `perfil_cliente` (uno a uno; `cliente_id` UNIQUE).
- `cliente` 1—N `venta` (asociación: la venta conoce al cliente que compró).
- `venta` 1—N `renglon_venta` (composición: el renglón no tiene sentido sin su venta; se crea con ella).
- `libro` 1—N `renglon_venta` (asociación: el renglón nombra un libro que ya existe).

## Entidades
### editorial
- Columnas: `id`, `nombre`, `pais`.
- Restricciones: `nombre` UNIQUE.

### genero
- Columnas: `id`, `nombre`.
- Restricciones: `nombre` UNIQUE.

### autor
- Columnas: `id`, `nombre`, `nacionalidad`.
- Restricciones: sin restricciones extra.

### libro
- Columnas: `id`, `isbn`, `titulo`, `precio` (NUMERIC(10,2)), `stock`, `editorial_id`, `genero_id` (nulo permitido).
- Restricciones: `isbn` UNIQUE; CHECK `precio > 0`; CHECK `stock ≥ 0`.
- Claves foráneas: `editorial_id`, `genero_id`.

### libro_autor
- Columnas: `libro_id`, `autor_id`, `rol`, `orden`.
- Restricciones: clave primaria (`libro_id`, `autor_id`); CHECK `orden ≥ 1`; CHECK `rol` dentro de `autor`, `coautor`, `traductor`, `ilustrador`.
- Índices: `libro_id` cubierto por la PK compuesta (`libro_id`, `autor_id`), sin índice propio adicional; `autor_id` lleva índice propio (necesario para navegar desde `autor`; la PK solo cubre el prefijo izquierdo `libro_id`, como `turno_practica.turno_id` en el TP anterior).

### cliente
- Columnas: `id`, `nombre`, `email`.
- Restricciones: `email` UNIQUE.

### perfil_cliente
- Columnas: `id`, `cliente_id`, `telefono`, `direccion`.
- Restricciones: `cliente_id` UNIQUE (uno a uno).

### venta
- Columnas: `id`, `cliente_id`, `fecha` (con zona horaria), `total` (NUMERIC(12,2)).
- Restricciones: CHECK `total ≥ 0`.
- Clave foránea: `cliente_id`.

### renglon_venta
- Columnas: `id`, `venta_id`, `libro_id`, `cantidad`, `precio_unitario` (NUMERIC(10,2)).
- Restricciones: CHECK `cantidad > 0`; CHECK `precio_unitario > 0`.
- Claves foráneas: `venta_id`, `libro_id`.

> Cada clave foránea lleva un índice (PostgreSQL no lo crea solo; excepción: `libro_autor.libro_id` cubierto por la PK compuesta — ver `libro_autor`) y navegación en los dos extremos con `Relationship(back_populates=.)`. El dinero se representa con `Decimal`, nunca con `float`. `Cliente.perfil` devuelve un objeto, no una lista.

## Seed data inicial
El proyecto incluye un script o comando que deja la base en un estado inicial conocido (para los casos de prueba y el despliegue en el VPS). Los ejemplos del enunciado son **referencias de forma**, no datos normativos literales:
- Venta con `cliente_id: 2` y renglones `libro_id: 1` (cantidad 2, precio 25000.00) y `libro_id: 4` (cantidad 1, precio 27000.00), total 77000.00, con títulos "Rayuela" y "Respiración artificial".
- Libro con autores `autor_id: 3` (coautor, orden 1) y `autor_id: 4` (coautor, orden 2), `editorial_id: 1`, `genero_id: 1`, ISBN `978-950-00-0006-6`, "Los que aman, odian", precio 21000.00, stock 4.

El contenido exacto del seed (qué filas, con qué ids) no lo fija el enunciado: queda definido por el implementador y debe ser **estable** para que los casos C-06/D-03 sean reproducibles. Ver 10_preguntas_abiertas.md.
