# Bitácora — Migración Planner → Kanboard

Registro paso a paso de la carga manual, en el mismo orden que
[`README.md`](README.md).

---

## Paso 1 — Crear usuarios locales

**Estado: ✅ Completada** (2026-07-25)

Usuarios creados, rol Standard, formato `nombre.apellido`:

- [x] Rocío Duarte → `rocio.duarte`
- [x] Bruno Miño → `bruno.mino`
- [x] Natalia Duarte → `natalia.duarte`
- [x] Elías Alfonzo → `elias.alfonzo`
- [x] Daniel Medina → `daniel.medina`
- [x] Marcos Casco → `marcos.casco`
- [x] Norberto Núñez → `norberto.nunez`
- [x] Andrés Semidei → `andres.semidei`
- [x] Fernando Fleitas → `fernando.fleitas`

---

## ⚠️ Cambio de enfoque #1 (2026-07-25) — 🔴 superado por el Cambio #2 más abajo

Después de crear los usuarios, se decidió **no** usar un único proyecto
"Proyectos OSS" con tags — en su lugar, cada etiqueta del Planner pasaría
a ser su propio proyecto de Kanboard, con identificador en mayúsculas
(ej. `adm-tech` → `ADMTECH`) y las mismas 4 columnas genéricas (`BackLog`,
`En Curso`, `En Revisión`, `Realizados`) para todos los proyectos.

**Esto se refinó más el mismo día — ver el Cambio de enfoque #2.**

---

## ⚠️ Cambio de enfoque #2 (2026-07-25) — vigente

Después de trabajar directamente en Kanboard, se formalizó un estándar
completo de organización. Ver
[`estandar-organizacion-kanboard.md`](estandar-organizacion-kanboard.md)
para el documento completo. Resumen de lo que cambia respecto al Cambio
#1:

- Cada proyecto define **su propio flujo de columnas** — ya no son 4
  columnas genéricas iguales para todos. INFRAWORK (proyecto de
  desarrollo) usa 5: `Pendiente de Análisis`, `Listo para Desarrollo`,
  `En Curso`, `En Revisión`, `Realizados`.
- Los títulos de tarea se reescriben con la convención
  `<Módulo> - <Funcionalidad>`, no se copian literales de Planner.
- Los tags de Kanboard se reservan para clasificación funcional/técnica
  (Backend, Frontend, Reportes, etc.) — nunca para nombres de proyecto ni
  de personas.
- Cada tarea importante se documenta con Objetivo/Alcance/Objetivos
  específicos/Resultado esperado (y Subtareas/Validaciones/
  Consideraciones técnicas si es un desarrollo grande).

**Proyectos identificados hasta ahora:** INFRAWORK (piloto), ADM-TECH,
VulnApp, SOC, Portal OSS.

🔴 **Pendiente de confirmar — mapeo de categorías viejas de Planner a
estos proyectos nuevos.** Las etiquetas originales de Planner que
todavía no tienen un proyecto nuevo claramente asignado:

| Etiqueta original de Planner | Cant. tareas | Posible destino |
|---|---|---|
| NCE | 1 | 🔴 A confirmar — ¿VulnApp? (ambas tareas de NCE/NCE-FAN son de "Gestión de Inventario - Vulnerabilidades") |
| NCE-FAN | 1 | 🔴 A confirmar — ¿VulnApp? |
| ODCIMLISY | 1 | 🔴 A confirmar |
| Video Wall | 1 | 🔴 A confirmar |
| OSS | 1 | 🔴 A confirmar — ¿Portal OSS? |
| TEMBIAPO - SIGAT | 1 | 🔴 A confirmar |
| Tembiapo OS | 2 | 🔴 A confirmar |
| (sin etiqueta, 7 tareas) | 7 | 🔴 A confirmar — ¿Portal OSS o un proyecto general aparte? |

No se asume ninguno de estos mapeos sin confirmación explícita — evitar
inventar a qué proyecto nuevo corresponde cada tarea vieja.

---

## Proyecto: INFRAWORK (8 tareas) — piloto del estándar

**Estado: ✅ Completado (2026-07-26)** — se toma como referencia metodológica para el resto de los proyectos.

- [x] Proyecto creado (nombre `INFRAWORK`, identificador `INFRAWORK`)
- [x] Flujo de columnas definido: `Pendiente de Análisis` → `Listo para Desarrollo` → `En Curso` → `En Revisión` → `Realizados`
- [x] Usuarios agregados como miembros de este proyecto (los 9 usuarios del Paso 1, no solo creados globalmente)
- [x] Primeras tareas migradas desde Planner
- [x] Descripciones estandarizadas (Objetivo/Alcance/Resultado esperado)
- [x] Subtareas documentadas
- [x] Etiquetas reorganizadas (funcionales/técnicas, no por sistema)

### Tareas de origen (Planner) — referencia, los títulos finales en Kanboard siguen la convención `<Módulo> - <Funcionalidad>`

- [ ] [BackLog] INFRAWORK - DEVENGAMIENTO
- [ ] [BackLog] INFRAWORK - Notas de acceso
- [ ] [BackLog] INFRAWORK - ZRE - CARGA MASIVA
- [ ] [BackLog] #INFRAWORK - Integracion Pedido Proveedor - Incidencias
- [ ] [BackLog] INFRAWORK - MODULO ENERGIA
- [ ] [BackLog] INFRAWORK - Reporte ZRE Alquiler de Sitios
- [ ] [En Revisión] INFRAWORK - Optimización / Compras informe sitios.
- [ ] [Realizados] INFRAWORK - Ficha tecnica

---

## Proyecto: ADM-TECH — segundo proyecto de referencia

**Estado: ✅ Completado (2026-07-26)** — migrado con la misma metodología que INFRAWORK.

Corresponde a la etiqueta `adm-tech` de Planner (4 tareas).

### Análisis del tipo de trabajo (antes de definir el flujo)

Las 4 tareas de origen, según `planner-data.json`:

| Tarea (título original Planner) | Bucket origen | Vencimiento | Asignados | Naturaleza |
|---|---|---|---|---|
| ADM-TECH - Actualizaciones administrativas | BackLog | 5 jul 2026 | Elías Alfonzo | Permitir edición de datos en estados posteriores + auditoría |
| ADM-TECH - Update masivo | BackLog | 31 dic 2026 | Elías Alfonzo | Edición masiva de campos + auditoría |
| ADM-TECH - Devoluciones pendientes | BackLog | 31 dic 2026 | Elías Alfonzo | Vista de control (materiales pendientes de devolución, alertas por correo) |
| ADM-TECH - Línea Capex (CTO) | En Curso | 31 jul 2026 | Elías Alfonzo, Daniel Medina, Marcos Casco | Importante — en curso, con imagen adjunta (`linea_capex_2.png`) |

🟡 **Inferencia razonable:** las 4 tareas son mejoras/funcionalidades nuevas
sobre un sistema administrativo ya existente (probablemente el mismo
sistema de gestión de reservas/materiales que aparece en varias tareas de
INFRAWORK) — no son incidentes ni soporte reactivo. Por naturaleza es un
proyecto de **desarrollo**, igual que INFRAWORK, pero con un volumen mucho
menor (4 tareas vs. 8) y sin evidencia de una etapa formal de análisis
separada del desarrollo en el uso real que se le daba en Planner (todas
nacían directo en BackLog o En Curso).

⚠️ Los textos de descripción capturados están **truncados a 200
caracteres** por la herramienta de extracción — antes de escribir la
descripción estandarizada final de cada tarea hay que abrir la tarea real
en Planner y copiar el contenido completo (mismo cuidado que ya se tomó
con el campo `checklist`, que tampoco es confiable).

### Flujo confirmado para ADM-TECH (2026-07-26)

Decisión del usuario: aunque ADM-TECH tiene menos tareas que INFRAWORK,
ambos son proyectos de tipo **Desarrollo** y deben mantener el mismo
estándar de flujo entre sí (ver
[`estandar-organizacion-kanboard.md`](estandar-organizacion-kanboard.md),
punto 2 — INFRAWORK como plantilla para todo proyecto de tipo Desarrollo).
Se descarta la propuesta de flujo corto de 4 columnas evaluada antes.

1. `Pendiente de Análisis`
2. `Listo para Desarrollo`
3. `En Curso`
4. `En Revisión`
5. `Realizados`

Miembros: los mismos 9 usuarios que en INFRAWORK (no solo los 3 asignados
en las tareas de origen), por el mismo criterio ya aplicado ahí.

### Carga finalizada (2026-07-26)

Realizado íntegramente de forma manual por el usuario en la interfaz web
de Kanboard — Claude Code no ejecutó ninguna acción sobre Kanboard (ni
API, ni CLI, ni base de datos), solo documentó el proceso.

- [x] Proyecto `ADM-TECH` creado
- [x] Flujo de columnas configurado (5 columnas, igual que INFRAWORK)
- [x] Miembros agregados (mismos 9 usuarios que en INFRAWORK)
- [x] Tareas migradas con título `<Módulo> - <Funcionalidad>`
- [x] Descripciones mejoradas (Objetivo/Alcance/Resultado esperado)
- [x] Subtareas agregadas donde correspondía a una acción concreta de trabajo
- [x] Reuniones, decisiones y avances registrados como comentarios en cada tarea (uso nuevo, ver punto 5 del estándar)
- [x] Etiquetas funcionales/técnicas asignadas

## Proyecto: SOC (6 tareas del Planner) — 🔴 Pendiente crear

## Proyecto: VulnApp — 🔴 Pendiente crear y confirmar alcance

Candidato para agrupar las tareas de vulnerabilidades (`NCE`, `NCE-FAN` —
ver tabla de mapeo pendiente arriba).

## Proyecto: Portal OSS — 🔴 Pendiente crear y confirmar alcance

Candidato para las tareas sin etiqueta y/o la etiqueta `OSS` — ver tabla
de mapeo pendiente arriba.

---

## Notas y decisiones transversales

### Tareas de origen ambiguo (verificar contra Planner antes de cargar)

"Tembiapo - Viaticos" e "INFRAWORK - Optimización / Compras informe
sitios." aparecieron en la extracción automática asociadas a "En
Revisión", pero ambas tienen texto de "Completada por..." (lo que sugiere
que en realidad están en Realizados o en otra columna intermedia no
capturada). **Verificar manualmente en Planner a qué columna pertenecen
antes de cargarlas.**

### Casos con más de un asignado (decisión a documentar)

Kanboard permite un solo asignado principal por tarea; Planner permite
varios. _(anotar acá qué se hizo caso por caso — ej. "INFRAWORK - ZRE -
CARGA MASIVA" tiene a Elías, Daniel y Marcos en Planner)_

---

## Verificación final

**Estado: 🔴 Pendiente**

Comparar los tableros finales de Kanboard (uno por proyecto) contra la
captura real de Planner (disponible en el scratchpad de la sesión:
`teams-screenshot-3.png`).
