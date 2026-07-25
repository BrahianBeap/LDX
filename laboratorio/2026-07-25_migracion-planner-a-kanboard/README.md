# Migración de "Proyectos OSS" (Microsoft Planner) a Kanboard

> **Fecha:** 2026-07-25
> **Ejecutor:** Elías Alfonzo (carga manual, guiado)
> **Estado:** 🟡 En progreso
> **Objetivo de negocio:** Tener una demo funcional para mostrar el lunes al equipo, con el mismo contenido real que ya usan en Planner, para evaluar reemplazarlo por Kanboard.

> ⚠️ **El enfoque de organización cambió durante la ejecución.** Ver
> [`estandar-organizacion-kanboard.md`](estandar-organizacion-kanboard.md)
> para el criterio vigente (un proyecto por sistema/producto, flujo propio
> por proyecto, tags solo para clasificación funcional/técnica). Las
> secciones de este documento que describían el plan original quedan
> marcadas como **histórico/superadas** más abajo — se conservan para
> entender por qué se cambió, no como referencia a seguir.

---

## Origen de los datos

Contenido extraído por automatización de navegador (Playwright + Edge,
mismo método que con el OneNote de Norberto) desde Microsoft Teams →
equipo **OSS** → pestaña **"Proyectos OSS"** (Microsoft Planner embebido),
vista Panel. Ver `planner-data.json` para el volcado completo.

## Por qué carga manual y no un script

Se evaluaron 3 opciones (manual / API scripteada / híbrida). Se eligió
**manual por la interfaz web** por dos razones: menor riesgo antes de la
demo del lunes, y porque el usuario quería familiarizarse con el flujo
real de Kanboard mientras carga el contenido — no solo automatizar.

## Mapeo de conceptos (Planner → Kanboard)

🔴 **Histórico — superado.** Ver la fila de "Etiqueta" corregida abajo y
[`estandar-organizacion-kanboard.md`](estandar-organizacion-kanboard.md)
para el criterio vigente.

| Planner | Kanboard | Nota |
|---|---|---|
| Plan | (ya no aplica 1 a 1) | Un plan de Planner puede repartirse en **varios** proyectos de Kanboard, uno por sistema/producto — ver estándar |
| Etiqueta de color (identifica el sistema, ej. `adm-tech`, `SOC`) | **Proyecto** de Kanboard | ✅ Vigente: la etiqueta de Planner pasó a indicar en qué *proyecto* de Kanboard va la tarea, no en qué tag |
| Bucket | Columna del tablero | 1 a 1 **dentro de cada proyecto**, pero el nombre/cantidad de columnas ya no es fijo — cada proyecto define su propio flujo (ver estándar, punto 2) |
| Tarea | Tarea | 1 a 1, pero el título se reescribe según la convención `<Módulo> - <Funcionalidad>` (ver estándar, punto 3) — no se copia literal desde Planner |
| Elemento de checklist | Subtarea | 1 a 1 |
| Asignado (uno o varios) | Asignado | ⚠️ Kanboard permite un solo asignado principal — Planner permite varios. Ver bitácora para cómo se resolvió caso por caso |
| Prioridad (Urgente/Importante) | Color de tarea | Kanboard no tiene el mismo concepto nativo — se aproxima con color |
| "Completada por X el fecha" | Tarea cerrada (closed) | El detalle de quién/cuándo se documenta en la descripción o comentario si importa conservarlo |
| — | **Tag de Kanboard** | ✅ Nuevo concepto sin equivalente directo en Planner: clasificación funcional/técnica (Backend, Frontend, Reportes, etc.) — ver estándar, punto 4 |

## Inventario de origen

| Bucket | Cant. tareas |
|---|---|
| BackLog | 10 |
| En Curso | 10 |
| En Revisión | 1 (+ 2 casos sin columna confirmada, ver bitácora) |
| Realizados - Culminados | 10 |

**Personas a crear como usuario local:** Rocío Duarte, Bruno Miño,
Natalia Duarte, Elías Alfonzo, Daniel Medina, Marcos Casco, Norberto
Núñez, Andrés Semidei, Fernando Fleitas.

**Etiquetas de Planner encontradas** (ya no se crean como tags — cada una
se convierte en un candidato a **proyecto** de Kanboard, ver
[`estandar-organizacion-kanboard.md`](estandar-organizacion-kanboard.md)):
`adm-tech`, `INFRAWORK`, `SOC`, `NCE`, `NCE-FAN`, `ODCIMLISY`,
`Tembiapo OS`, `TEMBIAPO - SIGAT`, `OSS`, `Video Wall`.

Los tags reales de Kanboard (clasificación funcional/técnica) se definen
por proyecto, sobre la marcha, según el vocabulario del estándar.

## Progreso

Ver [`bitacora.md`](bitacora.md) para el detalle paso a paso, y
[`estandar-organizacion-kanboard.md`](estandar-organizacion-kanboard.md)
para el criterio de organización vigente.

| Paso | Estado |
|---|---|
| 1 — Usuarios locales | ✅ Completado |
| 2 — Proyecto piloto INFRAWORK creado, con flujo propio de 5 columnas | ✅ Completado |
| 3 — Usuarios agregados como miembros del proyecto INFRAWORK | 🟡 En progreso |
| 4 — Carga de tareas (título estandarizado, descripción, subtareas) | 🟡 En progreso |
| 5 — Repetir para el resto de los proyectos (ADM-TECH, VulnApp, Portal OSS, SOC, ...) | 🔴 Pendiente |
| 6 — Verificación visual final vs Planner | 🔴 Pendiente |
