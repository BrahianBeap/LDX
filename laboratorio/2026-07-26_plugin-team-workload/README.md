# Plugin "TeamWorkload" — vista de carga de trabajo por persona

> **Fecha de inicio:** 2026-07-26
> **Estado:** ✅ Fase 1 y v1.1 implementadas y probadas en `PFR-KANBOARD-TEST`.

## Objetivo

Agregar a Kanboard una pantalla que, dada una persona, muestre todas sus
tareas abiertas en todos los proyectos a los que pertenece — necesidad
identificada al migrar de Microsoft Planner (un solo plan) a Kanboard
(un proyecto por sistema, ver
[`../2026-07-25_migracion-planner-a-kanboard/`](../2026-07-25_migracion-planner-a-kanboard/)).

## Documentos de este experimento

- [`../2026-07-26_investigacion-vista-global-tareas-kanboard/informe.md`](../2026-07-26_investigacion-vista-global-tareas-kanboard/informe.md) —
  investigación de soluciones existentes (ninguna sirve tal cual),
  validación en vivo contra `PFR-KANBOARD-TEST`, y análisis de
  reutilización del Core. Es el documento de arquitectura de referencia.
- [`diseno-fase1.md`](diseno-fase1.md) — diseño técnico completo de la
  Fase 1 (arquitectura, flujo de datos, interfaz, modelo de permisos,
  riesgos), aprobado antes de escribir código.
- [`fase1-implementacion.md`](fase1-implementacion.md) — resultado real:
  archivos creados, despliegue, las 10 pruebas mínimas realizadas,
  hallazgos durante las pruebas (`ENABLE_URL_REWRITE=false` en esta
  instancia, traducciones al español pendientes de resolver) y
  procedimiento de rollback.
- [`diseno-v1.1.md`](diseno-v1.1.md) — diseño de la versión 1.1 (modo
  "👥 Todos", columna de responsable, resumen superior), con el análisis
  previo de reutilización del Core y el camino documentado (sin
  implementar) para futuros modos de agrupación.
- [`v1.1-implementacion.md`](v1.1-implementacion.md) — resultado real de
  la v1.1: archivos modificados, pruebas realizadas, y el hallazgo de que
  `Request::getIntegerParam()` del Core no puede leer valores negativos.
- [`src/TeamWorkload/`](src/TeamWorkload/) — código fuente del plugin,
  desplegado tal cual a `plugins/TeamWorkload/` en el contenedor.

## Filosofía de desarrollo (acordada con el usuario)

- Reutilizar siempre el Core antes de escribir código nuevo.
- No duplicar lógica existente.
- No modificar el Core de Kanboard.
- Mantener el plugin lo más pequeño posible.
- Minimizar el mantenimiento futuro.
- Mantener compatibilidad con futuras versiones de Kanboard.

## Progreso

| Paso | Estado |
|---|---|
| Investigación de soluciones existentes | ✅ Completado |
| Validación en vivo del Core | ✅ Completado |
| Análisis de reutilización del Core | ✅ Completado |
| Diseño técnico de la Fase 1 | ✅ Aprobado |
| Implementación de la Fase 1 | ✅ Completada — 9/10 pruebas pasaron, 1 pendiente por falta de una cuenta Standard en el entorno |
| Diseño técnico de v1.1 (modo "Todos", responsable, resumen) | ✅ Aprobado |
| Implementación de v1.1 | ✅ Completada — 8/8 pruebas pasaron |
| Fase 2 / v1.2 (filtros, agrupar por persona/prioridad/fecha, tags/categoría) | 🔴 No iniciada — camino de extensión ya documentado en `diseno-v1.1.md` |

## Pendientes conocidos (no bloquean lo ya entregado)

1. Investigar y corregir la carga de las traducciones al español del
   plugin (las cadenas propias del plugin se muestran en inglés).
2. Probar el rechazo de acceso con una cuenta `Standard` (no existe
   ninguna en este entorno — todos los usuarios reales quedaron con rol
   `app-admin`, ver el informe de investigación, sección 10.1).
3. Corregir los roles `app-admin` de los usuarios migrados.
4. Completar la asignación individual de las tareas que todavía tienen
   `owner_id = 0` en Kanboard (13 de 18 al momento de esta versión).
5. Evaluar la Fase 2 / v1.2 (filtros, agrupar por persona/prioridad/fecha,
   tags/categoría) en una tarea o sesión separada.
