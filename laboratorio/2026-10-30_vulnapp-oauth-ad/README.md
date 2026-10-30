# Ingreso con AD en VulnApp NG (623 #1085320)

> **Fecha:** 2026-10-30
> **Estado:** ✅ Aplicado en producción. El responsable ingresó con su cuenta de AD (16:48).

## Objetivo

Que VulnApp NG (`https://oss.personal.com.py/vulnapp/`) tenga **un solo ingreso**: la cuenta de AD, por el OAuth de SDI. Decisión del responsable: solo entra quien ya tenga usuario creado en VulnApp, y se verifica por su TPPY.

## Qué cambió

| Tema | Antes | Ahora |
|---|---|---|
| Ingreso | Usuario y contraseña locales | Botón "Ingresar con usuario de AD". El formulario no se muestra y `POST /login` no autentica |
| Quién entra | Cualquier usuario activo con contraseña | Usuario activo cuyo `username` coincida con el claim `sub` del token, sin distinguir mayúsculas |
| Usuario sin alta | No entraba | No entra. No se crean usuarios: ve un mensaje para pedir el alta a un administrador |
| `admin`, `sdi`, `visita` | Entraban con contraseña | ✅ No entran, por decisión del responsable. 🟡 Solo entrarían si existiera en AD una cuenta con ese mismo nombre |
| Cambio de contraseña | Obligatorio con `debe_cambiar_password` | Se ignora: la marca trabaría a los 12 usuarios que la tienen, y la pantalla redirige al dashboard |

La aplicación OAuth es `Vulnapp-OSS`: id **47**, `client_id` `v42arEJ86g`, `auth_only: true`. ✅ El `client_secret` está solo en `env.conf` del contenedor. Nunca en un repositorio.

🟡 "Entrar por grupo de AD" no se implementó como un control de grupo: se entendió como ingresar por AD con usuario ya creado. Es `auth_only`, y en Kanboard, con la misma configuración, `grupos` llegó vacío. Exigir un grupo requiere un 623 nuevo.

## Cómo funciona

El canje es el mismo que en Kanboard y ADM-TECH: ver [arquitectura del plugin de Kanboard](../../proyectos/kanboard-oauth-sdi/docs/00_Arquitectura.md#por-qué-no-sirve-el-plugin-oficial). La diferencia es el vínculo:

- ✅ Los usuarios de VulnApp son usuarios de red (`alfonzel`), igual que `sub`. Por eso se vincula directo, sin pasar por el correo.
- 🟡 Solo está comprobado con `alfonzel`. Los usuarios `u99xxxx` y los demás falta confirmarlos a medida que entren.

El código es de la aplicación, en el repositorio `DockerLab` (`vulnapp-ng/app`): rutas `/oauth/login` y `/oauth/callback`, sin librerías nuevas. La URL registrada en SDI no lleva barra final y no tiene `?`, así que aquí no aplica [TRB-023](../../docs/07_Troubleshooting.md#trb-023--el-retorno-del-login-con-ad-oauth-de-sdi-da-action-not-implemented).

## Cambios en el cluster

1. **Regla de ACL** ✅ (`ACL-OVN-1`, 21 → 22 reglas). La ruta ya existía (`10.150.0.0/16 via 192.168.0.6`). Backup: `~/ACL-OVN-1.bak-20261030-vulnapp-oauth.yaml` en `pfr-oss`.
   ```bash
   lxc network acl rule add ACL-OVN-1 ingress --project default action=allow \
     source=192.168.0.14 destination=10.150.49.41 protocol=tcp destination_port=443 \
     "description=VulnApp NG: login con OAuth de SDI (ciberseg.personal.com.py) 623 #1085320" state=enabled
   ```
2. **Credenciales** ✅: `SDI_OAUTH_CLIENT_ID` y `SDI_OAUTH_CLIENT_SECRET` agregadas a `/opt/vulnapp/env.conf` (`root:www-data`, `640`).
3. **Código** ✅: `app.py`, `templates/login.html`, `base.html` y `perfil.html` en `/opt/vulnapp/app/` (`root:www-data`, `640`), y reinicio de `vulnapp`.

**Backup:** `/root/vulnapp-bak-20261030-oauth/` en `PFR-VULNAPP-APP` (permisos `700`). Contiene `env.conf` y los cuatro archivos.

> **Nota:** no hay snapshot previo: el proyecto `PRJ-OSS` rechazó la creación manual (`Project "PRJ-OSS" doesn't allow for snapshot creation`). No hubo cambios en la base, así que el backup de archivos alcanza.

## Verificación

- ✅ 15 comprobaciones sobre una copia temporal en el contenedor, con token, escrituras y SMS simulados: formulario oculto, `POST /login` sin efecto, `state` vencido o distinto, usuario inexistente, usuario sin `sub`, usuario existente y usuario con `debe_cambiar_password`.
- ✅ Desde el contenedor: `curl https://ciberseg.personal.com.py/ad/login/oauth/authorize/` → `200`, con el certificado válido.
- ✅ Ingreso real del responsable: `usuarios.ultimo_acceso` de `alfonzel` a las 16:48 y sin errores en `journalctl -u vulnapp`.

> **Nota:** los rechazos quedan en `journalctl -u vulnapp` con el prefijo `OAuth SDI:`. Los ingresos correctos no aparecen ahí, porque el nivel de log es `WARNING`. Se ven en `usuarios.ultimo_acceso`.

## Dependencia de SDI

> **Advertencia:** si `ciberseg.personal.com.py` no responde, **nadie puede entrar a VulnApp**. Los datos no se pierden.

**Acceso de emergencia (sin SDI):** vuelve a mostrar el formulario de contraseña. Las cuentas conservan la contraseña que tenían.

```bash
lxc exec --project PRJ-OSS PFR-VULNAPP-APP -- sh -c 'echo VULNAPP_LOGIN_LOCAL=1 >> /opt/vulnapp/env.conf && systemctl restart vulnapp'
```

Cuando SDI vuelva, quitar esa línea de `env.conf` y reiniciar `vulnapp`.

> **Advertencia:** con ese modo activo, los usuarios creados por un administrador tienen la contraseña inicial `cambiar123` hasta cambiarla. Mantenerlo el menor tiempo posible.

## Rollback

```bash
lxc exec --project PRJ-OSS PFR-VULNAPP-APP -- sh -c '
  B=/root/vulnapp-bak-20261030-oauth
  cp -p $B/app.py /opt/vulnapp/app/ && cp -p $B/templates/*.html /opt/vulnapp/app/templates/ &&
  cp -p $B/env.conf /opt/vulnapp/ && systemctl restart vulnapp'
lxc network acl rule remove ACL-OVN-1 ingress --project default source=192.168.0.14 destination=10.150.49.41 protocol=tcp destination_port=443
```

## Observaciones

- 🟡 El `client_secret` se vio en una captura compartida. Pedir a SDI que lo regenere.
- 🟡 En `templates/login.html`, `TIMEOUT_MS = 30 * 60 * 1` da 1,8 segundos, no 30 minutos: parece faltar un `* 1000`. Ese script solo corre en el modo de emergencia. No se tocó.
- `lxc snapshot` lee la entrada estándar. Dentro de un script enviado por `ssh ... bash -s` se consume el resto del script: usar `</dev/null`. Es la misma causa de [TRB-017](../../docs/07_Troubleshooting.md).
