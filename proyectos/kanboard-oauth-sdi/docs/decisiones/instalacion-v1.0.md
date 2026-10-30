# Instalación de la v1.0 en PFR-KANBOARD-TEST (2026-10-30)

Contenedor: `PFR-KANBOARD-TEST` (proyecto `default`, `192.168.0.106`), Kanboard **1.2.46**, PHP **8.5.4**. Se aplicó a pedido del responsable, desde `pfr-oss`.

## Verificación previa (solo lectura)

| Comprobación | Resultado |
|---|---|
| Plugins instalados | Calendar, OssTheme, Subtaskdescription, TeamWorkload, Telegram. Sin `OAuth2` |
| Extensiones PHP | `curl`, `openssl`, `json` ✅ |
| Base | SQLite, 10 usuarios `nombre.apellido` (todos `app-admin`). Solo 1 con correo cargado |
| Salida a internet | ❌ No hay: el plugin se copia a mano, no con el instalador de Kanboard |
| Ruta a `10.150.49.41` | Por `192.168.0.254`, la salida por defecto. Sin ruta por `PFR-GW-OAM`, a diferencia de ADM-TECH |
| Conexión a `10.150.49.41:443` | Rechazada: falta la regla de ACL |

## 1. Backup ✅

`/root/kanboard-bak-20261030-oauth/` (permisos `700`):

| Archivo | Contenido | SHA-256 |
|---|---|---|
| `db.sqlite` | Copia consistente con `VACUUM INTO` (10 usuarios) | `40754fa1…00507a4` |
| `kanboard-codigo.tar.gz` | `/var/www/kanboard` sin `data/` | `69fcb632…2827fb` |
| `config.php` | `config.php` original | `bc75bf78…cd177b` |

## 2. Ruta persistente ✅

Archivo nuevo `/etc/netplan/60-ruta-sdi-oauth.yaml` (permisos `600`). No se tocó `50-cloud-init.yaml`:

```yaml
network:
  version: 2
  ethernets:
    eth1:
      routes:
        - to: 10.150.49.41/32
          via: 192.168.0.6
```

Se validó con `netplan generate` y se aplicó en caliente con `ip route replace 10.150.49.41/32 via 192.168.0.6 dev eth1 proto static`, sin `netplan apply`, para no cortar la red. Solo cambia la salida hacia `10.150.49.41`: el resto sigue por `192.168.0.254`.

**Rollback:**
```bash
lxc exec PFR-KANBOARD-TEST -- sh -c 'rm /etc/netplan/60-ruta-sdi-oauth.yaml && ip route del 10.150.49.41/32'
```

## 3. Regla de ACL ✅

Aplicada con aprobación manual del responsable (el clasificador automático la había bloqueado por ser un recurso compartido). La ACL pasó de 20 a 21 reglas:

```bash
lxc network acl show ACL-OVN-1 --project default > ~/ACL-OVN-1.bak-20261030-kanboard-oauth.yaml
lxc network acl rule add ACL-OVN-1 ingress --project default action=allow \
  source=192.168.0.106 destination=10.150.49.41 protocol=tcp destination_port=443 \
  "description=Kanboard: login con OAuth de SDI (ciberseg.personal.com.py) 623 #1085317" state=enabled
```

**Verificación:** `lxc exec PFR-KANBOARD-TEST -- curl -sS -o /dev/null -w '%{http_code}\n' https://ciberseg.personal.com.py/ad/login/oauth/authorize/` → `200` en 0,04 s. Confirma también que el contenedor confía en el certificado de `ciberseg`.

**Rollback:**
```bash
lxc network acl rule remove ACL-OVN-1 ingress --project default source=192.168.0.106 destination=10.150.49.41 protocol=tcp destination_port=443
```

## 4. Instalación del plugin y credenciales ✅

- Sintaxis validada con `php -l` (PHP 8.5.4) antes de instalar.
- `src/OAuth2` copiado a `/var/www/kanboard/plugins/OAuth2` (dueño `root:www-data`, archivos `644`, como `OssTheme`). Hashes iguales a los del repositorio.
- Sin credenciales el login quedó igual, sin botón: el plugin se activa solo con las constantes.
- Constantes `SDI_OAUTH_CLIENT_ID` / `SDI_OAUTH_CLIENT_SECRET` agregadas al final de `config.php`, pasadas por la entrada estándar (no quedan en archivos intermedios ni en el repositorio). `config.php` pasó de `664` a `640` (`www-data:www-data`).
- Comprobación: el login muestra "Ingresar con usuario de AD" y el botón redirige a `.../oauth/authorize/?client_id=0oxVoD587y&state=...`.

**Rollback:** borrar `/var/www/kanboard/plugins/OAuth2` y las dos líneas de `config.php`, o restaurar `config.php` desde el backup.

## 5. Primera prueba y corrección (v1.0.1) ✅

- Primer intento: `Internal Error: Action not implemented`. SDI devolvió `...&plugin=OAuth2?code=...` y tampoco devolvió `state`. Ver [TRB-023](../../../../docs/07_Troubleshooting.md#trb-023--el-retorno-del-login-con-ad-oauth-de-sdi-da-action-not-implemented).
- Se corrigió `Plugin.php` (v1.0.1) y se probó con una URL armada igual y un código falso: llega al plugin y se rechaza por falta de ingreso pendiente, como corresponde.
- Segundo intento del responsable: ✅ ingresó como `elias.alfonzo`. `last_logins` registra `auth_type = SdiAd`.

## 6. Claims del token de `Kanboard-OSS` ✅

Para saber qué datos trae el token de esta aplicación (`auth_only`), se agregó **temporalmente, solo en el servidor**, un `error_log` con los nombres de los claims, sin valores. El responsable volvió a ingresar (15:08) y después se restauró el archivo del repositorio: el hash coincide y no queda rastro del cambio temporal.

Resultado:

```
grupos,perfil,displayName,dn,employeeID,mail,mobile,gerencia,cargo,iat,exp,aud,iss,sub | grupos=0
```

- ✅ Llegan los mismos datos de identidad que en ADM-TECH, más `dn`, `iat`, `exp`, `aud` e `iss`.
- ✅ `grupos` llega **vacío**: la aplicación se pidió sin grupos de AD. Para asignar roles por grupo hace falta un 623 nuevo.
- ✅ `sub` es el usuario de red de AD (`alfonzel`), no `nombre.apellido`. Por eso la vinculación usa `mail`.
- Los mensajes del plugin (`$this->logger`) salen en `/var/log/apache2/kanboard-error.log`, por ejemplo: `SdiAd: alfonzel ingresó como elias.alfonzo`.

## 7. Login con contraseña deshabilitado (salvo `admin`) ✅

A pedido del responsable (2026-10-30), mientras la aplicación siga sin grupos de AD: `disable_login_form = 1` para los 9 usuarios del equipo. `DatabaseAuth` de Kanboard rechaza el login con contraseña de esos usuarios (`->eq('disable_login_form', 0)`), así que solo pueden entrar con el botón de AD.

- `admin` sigue con contraseña, como **entrada de emergencia** si SDI no responde.
- Backup previo: `/root/kanboard-bak-20261030-oauth/db-antes-sin-password.sqlite` (`fdfcff6d…`).
- Al 30/10 solo `elias.alfonzo` había probado el ingreso por AD. 🟡 Si a alguien no le coincide el correo de AD con su usuario, no va a poder entrar: un administrador le reactiva la contraseña desde la interfaz (Usuarios → usuario → Autenticación → quitar "No permitir el formulario de inicio de sesión") o con el comando de abajo.
- 🟡 El formulario de contraseña sigue visible. Si un usuario bloqueado lo usa, ve el error genérico de usuario o contraseña incorrectos.
- Las sesiones abiertas con "Recordarme" siguen activas hasta que vencen.

**Rollback (todos o un usuario):**
```bash
lxc exec PFR-KANBOARD-TEST -- php -r '$d=new PDO("sqlite:/var/www/kanboard/data/db.sqlite"); echo $d->exec("update users set disable_login_form=0 where username<>\"admin\"");'
# un solo usuario: ... where username="nombre.apellido"
```
