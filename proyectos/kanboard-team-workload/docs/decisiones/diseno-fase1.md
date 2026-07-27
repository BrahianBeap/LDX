# Diseño técnico — Plugin "TeamWorkload", Fase 1

> **Estado:** 🟡 Propuesta — pendiente de aprobación. No se escribió ningún
> archivo PHP todavía.
> **Documento de arquitectura de referencia:**
> [`../01_Investigacion.md`](../01_Investigacion.md)
> (investigación + validación en vivo + análisis de reutilización del Core).
> **Principios que gobiernan este diseño** (confirmados por el usuario):
> reutilizar siempre el Core antes de escribir código nuevo, no duplicar
> lógica existente, no modificar el Core, mantener el plugin lo más chico
> posible, minimizar mantenimiento futuro, mantener compatibilidad con
> versiones futuras de Kanboard.

Todo lo afirmado en este documento sobre el Core de Kanboard fue
**verificado leyendo el código fuente real** de la instalación que se usó
para migrar (`C:\Users\alfonzel\Documents\GitHub\LXD\kamban\kanboard`,
v1.2.46 — la misma copia que corre en el contenedor `PFR-KANBOARD-TEST`),
no solo inferido de la documentación pública. Donde algo no se pudo
confirmar así, queda marcado explícitamente como 🔴.

---

## 0. Alcance de la Fase 1 (recordatorio)

Del plan de fases ya acordado en el informe de investigación:

> Selector de usuario, tareas abiertas agrupadas por proyecto, con enlace
> directo a cada tarea, acceso restringido a administradores.

Con un ajuste que se justifica en la sección 3: **prioridad y color de
tarea se incluyen en la Fase 1**, no en la Fase 2 como se había estimado
antes de confirmar el código real — porque la consulta del Core que vamos
a reutilizar ya los trae sin costo adicional. Tags/categoría siguen en
Fase 2, porque esos sí requieren una consulta extra que no viene incluida.

---

## 1. Arquitectura

### 1.1 Nombre y ubicación

- **Nombre del plugin:** `TeamWorkload`
- **Ubicación final:** `plugins/TeamWorkload/` dentro de la instalación de
  Kanboard (no en este repositorio de documentación — el código del
  plugin se desarrollará y probará directamente en
  `PFR-KANBOARD-TEST`, y este repositorio (`laboratorio/`) documenta el
  proceso, igual que se hizo con el resto de los experimentos).

### 1.2 Estructura de carpetas

```
plugins/
  TeamWorkload/
    Plugin.php
    Controller/
      WorkloadController.php
    Template/
      workload/
        show.php          (pantalla única: selector + resultado agrupado)
        sidebar.php        (contenido para el hook del sidebar del Dashboard)
    Locale/
      es_ES/
        translations.php
```

**No hay carpeta `Model/`.** Es una decisión deliberada, no una omisión:
toda la lógica de datos que hace falta ya existe en el Core (sección 2) y
se consume directamente desde el Controller. Agregar un Model propio que
solo reenviara llamadas al Core sería la duplicación que el usuario pidió
evitar.

**Una sola plantilla de contenido** (`workload/show.php`), no dos como se
había esbozado en el informe original (`index.php` + `show.php`
separados): la misma pantalla maneja tanto el estado "sin usuario
elegido" como el resultado, con un `if` simple — menos archivos, mismo
resultado, más fácil de mantener.

### 1.3 Responsabilidad de cada archivo

| Archivo | Responsabilidad |
|---|---|
| `Plugin.php` | Registrar la ruta, declarar el permiso (`applicationAccessMap`), y enganchar el link del sidebar del Dashboard (hook). Metadatos del plugin (nombre, versión, autor, versión compatible de Kanboard). |
| `Controller/WorkloadController.php` | Única clase de lógica propia. Lee el `user_id` de la URL, valida que exista, calcula sus proyectos reales, trae sus tareas reutilizando el Core, agrupa por proyecto, renderiza la plantilla. |
| `Template/workload/show.php` | Presentación: selector de usuario (componente del Core), y si hay resultado, una sección por proyecto con su tabla de tareas. |
| `Template/workload/sidebar.php` | Un `<li>` con el link "Carga de trabajo por persona", para inyectar en el sidebar del Dashboard nativo. |
| `Locale/es_ES/translations.php` | Traducciones de las cadenas de texto propias del plugin (Kanboard ya está en español en esta instalación; sin esto, los textos del plugin quedarían en el idioma en que se escriban literalmente en el código). |

### 1.4 Rutas

Un plugin real ya instalado en esta misma versión (`Customizer`, revisado
como referencia) registra así una ruta:

```php
$this->route->addRoute('settings/customizer', 'CustomizerFileController', 'show', 'Customizer');
```

Siguiendo exactamente ese patrón confirmado:

```php
$this->route->addRoute('workload', 'WorkloadController', 'show', 'TeamWorkload');
```

Con esto, `WorkloadController::show()` queda accesible en una URL corta
(`/workload`), y **también** sigue siendo accesible por la ruta genérica
`?controller=WorkloadController&action=show` que Kanboard expone
automáticamente para cualquier controlador — no hace falta declarar una
segunda ruta para el parámetro `user_id`, porque viaja como query string
(`?user_id=5`) sobre la misma acción, igual que hace
`ProjectUserOverviewController` con sus acciones.

### 1.5 Hooks

Dos hooks, ambos confirmados como existentes en el código real de esta
versión:

1. **`template:dashboard:sidebar`** — confirmado en
   `app/Template/dashboard/sidebar.php` de la instalación real. Es el
   punto de extensión que usa el Dashboard nativo para que los plugins
   agreguen contenido a su barra lateral.
   ```php
   $this->template->hook->attach('template:dashboard:sidebar', 'TeamWorkload:workload/sidebar');
   ```
2. No se necesita ningún otro hook para la Fase 1 (no se toca CSS/JS de
   layout, no se sobreescribe ninguna plantilla del Core — a diferencia
   de `Customizer`, que sí lo hace para su propio propósito de
   personalización visual).

### 1.6 Flujo de navegación

1. Un administrador entra al Dashboard (`/`, la pantalla que ya usa a
   diario).
2. En la barra lateral del Dashboard aparece un nuevo link: **"Carga de
   trabajo por persona"** (solo visible para administradores, ver
   sección 4).
3. Al hacer clic, llega a `/workload` sin ningún usuario elegido todavía:
   ve el selector, vacío, sin tabla debajo.
4. Elige una persona en el selector (autocompletado, ver sección 3): la
   página se recarga sola a `/workload?user_id=<ID>` (sin botón
   "Buscar" — el propio componente del Core maneja el redirect).
5. Ve sus tareas abiertas, agrupadas por proyecto, con link a cada una.
6. Puede cambiar de persona sin volver atrás: el selector sigue arriba,
   con el nombre actual ya cargado.

---

## 2. Flujo de datos

```
Usuario (admin)
   │  clic en el selector / entra a /workload?user_id=5
   ▼
WorkloadController::show()
   │  1. Kanboard ya validó el permiso ANTES de que este método se ejecute
   │     (applicationAccessMap, ver sección 4) — no hay código de permiso
   │     dentro del Controller.
   │
   │  2. $user_id = $this->request->getIntegerParam('user_id', 0);
   │
   │  3. Sin user_id (=0): arma solo la lista de usuarios y renderiza
   │     la plantilla en estado "vacío". Corta acá.
   │
   │  4. Con user_id: $user = $this->userModel->getById($user_id);
   │     Si no existe -> mensaje "Usuario no encontrado", corta acá.
   │     (Esto es intencional: NO cae a "mostrar todos", que es el bug
   │     confirmado de ProjectUserOverviewController.)
   ▼
Modelos del Core (sin escribir SQL propio)
   │  5. $project_ids =
   │       array_unique(array_merge(
   │         array_keys($this->projectUserRoleModel->getActiveProjectsByUser($user_id)),
   │         array_keys($this->projectGroupRoleModel->getProjectsByUser($user_id))
   │       ));
   │     -> proyectos ACTIVOS del usuario ELEGIDO (no del que consulta).
   │
   │  6. Si $project_ids está vacío: mensaje "Esta persona no pertenece
   │     a ningún proyecto activo", corta acá.
   │
   │  7. $tasks = $this->taskFinderModel
   │       ->getProjectUserOverviewQuery($project_ids, TaskModel::STATUS_OPEN)
   │       ->eq(TaskModel::TABLE.'.owner_id', $user_id)
   │       ->findAll();
   │     -> el mismo método que usa el Core en
   │        ProjectUserOverviewController::tasks(), reutilizado tal cual.
   │        Ya trae: id, title, date_due, date_started, project_id,
   │        color_id, priority, project_name, column_name — sin joins
   │        propios.
   ▼
Agrupación (PHP puro, en el Controller, sin SQL nuevo)
   │  8. $grouped = array();
   │     foreach ($tasks as $task) {
   │         $grouped[$task['project_id']]['name'] = $task['project_name'];
   │         $grouped[$task['project_id']]['tasks'][] = $task;
   │     }
   ▼
View (Template/workload/show.php)
   │  9. Recibe: $all_users (para el selector), $selected_user_id,
   │     $grouped (proyectos -> tareas). Renderiza el selector siempre;
   │     si $grouped no está vacío, una sección por proyecto con su
   │     tabla de tareas.
```

**Qué modelo participa en cada paso** (todos ya existentes en el Core,
confirmados en el código fuente real):

| Paso | Modelo/servicio del Core | Método |
|---|---|---|
| Permiso | `Kanboard\Core\Security\Authorization` (vía `applicationAccessMap`, declarado en `Plugin.php`) | — (declarativo, no se llama a mano) |
| Lista para el selector | `UserModel` | `getActiveUsersList()` |
| Validar usuario elegido | `UserModel` | `getById($user_id)` |
| Proyectos del usuario elegido | `ProjectUserRoleModel` | `getActiveProjectsByUser($user_id)` |
| Proyectos heredados por grupo | `ProjectGroupRoleModel` | `getProjectsByUser($user_id)` |
| Tareas abiertas, multi-proyecto | `TaskFinderModel` | `getProjectUserOverviewQuery($project_ids, $is_active)` + filtro `owner_id` |

**Corrección importante respecto al informe original:** la investigación
inicial había identificado `TaskFinderModel::getUserQuery($user_id)` como
la pieza a reutilizar. Al leer el código real de
`ProjectUserOverviewController`, se confirmó que el propio Core **no**
usa ese método para esta pantalla — usa
`getProjectUserOverviewQuery($project_ids, $is_active)` y le agrega el
filtro de `owner_id` por fuera. Este diseño sigue exactamente ese patrón
ya probado en producción, en lugar del que se había supuesto antes de
leer el código — es una consulta más simple y que además ya trae
`project_name`, `column_name` y `priority` sin joins adicionales.

---

## 3. Interfaz

### 3.1 Selector de usuario: reutilizar el componente del Core, no crear uno propio

`ProjectUserOverviewController` ya resuelve el selector de usuario con un
componente reutilizable de Kanboard
(`app/Template/project_user_overview/sidebar.php`, confirmado en el
código real):

```php
<?= $this->app->component('select-dropdown-autocomplete', array(
    'name' => 'user_id',
    'items' => $all_users,
    'defaultValue' => $selected_user_id,
    'sortByKeys' => true,
    'ariaLabel' => t('User filters'),
    'redirect' => array(
        'regex' => 'USER_ID',
        'url' => $this->url->to('WorkloadController', 'show', array('user_id' => 'USER_ID')),
    ),
)) ?>
```

Es un autocompletado con búsqueda por nombre que, al elegir una persona,
redirige solo (sin botón "Buscar", sin JavaScript propio) a la URL con su
`user_id`. **Se reutiliza literal**, cambiando únicamente a qué
controlador redirige.

### 3.2 Mockup de la pantalla completa

```
┌──────────────────────────────────────────────────────────────────────┐
│  Carga de trabajo por persona                                        │
│                                                                       │
│  Persona: [ Elías Alfonzo                              ▾ ]           │
│           (autocompletado — escribir para buscar)                    │
│                                                                       │
│  ┌── Fase 2 (no implementado en la Fase 1, layout previsto) ───────┐ │
│  │ Proyecto: [ Todos ▾ ]  Columna: [_______]  Vencimiento: [__-__] │ │
│  └──────────────────────────────────────────────────────────────────┘│
│                                                                       │
│  ── INFRAWORK ──────────────────────────────────────────────────────│
│  ┌────┬──────────────────────────────────┬─────────────┬──────────┐ │
│  │ #  │ Tarea                            │ Columna     │ Vence    │ │
│  ├────┼──────────────────────────────────┼─────────────┼──────────┤ │
│  │ 1  │ Notas de Acceso - Refact. Backend│ Listo p/Dev │ 31/08/26 │ │
│  └────┴──────────────────────────────────┴─────────────┴──────────┘ │
│                                                                       │
│  ── adm-tech ───────────────────────────────────────────────────────│
│  ┌────┬──────────────────────────────────┬─────────────┬──────────┐ │
│  │ 17 │ Capex - Módulo de Planificación  │ En Curso    │ Sin fecha│ │
│  │ 18 │ Reservas - Automatización SAP    │ En Curso    │ Sin fecha│ │
│  └────┴──────────────────────────────────┴─────────────┴──────────┘ │
│                                                                       │
│  Total: 3 tareas abiertas en 2 proyectos                             │
└──────────────────────────────────────────────────────────────────────┘
```

Cada fila de tarea es un enlace directo a la tarea (igual que en
`ProjectUserOverviewController`); el color de fondo/borde de la fila usa
el `color_id` de la tarea, igual que el Core (`class="task-table
color-<?= $task['color_id'] ?>"`) — reutilizando la misma clase CSS ya
existente, cero CSS propio.

**Estados vacíos, diseñados explícitamente (corrigen los 2 defectos reales
encontrados en la validación):**

| Situación | Qué se muestra |
|---|---|
| Sin persona elegida todavía | Solo el selector, con un texto: "Elegí una persona para ver su carga de trabajo." — **nunca** una lista de todas las tareas de todos (a diferencia del Core, ver Hallazgo de la validación) |
| `user_id` no existe | "No se encontró ese usuario." — nunca cae a "todos" |
| Usuario sin proyectos activos | "Esta persona no pertenece a ningún proyecto activo." |
| Usuario con proyectos pero sin tareas abiertas | "Esta persona no tiene tareas abiertas asignadas." (incluye la nota operativa: con los datos reales de hoy, esto va a pasar seguido, porque 13 de 18 tareas migradas todavía no tienen dueño individual cargado — ver informe, sección 10.1) |
| Fecha de vencimiento en cero | "Sin fecha" — nunca "31/12/1969" |

### 3.3 Acciones disponibles en esta pantalla

**Ninguna acción de edición.** Es intencional: la Fase 1 es una vista de
**solo lectura** (consulta, no gestión). La única interacción por fila es
navegar a la tarea o al tablero del proyecto (enlaces, ya incluidos en la
consulta reutilizada). Reasignar, cambiar de columna o editar cualquier
dato desde esta pantalla queda **fuera de alcance** — si se necesitara
más adelante, es una decisión de producto a discutir aparte, no algo que
se vaya a necesitar "igual" en una fase posterior.

### 3.4 Alternativas de presentación consideradas

| Alternativa | Ventajas | Desventajas | Decisión |
|---|---|---|---|
| **Tabla agrupada por proyecto** (elegida) | Reutiliza 100% las clases CSS `table-small`/`table-striped`/`task-table color-*` ya usadas por `ProjectUserOverviewController` — cero CSS propio. Densa, fácil de escanear muchas tareas. Ordenable por columna (el `paginator->order()` del Core ya lo resuelve gratis). | Menos "visual" que un tablero kanban. | ✅ Elegida — máxima reutilización, mínimo código, consistente con el resto de Kanboard |
| Tarjetas estilo tablero Kanban, agrupadas por proyecto | Más parecida a la experiencia habitual de Kanboard. | Cada proyecto tiene su propio set de columnas (nuestro propio estándar lo garantiza) — agrupar tarjetas de columnas distintas en un solo tablero visual sería confuso, no una ventaja. Requiere CSS/JS propio nuevo. | ❌ Descartada — más código propio, sin beneficio real dado que los proyectos no comparten columnas |
| Acordeón colapsable por proyecto | Útil si una persona tiene muchos proyectos. | No se confirmó que Kanboard tenga un componente de acordeón reutilizable ya armado (a diferencia del selector de usuario, que sí) — implicaría JS propio. Con ~25 proyectos como máximo y una persona rara vez en más de 4-5, el beneficio es marginal hoy. | ❌ Descartada para la Fase 1 — se puede reconsiderar en Fase 3 si la cantidad de proyectos por persona crece mucho |

---

## 4. Modelo de permisos

### 4.1 Mecanismo elegido: `applicationAccessMap`, no un `if` manual

Se investigó cómo Kanboard restringe sus propias pantallas equivalentes
(`UserListController`, `ConfigController`, `GroupListController`, todas
admin-only) y **ninguna lo hace con un `if ($this->userSession->isAdmin())`
dentro del controlador** — todas se declaran de forma centralizada así
(confirmado en `app/ServiceProvider/AuthenticationProvider.php` del
código real):

```php
$acl->add('UserListController', '*', Role::APP_ADMIN);
```

Un plugin real ya instalado (`Customizer`) usa exactamente el mismo
mecanismo, expuesto como `$this->applicationAccessMap` dentro de
`Plugin.php`:

```php
$this->applicationAccessMap->add('CustomizerFileController', array('image', 'loginlogo', ...), Role::APP_PUBLIC);
```

**Diseño de este plugin, siguiendo ese mismo patrón exacto:**

```php
// Plugin.php
$this->applicationAccessMap->add('WorkloadController', '*', Role::APP_ADMIN);
```

Con esto, **Kanboard rechaza el acceso antes de que
`WorkloadController::show()` se ejecute** — no hace falta ningún chequeo
de permiso escrito a mano dentro del Controller. Es el mecanismo más
"nativo" posible: es literalmente el mismo usado por el propio Core para
sus pantallas administrativas, no una imitación.

### 4.2 Por qué esto ya queda bien diseñado, aunque hoy todos sean `app-admin`

El rol se resuelve leyendo la columna `role` real de cada usuario en la
base — no depende de ninguna suposición sobre cuántos usuarios son admin
hoy. Con los 9 usuarios actuales en `app-admin` (hallazgo de la
validación), todos van a poder ver la pantalla — ni más ni menos
permisivo que hoy con cualquier otra pantalla de admin de Kanboard (ellos
ya pueden entrar a Users management, Config, etc., por el mismo motivo).

**El día que se corrija el rol a `Standard`** (`Role::APP_USER`), sin
tocar una sola línea de este plugin, el control empieza a funcionar
exactamente como se diseñó: solo `admin` (o quien sea admin real en ese
momento) va a poder ver el trabajo de otras personas. No hace falta
ningún cambio de código — el diseño ya es correcto para ese escenario
futuro, simplemente hoy no se nota porque el dato de origen (roles) está
mal cargado.

### 4.3 Camino de extensión ya identificado para más adelante (fuera de alcance de la Fase 1)

Kanboard define un tercer rol de aplicación, `Role::APP_MANAGER`
(confirmado en `Role.php`), intermedio entre `APP_USER` y `APP_ADMIN`,
con jerarquía ya establecida en el Core
(`$acl->setRoleHierarchy(Role::APP_ADMIN, array(Role::APP_MANAGER, Role::APP_USER, Role::APP_PUBLIC))`).
Si en el futuro se quisiera que, por ejemplo, un líder de equipo (no
admin) también pueda ver la carga de trabajo de su gente sin ser
administrador completo de Kanboard, el cambio sería **una sola línea**:

```php
$this->applicationAccessMap->add('WorkloadController', '*', Role::APP_MANAGER);
```

(Y asignarle rol `Manager` a esas personas puntuales, en vez de
`Standard`.) No es parte de la Fase 1 — se deja documentado como el punto
de extensión ya confirmado que existe, para no tener que investigarlo de
nuevo más adelante.

---

## 5. Riesgos identificados antes de escribir código

| # | Riesgo | Severidad | Mitigación |
|---|---|---|---|
| 1 | El prefijo real de la URL generado por `addRoute('workload', ...)` podría no ser exactamente `/workload` según la configuración de reescritura de URLs del servidor (`mod_rewrite`, `.htaccess`) | Baja | Se confirma en el primer request de prueba; si no coincide, la ruta genérica `?controller=WorkloadController&action=show` siempre funciona igual como respaldo, sin cambiar el Controller |
| 2 | El grupo `Role::APP_MANAGER` no se usa en absoluto hoy en esta instancia — no se pudo confirmar en la práctica que `applicationAccessMap` con ese rol se comporte como espera la documentación (sección 4.3) | Baja, y no bloquea la Fase 1 (usa `APP_ADMIN`, sí verificado con múltiples usos reales en el Core) | Validar recién si/cuando se implemente la extensión de la sección 4.3 |
| 3 | `getProjectUserOverviewQuery()` es un método interno, no documentado como parte de una API pública estable — una actualización mayor de Kanboard podría cambiar su firma | Media (mismo riesgo ya aceptado y documentado en el informe de investigación, sección 9.6) | Fijar la versión de Kanboard en uso; revisar el `ChangeLog` antes de actualizar; el acoplamiento es a un Modelo (capa estable), no a un Controller (capa que cambia más seguido) |
| 4 | Con los datos reales de hoy, la mayoría de las tareas migradas no tienen `owner_id` cargado (13 de 18, ver informe sección 10.1) — la pantalla va a mostrar poco contenido hasta que se complete la asignación individual en Kanboard | Baja (no es un defecto del plugin) | Ya documentado como nota operativa en el mockup (sección 3.2); no requiere ningún cambio de diseño |
| 5 | El componente `select-dropdown-autocomplete` depende de JavaScript ya incluido en el layout base de Kanboard — no se verificó si algún otro plugin instalado (p. ej. `Customizer`, que sobreescribe `layout`) interfiere con su carga | Baja | Se confirma visualmente en la primera prueba manual; si hay conflicto, es un problema de interacción entre plugins ya existente, no algo introducido por este diseño |
| 6 | Los 9 usuarios de la migración están en `app-admin` (ver sección 4.2) — mientras no se corrija, no se puede demostrar en este entorno que el `applicationAccessMap` efectivamente bloquea a un usuario `Standard` | Baja, aceptado explícitamente por el usuario como "no bloquea el desarrollo" | Repetir la prueba de permisos apenas se corrija el rol (ya anotado como pendiente en el informe de investigación) |

Ningún riesgo identificado es bloqueante para empezar la Fase 1.

---

## 6. Qué NO incluye la Fase 1 (límite explícito)

- Filtros por proyecto/columna/vencimiento (Fase 2).
- Tags/categoría (Fase 2 — a diferencia de prioridad, sí requiere una
  consulta adicional).
- Tabla resumen (Pendientes/En curso/En revisión/Total) (Fase 3, con el
  riesgo de heterogeneidad de columnas ya documentado en el informe).
- Cualquier acción de edición/reasignación desde esta pantalla.
- Soporte para roles `APP_MANAGER` (queda documentado como extensión
  futura, sección 4.3, no implementado ahora).
- Corregir el rol de los 9 usuarios existentes (tarea aparte, de
  configuración, no de este plugin).

---

## 7. Checklist de aprobación

Antes de escribir el primer archivo PHP, confirmar que este diseño cubre
lo pedido:

- [ ] Arquitectura (estructura, responsabilidades, rutas, hooks) — sección 1
- [ ] Flujo de datos completo, con el modelo del Core en cada paso — sección 2
- [ ] Interfaz completa, con alternativas evaluadas — sección 3
- [ ] Modelo de permisos, correcto hoy y preparado para el rol Standard — sección 4
- [ ] Riesgos identificados — sección 5
- [ ] Límites explícitos de la Fase 1 — sección 6

Una vez aprobado, el siguiente paso es escribir `Plugin.php`,
`WorkloadController.php` y las dos plantillas, y probarlos en
`PFR-KANBOARD-TEST` antes de considerar la Fase 1 terminada.
