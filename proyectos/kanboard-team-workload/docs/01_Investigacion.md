# Investigación - Vista global de tareas por usuario en Kanboard

> **Fecha:** 2026-07-26
> **Alcance:** Determinar si existe una funcionalidad nativa, plugin, fork o
> solución externa que permita ver, para una persona elegida, todas sus
> tareas abiertas en todos los proyectos de Kanboard a los que pertenece —
> y si no existe, diseñar una arquitectura de plugin propio.
> **Contexto de uso real:** ~15 usuarios, ~25 proyectos, volumen moderado de
> tareas activas (ver [`estandar-organizacion-kanboard.md`](../../../laboratorio/2026-07-25_migracion-planner-a-kanboard/estandar-organizacion-kanboard.md)).
> No se instaló ni modificó nada en Kanboard, no se tocó ninguna base de
> datos y no se clonó código de terceros a este repositorio.

Convención de clasificación usada en este informe: ✅ hecho comprobado
(verificado en código fuente, documentación oficial o fuente primaria) /
🟡 inferencia razonable (deducida de evidencia indirecta) / 🔴 pendiente de
verificación (no se pudo confirmar con las fuentes disponibles — requiere
prueba manual en el Kanboard real del equipo).

---

## 1. Necesidad analizada

El equipo migró su gestión de tareas desde Microsoft Planner a Kanboard
usando el modelo **un proyecto de Kanboard por sistema/producto**
(INFRAWORK, ADM-TECH, VulnApp, Portal OSS, SOC — ver
[`bitacora.md`](../../../laboratorio/2026-07-25_migracion-planner-a-kanboard/bitacora.md)).
Ese modelo resuelve la organización del trabajo por sistema, pero introduce
un problema nuevo que Planner no tenía: **una persona ya no tiene un solo
lugar donde ver todo lo que tiene asignado** — sus tareas están repartidas
entre proyectos independientes, cada uno con su propio tablero.

Se necesita una vista que, dado un usuario, muestre:

- Todas sus tareas **abiertas/activas**, en **todos los proyectos** a los
  que pertenece.
- Como mínimo por tarea: usuario, proyecto, tarea, columna/estado, fecha de
  vencimiento, prioridad, categoría/tags, enlace directo.
- Filtros por usuario, proyecto, columna y vencimiento.
- Idealmente una tabla resumen por usuario (Pendientes / En curso / En
  revisión / Total).

No es necesario diseñar para instalaciones masivas — con ~15 usuarios y
~25 proyectos, la prioridad es una solución simple y mantenible, no
performance a gran escala (se indica en la sección 9 qué cambiaría si esto
creciera mucho).

---

## 2. Capacidades nativas de Kanboard

### 2.1 Dashboard del usuario ("Mis tareas")

✅ Kanboard tiene un Dashboard por usuario (`DashboardController`,
[código fuente](https://github.com/kanboard/kanboard/blob/main/app/Controller/DashboardController.php))
con acciones `show()`, `tasks()`, `subtasks()`, `projects()`. Estas
acciones **sí agregan tareas de todos los proyectos activos del usuario**
en una sola vista — es decir, el problema de "multi-proyecto" ya está
resuelto para el caso de "mis propias tareas".

✅ El límite real: las cuatro acciones toman el `user_id` exclusivamente
de la sesión actual (`$this->getUser()['id']`), sin aceptar ningún
parámetro para consultar a otro usuario. Es decir, **cada persona solo
puede ver su propio Dashboard**, nunca el de otra. No hay forma nativa
(sin plugin) de que un responsable de equipo abra el Dashboard de otra
persona.

Vía JSON-RPC existe el equivalente `getMyDashboard`, `getMyOverdueTasks`,
`getMyProjectsList`, `getMyProjects`, `getMyActivityStream`
([Current User API Procedures](https://docs.kanboard.org/v1/api/me_procedures/))
— todos con el mismo límite: solo devuelven datos del usuario autenticado
que hace la llamada, nunca de un tercero.

### 2.2 El hallazgo más relevante: `ProjectUserOverviewController` (Core, no documentado)

✅ En el código fuente actual de Kanboard existe
[`app/Controller/ProjectUserOverviewController.php`](https://github.com/kanboard/kanboard/blob/main/app/Controller/ProjectUserOverviewController.php),
con acciones `managers()`, `members()`, `opens()`, `closed()`, `users()`.
Las acciones `opens()`/`closed()` hacen casi exactamente lo pedido:

- Reciben `user_id` como parámetro de la URL (`getIntegerParam('user_id', UserModel::EVERYBODY_ID)`).
- Calculan la lista de proyectos accesibles así: si quien consulta es
  admin, `projectModel->getAllIds()` (todos los proyectos); si no,
  `projectPermissionModel->getActiveProjectIds($viewer_id)` (los proyectos
  del que consulta, **no** los del usuario elegido — ver limitación abajo).
- Filtran tareas por `owner_id = user_id`, abiertas o cerradas según la
  acción, **en todos esos proyectos a la vez**.
- Renderizan una tabla plana (`project_user_overview/tasks`) con: ID de
  tarea (enlace a la tarea), **nombre del proyecto** (enlace al tablero),
  columna actual, título (enlace a la tarea), asignado, fecha de inicio y
  **fecha de vencimiento**.

✅ Esta página **no está documentada** en la guía de usuario oficial
(no aparece en [`docs.kanboard.org/v1/user/projects/`](https://docs.kanboard.org/v1/user/projects/)
ni en ninguna otra página de la documentación de usuario revisada) y **no
tiene un enlace visible en el menú estándar** — no se encontró ningún
lugar de la interfaz (lista de usuarios, dashboard, proyecto) que enlace a
ella. Se accede escribiendo la URL manualmente, con el patrón:

```
https://tu-kanboard/?controller=ProjectUserOverviewController&action=opens&user_id=<ID>
https://tu-kanboard/?controller=ProjectUserOverviewController&action=closed&user_id=<ID>
```

Esto quedó confirmado no solo por el código, sino por un uso real
reportado por un usuario de la comunidad en diciembre de 2025 usando
exactamente ese patrón de URL para la acción `managers`
([hilo del foro, dic. 2025](https://kanboard.discourse.group/t/toggle-open-or-closed-projects/3577)) —
es decir, la página sigue viva y funcional en versiones recientes, aunque
sea una funcionalidad "oculta"/heredada.

**Limitaciones reales de esta página, verificadas:**

| Limitación | Detalle |
|---|---|
| Alcance de proyectos = del que consulta, no del usuario elegido | Si un responsable no es miembro de todos los proyectos del usuario que quiere revisar, va a ver una lista incompleta. Solo un admin ve siempre el universo completo. |
| Sin agrupación por proyecto | La tabla es plana; no agrupa visualmente por proyecto como pide el mockup del punto de partida. |
| Sin prioridad ni tags/categoría | El template confirmado no incluye esos campos. |
| Sin selector de usuario en la UI | Hay que conocer/escribir el `user_id` en la URL; no hay un `<select>` de personas. |
| Sin tabla resumen (Pendientes/En curso/En revisión/Total) | No existe, habría que construirla aparte. |
| Sin filtros por columna o por rango de vencimiento | Solo separa abiertas (`opens`) vs. cerradas (`closed`). |

🟡 **Conclusión de esta sección:** el Core de Kanboard ya resuelve, sin
ningún plugin, la parte técnicamente más difícil del problema (consulta
multi-proyecto respetando permisos), pero como página de usuario está
incompleta y efectivamente oculta. No alcanza como solución "lista para
usar" tal como la pide el equipo, pero es la base ideal para construir
sobre ella (ver sección 9).

### 2.3 Consulta reutilizable en el modelo de tareas: `TaskFinderModel`

✅ [`app/Model/TaskFinderModel.php`](https://github.com/kanboard/kanboard/blob/main/app/Model/TaskFinderModel.php)
ya contiene la consulta exacta que hace falta:

- **`getUserQuery($user_id)`** — la que usa el propio Dashboard nativo:
  "tareas donde el usuario es el dueño (`owner_id`) o está asignado a una
  subtarea, filtrando tareas activas y proyectos activos, excluyendo
  columnas ocultas del dashboard". Ya recibe `$user_id` como parámetro
  arbitrario — el límite de "solo mi propio usuario" está en el
  **controlador** (`DashboardController`), no en el modelo.
- **`getProjectUserOverviewQuery(array $project_ids, $is_active)`** — la
  que usa `ProjectUserOverviewController`, ya pensada para múltiples
  proyectos a la vez.
- **`getOverdueTasksByUser($user_id)`** — tareas vencidas de un usuario
  específico, también ya multi-proyecto.

✅ Y en [`app/Pagination/TaskPagination.php`](https://github.com/kanboard/kanboard/blob/main/app/Pagination/TaskPagination.php),
`getDashboardPaginator($userId, $method, $max)` recibe `$userId` como
parámetro explícito y arma la paginación llamando a
`$this->taskFinderModel->getUserQuery($userId)` — es decir, **es
completamente reutilizable para cualquier usuario**, el Dashboard nativo
simplemente nunca lo invoca con otro `$userId` que no sea el de la sesión.

✅ [`app/Pagination/DashboardPagination.php`](https://github.com/kanboard/kanboard/blob/main/app/Pagination/DashboardPagination.php)
tiene un único método, `getOverview($userId)`, que recorre **todos los
proyectos activos** del usuario indicado (vía `projectUserRoleModel`) y
arma un paginador de tareas por proyecto — otra pieza ya lista para
reusar tal cual.

✅ Para resolver correctamente qué proyectos pertenecen al usuario
**elegido** (no al que consulta, corrigiendo la limitación 2.2),
`ProjectUserRoleModel` expone `getActiveProjectsByUser($user_id)` /
`getProjectsByUser($user_id)`, y `ProjectGroupRoleModel::getProjectsByUser($user_id)`
cubre el acceso heredado por grupo.

**Respuesta explícita a las preguntas planteadas:**

- **¿Existe una consulta equivalente?** Sí — varias, y todas ya
  parametrizadas por `user_id`.
- **¿Puede reutilizarse?** Sí, directamente, desde un plugin, sin tocar
  el Core (son modelos/paginadores inyectados por el contenedor de
  servicios, a los que cualquier plugin puede acceder).
- **¿Qué haría falta extender?** Tres cosas que hoy no existen: (1) un
  controlador que use el `user_id` **elegido** en vez del de la sesión y
  calcule sus proyectos con `getActiveProjectsByUser($user_id)`, (2) una
  plantilla que agrupe por proyecto y agregue prioridad/tags, y (3) la
  tabla resumen — no hay ningún método nativo que cuente tareas por
  "bucket lógico" (Pendiente/En curso/En revisión), porque Kanboard no
  tiene un concepto nativo de "tipo de columna" — cada proyecto nombra sus
  columnas libremente (más aún con nuestro propio estándar, que permite un
  flujo distinto por tipo de proyecto). Este punto se retoma como riesgo
  en la sección 9.

### 2.4 API JSON-RPC

✅ Revisando [Task API Procedures](https://docs.kanboard.org/v1/api/task_procedures/)
y [User API Procedures](https://docs.kanboard.org/v1/api/user_procedures/):
no existe ningún método que devuelva "todas las tareas abiertas de un
usuario en todos los proyectos" en una sola llamada. Los métodos de
tareas (`getAllTasks`, `searchTasks`, `getOverdueTasksByProject`, etc.)
son por proyecto (`project_id` obligatorio), con la única excepción de
`getOverdueTasks()` (vencidas, de todo el sistema, sin filtrar por
usuario) y `getOverdueTasksByUser($user_id)` — que si es multi-proyecto y
por usuario, pero limitado a vencidas, no a "todas las abiertas".

🟡 **Forma más limpia de resolverlo vía API, si se quisiera consumir desde
afuera de Kanboard** en vez de plugin: combinar `getAllUsers` +
`getAllProjects`/`getMyProjects` + iterar `searchTasks(project_id,
'assignee:"Nombre" status:open')` proyecto por proyecto. Con ~25
proyectos esto es perfectamente viable (25 llamadas JSON-RPC), pero
implica lógica externa (script, no una vista dentro de Kanboard) y no
resuelve la experiencia de uso que se busca (una pantalla dentro de
Kanboard mismo).

### 2.5 Buscador global / filtros

🟡 El cuadro de búsqueda/filtros con el lenguaje de consultas de Kanboard
(`assignee:`, `status:`, `due:`, etc. — ver
[Advanced Search Syntax](https://docs.kanboard.org/v1/user/search/)) vive
dentro del tablero de **un** proyecto. Los filtros personalizados
("Custom filters") se guardan **por proyecto** y, si su creador es
manager del proyecto, puede compartirlos con el resto — pero siguen
acotados a ese proyecto, no son globales. No existe en el Core un cuadro
de búsqueda único que abarque todos los proyectos a la vez (por eso
existen plugins de terceros como "Global Search", ver sección 4).

---

## 3. Plugins oficiales o listados por Kanboard

El catálogo oficial está en [kanboard.org/plugins.html](https://kanboard.org/plugins.html)
(sin proceso de revisión de código — cualquiera puede publicar el suyo,
según la propia [documentación de instalación de plugins](https://docs.kanboard.org/v1/admin/plugins/)).
De los plugins listados, los más cercanos a la necesidad son "Bigboard",
"TableView", "Global Search", "ProjectReports" y "HoursView" — todos
comunitarios, ninguno mantenido directamente por el equipo core de
Kanboard. Se analizan en la sección 4. **No existe ningún plugin propio
del equipo de Kanboard (organización `kanboard/` en GitHub) dedicado a
esto** — sus plugins oficiales son de integración (OAuth2, Slack, Google
Auth, GitHub, almacenamiento en BD), no de reportes/vistas.

---

## 4. Plugins comunitarios

| # | Nombre | Repositorio | Autor | Última actividad | Estado |
|---|---|---|---|---|---|
| 1 | BigBoard | [TimoStahl/kanboard_plugin_bigboard](https://github.com/TimoStahl/kanboard_plugin_bigboard) | Thomas Stinner (original), mantenido por TimoStahl y colaboradores | Último commit real: 22 mar. 2023 | Mantenimiento mínimo (sin desarrollo activo) |
| 2 | TableView | [greyaz/TableView](https://github.com/greyaz/TableView) | greyaz | Último commit: 23 ago. 2024. **Repositorio archivado por su dueño el 6 may. 2026** | Abandonado (archivado) |
| 3 | Tabler | [aljawaid/Tabler](https://github.com/aljawaid/Tabler) | aljawaid | No verificado en detalle (extensión de TableView) | 🔴 Sin verificar |
| 4 | Global Search | [kenlog/global-search-kanboard](https://github.com/kenlog/global-search-kanboard) | Valentino Pesce (kenlog) | 17 commits totales, 6 stars, 2 forks, 0 issues abiertas — fecha exacta del último commit no confirmada | Bajo uso, sin señales de abandono ni de actividad reciente confirmada |
| 5 | Group_assign | [creecros/Group_assign](https://github.com/creecros/Group_assign) (fork activo) y [davgit/KANBOARD-Group_assign](https://github.com/davgit/KANBOARD-Group_assign) | creecros / davgit | 🔴 Sin verificar en detalle | 🔴 Sin verificar |
| 6 | ProjectReports | [noredis/ProjectReports](https://github.com/noredis/ProjectReports) | noredis | 🔴 Sin verificar en detalle | 🔴 Sin verificar |
| 7 | HoursView → WeekHelper | [Tagirijus/HoursView](https://github.com/Tagirijus/HoursView) (discontinuado desde el 29 oct. 2023, fusionado en WeekHelper) | Tagirijus | Discontinuado explícitamente por el autor | Abandonado a favor de otro plugin |

**Detalle de validación:**

### BigBoard
- **Qué hace realmente:** según un usuario de la comunidad que lo usó
  para este mismo propósito, "no mezcla las tareas de proyectos distintos
  en un solo tablero", sino que "muestra un tablero por proyecto,
  apilados en una sola vista" ([hilo de discourse](https://kanboard.discourse.group/t/view-all-my-tasks-from-all-projects-on-a-board/2586)).
  **No filtra por asignado** ni consolida tareas de una persona — es una
  vista de "varios proyectos uno debajo del otro", no "todas las tareas de
  Fulano".
- **Licencia:** MIT.
- **Compatibilidad declarada:** no encontrada explícitamente; su último
  commit real es de marzo de 2023, más de 3 años antes de la versión
  actual de Kanboard (1.2.53, jul. 2026) — riesgo de incompatibilidad no
  descartable sin probarlo.
- **Instalación:** copiar a `plugins/Bigboard` o vía gestor de plugins.
- **Recomendación:** descartar para este objetivo puntual (no resuelve
  "vista por persona"); podría evaluarse aparte si algún día se quiere un
  tablero consolidado por proyectos, no por persona.

### TableView
- **Qué hace:** tabla configurable de tareas con columna de asignado,
  prioridad, fecha de vencimiento, etc. — pero **de un solo proyecto a la
  vez** (no se encontró evidencia de que agregue múltiples proyectos).
- **Estado:** repositorio **archivado por su propio dueño el 6 de mayo de
  2026** — es decir, formalmente descontinuado, muy recientemente.
- **Recomendación:** descartar. No resuelve multi-proyecto y ya no tiene
  mantenimiento.

### Global Search
- **Qué hace:** agrega un buscador global (tareas, comentarios, proyectos)
  respetando permisos, con resultados ordenados por fecha de
  creación/modificación ([README](https://github.com/kenlog/global-search-kanboard/blob/master/README.md)).
- **Multiproyecto:** sí, busca en todos los proyectos accesibles.
- **Vista por usuario:** no directamente — es un buscador de texto libre,
  **no confirmado que soporte el lenguaje de filtros** (`assignee:`,
  `status:`) de Kanboard; el README no lo menciona. No arma una vista
  consolidada por persona ni tabla resumen.
- **Compatibilidad:** Kanboard v1.2.32+.
- **Licencia:** MIT.
- **Riesgo:** proyecto pequeño (6 estrellas, 17 commits) — bajo respaldo
  comunitario, aunque cero issues abiertas sugiere que no hay reportes de
  problemas activos.
- **Recomendación:** probar en laboratorio solo si se quiere mejorar la
  búsqueda de texto libre entre proyectos; **no** resuelve la necesidad
  puntual de este informe (vista de carga de trabajo por persona).

### Group_assign, ProjectReports, HoursView/WeekHelper
- Resuelven problemas adyacentes pero distintos: asignación múltiple por
  tarea, reportes dentro de **un** proyecto, y seguimiento de horas —
  ninguno agrega tareas de una persona **entre** proyectos.
- **Recomendación:** descartar para este objetivo.

---

## 5. Issues, discusiones y solicitudes similares

Esta es la evidencia más directa de que la comunidad pidió exactamente
esto, varias veces, y de que el mantenedor lo rechazó explícitamente como
funcionalidad nativa:

| Fuente | Fecha | Resumen | Resultado |
|---|---|---|---|
| [Issue #381 — "Display my tasks (globally, not by project)"](https://github.com/kanboard/kanboard/issues/381) | Nov. 2014 | Pedido casi idéntico: ver todas las tareas propias agrupadas por columna, sin importar el proyecto. | Cerrado por `fguillot` en jul. 2015 como duplicado del #426. |
| [Issue #3375 — "Feature Request: Resource Management / Workload Reporting"](https://github.com/kanboard/kanboard/issues/3375) | Ago. 2017 | Pedido de ver carga de trabajo de todo el equipo, entre proyectos, contra el tiempo. | `fguillot` respondió textualmente: **"I prefer to keep the software simple, the number of features is voluntary limited."** (7 oct. 2017). No implementado. |
| [Issue #2926 — "working time tracking"](https://github.com/kanboard/kanboard/issues/2926) | — | Pedido de ver horas trabajadas por usuario y por día, para todos los usuarios y todos los proyectos (vista de manager/admin). | Cerrado, sin registro de respuesta del mantenedor en el contenido revisado. |
| [Discourse — "View all my tasks from all projects on a board"](https://kanboard.discourse.group/t/view-all-my-tasks-from-all-projects-on-a-board/2586) | — | Usuario pregunta directamente por esta funcionalidad. | La comunidad responde con BigBoard (no resuelve del todo, ver arriba) y con el Gantt entre proyectos ("Dashboard → Project management → Projects Gantt chart"), calificado por un usuario como "claramente inferior a un tablero kanban". Ningún maintainer confirmó una solución nativa. |
| [Discourse — "Toggle Open or Closed Projects"](https://kanboard.discourse.group/t/toggle-open-or-closed-projects/3577) | Dic. 2025 | Confirma el uso real y vigente de `ProjectUserOverviewController` vía URL manual (ver sección 2.2), y reporta como limitación no poder filtrar proyectos cerrados desde esa página. | Sin solución oficial; el usuario tuvo que revisar el esquema de base de datos por su cuenta. |

**Conclusión de esta sección:** la necesidad es reconocida por la propia
comunidad desde 2014, fue pedida formalmente como feature request en más
de una ocasión, y el mantenedor la rechazó explícitamente citando su
filosofía de mantener el software simple. Esto confirma que **no va a
aparecer como funcionalidad nativa completa en el futuro** — cualquier
solución completa depende de un plugin o de reutilizar la página oculta
`ProjectUserOverviewController`.

---

## 6. Forks o soluciones externas

No se encontró ningún fork del Core de Kanboard orientado específicamente
a resolver esto (los forks encontrados en la búsqueda — p. ej.
`salopant/Kanboard`, `TravisNoles/kanboard`, `stefanoco/kanboard` — son
copias de desarrollo/despliegue personal, sin evidencia de agregar esta
funcionalidad). Tampoco se encontró una solución externa (aplicación
separada que consuma la API JSON-RPC) publicada y mantenida
específicamente para "vista de carga de trabajo por persona en Kanboard".
La única vía externa viable sería un script propio contra la API (ver
2.4), que no es lo que el equipo pidió (una vista dentro de Kanboard).

---

## 7. Comparativa

| Alternativa | Multiproyecto | Vista por usuario | Mantenida | Compatible (Kanboard actual) | Recomendación |
|---|---|---|---|---|---|
| Dashboard nativo ("Mis tareas") | Sí | Solo el propio usuario, no otros | ✅ Core, activo | ✅ | Usar tal cual, pero no resuelve la necesidad (no sirve para ver a otra persona) |
| `ProjectUserOverviewController` (Core, oculto) | Sí (con la limitación de permisos del punto 2.2) | Sí, vía `user_id` en la URL | ✅ Core, activo (visto en uso en dic. 2025; **confirmado funcional en vivo en nuestra instancia el 2026-07-26, ver sección 10**) | ✅ | **Usar como base de referencia** para el plugin propio — no como solución final por sus limitaciones de UI |
| BigBoard | Parcial (apila tableros, no fusiona) | No filtra por asignado | 🟡 Mantenimiento mínimo | 🔴 Sin confirmar (último commit 2023) | Descartar para este objetivo |
| TableView | No (un proyecto) | No | ❌ Archivado 2026-05-06 | ❌ | Descartar |
| Global Search | Sí (búsqueda de texto) | No (no es una vista consolidada) | 🟡 Bajo uso, sin señales de abandono | ✅ (v1.2.32+) | Descartar para este objetivo; evaluar aparte solo como buscador |
| Group_assign / ProjectReports / HoursView-WeekHelper | No | No | Variable | 🔴 Sin confirmar | Descartar para este objetivo |
| Script externo vía API JSON-RPC | Sí (iterando proyecto por proyecto) | Sí | Depende de quién lo mantenga | ✅ | Usar como referencia solo si se quisiera un reporte fuera de Kanboard (ej. Excel/BI), no como vista dentro de la app |
| Plugin propio reutilizando el Core | Sí | Sí | A definir por el equipo | ✅ (diseñado para ello) | **Desarrollar** |

---

## 8. Conclusión

**No existe un plugin (oficial, comunitario o fork) listo para instalar
que resuelva la necesidad completa**, y la comunidad la pidió varias veces
sin éxito porque el mantenedor de Kanboard decidió explícitamente no
implementarla para mantener el software simple.

Sin embargo, la investigación encontró algo más valioso que "ningún
plugin sirve": **el Core de Kanboard ya contiene, sin documentar y sin
exponer en el menú, casi toda la lógica de backend necesaria**
(`ProjectUserOverviewController`, `TaskFinderModel::getUserQuery()` /
`getProjectUserOverviewQuery()`, `TaskPagination::getDashboardPaginator()`,
`ProjectUserRoleModel::getActiveProjectsByUser()`), todo parametrizado por
`user_id` y ya usado en producción por el propio Dashboard nativo. Esto
significa que desarrollar un plugin propio no implica escribir la parte
difícil (consultas multi-proyecto respetando permisos) desde cero, sino
**envolver y completar** lo que ya existe.

**Conclusión formal:** de las tres opciones planteadas, la que mejor
describe la situación es *"no existe y conviene desarrollar un plugin
propio"* — con la salvedad importante de que es un desarrollo de esfuerzo
**bajo a medio**, no de "empezar de cero", porque reutiliza modelos y
consultas ya existentes en el Core sin necesidad de tocarlo.

---

## 9. Propuesta técnica si no existe

### 9.1 Preguntas de arquitectura, respondidas explícitamente

- **¿Puede desarrollarse completamente mediante un Plugin?** Sí. No hace
  falta modificar el Core: se puede registrar un controlador, una ruta y
  una plantilla nuevos, y consumir los modelos existentes (`TaskFinderModel`,
  `ProjectUserRoleModel`, `ProjectGroupRoleModel`, `UserModel`) desde el
  contenedor de servicios del plugin, tal como lo hace cualquier
  controlador del Core.
- **¿Es necesario modificar el Core?** No.
- **¿Qué componentes reutilizaría?**
  - `TaskFinderModel::getUserQuery($user_id)` — tareas abiertas de un
    usuario (dueño o asignado a subtarea).
  - `ProjectUserRoleModel::getActiveProjectsByUser($user_id)` +
    `ProjectGroupRoleModel::getProjectsByUser($user_id)` — proyectos
    reales del usuario **elegido** (corrige la limitación de
    `ProjectUserOverviewController` de usar los proyectos del que
    consulta).
  - `UserModel::getAllUsers()` — para el selector de usuario.
  - El patrón de plantilla de `project_user_overview/tasks.php` como
    punto de partida visual (tabla con proyecto, columna, título,
    vencimiento, enlaces).
  - Hook `template:dashboard:sidebar` para agregar el enlace a la nueva
    vista, y `$this->userSession->isAdmin()` para restringir quién puede
    usarla.
- **¿Qué componentes nuevos crearía?**
  - Un controlador propio (p. ej. `WorkloadController`) que, a diferencia
    de `ProjectUserOverviewController`, calcule los proyectos a partir del
    usuario **elegido**, no del que consulta.
  - Una plantilla que **agrupe por proyecto** (no lista plana) y agregue
    las columnas que hoy faltan: prioridad y tags/categoría.
  - Un selector de usuario (dropdown simple).
  - Los filtros por proyecto/columna/vencimiento pedidos.
  - La tabla resumen (ver riesgo abajo).

### 9.2 Riesgo técnico a tener en cuenta: la tabla resumen

Kanboard no tiene un concepto nativo de "tipo de columna" (no distingue
que "Backlog" y "Pendiente de Análisis" son ambas "pendiente" en términos
que el sistema entienda) — cada proyecto nombra sus columnas libremente,
y nuestro propio estándar de organización agrava esto a propósito (cada
*tipo* de proyecto define su flujo). Por lo tanto, una tabla como
"Pendientes / En curso / En revisión / Total" **no puede calcularse de
forma genérica y automática** sin alguna convención adicional. Opciones,
de menor a mayor esfuerzo:

1. **Solo contar Total / Vencidas / Cerradas recientes** (datos que sí son
   universales, sin heurísticas) — fase 1-2, sin riesgo.
2. Definir una convención de nombres de columna reservados en el estándar
   (p. ej. que todo proyecto exponga una columna marcada como "de cierre"
   final) y mapear el resto por posición relativa (primera columna =
   pendiente, última = hecho) — funciona razonablemente bien en la
   mayoría de los casos pero es una heurística, no una garantía.
3. Agregar un campo de metadato por columna (vía configuración del
   plugin, no del Core) que declare a qué "bucket" lógico pertenece cada
   columna de cada proyecto — más preciso, pero exige mantenimiento manual
   cada vez que se crea un proyecto.

Se recomienda **empezar con la opción 1** y evaluar la 2 o 3 recién en la
Fase 3, cuando haya más proyectos reales para validar el patrón.

### 9.3 Estructura de carpetas propuesta del plugin

```
plugins/
  TeamWorkload/
    Plugin.php
    Controller/
      WorkloadController.php
    Template/
      workload/
        index.php        (selector de usuario)
        show.php          (tareas agrupadas por proyecto + filtros)
        sidebar.php        (contenido para template:dashboard:sidebar)
    Locale/
      es_ES/
        translations.php
```

No hace falta carpeta `Model/` propia en la Fase 1 — todo se resuelve
reutilizando modelos del Core inyectados por el contenedor.

### 9.4 Rutas y permisos

```php
// Plugin.php
$this->route->addRoute('/workload', 'WorkloadController', 'index', 'teamworkload');
$this->route->addRoute('/workload/:user_id', 'WorkloadController', 'show', 'teamworkload');

$this->template->hook->attach('template:dashboard:sidebar', 'teamworkload:workload/sidebar');
```

```php
// WorkloadController.php
public function show()
{
    if (! $this->userSession->isAdmin()) {
        throw new AccessForbiddenException();
    }

    $user_id = $this->request->getIntegerParam('user_id');
    $project_ids = array_unique(array_merge(
        array_keys($this->projectUserRoleModel->getActiveProjectsByUser($user_id)),
        array_keys($this->projectGroupRoleModel->getProjectsByUser($user_id))
    ));

    $tasks = $this->taskFinderModel->getUserQuery($user_id)
        ->in(TaskModel::TABLE.'.project_id', $project_ids)
        ->findAll();

    // agrupar $tasks por project_id antes de pasarlos a la plantilla
}
```

Restringir a `isAdmin()` es la opción más simple y segura para la Fase 1.
Si más adelante se quiere permitir también a "responsables de equipo" no
admin, se puede reemplazar por un chequeo de rol específico usando
`$this->projectAccessMap` o un rol custom, sin cambiar el resto de la
arquitectura.

### 9.5 Plan de implementación por fases (MVP)

**Fase 1 — Vista global por usuario (complejidad: baja)**
- Selector de usuario (dropdown con `getAllUsers()`).
- Tareas abiertas agrupadas por proyecto, reutilizando
  `getUserQuery()` + `getActiveProjectsByUser()`.
- Columnas: proyecto, columna actual, título (con enlace directo a la
  tarea), fecha de vencimiento.
- Acceso restringido a administradores.

**Fase 2 — Filtros y datos adicionales (complejidad: media)**
- Filtros por proyecto, por columna y por rango de vencimiento.
- Agregar prioridad y tags/categoría a la tabla (requiere unir
  `TaskTagModel`/campo de categoría, no incluidos en `getUserQuery()` por
  defecto).
- Enlace directo a cada tarea ya cubierto desde la Fase 1.

**Fase 3 — Dashboard ejecutivo (complejidad: media-alta)**
- Tabla resumen por usuario (Pendientes/En curso/En revisión/Total) —
  aplicando una de las opciones descritas en 9.2, empezando por la más
  simple.
- Vista tipo calendario (reutilizando el patrón de
  `getICalQuery()` de `TaskFinderModel` si aplica).
- Indicadores por proyecto (tareas vencidas, carga por persona).

### 9.6 Riesgos generales

- **Compatibilidad futura:** los nombres de métodos usados
  (`getUserQuery`, `getActiveProjectsByUser`, etc.) son internos del Core;
  no son parte de una API pública estable, así que una actualización mayor
  de Kanboard podría renombrarlos. Mitigación: fijar la versión de
  Kanboard usada y revisar el `ChangeLog` antes de actualizar.
- **Seguridad:** exponer datos de tareas de terceros exige el control de
  permisos correcto desde el día uno (Fase 1 ya lo contempla con
  `isAdmin()`). No copiar el patrón de `ProjectUserOverviewController` de
  calcular proyectos según el que consulta si se decide abrir esta vista a
  no-admins — hacerlo mal filtraría tareas de proyectos donde el usuario
  que consulta no debería tener visibilidad.
- **Mantenimiento:** al ser un plugin propio (no de terceros), el equipo
  es responsable de mantenerlo al día con cada actualización de Kanboard
  — a cambio, se evita el riesgo de depender de un plugin comunitario que
  se abandone (como pasó con TableView y HoursView).

### 9.7 Escalabilidad

Con ~15 usuarios y ~25 proyectos, iterar sobre los proyectos del usuario
elegido y traer sus tareas es una operación trivial en costo (decenas de
filas, un puñado de consultas). La arquitectura propuesta **escalaría sin
cambios estructurales** hasta varios cientos de proyectos/usuarios, dado
que las consultas ya filtran por `project_id IN (...)` en una sola
sentencia (no hace una consulta por proyecto). Si en el futuro la
instalación creciera a un volumen mucho mayor (miles de proyectos), lo
primero que convendría revisar es agregar índices específicos y, recién
ahí, evaluar cachear la lista de proyectos por usuario — pero no es una
preocupación real al tamaño actual ni al previsible a mediano plazo.

---

## 10. Validación en la instancia real (2026-07-26)

> Prueba de **solo lectura** contra `PFR-KANBOARD-TEST` (proyecto LXD
> `default`, host `pfr-oss`, ver
> [`laboratorio/2026-07-24_kanboard-contenedor-prueba/README.md`](../../../laboratorio/2026-07-24_kanboard-contenedor-prueba/README.md)).
> El usuario autorizó explícitamente, solo para esta tarea, consultas
> `SELECT` directas contra el SQLite y un login programático de solo
> lectura contra el propio Kanboard. No se ejecutó ningún `INSERT`,
> `UPDATE`, `DELETE` ni cambio de esquema; los archivos temporales
> generados durante la prueba (cookies de sesión, HTML descargado) se
> borraron del servidor al finalizar.

### 10.1 Estado real de los datos (contexto necesario para interpretar la prueba)

Antes de probar la vista, se relevó el estado real de la base (consultas
`SELECT` únicamente):

- **Usuarios:** los 9 usuarios locales creados durante la migración
  (`rocio.duarte`, `bruno.mino`, `natalia.duarte`, `elias.alfonzo`,
  `daniel.medina`, `marcos.casco`, `norberto.nunez`, `andres.semidei`,
  `fernando.fleitas`) tienen **rol `app-admin`**, igual que `admin`. 🔴
  **Esto contradice lo documentado en
  [`bitacora.md`](../../../laboratorio/2026-07-25_migracion-planner-a-kanboard/bitacora.md)**,
  que registra "rol Standard" para estos usuarios. Es un hallazgo real
  que conviene corregir antes de pasar a producción: hoy, cualquier
  persona del equipo tiene permisos de administrador completo sobre
  Kanboard (crear/borrar usuarios, instalar plugins, editar cualquier
  proyecto), no solo sobre sus propias tareas. Esto además significa que
  **no pudimos probar en este entorno la limitación de permisos descrita
  en la sección 2.2** (el alcance de proyectos según quien consulta, no
  según el usuario elegido), porque todos los usuarios disponibles son
  admin y un admin siempre ve el universo completo de proyectos.
- **Proyectos:** existen 5 (`INFRAWORK`, `SOC`, `adm-tech`, `Tembiapo OS`,
  `VulnApp`). Solo `INFRAWORK` y `adm-tech` tienen el flujo de 5 columnas
  definido (`📥 Pendiente de Análisis` → `📌 Listo para Desarrollo` →
  `⚙️ En Curso` → `🔎 En Revisión` → `✅ Realizados`) y tareas cargadas; los
  otros tres todavía tienen las columnas por defecto de Kanboard (`En
  espera`/`Listo`/`En curso`/`Hecho`) sin tareas propias — consistente con
  lo documentado (solo INFRAWORK y ADM-TECH migrados hasta ahora).
- **Asignación real de tareas:** de las 18 tareas cargadas, **13 tienen
  `owner_id = 0` (sin asignar)** y solo 5 tienen un responsable individual
  cargado en Kanboard (3 de Elías Alfonzo, 2 de Daniel Medina) — aunque en
  Planner esas tareas sí tenían asignados. 🟡 Esto no es un problema de la
  vista que estamos evaluando, pero sí una alerta operativa: **mientras no
  se complete la asignación individual de cada tarea dentro de Kanboard,
  cualquier vista de "carga de trabajo por persona" (nativa o del plugin
  futuro) va a mostrar información incompleta**, no porque la vista falle,
  sino porque el dato de origen no está cargado todavía.
- **Tags:** confirmados como **específicos por proyecto** (una tabla
  `tags` con `project_id`), tal como se dedujo en la sección 2 sin acceso
  directo a datos. Nota aparte sin relación con esta investigación: se
  detectó que la tarea "Notas de Acceso - Refactorización Backend" en
  INFRAWORK usa la etiqueta `Infrawork`, lo que contradice la propia regla
  del [estándar de organización](../../../laboratorio/2026-07-25_migracion-planner-a-kanboard/estandar-organizacion-kanboard.md#4-uso-de-etiquetas-tags)
  de no usar el nombre del proyecto como etiqueta dentro de sí mismo — se
  menciona solo como dato observado, a corregir aparte, no es parte del
  alcance de este informe.

### 10.2 Resultado de la prueba de `ProjectUserOverviewController`

Se inició sesión como `admin` (login programático de solo lectura,
autorizado para esta tarea) y se accedió a las URLs reales:

```
http://localhost:8080/?controller=ProjectUserOverviewController&action=opens&user_id=5
http://localhost:8080/?controller=ProjectUserOverviewController&action=closed&user_id=5
```

(`user_id=5` = Elías Alfonzo, verificado contra la tabla `users`).

**✅ La URL responde correctamente** — HTTP 200, sin redirigir al login,
en una instalación real con PHP 8.5.4 y los datos reales de la migración
(no es exclusivo de una instalación de laboratorio genérica ni de una
versión vieja de Kanboard).

**Qué muestra exactamente** — tabla real extraída de la respuesta
(`action=opens`, título de página: `Tareas asignadas a "Elías Alfonzo"`):

| Identificador | Proyecto | Columna | Título | Persona asignada | Fecha de inicio | Fecha Límite |
|---|---|---|---|---|---|---|
| #1 | INFRAWORK | 📌 Listo para Desarrollo | Notas de Acceso - Refactorización Backend | Elías Alfonzo | — | 31/08/2026 12:00 am |
| #17 | adm-tech | ⚙️ En Curso | Capex - Módulo de Planificación | Elías Alfonzo | — | 31/12/1969 8:00 pm |
| #18 | adm-tech | ⚙️ En Curso | Reservas - Automatización Export SAP | Elías Alfonzo | — | 31/12/1969 8:00 pm |

Coincide exactamente con lo que la base de datos indicaba para el
`owner_id = 5` — confirma que la consulta agrega correctamente tareas de
**dos proyectos distintos** (INFRAWORK y adm-tech) en una sola tabla, tal
como predecía el análisis de código de la sección 2.2.

**Con `action=closed`:** Elías no tiene tareas cerradas, y la página
respondió igualmente con HTTP 200 mostrando un estado vacío correcto (sin
error) — comportamiento correcto.

**Hallazgo nuevo, no visible solo leyendo el código fuente:** las tareas
sin fecha de vencimiento (`date_due = 0` en la base) se muestran
literalmente como **`31/12/1969 8:00 pm`** (época Unix cero, mal formateada)
en vez de dejarse en blanco o decir "Sin fecha". Es un defecto de
presentación real de esta página oculta del Core — confirmado en vivo, no
documentado en ningún lado. Si se reutiliza esta lógica en el plugin
propio, hay que tratar explícitamente `date_due == 0` como "sin fecha".

**Casos límite probados:**

| Caso | Resultado observado |
|---|---|
| `user_id` de un usuario sin tareas propias (Rocío Duarte, id 2) | HTTP 200, tabla vacía — comportamiento correcto |
| `user_id` inexistente (`9999`) | HTTP 200, pero **muestra las tareas de TODOS los usuarios de todos los proyectos accesibles**, incluidas las "Sin asignar" — no valida que el usuario exista, cae al valor por defecto `UserModel::EVERYBODY_ID` sin avisar |
| Sin parámetro `user_id` | Mismo comportamiento que el caso anterior — mismo motivo (`EVERYBODY_ID` es el valor por defecto) |

🟡 Esto es una limitación real a tener en cuenta: si el plugin propio
reutiliza este patrón sin validar el `user_id` contra la lista real de
usuarios antes de consultar, un error de tipeo en la URL (o un enlace mal
armado) no daría un error visible — silenciosamente mostraría los datos
de todo el equipo en vez de los de la persona buscada. El plugin propio
**debe validar explícitamente** que el `user_id` recibido exista.

### 10.3 Qué parte del problema ya resuelve el Core, y qué falta complementar

| Requisito pedido | ¿Lo resuelve `ProjectUserOverviewController` hoy? |
|---|---|
| Elegir una persona y ver sus tareas en todos sus proyectos | 🟡 Sí, pero sin selector — hay que conocer el `user_id` y escribirlo en la URL |
| Mostrar proyecto, tarea, columna, vencimiento, enlace | ✅ Sí, confirmado en vivo (enlaces de tarea y de proyecto incluidos en el HTML real) |
| Mostrar prioridad | ❌ No — no está en la plantilla |
| Mostrar categoría/tags | ❌ No — no está en la plantilla |
| Agrupar visualmente por proyecto | ❌ No — lista plana |
| Filtros por proyecto/columna/vencimiento | ❌ No — solo separa abiertas vs. cerradas |
| Tabla resumen por usuario | ❌ No existe |
| Validación de que el usuario elegido exista | ❌ No — cae a "todos" sin avisar (ver 10.2) |
| Alcance de proyectos según el usuario **elegido** (no según quien consulta) | 🔴 No se pudo confirmar en este entorno (todos son admin) — según el código fuente (sección 2.2), usa los proyectos del que consulta |

---

## 11. Análisis de reutilización del Core

### 11.1 ¿Conviene reutilizar `ProjectUserOverviewController` directamente?

**No, tal cual.** La prueba en vivo (sección 10) confirma que funciona,
pero también confirma en la práctica sus límites: sin selector de
usuario, sin agrupar por proyecto, sin prioridad/tags, sin validar el
`user_id`, con un defecto de formato de fecha, y calculando el universo de
proyectos según quien consulta y no según la persona elegida. Usarlo "tal
cual" significaría pedirle a cada responsable que memorice o guarde una
URL con un ID numérico — no es una solución presentable al equipo.

### 11.2 ¿Es posible extenderlo mediante herencia?

Técnicamente sí (es una clase PHP normal, `ProjectUserOverviewController
extends BaseController`), pero **no es recomendable**, por tres razones
concretas:

1. **El problema principal no se hereda resuelto.** El cálculo de
   proyectos según "quien consulta" vive en un método privado (`common()`,
   confirmado en la sección 2.2) — no es un punto de extensión pensado
   para sobreescribirse. Para corregirlo (usar los proyectos del usuario
   **elegido**) habría que reimplementar esa lógica de todos modos, con lo
   cual la herencia no ahorra el trabajo que más importa.
2. **No es una superficie de extensión oficial.** La documentación de
   plugins de Kanboard describe rutas, hooks de plantilla y *class
   overriding* para **modelos/servicios** del contenedor de inyección de
   dependencias — no documenta un mecanismo soportado para heredar
   Controllers del Core de forma segura. Depender de una clase interna no
   documentada como superclase expone al plugin a romperse sin aviso ante
   cualquier refactor del Core (nombres de métodos, firmas, visibilidad).
3. **Mayor acoplamiento, no menor.** Heredar ata el plugin a los detalles
   internos exactos de una clase pensada para un caso de uso más limitado
   (proyectos del que consulta) que el nuestro (proyectos del usuario
   elegido) — en la práctica se termina sobreescribiendo casi todo.

### 11.3 ¿Conviene crear un Controller completamente nuevo?

**Sí — es la opción recomendada.** No hereda de
`ProjectUserOverviewController` ni de ninguna otra clase del Core más
allá de `BaseController` (el mismo punto de partida que usa cualquier
controlador, incluido el que estamos evaluando). En vez de reutilizar el
*Controller*, reutiliza los **Modelos y Paginadores** — que es la capa
que Kanboard sí expone de forma estable a través del contenedor de
servicios, y que ya vimos (secciones 2.3 y 10) que aceptan `user_id` como
parámetro explícito:

- `TaskFinderModel::getUserQuery($user_id)`
- `ProjectUserRoleModel::getActiveProjectsByUser($user_id)`
- `ProjectGroupRoleModel::getProjectsByUser($user_id)`
- `UserModel::getAllUsers()` / `UserModel::getById($user_id)` (para
  validar que el usuario elegido exista — corrige la limitación 10.2)

### 11.4 Ventajas y desventajas de cada alternativa

| | Reutilizar el Controller tal cual | Extender por herencia | Controller nuevo + Modelos reutilizados |
|---|---|---|---|
| Código propio a escribir | Ninguno | Medio (hay que sobreescribir lo importante igual) | Bajo (un controlador corto + plantilla) |
| Resuelve el requisito completo | No | Parcialmente, con esfuerzo similar al de un controller nuevo | Sí |
| Acoplamiento a internals no documentados del Core | Alto (URL y parámetros exactos) | Muy alto (hereda de una clase interna completa) | Bajo (solo de los Modelos, más estables) |
| Riesgo ante futuras actualizaciones de Kanboard | Alto | Alto | Medio-bajo |
| Corrige el bug de fecha / falta de validación de usuario | No | Sí, pero reimplementando | Sí, se escribe correcto desde el inicio |
| Requiere modificar el Core | No | No | No |

### 11.5 ¿Cuál implica menor mantenimiento a futuro?

**El Controller nuevo apoyado en Modelos.** Los Modelos de Kanboard
(`TaskFinderModel`, `ProjectUserRoleModel`, etc.) son la capa de acceso a
datos del sistema — cambian con mucha menor frecuencia que los
Controllers y las plantillas (que sí se ajustan seguido por temas de UI).
Además, al no heredar de una clase del Core, un cambio de nombre o firma
en `ProjectUserOverviewController` (que ni siquiera está documentado
oficialmente, así que no tiene compromiso de estabilidad) **no rompe
nuestro plugin en absoluto**.

### 11.6 Cuánto código propio hace falta si se reutiliza bien

Con las piezas confirmadas en las secciones 2.3, 10 y 11.3, el plugin
necesita escribir, aproximadamente:

- **1 Controller** (~40-60 líneas): una acción para el selector, una
  acción `show($user_id)` que valida el usuario, calcula sus proyectos
  combinando `ProjectUserRoleModel` + `ProjectGroupRoleModel`, trae sus
  tareas con `TaskFinderModel::getUserQuery()` filtradas a esos
  proyectos, y agrupa el resultado por `project_id` en PHP antes de
  pasarlo a la plantilla (un `array` indexado por proyecto, con un
  `foreach` — no hace falta SQL adicional).
- **2 plantillas** (~30-50 líneas cada una): el selector de usuario
  (`<select>` con `getAllUsers()`) y la tabla agrupada por proyecto
  (adaptando el layout ya visto en la sección 10.2, agregando
  prioridad/tags y corrigiendo el formato de fecha).
- **`Plugin.php`** (~15 líneas): registro de las 2 rutas y el hook
  `template:dashboard:sidebar` para el enlace de menú.
- **0 líneas de SQL propio** — todo se resuelve con los métodos de los
  Modelos ya existentes; el agrupamiento por proyecto se hace en PHP sobre
  el resultado ya traído, no con una consulta nueva.

En total, del orden de **150-200 líneas de código propio para la Fase 1
completa** — la mayoría plantilla/presentación, no lógica de negocio, que
es exactamente lo que ya resuelve el Core.

---

## 12. Recomendación final de arquitectura

**Desarrollar un Controller nuevo y liviano** (no heredar de
`ProjectUserOverviewController`, no reescribir consultas), cuya única
responsabilidad sea:

1. Agregar una entrada al menú/Dashboard (hook `template:dashboard:sidebar`,
   visible solo para `$this->userSession->isAdmin()` — ver nota de
   seguridad abajo).
2. Ofrecer un selector de usuario (reutilizando `UserModel::getAllUsers()`).
3. Reutilizar `TaskFinderModel::getUserQuery()` +
   `ProjectUserRoleModel::getActiveProjectsByUser()` +
   `ProjectGroupRoleModel::getProjectsByUser()` para traer las tareas del
   usuario elegido en todos sus proyectos reales (corrigiendo la
   limitación de `ProjectUserOverviewController` de usar los proyectos de
   quien consulta).
4. Agrupar las tareas por proyecto en la plantilla.
5. Agregar filtros (proyecto, columna, vencimiento) sobre el resultado ya
   obtenido — sin necesidad de nuevas consultas complejas al tamaño actual
   (~25 proyectos).
6. Sumar prioridad, categoría/tags y el enlace directo a cada tarea
   (estos sí requieren un join adicional simple, ya que `getUserQuery()`
   no los trae por defecto).
7. Corregir en el propio plugin los dos defectos reales detectados en la
   sección 10: fechas en cero mostradas como "31/12/1969" y `user_id`
   inválido cayendo silenciosamente a "todos".
8. Agregar la tabla resumen **solo si aporta valor real** — dado el
   hallazgo de la sección 9.2 (Kanboard no tiene un concepto nativo de
   "tipo de columna"), se recomienda arrancar con un resumen simple y
   confiable (Total / Vencidas, que no requieren heurísticas) en la Fase
   1-2, y evaluar recién en la Fase 3 si vale la pena invertir en una
   convención de columnas "pendiente/en curso/en revisión" más elaborada.

**Nota de seguridad, a partir del hallazgo de la sección 10.1:** antes de
decidir quién puede ver el trabajo de otras personas, conviene corregir
que los 9 usuarios de la migración quedaron con rol `app-admin` en lugar
de `Standard`. Si se deja así, la restricción `isAdmin()` del plugin no
protege nada, porque todo el equipo ya es administrador.

## 13. Estimación de esfuerzo real

| Fase | Alcance | Complejidad | Estimación |
|---|---|---|---|
| Fase 1 | Selector de usuario + tareas agrupadas por proyecto + enlaces, con las correcciones de la sección 10.2 | Baja | ~150-200 líneas de código propio (sección 11.6); la mayor parte del esfuerzo es de plantilla/presentación, no de lógica, porque las consultas ya existen en el Core |
| Fase 2 | Filtros (proyecto/columna/vencimiento) + prioridad + tags/categoría | Media | Requiere un join adicional a `tags`/`task_has_tags` (no cubierto por `getUserQuery()`) y la lógica de filtrado en PHP/plantilla — comparable en tamaño a la Fase 1 |
| Fase 3 | Tabla resumen + calendario + indicadores | Media-alta | La parte de mayor incertidumbre es la tabla resumen por la heterogeneidad de columnas entre proyectos (sección 9.2) — el resto (calendario, indicadores por proyecto) reutiliza patrones ya presentes en el Core (`getICalQuery()`, conteos por proyecto) |

**Conclusión de esfuerzo:** con la reutilización confirmada del Core, la
Fase 1 es una tarea de complejidad baja y acotada — no un desarrollo desde
cero. Es razonable arrancarla como siguiente paso.

---

## Fuentes consultadas

- [Kanboard — sitio oficial](https://kanboard.org/)
- [Kanboard — catálogo de plugins](https://kanboard.org/plugins.html)
- [Documentación oficial — Dashboard/Users/Projects/Search](https://docs.kanboard.org/v1/user/)
- [Documentación oficial — API JSON-RPC](https://docs.kanboard.org/v1/api/)
- [Documentación oficial — Plugins (registro, rutas, hooks)](https://docs.kanboard.org/v1/plugins/)
- [github.com/kanboard/kanboard](https://github.com/kanboard/kanboard) (código fuente: `DashboardController.php`, `ProjectUserOverviewController.php`, `TaskFinderModel.php`, `TaskPagination.php`, `DashboardPagination.php`, `ProjectUserRoleModel.php`)
- [Issue #381](https://github.com/kanboard/kanboard/issues/381), [Issue #3375](https://github.com/kanboard/kanboard/issues/3375), [Issue #2926](https://github.com/kanboard/kanboard/issues/2926)
- [Foro de la comunidad — kanboard.discourse.group](https://kanboard.discourse.group/) (hilos citados arriba)
- [TimoStahl/kanboard_plugin_bigboard](https://github.com/TimoStahl/kanboard_plugin_bigboard)
- [greyaz/TableView](https://github.com/greyaz/TableView)
- [kenlog/global-search-kanboard](https://github.com/kenlog/global-search-kanboard)
- [Tagirijus/HoursView](https://github.com/Tagirijus/HoursView)
- [noredis/ProjectReports](https://github.com/noredis/ProjectReports), [creecros/Group_assign](https://github.com/creecros/Group_assign)

## Qué quedó marcado como pendiente de verificar (no asumido)

- ✅ **Resuelto el 2026-07-26** ~~Si `ProjectUserOverviewController`
  funciona igual en la instalación real del equipo~~ — confirmado en vivo
  contra `PFR-KANBOARD-TEST`, ver sección 10.
- 🔴 Compatibilidad exacta de Global Search, Group_assign y ProjectReports
  con la versión de Kanboard 1.2.53 — no se instaló nada para confirmarlo.
- 🔴 Fecha exacta del último commit de Global Search y Group_assign (no
  se pudo extraer con precisión de las páginas consultadas).
- 🔴 **Nuevo, surgido de la validación:** el comportamiento de
  `ProjectUserOverviewController` para un usuario **no-admin** (¿ve solo
  los proyectos del usuario elegido que coinciden con los suyos propios,
  tal como predice el código?) no se pudo probar porque los 9 usuarios de
  la migración quedaron con rol `app-admin` (ver 10.1). Si se corrige ese
  rol a `Standard`, valdría la pena repetir esta prueba puntual con una
  cuenta no-admin antes de dar la arquitectura por completamente validada.
- 🔴 No se tomaron capturas de pantalla — la validación se hizo
  extrayendo y reproduciendo el contenido real de la respuesta HTTP
  (sección 10.2), que es exacto y citable, pero no es una imagen. Se
  puede complementar con una captura manual si se necesita para una
  presentación.
