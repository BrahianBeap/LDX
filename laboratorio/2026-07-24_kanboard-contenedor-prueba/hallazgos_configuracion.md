# Hallazgos — Panel de administración de Kanboard

> Relevado el 2026-07-24 sobre `PFR-KANBOARD-TEST` (`http://localhost:8080`,
> vía túnel SSH), recorriendo el menú de Configuración (ícono de tuerca)
> logueado como `admin`. Sirve como referencia para explicar cómo se
> configura esta instancia y qué trae "de fábrica" desde la copia local.

---

## Cómo se llega acá

Menú lateral (ícono de tuerca, arriba a la derecha) → cada ítem carga
`?controller=ConfigController&action=X` (o un controlador propio para las
secciones que no son "configuración" en sentido estricto, como Tags o
Usuarios).

## Índice de secciones encontradas

| # | Sección (menú) | Controlador | Qué es |
|---|---|---|---|
| 1 | About | `ConfigController&action=index` | Info de versión + backup de la base |
| 2 | Application settings | `ConfigController&action=application` | Idioma, huso horario, formatos, URL |
| 3 | Email settings | `ConfigController&action=email` | Transporte de correo saliente |
| 4 | Project settings | `ConfigController&action=project` | Valores por defecto para proyectos nuevos |
| 5 | Board settings | `ConfigController&action=board` | Intervalos de refresco del tablero |
| 6 | Tags management | `TagController&action=index` | Tags globales (compartidos entre proyectos) |
| 7 | Link labels | `LinkController&action=show` | Tipos de relación entre tareas |
| 8 | Currency rates | `CurrencyController&action=show` | Tasas de cambio (para campos de costo) |
| 9 | Integrations | `ConfigController&action=integrations` | Telegram (u otros, según plugins) |
| 10 | Webhooks | `ConfigController&action=webhook` | URL de webhook saliente |
| 11 | API | `ConfigController&action=api` | Token y endpoint de la API JSON-RPC |
| 12 | Calendar settings | `ConfigController&action=show&plugin=Calendar` | Config del plugin Calendar |
| 13 | Plugins | `PluginController&action=show` | Plugins instalados |
| — | Users / Groups | `UserListController` / `GroupListController` | Gestión de cuentas y grupos (no es "Config", pero vive en el mismo menú de administración) |

---

## 1. About

Info de solo lectura + herramientas de mantenimiento de la base:

| Dato | Valor en esta prueba |
|---|---|
| Versión de Kanboard | 1.2.46 |
| Versión de PHP | 8.5.4 |
| Driver de base de datos | sqlite |
| Tamaño de la base | 396 KB |
| `journal_mode` | `wal` |

**Acciones disponibles acá:** descargar la base (`.sqlite` comprimido),
subir una base nueva, optimizar (`VACUUM`). Útil para hacer un backup
manual rápido del contenedor de prueba antes de experimentar.

## 2. Application settings

| Campo | Valor actual | Notas |
|---|---|---|
| Application URL | vacío | Se puede fijar para que los links en emails/notificaciones usen la URL real en vez de la detectada por request |
| Language | `en_US` | Hay 38 idiomas disponibles, **no incluye español** de forma nativa en esta lista — revisar si hace falta un paquete de idioma aparte |
| Timezone | `UTC` | Cambiar a `America/Asuncion` si se pone en producción |
| Date format | `m/d/Y` (formato US) | Cambiar a `d/m/Y` para formato local |
| Time format | `H:i` (24hs) | — |
| Password reset | habilitado | Permite "olvidé mi contraseña" — depende de que el email esté configurado (sección 3) |
| Notifications | deshabilitado | — |

## 3. Email settings

| Campo | Valor actual |
|---|---|
| Transporte | `mail` (función `mail()` de PHP, sin configurar) |
| Sender address | vacío |

**Nota:** para que funcionen notificaciones por correo o "recuperar
contraseña" hace falta configurar esto — con `mail` nativo de PHP
normalmente no llega nada sin un MTA local configurado. Lo más viable en
este entorno sería `smtp` apuntando a un relay interno (a definir con el
equipo de infraestructura).

## 4. Project settings (valores por defecto para proyectos nuevos)

| Campo | Valor actual |
|---|---|
| Color de tarea por defecto | Amarillo |
| Columnas por defecto | (ver `board_columns`, típicamente "Backlog, Ready, Work in progress, Done") |
| Categorías por defecto | vacío |
| Proyectos privados deshabilitados | no marcado |
| Restricción de subtareas / time tracking | subtask_time_tracking habilitado |
| CFD incluye tareas cerradas | habilitado |

## 5. Board settings

| Campo | Valor actual | Qué controla |
|---|---|---|
| Task highlight period | 172800 (segundos = 48hs) | Resalta tareas sin actividad reciente |
| Refresh interval (tablero público) | 60s | — |
| Refresh interval (tablero personal) | 10s | — |

## 6. Tags management

Vacío — "There is no global tag at the moment." Los tags específicos de
cada proyecto se manejan aparte, dentro del proyecto.

## 7. Link labels

Ya trae **8 tipos de relación por defecto** entre tareas (de fábrica de
Kanboard, no personalizado): `relates to`, `blocks`/`is blocked by`,
`duplicates`/`is duplicated by`, `is a child of`/`is a parent of`,
`targets milestone`/`is a milestone of`, `fixes`/`is fixed by`.

## 8. Currency rates

Moneda de referencia: **USD**. Sin tasas de cambio cargadas. Solo es
relevante si se usan campos de costo/presupuesto en las tareas.

## 9. Integrations

Solo aparece **Telegram** (username del bot, API key, proxy) — porque es
el único plugin de integración instalado (ver sección 13). Todo vacío, no
configurado.

## 10. Webhooks

Vacío. Cuando se configure una URL acá, Kanboard va a mandar un POST a esa
URL en eventos del sistema (tarea creada, movida, etc.) — útil para
integrarlo con otra herramienta interna.

## 11. API

Hay un **token de API ya generado** y el endpoint
`http://localhost/jsonrpc.php` (⚠️ ese hostname va a estar mal en cuanto se
acceda por otra vía que no sea `localhost` — revisar `application_url` de
la sección 2 antes de usar la API desde afuera). El token en sí **no se
incluye en este documento** por ser una credencial activa — se puede ver o
regenerar (botón "Reset token") desde esta misma pantalla logueado como
admin.

## 12. Calendar settings

Config del plugin **Calendar** (viene preinstalado, ver sección 13):
vista preferida (mes/semana/día), primer día de la semana, qué fecha usa
como base (inicio o creación), horario laboral, etc. Todo en sus valores
por defecto.

## 13. Plugins instalados

La copia que se trajo desde la PC local **ya tenía 5 plugins instalados**
en la carpeta `plugins/` (esto no lo instalamos nosotros, vino con la
copia):

| Plugin | Autor | Versión | Qué hace |
|---|---|---|---|
| Essential | Valentino Pesce | 1.1.3 | Tema visual |
| Telegram | Manu Varkey | 1.5.0 | Notificaciones por Telegram |
| Customizer | Craig Crosby | 1.14.2 | Logos, favicons, temas personalizados |
| Calendar | Frédéric Guillot, Alfred Bühler | 1.5.0 | Vista de calendario |
| SubtaskDescription | Shaun Fong | 1.1.1 | Campo de descripción en subtareas |

## Usuarios y grupos

- **1 usuario**: `admin`, rol Administrator, cuenta local (no LDAP).
- **0 grupos**.

Desde acá también se administra: perfil, avatar, cambio de contraseña,
2FA, acceso público, notificaciones, cuentas externas, integraciones, API
access, dashboard, time tracking, historial de logins y de resets de
contraseña — todo por usuario, vía "Users management" → clic en el
usuario.

---

## Resumen para explicar esta instancia a alguien más

1. **Es la copia real de tu Kanboard local**, incluidos sus 5 plugins y su
   único usuario (`admin`). No es una instalación limpia.
2. **Nada de email está configurado** — sin esto, "olvidé mi contraseña" y
   las notificaciones por correo no van a funcionar.
3. **El idioma/formato de fecha están en inglés/US** — cambiar en
   "Application settings" si se pone en uso real.
4. **La URL de la aplicación está vacía** — importante fijarla antes de
   usar la API o los webhooks desde fuera de `localhost`, si no los links
   van a salir mal armados.
5. **Hay un token de API activo** — tratarlo como una credencial real
   (no compartirlo, resetear si se expone).
