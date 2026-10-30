# Arquitectura del plugin "OAuth2" (ingreso con AD)

## Flujo de ingreso

```
 Navegador                Kanboard (PFR-KANBOARD-TEST)             SDI (ciberseg, 10.150.49.41)
    │  clic "Ingresar con      │                                          │
    │  usuario de AD"          │                                          │
    ├─────────────────────────►│ guarda state en la sesión (10 min)       │
    │◄──── redirección ────────┤                                          │
    ├──────── /ad/login/oauth/authorize/?client_id=…&state=… ────────────►│
    │                          │                       login de AD        │
    │◄─────────────── retorno a la URL registrada ?code=… ────────────────┤
    ├─────────────────────────►│ valida el state                          │
    │                          ├── POST JSON {client_id, secret, code} ──►│
    │                          │◄── {"status":"success","data":{JWT}} ────┤
    │                          │ lee mail del JWT → nombre.apellido       │
    │                          │ busca ese username (no crea usuarios)    │
    │◄──── sesión iniciada ────┤                                          │
```

El pedido del token sale del contenedor por `PFR-GW-OAM` (`192.168.0.6`). Necesita una ruta propia y una regla en `ACL-OVN-1`; ver [instalacion-v1.0.md](decisiones/instalacion-v1.0.md).

## Por qué no sirve el plugin oficial

✅ Se comparó con el código de ADM-TECH (`/var/www/adm/index.php`), que ya ingresa contra SDI (2026-10-29).

| Punto | Plugin oficial / OAuth estándar | SDI |
|---|---|---|
| Pedido del token | Formulario con `grant_type` y `redirect_uri` | JSON con `client_id`, `client_secret` y `code`. 🔴 No se sabe si acepta el formulario |
| Respuesta del token | `access_token` en el primer nivel | Dentro de `data`: `{"status":"success","data":{"access_token":…}}`. ✅ Con esto alcanza para que el oficial falle |
| Datos del usuario | Los pide a una URL aparte con el token | No hay esa URL conocida. Los datos vienen en el propio JWT (`sub` = TPPY, `mail`, `displayName`, `grupos`…) |

## Corrección de la URL de retorno

✅ SDI agrega `?code=...` a la URL registrada aunque esta ya tenga `?`. El retorno llega como `...&plugin=OAuth2?code=XXX` y el Router de Kanboard descarta ese nombre de plugin ("Action not implemented"). Los plugins se inicializan antes de `Router::dispatch()`, así que `Plugin::fixSdiCallbackUrl()` separa `code` y deja `plugin=OAuth2` con `Request::setParams()`. Ver [TRB-023](../../../docs/07_Troubleshooting.md#trb-023--el-retorno-del-login-con-ad-oauth-de-sdi-da-action-not-implemented).

## Componentes

| Archivo | Función |
|---|---|
| `Plugin.php` | Si están las constantes `SDI_OAUTH_CLIENT_*`, corrige la URL de retorno de SDI (ver abajo), registra el proveedor `SdiAd`, abre `OAuthController::handler` sin sesión y agrega el botón al login |
| `Controller/OAuthController.php` | Hereda el flujo del Core (`step1`/`step2`). Agrega tres cosas: no hace nada con sesión iniciada, corta si SDI vuelve con `error` y muestra el motivo del rechazo |
| `Auth/SdiOAuthService.php` | Arma la URL de autorización, valida el `state` y canjea el código por el JWT, igual que ADM-TECH |
| `Auth/SdiAuthProvider.php` | Vincula el usuario de AD con el usuario local |
| `User/SdiUserProvider.php` | Devuelve el `id` del usuario local, y el Core inicia la sesión sin crear ni sincronizar nada |
| `Template/auth/login.php` | Botón "Ingresar con usuario de AD". Se engancha en `template:auth:login-form:after`, que la plantilla de login de `OssTheme` conserva |

## Datos que trae el token

✅ Verificado el 2026-10-30 (ver [instalacion-v1.0.md](decisiones/instalacion-v1.0.md#6-claims-del-token-de-kanboard-oss-)):

| Claim | Uso actual / posible |
|---|---|
| `sub` | Usuario de red de AD (ej. `alfonzel`). Se registra en el log |
| `mail` | **Vinculación** con el usuario local |
| `displayName` | Posible: completar el nombre del perfil |
| `gerencia`, `cargo`, `employeeID`, `perfil`, `mobile`, `dn` | Sin uso |
| `grupos` | **Vacío**: la aplicación es solo de autenticación. Roles por grupo requieren un 623 nuevo |
| `iat`, `exp`, `aud`, `iss` | Datos estándar del JWT. Sin uso (la firma no se verifica, ver Seguridad) |

## Vinculación de usuarios

- Se toma el claim `mail` del JWT. Tiene que terminar en `@personal.com.py`.
- La parte anterior a la `@` tiene que coincidir con un `username` de Kanboard (hoy los 10 usuarios tienen el formato `nombre.apellido`).
- **No se crean usuarios.** Sin coincidencia se rechaza el ingreso, con un mensaje que indica pedir el alta.
- Un usuario desactivado en Kanboard (`is_active = 0`) no puede ingresar: lo controla el Core.
- El log de Kanboard (`LOG_DRIVER=system`, syslog) registra cada ingreso y cada rechazo con el TPPY.

🟡 No está verificado que el `mail` de AD tenga siempre el formato `nombre.apellido`. Si para alguien no coincide, hay dos opciones: renombrar su usuario en Kanboard o agregar en el plugin una tabla de excepciones.

## Seguridad

| Tema | Decisión |
|---|---|
| `state` | Se genera y se guarda en la sesión por 10 minutos, y es de un solo uso. Si SDI lo devuelve, tiene que coincidir. ✅ SDI no lo devuelve (2026-10-30): en ese caso alcanza con que este navegador haya iniciado el ingreso: protege contra un `code` inyectado desde otro sitio, pero no tanto como el `state` completo |
| Firma del JWT | No se verifica (ADM-TECH tampoco lo hace). El token llega directo de SDI por HTTPS, con el certificado validado (`HTTP_VERIFY_SSL_CERTIFICATE = true`), en un pedido autenticado con el secreto |
| Secreto | Solo en `config.php` del contenedor, con permisos `640`. Nunca en el repositorio |
| Login local | Deshabilitado para todos y formulario oculto (`HIDE_LOGIN_FORM`) desde el 2026-10-30. Si SDI no responde, ver el acceso de emergencia en [instalacion-v1.0.md](decisiones/instalacion-v1.0.md#8-solo-ingreso-con-ad-formulario-oculto-y-admin-sin-contraseña-) |

## Duración de la sesión

✅ Verificado en el código y la configuración de Kanboard 1.2.46 (2026-10-30):

| Qué | Valor | Efecto |
|---|---|---|
| `SESSION_DURATION` (`config.php`) | `0` | La cookie dura hasta que se cierra el navegador |
| `session.gc_maxlifetime` (PHP) | `1440` s | La sesión vence tras **24 minutos sin actividad**. `SessionHandler::write` corre el vencimiento en cada pedido |
| "Recordarme" | 60 días | No se crea: el ingreso por AD no lo usa y el formulario está oculto. `RememberMeAuth` no controla `disable_login_form`, por eso se borraron los existentes |

🔴 No se sabe si SDI mantiene una sesión propia. Si la mantiene, al volver a entrar no se pide de nuevo la contraseña de AD.

## Dependencias

| Dependencia | Si falla |
|---|---|
| `ciberseg.personal.com.py` (`10.150.49.41:443`) | El botón de AD da error y **nadie puede entrar** (sin login local). Las sesiones ya abiertas siguen |
| Ruta `10.150.49.41 via 192.168.0.6` y `PFR-GW-OAM` | Igual que la anterior |
| Regla `192.168.0.106 → 10.150.49.41 tcp/443` en `ACL-OVN-1` | Igual que la anterior |
| Constantes en `config.php` | El plugin no se activa y el botón no aparece |
