# Fase 1 — Implementación y pruebas del plugin TeamWorkload

> **Fecha:** 2026-07-26
> **Estado:** ✅ Fase 1 completa y probada en `PFR-KANBOARD-TEST`
> **Entorno:** contenedor LXD `PFR-KANBOARD-TEST` (proyecto `default`, host
> `pfr-oss`), Kanboard v1.2.46, PHP 8.5.4 — ver
> [`../2026-07-24_kanboard-contenedor-prueba/README.md`](../2026-07-24_kanboard-contenedor-prueba/README.md).
> No se instaló nada en producción, no se modificó ningún archivo del
> Core, no se ejecutó ningún `INSERT`/`UPDATE`/`DELETE`/`ALTER` sobre la
> base de datos. Toda validación de datos fue de solo lectura, autorizada
> explícitamente por el usuario para esta tarea.

---

## 1. Ajustes de diseño incorporados antes de codear

Sobre [`diseno-fase1.md`](diseno-fase1.md), se aplicaron los tres ajustes
pedidos:

1. **Alcance de proyectos:** confirmado — el código calcula los proyectos
   a partir del usuario **elegido** (`ProjectUserRoleModel::getActiveProjectsByUser($user_id)`
   + `ProjectGroupRoleModel::getProjectsByUser($user_id)`), nunca
   intersectado con los del administrador que consulta. Documentado con
   un comentario explícito en el código para que nadie lo "simplifique"
   sin repensar el alcance si algún día se habilita `Role::APP_MANAGER`.
2. **Selector de usuario:** se confirmó, leyendo el código real de
   `UserModel::getActiveUsersList()`/`prepareList()`, que sin el parámetro
   `prepend` ya excluye "Everybody", ya filtra `is_active = 1` y ya
   ordena alfabéticamente por nombre visible (`asort()` sobre el
   resultado de `getFullname()`). No hizo falta escribir ningún filtro
   propio.
3. **Orden de visualización:** la consulta reutilizada no traía la
   posición real de columna — se resolvió con `ColumnModel::getAll($project_id)`
   (ya ordenado por posición) para construir un mapa `título de columna
   → posición`, y un `usort()` propio de tres niveles: posición de
   columna → prioridad descendente → vencimiento ascendente (sin fecha al
   final). Proyectos ordenados alfabéticamente con `uasort()`.

## 2. Archivos creados

Todos en `plugins/TeamWorkload/` (código fuente versionado en este
repositorio en [`src/TeamWorkload/`](src/TeamWorkload/), desplegado tal
cual al contenedor):

| Archivo | Líneas | Contenido |
|---|---|---|
| `Plugin.php` | 51 | Registro de permiso (`applicationAccessMap` + `Role::APP_ADMIN`), ruta, hook del sidebar, metadatos |
| `Controller/WorkloadController.php` | 162 | Única clase de lógica: `show()`, `getGroupedOpenTasks()`, `sortTasksByColumnPriorityAndDueDate()` |
| `Template/workload/show.php` | 68 | Selector + estados vacíos + tablas agrupadas por proyecto |
| `Template/workload/sidebar.php` | 5 | Link del Dashboard, visible solo para admins |
| `Locale/es_ES/translations.php` | 10 | Traducciones al español de las cadenas propias |

## 3. Despliegue

Mismo procedimiento que el resto de este laboratorio: `pscp` (PC → host)
+ `lxc file push` (host → contenedor) + `chown www-data:www-data`. Sin
pasos de "instalación" adicionales — Kanboard escanea `plugins/` en cada
request y carga cualquier carpeta con un `Plugin.php` válido
(confirmado leyendo `app/Core/Plugin/Loader.php::scan()`).

```bash
# Desde la PC
pscp -pw <PASSWORD> -r plugins/TeamWorkload alfonzel_opr@10.143.11.228:/tmp/

# Desde el host
lxc file push -r /tmp/TeamWorkload PFR-KANBOARD-TEST/var/www/kanboard/plugins/ --project default
lxc exec PFR-KANBOARD-TEST --project default -- chown -R www-data:www-data /var/www/kanboard/plugins/TeamWorkload
```

**Verificación de instalación:** `php -l` sobre los 5 archivos (sin
errores) y confirmación visual en `Configuración → Complementos`, donde
aparece listado con nombre, autor, versión y descripción correctos.

## 4. Hallazgo importante durante las pruebas (no era un bug del plugin)

Las primeras pruebas contra la ruta "bonita" `/workload?user_id=X`
fallaban sistemáticamente, devolviendo la pantalla genérica "Página no
encontrada" del Core — pero **solo quedaba claro que era un problema real
al probar en vivo**, no se podía haber anticipado leyendo el código en
abstracto.

**Diagnóstico** (leyendo `app/Core/Http/Router.php` y
`app/ServiceProvider/RouteProvider.php` del código real): esta instancia
tiene `define('ENABLE_URL_REWRITE', false)` en `config.php`. Con eso,
`$container['route']->enable()` **nunca se ejecuta**, y por lo tanto
`addRoute()` — la nuestra y las más de 150 rutas "bonitas" que trae el
propio Core — es una operación que no hace nada. Se confirmó cruzando
esto contra los enlaces que el propio Kanboard genera en su menú: todos
usan la forma `?controller=X&action=Y`, nunca rutas bonitas como
`/board/3` — coherente con `ENABLE_URL_REWRITE = false`.

**Por qué esto no rompe el plugin igual:** `$this->url->link()` /
`$this->url->to()` (usados en `sidebar.php` y en el selector de
`show.php`) ya manejan este caso automáticamente — si no encuentran una
ruta bonita registrada, arman solos la URL con `?controller=...&action=...`.
Es decir, **para un usuario real que hace clic en la interfaz, el plugin
funciona perfectamente sin ningún cambio** — el problema apareció
únicamente porque, para probar rápido por curl, se escribió la URL
`/workload?user_id=X` a mano, un patrón que esta instancia en particular
no soporta.

**Corrección aplicada:** ninguna al plugin — se corrigió el **método de
prueba**, usando la forma real que la interfaz genera:
`?controller=WorkloadController&action=show&plugin=TeamWorkload&user_id=X`.
Confirmado explícitamente inspeccionando el HTML generado por el propio
selector de usuario del plugin: su URL de redirección es
`/?controller=WorkloadController&action=show&user_id=USER_ID&plugin=TeamWorkload`
— exactamente la forma correcta, autogenerada, sin intervención manual.

🟡 **Nota para el futuro:** si algún día se activa `ENABLE_URL_REWRITE`,
la ruta bonita `/workload` que ya está registrada en `Plugin.php`
empezará a funcionar sin cambios adicionales — se dejó registrada a
propósito por eso, aunque hoy no se use.

## 5. Segundo hallazgo (menor, cosmético): las traducciones al español no cargan

Confirmado en las pruebas: los textos propios del plugin ("Team
workload", "Choose a person to see their workload.", etc.) se muestran
en **inglés**, no en español, pese a que la interfaz general de Kanboard
sí está en español y a que `Plugin.php` carga
`Locale/es_ES/translations.php` en `onStartup()` siguiendo el mismo
patrón exacto que usa el plugin real `Customizer` ya instalado.

🔴 **Causa exacta no confirmada** — hipótesis más probable: el evento
`app.bootstrap` dispara los listeners de todos los plugins en el orden en
que Kanboard los escanea, y es posible que la carga de idioma del propio
Core ocurra en un punto distinto del ciclo que sobrescribe o precede a la
de los plugins. No se investigó más a fondo porque **no afecta la
funcionalidad** — todos los textos son perfectamente legibles en inglés —
y no era parte de los criterios de aceptación de la Fase 1. Queda anotado
como mejora cosmética pendiente, no como defecto bloqueante.

## 6. Resultado de las 10 pruebas mínimas pedidas

| # | Caso | Resultado |
|---|---|---|
| 1 | Acceso como administrador | ✅ HTTP 200, contenido correcto en todas las pruebas (se usó `admin`, el único rol disponible hoy — ver punto 9) |
| 2 | Acceso directo sin `user_id` | ✅ Muestra solo el selector y el mensaje "Choose a person to see their workload." — **no** cae a mostrar tareas de todos (a diferencia del defecto real de `ProjectUserOverviewController` documentado en la investigación) |
| 3 | Usuario válido con tareas en varios proyectos | ✅ Elías Alfonzo (id 5): 3 tareas agrupadas correctamente en 2 proyectos (`adm-tech`, `INFRAWORK`, en ese orden alfabético), "Total: 3 open tasks in 2 projects" |
| 4 | Usuario válido sin tareas | ✅ Rocío Duarte (id 2): "Rocío Duarte has no open tasks assigned in any active project." |
| 5 | Usuario inexistente | ✅ `user_id=9999`: "Usuario(a) no encontrado(a)." — **corrige** el defecto real confirmado en la investigación (el Core cae silenciosamente a mostrar las tareas de todo el mundo) |
| 6 | Tarea sin fecha de vencimiento | ✅ Se muestra "No due date" — **corrige** el defecto real confirmado en la investigación (el Core muestra `31/12/1969 8:00 pm`) |
| 7 | Enlaces hacia tarea y proyecto | ✅ Verificados en el HTML real: `?controller=TaskViewController&action=show&task_id=X` y `?controller=BoardViewController&action=show&project_id=X`, generados automáticamente |
| 8 | Selector con autocompletado | ✅ Confirmado en el HTML real: componente `select-dropdown-autocomplete` con los 10 usuarios activos, `defaultValue` igual al usuario actual, `redirect.url` con la forma correcta (incluye `plugin=TeamWorkload`) |
| 9 | Acceso con usuario Standard | 🔴 **No se pudo probar** — los 9 usuarios de la migración quedaron con rol `app-admin` (hallazgo ya documentado en el informe de investigación, sección 10.1); no hay ninguna cuenta no-admin disponible en este entorno. El mecanismo de permiso (`applicationAccessMap` + `Role::APP_ADMIN`) es el mismo que usa el propio Core para sus páginas de administración — hay alta confianza en que funcione, pero queda pendiente de una prueba real apenas se corrija el rol de algún usuario |
| 10 | Desactivar/retirar el plugin sin afectar el Core | ✅ Se renombró la carpeta del plugin (`TeamWorkload` → `TeamWorkload.disabled`) en caliente: el Dashboard y la lista de usuarios (páginas del Core) siguieron funcionando con HTTP 200 sin cambios; el propio Loader de Kanboard capturó el error de clase no encontrada y lo registró como `critical` en el log **sin caerse** (`Unable to load this plugin class`); nuestra propia URL respondió HTTP 200 con una pantalla de "no encontrado" en vez de un error 500. Al restaurar la carpeta, el plugin volvió a funcionar de inmediato sin reiniciar nada |

## 7. Evidencia HTTP (extraída de las respuestas reales)

**Caso 3 — Elías Alfonzo (id 5):**

```
Identificador | Columna                  | Título                                    | Prioridad | Fecha Límite
#17           | ⚙️ En Curso               | Capex - Módulo de Planificación          | 0         | No due date
#18           | ⚙️ En Curso               | Reservas - Automatización Export SAP     | 0         | No due date

Identificador | Columna                  | Título                                    | Prioridad | Fecha Límite
#1            | 📌 Listo para Desarrollo | Notas de Acceso - Refactorización Backend | 0         | 31/08/2026

Total: 3 open tasks in 2 projects
```

(Proyectos en orden alfabético: `adm-tech` antes que `INFRAWORK` — correcto.)

**Caso extra — Daniel Medina (id 6), para confirmar el orden por columna:**

```
Identificador | Columna                    | Título
#10           | 📥 Pendiente de Análisis   | Fondo Fijo - Automatización de Arqueos
#2            | 📌 Listo para Desarrollo   | ZRE - Automatización del Proceso de Pagos

Total: 2 open tasks in 1 projects
```

(`Pendiente de Análisis` es la primera columna del tablero de INFRAWORK,
`Listo para Desarrollo` la segunda — el orden coincide con la posición
real, no con el orden en que las tareas fueron creadas.)

No se tomaron capturas de pantalla (se validó extrayendo y verificando el
HTML real de cada respuesta, más preciso y citable que una imagen para
este documento) — se puede complementar con una captura manual si hace
falta para una presentación.

## 8. Procedimiento de rollback

Confirmado en la prueba del punto 10: alcanza con quitar (o renombrar) la
carpeta `plugins/TeamWorkload/` del contenedor.

```bash
lxc exec PFR-KANBOARD-TEST --project default -- mv \
  /var/www/kanboard/plugins/TeamWorkload \
  /var/www/kanboard/plugins/TeamWorkload.disabled
```

No hace falta:
- Reiniciar Apache ni PHP.
- Tocar la base de datos (el plugin no creó ninguna tabla propia — no
  tiene carpeta `Schema/`, decisión explícita de la Fase 1 al no
  necesitar persistencia propia).
- Revertir ningún archivo del Core (nunca se tocó ninguno).

Para reinstalar, restaurar la carpeta con el mismo nombre exacto
(`TeamWorkload`, con mayúsculas — ver la nota de la sección 9.1 de
`diseno-fase1.md` sobre por qué el casing exacto importa para la
resolución de rutas/plantillas).

## 9. Conclusión de la Fase 1

Los 3 ajustes de diseño quedaron incorporados y verificados en el código
real. De las 10 pruebas pedidas, **9 pasaron correctamente** y **1 quedó
pendiente** por una limitación real y ya conocida del entorno (todos los
usuarios son `app-admin` hoy) — no por una falla del plugin.

El único problema real encontrado durante las pruebas (`ENABLE_URL_REWRITE = false`)
no fue un defecto del plugin sino un hallazgo sobre el entorno, y quedó
resuelto sin tocar una sola línea de código porque el diseño ya usaba los
helpers de URL del Core (`$this->url->link()`/`to()`) en vez de rutas
escritas a mano — otro caso donde reutilizar el Core correctamente evitó
un problema, no lo causó.

**La Fase 1 se da por completa y funcional en el entorno de prueba.**
