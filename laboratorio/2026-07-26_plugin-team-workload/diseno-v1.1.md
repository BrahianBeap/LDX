# Diseño técnico — Plugin "TeamWorkload", versión 1.1

> **Estado:** ✅ Implementada y probada en `PFR-KANBOARD-TEST` — ver
> [`v1.1-implementacion.md`](v1.1-implementacion.md).
> **Base:** [`diseno-fase1.md`](diseno-fase1.md) — esta versión no cambia
> la arquitectura general (Controller único, sin Model propio, mismo
> permiso, misma ruta, mismo hook), solo la extiende.

## Objetivo

Convertir la vista individual de la Fase 1 en una pequeña vista de
gestión de equipo: agregar un modo "👥 Todos" que muestre las tareas
abiertas de todas las personas a la vez, con quién es el responsable de
cada una y un resumen numérico rápido.

## Análisis previo (pedido explícitamente antes de escribir código)

**Pregunta:** ¿existe ya una función del Core que devuelva todas las
tareas abiertas de varios proyectos sin filtrar por propietario?

**Respuesta: sí, exactamente la misma que ya usa este plugin desde la
Fase 1.** Releyendo el código real de
[`TaskFinderModel::getProjectUserOverviewQuery($project_ids, $is_active)`](https://github.com/kanboard/kanboard/blob/main/app/Model/TaskFinderModel.php)
(confirmado también en la copia local exacta de esta instalación):

```php
public function getProjectUserOverviewQuery(array $project_ids, $is_active)
{
    // ...
    return $this->db->table(TaskModel::TABLE)
        ->columns(/* ... incluye project_name, column_name,
                     assignee_username, assignee_name ... */)
        ->eq(TaskModel::TABLE.'.is_active', $is_active)
        ->in(ProjectModel::TABLE.'.id', $project_ids)
        ->join(ProjectModel::TABLE, 'id', 'project_id')
        ->join(ColumnModel::TABLE, 'id', 'column_id', TaskModel::TABLE)
        ->join(UserModel::TABLE, 'id', 'owner_id', TaskModel::TABLE); // LEFT JOIN
}
```

**Esta consulta nunca filtró por propietario.** El filtro
`.eq('owner_id', $user_id)` lo agrega el *controlador* por fuera (tanto
`ProjectUserOverviewController::tasks()` en el Core como
`WorkloadController::getOpenTasks()` en este plugin desde la Fase 1). Es
decir: **el modo "Todos" no necesitó ninguna consulta nueva** — alcanza
con no encadenar ese `.eq()`.

Dos consecuencias de leer el join con atención:

1. El `join()` con `UserModel` es un **LEFT JOIN** (confirmado en
   `libs/picodb/lib/PicoDb/Table.php::join()`), no un `INNER JOIN`. Por
   eso las tareas con `owner_id = 0` (sin responsable) **ya aparecen**
   en el resultado con `assignee_username`/`assignee_name` en `null` —
   el requisito 3 (mostrar tareas sin asignar) se cumple solo, sin
   ningún cambio adicional.
2. La consulta **no selecciona la columna `owner_id`** en el resultado
   (solo el nombre/usuario ya resuelto por el join) — hay que usar
   `assignee_username` como identificador de persona para el resumen,
   no `owner_id` (ver sección "Resumen").

Con esto confirmado, la implementación completa de este objetivo fue
**extender el Controller existente**, sin tocar el Core y sin escribir
ninguna consulta SQL propia.

## Arquitectura — qué cambia y qué no

No cambia: nombre del plugin, ruta, permiso (`Role::APP_ADMIN`), hook del
sidebar, estructura de carpetas, ausencia de `Model/` propio.

Cambia únicamente dentro de `WorkloadController` y `Template/workload/show.php`:

| Pieza | Antes (Fase 1) | Ahora (v1.1) |
|---|---|---|
| `show()` | Un solo camino: usuario elegido o nada | Tres caminos: nada elegido, modo "Todos" (`UserModel::EVERYBODY_ID`), usuario individual |
| Cálculo de tareas | Un método (`getGroupedOpenTasks`) mezclaba fetch + agrupar | Separado en `getOpenTasks()` (fetch) y `groupByProject()` (agrupar) — necesario para reutilizar el fetch en dos modos sin duplicar el agrupamiento |
| Proyectos para "Todos" | — | `getAllActiveProjectIds()`, nuevo, pero es un `array_column()` de una línea sobre `ProjectModel::getAllByStatus()` (ya existente) |
| Resumen | — | `buildSummary()`, nuevo, PHP puro sobre la lista de tareas ya traída — cero consultas nuevas |
| Plantilla | Tabla fija de 5 columnas | Columna "Responsable" y bloque de resumen, ambos condicionados a `$everybody_mode` |

## El sentinel `UserModel::EVERYBODY_ID` y un hallazgo real durante la prueba

Se reutilizó `UserModel::EVERYBODY_ID` (`-1`, confirmado en
`app/Model/UserModel.php`) — la misma constante que ya usa
`ProjectUserOverviewController` para su propio modo "todos" — en vez de
inventar un sentinel propio.

**Se decidió NO usar `getActiveUsersList(true)`** (que antepondría
automáticamente la entrada "Everybody" con esa clave) porque su etiqueta
sale de la clave de traducción compartida `'Everybody'`. Si el plugin le
diera su propia traducción a esa clave (`'👥 Todos'`), **cambiaría también
el texto de `'Everybody'` en cualquier otra pantalla del Core** que la
use (por ejemplo, el propio `ProjectUserOverviewController`), porque el
diccionario de traducciones de Kanboard es global, no por página. Se
resolvió anteponiendo la opción a mano con una clave de traducción propia
(`'👥 All'`), evitando cualquier colisión con el Core — reutilización sin
efectos secundarios sobre pantallas ajenas.

**Hallazgo real, encontrado al probar, no al leer el código:** la
primera implementación usaba `$this->request->getIntegerParam('user_id', 0)`,
igual que en la Fase 1. Al probar `user_id=-1` en la URL, el modo "Todos"
nunca se activaba. La causa, leyendo `app/Core/Http/Request.php`:

```php
public function getIntegerParam($name, $default_value = 0)
{
    return isset($this->get[$name]) && ctype_digit((string) $this->get[$name])
        ? (int) $this->get[$name] : $default_value;
}
```

`ctype_digit()` rechaza el signo `-` — **`getIntegerParam()` nunca puede
devolver un número negativo**, así que `user_id=-1` siempre caía al valor
por defecto. Se corrigió leyendo el valor crudo con `getStringParam()` (sin esa
restricción) y convirtiéndolo con un cast `(int)` de PHP, que sí interpreta
`"-1"` correctamente. Sigue siendo un helper del Core (`getStringParam`),
solo se evitó el que tiene la limitación.

## Resumen — de dónde sale cada número

Todo calculado en PHP puro sobre la lista de tareas ya traída por
`getOpenTasks()`, sin ninguna consulta adicional:

- **Tareas abiertas:** `count($tasks)`.
- **Proyectos:** `count($grouped_tasks)` (proyectos que efectivamente
  tienen al menos una tarea abierta — un proyecto activo sin tareas no
  suma acá, ver sección de pruebas).
- **Sin asignar:** cantidad de tareas con `assignee_username` vacío.
- **Usuarios con tareas:** cantidad de valores **distintos** de
  `assignee_username` entre las tareas asignadas.

## Camino para futuras vistas (documentado, no implementado)

Pedido explícitamente: dejar la arquitectura preparada para nuevos modos
de agrupación, sin implementarlos todavía.

La separación ya introducida en esta versión —
`getOpenTasks($user_id, $project_ids)` (trae los datos) por un lado, y
`groupByProject($tasks)` (decide cómo presentarlos) por otro — es
exactamente el punto de apoyo para esto. Ninguna vista futura de la
siguiente lista necesitaría tocar `getOpenTasks()`, porque ya trae todos
los campos que hacen falta (`priority`, `date_due`,
`assignee_username`/`assignee_name`, `project_name`, `column_name`):

| Vista futura | Cómo se agregaría |
|---|---|
| Agrupar por Persona | Un método hermano `groupByAssignee(array $tasks)`, misma firma que `groupByProject()`, agrupando por `assignee_username` en vez de `project_id` |
| Agrupar por Prioridad | `groupByPriority(array $tasks)` — agrupar por el campo `priority` ya presente en cada tarea |
| Agrupar por Fecha de vencimiento | `groupByDueDate(array $tasks)` — con el mismo criterio ya usado en `sortTasksByColumnPriorityAndDueDate()` para tratar `date_due = 0` como "sin fecha" |
| Solo tareas sin asignar | Un filtro previo de una línea sobre `$tasks` (`array_filter` por `empty($task['assignee_username'])`) antes de agrupar — no requiere cambiar la consulta |
| Solo tareas vencidas | Mismo patrón: filtrar `$tasks` por `date_due` vencido antes de agrupar |

En todos los casos, `show()` seguiría llamando a `getOpenTasks()` una
sola vez y decidiendo qué función de agrupación usar según un parámetro
nuevo (por ejemplo `?group_by=assignee`) — sin duplicar la obtención de
datos ni agregar una consulta por modo.

## Compatibilidad (verificada, no solo esperada)

Ver [`v1.1-implementacion.md`](v1.1-implementacion.md) para el detalle de
pruebas — se confirmó que el modo individual, el orden de tareas, el
permiso de administrador y el mecanismo de instalación/rollback siguen
funcionando exactamente igual que en la Fase 1.
