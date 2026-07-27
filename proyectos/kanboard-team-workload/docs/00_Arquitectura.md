# Arquitectura actual — Plugin TeamWorkload

> **Última actualización:** 2026-07-27 (después de la v1.1).
> Este documento describe **cómo funciona el plugin hoy**. Se reescribe
> en cada versión para reflejar el estado actual — el *por qué* de cada
> decisión y lo que se probó en cada versión vive en
> [`decisiones/`](decisiones/), que nunca se reescribe.

## Qué hace

Muestra, dentro de Kanboard, las tareas abiertas de una persona elegida
(o de todas a la vez, desde la v1.1) en **todos los proyectos** a los que
pertenece — algo que Kanboard no ofrece de forma nativa ni completa (ver
[`01_Investigacion.md`](01_Investigacion.md)).

## Estructura de archivos

```
src/TeamWorkload/
  Plugin.php                          — registro de ruta, permiso y hook
  Controller/
    WorkloadController.php            — única clase de lógica propia
  Template/
    workload/
      show.php                        — pantalla única (selector + resultado)
      sidebar.php                     — link en el sidebar del Dashboard
  Locale/
    es_ES/
      translations.php                — traducciones propias (ver limitación conocida más abajo)
```

Sin carpeta `Model/` propia — toda la lógica de datos se apoya en
modelos ya existentes del Core, inyectados por el contenedor de
servicios de Kanboard (`$this->taskFinderModel`, `$this->userModel`,
`$this->projectModel`, `$this->projectUserRoleModel`,
`$this->projectGroupRoleModel`, `$this->columnModel`).

## Ruta y permiso

- Ruta registrada: `workload` → `WorkloadController::show()`.
- **Nota real de esta instalación:** `ENABLE_URL_REWRITE = false` en
  `config.php`, así que esa ruta "bonita" nunca se activa en la práctica
  — todo el tráfico real usa la forma
  `?controller=WorkloadController&action=show&plugin=TeamWorkload`, que
  Kanboard genera solo si se usan sus propios helpers de URL
  (`$this->url->link()`/`to()`, como hace este plugin) en vez de rutas
  escritas a mano. Ver el detalle en
  [`decisiones/pruebas-fase1.md`](decisiones/pruebas-fase1.md), sección 4.
- Permiso: `applicationAccessMap->add('WorkloadController', '*', Role::APP_ADMIN)`,
  declarado en `Plugin.php` — el mismo mecanismo declarativo que usa el
  propio Core para sus pantallas de administración (`UserListController`,
  `ConfigController`, etc.), no un `if` a mano dentro del controlador.
- Hook: `template:dashboard:sidebar` → agrega el link "Team workload" al
  sidebar del Dashboard nativo, visible solo si `$this->user->isAdmin()`.

## Flujo de datos

```
WorkloadController::show()
   │
   │ 1. Lee "user_id" — con (int) sobre getStringParam(), no con
   │    getIntegerParam() (ese helper del Core rechaza negativos, ver
   │    "Limitaciones conocidas").
   │
   ├── user_id === UserModel::EVERYBODY_ID (-1)  →  modo "Todos"
   │      project_ids = getAllActiveProjectIds()
   │        (ProjectModel::getAllByStatus(ProjectModel::ACTIVE))
   │
   ├── user_id > 0  →  modo individual
   │      user = UserModel::getById(user_id) — si no existe, mensaje de
   │        error explícito (nunca cae a mostrar todo)
   │      project_ids = getProjectIdsForUser(user_id)
   │        (ProjectUserRoleModel::getActiveProjectsByUser +
   │         ProjectGroupRoleModel::getProjectsByUser)
   │
   └── sin user_id  →  solo se muestra el selector, sin resultado
   │
   ▼
getOpenTasks(user_id, project_ids)
   │  TaskFinderModel::getProjectUserOverviewQuery(project_ids, STATUS_OPEN)
   │  + .eq('owner_id', user_id)  — SOLO si no es el modo "Todos"
   ▼
groupByProject(tasks)  →  ordena por proyecto (alfabético) y, dentro de
   │                       cada uno, por columna → prioridad → vencimiento
   │                       (sortTasksByColumnPriorityAndDueDate)
   ▼
buildSummary(tasks, grouped)  →  solo en modo "Todos": usuarios con
   │                              tareas, proyectos, tareas abiertas, sin asignar
   ▼
Template/workload/show.php
```

## Modelos y métodos del Core reutilizados

| Modelo | Método | Para qué |
|---|---|---|
| `TaskFinderModel` | `getProjectUserOverviewQuery($project_ids, $is_active)` | Trae las tareas — ya incluye `project_name`, `column_name`, `priority`, `assignee_username`, `assignee_name` sin joins propios |
| `UserModel` | `getActiveUsersList()`, `getById()`, constante `EVERYBODY_ID` | Selector de personas y validación |
| `ProjectUserRoleModel` | `getActiveProjectsByUser()` | Proyectos del usuario elegido (modo individual) |
| `ProjectGroupRoleModel` | `getProjectsByUser()` | Proyectos heredados por grupo |
| `ProjectModel` | `getAllByStatus(ProjectModel::ACTIVE)` | Todos los proyectos activos (modo "Todos") |
| `ColumnModel` | `getAll($project_id)` | Posición real de cada columna, para el orden de las tareas |

No se escribió ninguna consulta SQL propia — todo el ordenamiento y el
resumen se calculan en PHP puro sobre los resultados ya traídos.

## Decisiones de alcance que no deben "simplificarse" sin releer esto

- **El alcance de proyectos en modo individual es del usuario elegido,
  nunca del administrador que consulta.** Si en el futuro se habilita
  `Role::APP_MANAGER` en vez de `Role::APP_ADMIN`, este criterio hay que
  revisarlo explícitamente — un manager no-admin probablemente no deba
  ver proyectos a los que no pertenece.
- **La etiqueta "👥 Todos" del selector no reutiliza la traducción
  compartida `'Everybody'` del Core** — se construye a mano para no
  afectar el texto de otras pantallas del propio Kanboard que sí usan esa
  clave de traducción.

## Limitaciones conocidas

1. **Las traducciones propias del plugin no cargan** (se ven en inglés:
   "Team workload", "Choose a person...", etc.) — las cadenas que
   coinciden con claves ya existentes del Core (`Assignee`, `Priority`,
   `Projects`, `Open tasks`, `Unassigned`...) sí se ven en español,
   porque no dependen de la carga del archivo de traducción propio.
   Causa exacta no confirmada — ver
   [`decisiones/pruebas-fase1.md`](decisiones/pruebas-fase1.md), sección 5.
2. **`Request::getIntegerParam()` del Core no acepta enteros negativos**
   (usa `ctype_digit()`, que rechaza el signo `-`) — por eso el modo
   "Todos" (`user_id = -1`) se lee con `getStringParam()` + cast `(int)`
   en vez del helper "obvio". Ver
   [`decisiones/diseno-v1.1.md`](decisiones/diseno-v1.1.md).
3. Sin carpeta `Schema/` — el plugin no persiste nada propio en la base
   de datos, por eso instalar/desinstalar es tan simple como copiar o
   quitar la carpeta.
4. Todos los usuarios reales de esta instancia están en rol `app-admin`
   (no `Standard`) — no se pudo probar en vivo que el permiso
   `Role::APP_ADMIN` efectivamente bloquee a alguien. El mecanismo es el
   mismo que usa el Core para sus propias pantallas de administración,
   pero la prueba real queda pendiente.

## Qué no incluye todavía

Filtros (proyecto/columna/vencimiento), otros modos de agrupación
(persona/prioridad/vencimiento), y una tabla resumen con heurística de
"tipo de columna" — ver el camino de extensión ya documentado en
[`decisiones/diseno-v1.1.md`](decisiones/diseno-v1.1.md#camino-para-futuras-vistas-documentado-no-implementado).
