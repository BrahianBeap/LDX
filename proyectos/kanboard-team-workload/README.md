# Plugin "TeamWorkload" — vista de carga de trabajo por persona

> **Fecha de inicio:** 2026-07-26
> **Estado:** ✅ Fase 1 y v1.1 implementadas y probadas en `PFR-KANBOARD-TEST`.
> **Reorganizado el 2026-07-27:** este proyecto vivía dentro de
> `laboratorio/` como dos experimentos separados. Se promovió a su propia
> carpeta al dejar de ser un experimento puntual y pasar a ser un
> artefacto de software con su propio ciclo de versiones — ver
> [`CHANGELOG.md`](CHANGELOG.md).

## Objetivo

Agregar a Kanboard una pantalla que, dada una persona (o "todas" desde la
v1.1), muestre las tareas abiertas en todos los proyectos a los que
pertenece — necesidad identificada al migrar de Microsoft Planner (un
solo plan) a Kanboard (un proyecto por sistema, ver
[`laboratorio/2026-07-25_migracion-planner-a-kanboard/`](../../laboratorio/2026-07-25_migracion-planner-a-kanboard/)).

## Documentación

| Documento | Contenido |
|---|---|
| [`docs/00_Arquitectura.md`](docs/00_Arquitectura.md) | **Cómo funciona el plugin hoy** — se actualiza en cada versión. Punto de partida para cualquiera que llegue nuevo al proyecto |
| [`docs/01_Investigacion.md`](docs/01_Investigacion.md) | Por qué existe este plugin: investigación de soluciones existentes (ninguna sirve tal cual), validación en vivo del Core de Kanboard, y el análisis de reutilización que definió la arquitectura |
| [`CHANGELOG.md`](CHANGELOG.md) | Historial de versiones del plugin |
| [`docs/decisiones/`](docs/decisiones/) | Registro histórico, uno por versión: por qué se diseñó así y qué se probó. No se reescribe — funciona igual que los ADR de la documentación general de LDX |
| [`src/TeamWorkload/`](src/TeamWorkload/) | Código fuente del plugin, desplegado tal cual a `plugins/TeamWorkload/` en el contenedor de prueba |

## Filosofía de desarrollo (acordada con el usuario)

- Reutilizar siempre el Core antes de escribir código nuevo.
- No duplicar lógica existente.
- No modificar el Core de Kanboard.
- Mantener el plugin lo más pequeño posible.
- Minimizar el mantenimiento futuro.
- Mantener compatibilidad con futuras versiones de Kanboard.

## Estado actual

| Versión | Estado |
|---|---|
| Investigación previa | ✅ Completada — [`docs/01_Investigacion.md`](docs/01_Investigacion.md) |
| Fase 1 | ✅ Completada — 9/10 pruebas pasaron, 1 pendiente por falta de una cuenta Standard en el entorno |
| v1.1 | ✅ Completada — 8/8 pruebas pasaron |
| Próxima versión (filtros, agrupar por persona/prioridad/fecha, tags/categoría) | 🔴 No iniciada — camino de extensión ya documentado en [`docs/decisiones/diseno-v1.1.md`](docs/decisiones/diseno-v1.1.md) |

Detalle completo de cada versión en [`CHANGELOG.md`](CHANGELOG.md).

## Pendientes conocidos (no bloquean lo ya entregado)

1. Investigar y corregir la carga de las traducciones al español del
   plugin (las cadenas propias del plugin se muestran en inglés).
2. Probar el rechazo de acceso con una cuenta `Standard` (no existe
   ninguna en este entorno — todos los usuarios reales quedaron con rol
   `app-admin`, ver [`docs/01_Investigacion.md`](docs/01_Investigacion.md), sección 10.1).
3. Corregir los roles `app-admin` de los usuarios migrados.
4. Completar la asignación individual de las tareas que todavía tienen
   `owner_id = 0` en Kanboard (13 de 18 al momento de la v1.1).
5. Evaluar la próxima versión (filtros, agrupar por persona/prioridad/fecha,
   tags/categoría) en una tarea o sesión separada.
