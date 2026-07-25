# Estándar de organización de Kanboard

> **Estado:** ✅ Decisión confirmada por el equipo (2026-07-25)
> **Alcance:** Aplica a la migración de "Proyectos OSS" (Microsoft Planner)
> y a cualquier proyecto nuevo que se cargue en Kanboard de ahora en más,
> salvo que se indique explícitamente lo contrario.
> **Proyecto piloto de este estándar:** INFRAWORK.

Este documento reemplaza el enfoque inicial descrito en
[`README.md`](README.md) (un único proyecto "Proyectos OSS" con tags por
módulo). Después de trabajar directamente en Kanboard, el enfoque
evolucionó a lo que sigue.

---

## 1. Un proyecto = un sistema o producto

Cada sistema/producto importante tiene su **propio proyecto
independiente** en Kanboard. Un tablero nunca mezcla tareas de múltiples
aplicaciones distintas.

Proyectos identificados hasta ahora:

- INFRAWORK
- ADM-TECH
- VulnApp
- Portal OSS
- SOC
- (y los demás que vayan apareciendo)

Los proyectos con pocas tareas se evalúan más adelante para decidir si
quedan independientes o se agrupan — no hay que decidirlo de una.

## 2. Cada proyecto define su propio flujo de trabajo

No existe una estructura de columnas única para todos los proyectos. Cada
uno define el flujo que representa su proceso real de trabajo. Ejemplos
de tipo de proyecto y su flujo:

- Desarrollo
- Infraestructura
- Operaciones
- Documentación
- Auditoría
- Soporte
- Proyectos personales

**Ejemplo — INFRAWORK** (proyecto de desarrollo de software):

1. Pendiente de Análisis
2. Listo para Desarrollo
3. En Curso
4. En Revisión
5. Realizados

## 3. Convención de nombres de tareas

Formato: **`<Módulo> - <Funcionalidad>`**

Ejemplos:
- `Notas de Acceso - Refactorización Backend`
- `Compras - Workflow de Aprobaciones`
- `ZRE - Carga Masiva (Agosto 2026)`
- `Energía - Gestión de Consumos`
- `Fondo Fijo - Automatización de Arqueos`

**No se usan prefijos de tipo** (`BUG`, `MEJORA`, `DESARROLLO`, `REUNIÓN`,
`AUTOMATIZACIÓN`, `FEATURE`) — la columna del tablero ya indica el estado,
y el proyecto ya indica el sistema. Los títulos deben ser cortos, claros y
fáciles de identificar.

## 4. Uso de etiquetas (tags)

**Las etiquetas ya no representan proyectos.** Se usan únicamente para
clasificar información funcional o técnica dentro de un proyecto.

Vocabulario de etiquetas (usar las que tengan sentido, no es una lista
cerrada): `Backend`, `Frontend`, `Workflow`, `Auditoría`, `Compras`,
`Reportes`, `PDF`, `Correo`, `Documentación`, `Automatización`,
`GestiónSitios`, `Alquiler`, `Energía`, `ZRE`, `SOLPED`,
`ÓrdenesTrabajo`, `Excel`, `API`.

Reglas:
- **No** usar el nombre del proyecto como etiqueta dentro de sí mismo (ej. no usar la etiqueta `INFRAWORK` dentro del proyecto INFRAWORK — es redundante).
- **No** usar etiquetas con nombres de personas — los responsables ya los administra Kanboard (campo Assignee), y los solicitantes originales quedan registrados en la descripción de la tarea.

## 5. Estructura del contenido de cada tarea

Cuando tenga sentido, cada tarea importante incluye:

- Objetivo
- Alcance
- Objetivos específicos
- Resultado esperado

Para desarrollos grandes, además:

- Subtareas
- Resultado esperado por subtarea
- Validaciones
- Consideraciones técnicas

**Criterio:** cualquier desarrollador debe poder entender la tarea sin
necesidad de buscar el correo o mensaje original que la originó.

## 6. Objetivo de la migración (no es solo "copiar y pegar")

- Limpiar requerimientos antiguos.
- Mejorar la documentación de cada tarea.
- Estandarizar nombres.
- Separar correctamente los módulos.
- Crear una base de conocimiento técnica reutilizable.
- Mantener trazabilidad del análisis realizado.

## 7. Principios de organización (resumen)

- Cada proyecto representa un sistema o producto — nunca una mezcla.
- Cada proyecto puede definir su propio flujo de trabajo.
- Los nombres de tarea son simples, claros, y siguen `<Módulo> - <Funcionalidad>`.
- Las etiquetas son funcionales/técnicas — nunca proyectos ni personas.
- Cada tarea contiene suficiente contexto para retomarse meses después sin depender de memoria o correos externos.
- La estructura prioriza mantenibilidad, visibilidad del trabajo pendiente y reutilización del conocimiento — no uniformidad forzada entre proyectos distintos.

## Por qué se abandonó el enfoque de "un solo proyecto con tags"

El plan original (ver [`README.md`](README.md)) usaba las etiquetas de
Planner como tags dentro de un único proyecto "Proyectos OSS". Al
empezar a cargar datos reales se identificaron dos problemas:

1. Mezclar sistemas distintos (INFRAWORK, SOC, ADM-TECH, etc.) en un
   mismo tablero no refleja cómo trabaja realmente cada área — un tablero
   debería representar un producto, no una mezcla de aplicaciones.
2. Las etiquetas de Planner ya estaban usadas para identificar el
   *sistema* de la tarea (equivalente a "proyecto"), dejando sin uso real
   el concepto de tag de Kanboard para clasificación funcional/técnica —
   que es donde más valor aporta.
