# Tema OssTheme para Kanboard (2026-10-26)

## Objetivo

Dar a Kanboard (`https://oss.personal.com.py/kanboard/`) la identidad visual de OSS (misma familia que VulnApp y el Portal OSS), empezando por el inicio de sesión. Pedido y aprobación del usuario el 2026-10-26.

El código y su documentación (concepto, archivos, desactivación, mantenimiento) están en el repositorio de Kanboard del usuario: `C:\Users\alfonzel\Documents\GitHub\kanboard\plugins\OssTheme\README.md`.

## Relevamiento previo (solo lectura)

| Elemento | Estado |
|---|---|
| Contenedor | `PFR-KANBOARD-TEST`, proyecto `default`, `pfr.1`, `192.168.0.106`; snapshots cada 6 h, retención 7 días |
| Software | Kanboard 1.2.46, PHP 8.5.4, Apache 2.4.66, Ubuntu 26.04 |
| Datos | SQLite `data/db.sqlite` (10 MB) + adjuntos (49 MB en total); 19 proyectos, 396 tareas |
| Acceso | Solo usuarios locales (`LDAP_AUTH` y `REVERSE_PROXY_AUTH` desactivados); "Recuérdame" y recuperación de contraseña activos |
| Plugins | Calendar, Customizer (tema KindaDark para todos, login propio), Essential (tema), Subtaskdescription, TeamWorkload, Telegram |
| Observación | Los 10 usuarios tienen rol `app-admin` 🟡 (revisar aparte) |

## Entorno de prueba

| Elemento | Valor |
|---|---|
| Contenedor | `PFR-KANBOARD-PRUEBA` (copia del snapshot `snap71`), `192.168.0.107`, sin snapshots programados, `web-public` en `127.0.0.1:8089` |
| Aislamiento | `MAIL_TRANSPORT` cambiado a `mail` (no hay `sendmail`: no envía); plugin Telegram movido a `/root`; Customizer y Essential fuera de `plugins/` |
| Publicación | `https://oss.personal.com.py/kanboard-prueba/`, solo `10.150.60.85` (`LB.conf` de `PFR-GW-SRV`, backup `/root/LB.conf.bak-20261026-kbprueba`, `Alias /kanboard-prueba` en el vhost de la copia) |
| Usuario de prueba | `oss.prueba` (`app-admin`), **solo en la copia** |

> **Nota:** durante la prueba de mover tareas, un pedido con nombres de campo incorrectos (`column_id` en lugar de `dst_column_id`/`src_column_id`) dejó la tarea #394 **de la copia** sin columna. Se restauró con la API correcta y se repitió la prueba (201 ida y vuelta). Producción no se vio afectada.

## Pase a producción (2026-10-26, 19:26 hora del contenedor)

✅ Con aprobación del usuario.

**Respaldos previos:**

| Respaldo | Ubicación |
|---|---|
| Snapshot LXD | `PFR-KANBOARD-TEST/pre-osstheme-20261026-1926` |
| Carpeta de la aplicación (plugins y config, sin `data/`) | `/root/kanboard-app-20261026-1926.tgz` (4,4 MB) |
| Base (copia consistente con `VACUUM INTO`, `integrity_check` = ok, 396 tareas) | `/root/db-20261026-1926.sqlite` (10 MB) |
| Adjuntos | `/root/kanboard-files-20261026-1926.tgz` (44 MB) |
| Plugins desactivados | `/root/plugins-desactivados-20261026-1926/` (Customizer, Essential) |

Todos con permisos `600`, dentro del contenedor.

> **Nota:** el primer intento se detuvo solo en el paso de la base por un error de comillas (la fecha quedó vacía). No había tocado ningún plugin. Se completó en un segundo paso.

**Cambios:** Customizer y Essential movidos fuera de `plugins/`; `plugins/OssTheme` instalado (`root:www-data`, `0755`/`0644`, `php -l` sin errores). Plugins activos: Calendar, OssTheme, Subtaskdescription, TeamWorkload, Telegram.

**Verificación:** login con el diseño nuevo, CSRF, `autocomplete`, "Recordarme" y recuperación presentes; recursos del plugin 200; panel sin sesión → login; recuperación 200. El ingreso con usuario real lo verifica el equipo (no hay credenciales de producción en esta sesión).

## Rollback

**Desactivar solo el tema** (vuelve el aspecto original de Kanboard, sin Customizer):
```bash
lxc exec PFR-KANBOARD-TEST --project default -n -- mv /var/www/kanboard/plugins/OssTheme /root/OssTheme.desactivado-$(date +%Y%m%d) < /dev/null
```

**Volver exactamente al estado anterior** (tema KindaDark):
```bash
lxc exec PFR-KANBOARD-TEST --project default -n -- sh -c 'mv /var/www/kanboard/plugins/OssTheme /root/OssTheme.desactivado-$(date +%Y%m%d) && mv /root/plugins-desactivados-20261026-1926/Customizer /root/plugins-desactivados-20261026-1926/Essential /var/www/kanboard/plugins/' < /dev/null
```

## Pendientes

- [ ] Prueba manual del equipo en producción: arrastrar tarjetas, ventana de edición, teléfono, tema oscuro (Perfil > Tema).
- [ ] Traducir "My calendar" (Calendar) y "Team workload" (TeamWorkload).
- [ ] Retirar el entorno de prueba: contenedor `PFR-KANBOARD-PRUEBA` y bloque `/kanboard-prueba/` del `LB.conf` (restaurar `/root/LB.conf.bak-20261026-kbprueba` solo si no hubo otros cambios después; si no, quitar el bloque).
- [ ] Borrar los respaldos de `/root` del contenedor cuando ya no hagan falta (el snapshot `pre-osstheme` vence con la retención normal solo si se la configura; hoy los snapshots manuales no expiran).
- [ ] Revisar el rol `app-admin` de los 10 usuarios.
