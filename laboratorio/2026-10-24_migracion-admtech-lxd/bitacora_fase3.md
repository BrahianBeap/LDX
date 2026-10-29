# Bitácora — Fase 3: entorno de desarrollo de ADM-TECH (2026-10-24/25)

## Cómo se ejecutó

- **24/10, noche:** un agente en segundo plano ejecutó los pasos 1 a 6 de [`fase3_entorno_desarrollo.md`](fase3_entorno_desarrollo.md).
- **Interrupción:** al llegar al paso del gateway, el agente ejecutó en la PC del usuario `Get-NetIPAddress` (PowerShell) para confirmar su IP. El antivirus/EDR corporativo lo bloqueó como reconocimiento de red y cortó el proceso de Claude Code. El agente no llegó a escribir su informe.
- **25/10:** revisión de estado de solo lectura, y el paso 7 (gateway) ejecutado de forma supervisada.

> **Lección:** los agentes sin supervisión no deben ejecutar comandos de reconocimiento sobre la PC del operador (interfaces, red, procesos), aunque sean inofensivos. Las instrucciones tienen que listar los comandos permitidos, no solo los prohibidos.

## Estado verificado (25/10, solo lectura)

| Elemento | Resultado |
|---|---|
| `DEV-ADMTECH-DB` | `RUNNING`, `pfr.1`, `192.168.0.18`, PostgreSQL 18.6, base `admtech` de 65 MB (dueño `admtech_app`, sin superusuario) |
| `DEV-ADMTECH-APP` | `RUNNING`, `pfr.1`, `192.168.0.19`, PHP 8.5.4, vhost `adm-dev`, `/adm/` responde 200 |
| Volumen `admtech-archivos-dev` | Montado en `/var/www/adm/archivos`, 699 archivos de muestra |
| Perfiles | `PRF-ADMTECH-DEV-DB`, `PRF-ADMTECH-DEV-APP` |
| `ACL-OVN-1` | Una regla nueva: `192.168.0.19 → 192.168.0.18 tcp/5432` ("DEV ADM-TECH: app hacia PostgreSQL") |
| Dump con datos de producción | **Ninguna copia remanente** (PC, `/tmp` de `pfr-oss` y contenedores revisados) |
| Repo `adm-tech` | Rama del usuario intacta. Refactor en el worktree `adm-tech-php85`, rama `feature/php85`, **11 commits locales sin push**, creada desde `fix/seguridad-tanda2` (`0920f54`) y no desde `master` |
| Credenciales de la base de desarrollo | Solo en el scratchpad local de la sesión (`agente_admtech/credenciales_dev.txt`), fuera de los repos |

**Corrección del relevamiento:** no hay llamadas PHP a `each()` ni `split()`. Los conteos del 24/10 eran código JavaScript embebido (`$.each`, `.split`). Los cambios reales que exigió PHP 8.5 son los de los commits de `feature/php85`.

## Paso 7 — Ruta `/adm` en `PFR-GW-SRV` (25/10, supervisado)

Procedimiento: [Modificar el LB.conf de un gateway de forma controlada](../../docs/06_Operacion.md#modificar-el-lbconf-de-un-gateway-de-forma-controlada).

- Backup: `/root/LB.conf.bak-20261025` (SHA-256 `f8dd2cb7…bb40eb2`, la versión del 16/10).
- Bloque insertado antes de `ProxyPass / http://192.168.0.106:80/` (fines de línea CRLF):

```apache
    # ADM-TECH entorno de desarrollo (DEV-ADMTECH-APP 192.168.0.19), solo desde 10.150.60.85 (2026-10-25)
    RedirectMatch ^/adm$ /adm/
    ProxyPass /adm/ http://192.168.0.19/adm/
    ProxyPassReverse /adm/ http://192.168.0.19/adm/
    ProxyPass /adm !
    <LocationMatch "^/adm(/|$)">
      Require ip 10.150.60.85
    </LocationMatch>
```

- `ProxyPass /adm !` se agregó en un segundo cambio: sin esa exclusión, `/adm` (sin barra) lo capturaba `ProxyPass /` y terminaba en Kanboard, porque `ProxyPass` tiene prioridad sobre `RedirectMatch`.
- Archivo final: SHA-256 `5058d432…72fd635`. `configtest` OK y recarga sin cortar conexiones.

| Ruta | Antes | Después |
|---|---|---|
| Kanboard (`/`, login, `/kanboard`), `/vulnapp/`, `/web.config`, `/ntf`, HTTP→HTTPS | 302 / 200 / 302 / 302 / 403 / 403 / 302 | **Sin cambios** |
| `/adm` | — | 302 → `/adm/` |
| `/adm/` (desde 10.150.60.85) | — | **200**, título `adm-tech` |

**Rollback:**
```bash
lxc exec PFR-GW-SRV --project PRJ-OSS -n -- sh -c 'cat /root/LB.conf.bak-20261025 > /etc/apache2/sites-available/LB.conf && apache2ctl configtest && systemctl reload apache2'
```

## Cómo probar

- URL: **`https://10.143.11.8/adm/`**, solo desde `10.150.60.85`. Desde cualquier otra IP responde 403.
- **Login:** OAuth no funciona en desarrollo (la URL de retorno registrada en SDI es la de producción), y el ingreso con usuario y contraseña está deshabilitado en el código desde el 2026-10-19 (DEC-014). Por eso se agregó un **ingreso de desarrollo** (commit `cbb6159` en `feature/php85`, autorizado por el usuario el 2026-10-25): botón "Ingresar como alfonzel (desarrollo, sin OAuth)" en la pantalla de login, o `https://10.143.11.8/adm/index.php?dev_login=1`.
  - Solo se activa con `SetEnv ADM_ENTORNO desarrollo`, `ADM_DEV_LOGIN_TPPY alfonzel` y `ADM_DEV_LOGIN_GRUPO ADMTECH_TEC_ADMIN` en `/etc/apache2/sites-available/adm-dev.conf` del contenedor (backup del vhost: `/root/adm-dev.conf.bak-20261025`).
  - Sigue el flujo real de `sing-in-backend.php` (grupos AD y permisos). Verificado: termina en `main.php` con sesión iniciada.
  - > **Advertencia:** esas variables **nunca** deben existir en el vhost de producción. Al hacer el pase, conviene quitar el bloque del código o dejarlo documentado como exclusivo de desarrollo.
  - Para retirarlo cuando OAuth funcione (URL de retorno `https://oss.personal.com.py/adm/` pedida a Ciberseguridad): borrar las tres `SetEnv` del vhost y recargar Apache.
- **Correo:** no se envía. `enviarMail()` no tiene la conexión a `Infraestructura` y lo registra en el log, que es lo esperado.
- **Log de errores:** `lxc exec DEV-ADMTECH-APP --project PRJ-OSS -n -- tail -f /var/log/apache2/error.log` (incluye `E_DEPRECATED`).

## Acceso abierto a cualquier IP (2026-10-26)

✅ Por decisión del responsable de la aplicación (Elías Alfonzo), que considera que los datos de desarrollo no son oficiales. Se le advirtió antes que el ingreso de desarrollo permite entrar como `alfonzel` con el grupo `ADMTECH_TEC_ADMIN` sin contraseña, y que la base es una copia de producción.

- `PFR-GW-SRV`: se quitó el bloque `<LocationMatch "^/adm(/|$)"> Require ip 10.150.60.85 </LocationMatch>` y se actualizó el comentario. Backup `/root/LB.conf.bak-20261026-adm`; `LB.conf` nuevo `6e02fb15…`; `configtest` OK y recarga sin cortar conexiones.
- Prueba desde un origen no autorizado antes (`127.0.0.1` en el gateway): `403` → después: `200`. Kanboard, VulnApp NG y el portal, sin cambios.

> **Advertencia:** con el acceso abierto, **cualquier persona de la red corporativa** que llegue a `https://oss.personal.com.py/adm/` puede usar el botón de ingreso de desarrollo. Antes de cualquier uso con datos oficiales o del pase a producción, hay que quitar las 3 `SetEnv` `ADM_*` del vhost `adm-dev.conf` (o volver a restringir por IP).

**Rollback** (volver a restringir):
```bash
lxc exec PFR-GW-SRV --project PRJ-OSS -n -- sh -c 'cat /root/LB.conf.bak-20261026-adm > /etc/apache2/sites-available/LB.conf && apache2ctl configtest && systemctl reload apache2' < /dev/null
```

## Login con OAuth de SDI (2026-10-29)

✅ SDI creó la aplicación OAuth `ADM-TECH-OSS` (623 #1084774, id 45, retorno `https://oss.personal.com.py/adm/`). Ver [18_Inventario_Ciberseguridad.md](../../docs/18_Inventario_Ciberseguridad.md). Se aplicó a pedido del responsable, desde `pfr-oss`.

**Verificación previa (solo lectura):**

| Comprobación | Resultado |
|---|---|
| Variables del vhost `adm-dev.conf` (solo nombres) | `DB_*`, `ADM_DEBUG`, `ADM_ENTORNO`, `ADM_DEV_LOGIN_TPPY`, `ADM_DEV_LOGIN_GRUPO`. **Faltaban** `ADM_CLIENT_ID` y `ADM_CLIENT_SECRET`, que el código usa en `index.php` (botón de AD y canje del código por el token) |
| Salida a `ciberseg.personal.com.py` (`10.150.49.41`) | Ruta por `192.168.0.6` (`PFR-GW-OAM`), pero la conexión era **rechazada** (7 ms): no había regla en `ACL-OVN-1` |

**1. Credenciales en el vhost**

- Backup: `/root/adm-dev.conf.bak-20261029-oauth` (SHA-256 `6fe98cf9…cc4faf2a`, verificado antes del cambio).
- Se agregaron 3 líneas después de `SetEnv ADM_DEBUG`: un comentario con la referencia al ticket, `SetEnv ADM_CLIENT_ID` y `SetEnv ADM_CLIENT_SECRET`. Los valores se pasaron por la entrada estándar de la sesión, sin quedar en archivos intermedios, argumentos ni historial. **No se registran en este repositorio.**
- Permisos sin cambios: `640 root:www-data`. `configtest` OK, recarga sin corte.
- Comprobación: `/adm/` arma el botón con `oauth/authorize/?client_id=<id nuevo>`.

> **Nota:** el `client_id` se transcribió de una captura del ticket. SDI devuelve la misma página para cualquier `client_id`, así que solo el login real confirma que es correcto. Si falla, cargar el valor copiado como texto desde el correo del ticket.

**2. Regla de firewall**

Backup de la ACL: `~/ACL-OVN-1.bak-20261029-oauth.yaml` en `pfr-oss` (19 reglas).

```bash
lxc network acl rule add ACL-OVN-1 ingress --project default action=allow \
  source=192.168.0.19 destination=10.150.49.41 protocol=tcp destination_port=443 \
  "description=DEV ADM-TECH: app hacia OAuth de SDI (ciberseg.personal.com.py)" state=enabled
```

Resultado: 20 reglas. Desde `DEV-ADMTECH-APP`, `curl https://ciberseg.personal.com.py/ad/login/oauth/authorize/` → `HTTP 200` en 0,04 s.

**Rollback:**
```bash
lxc network acl rule remove ACL-OVN-1 ingress source=192.168.0.19 destination=10.150.49.41 protocol=tcp destination_port=443
lxc exec DEV-ADMTECH-APP --project PRJ-OSS -- sh -c 'cat /root/adm-dev.conf.bak-20261029-oauth > /etc/apache2/sites-available/adm-dev.conf && apache2ctl configtest && systemctl reload apache2'
```

**Pendiente:**
- ✅ Prueba de login del responsable: **OK** (29/10). Confirma además que el `client_id` transcripto era correcto.
- ✅ Ingreso de desarrollo quitado el mismo día. Ver la sección siguiente.
- Antes del pase a producción: pedir a SDI que regeneren el `client_secret`, que quedó expuesto en una captura compartida en una conversación.
- En producción (`PFR-ADMTECH-APP`, `192.168.0.17`), crear la regla equivalente con ese origen.

## Ingreso de desarrollo retirado (2026-10-29)

✅ A pedido del responsable, después de probar el login con AD. Cierra la advertencia de la sección [Acceso abierto a cualquier IP](#acceso-abierto-a-cualquier-ip-2026-10-26): `/adm/` sigue abierto a la red corporativa, pero ahora solo se entra con una cuenta de AD que tenga un grupo `ADMTECH_TEC_*`.

- Verificado antes: las tres variables solo las usa `index.php` (botón "Ingresar como alfonzel (desarrollo, sin OAuth)" y `?dev_login=1`), tanto en `feature/php85` como en el código desplegado. `ADM_ENTORNO` no controla el envío de correos ni nada más.
- Backup: `/root/adm-dev.conf.bak-20261029-sin-devlogin` (SHA-256 `afbcbe84…58071d91`, verificado antes del cambio).
- Se quitaron 3 líneas: `SetEnv ADM_ENTORNO`, `ADM_DEV_LOGIN_TPPY` y `ADM_DEV_LOGIN_GRUPO`. `configtest` OK, recarga sin corte, permisos `640 root:www-data`.

| Prueba | Resultado |
|---|---|
| Botón de desarrollo en `/adm/` | No aparece (0 coincidencias; antes 1) |
| Botón "Iniciar sesión con Active Directory" | Sigue (1) |
| Forzar `index.php?dev_login=1` | `200` con la pantalla de login: no abre sesión ni redirige a la aplicación |

**Rollback** (vuelve a habilitar el ingreso sin contraseña; solo para diagnóstico):
```bash
lxc exec DEV-ADMTECH-APP --project PRJ-OSS -- sh -c 'cat /root/adm-dev.conf.bak-20261029-sin-devlogin > /etc/apache2/sites-available/adm-dev.conf && apache2ctl configtest && systemctl reload apache2'
```

> **Nota:** el código del ingreso de desarrollo (commit `cbb6159` de `feature/php85`) sigue en la aplicación, inactivo sin esas variables. Conviene quitarlo antes de unir la rama a `master`, para que no llegue a producción.

## Retiro del entorno

Ver la sección final de [`fase3_entorno_desarrollo.md`](fase3_entorno_desarrollo.md). Además, quitar el bloque `/adm` de `LB.conf` (o restaurar el backup) y la regla `.19 → .18` de la ACL.
