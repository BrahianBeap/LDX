# Kanboard en `/kanboard/` y raíz libre para el portal (2026-10-26)

## Objetivo

Hoy `https://10.143.11.8/` publica Kanboard en la raíz. Se mueve Kanboard a `https://10.143.11.8/kanboard/` para que la raíz quede libre para un **portal** con la lista de aplicaciones del área.

✅ Pedido del usuario (Elías Alfonzo), 2026-10-26.

## Estado previo (relevado, solo lectura)

| Elemento | Estado |
|---|---|
| `PFR-GW-SRV` `LB.conf` (SHA-256 `5058d432…72fd635`) | `ProxyPass / http://192.168.0.106:80/` (toda la raíz a Kanboard) y `Redirect /kanboard /` (lo inverso de lo buscado) |
| Vhost de `PFR-KANBOARD-TEST` (`/etc/apache2/sites-available/kanboard.conf`) | `DocumentRoot /var/www/kanboard`, `AllowOverride All` |
| URL de la aplicación en Kanboard (`settings.application_url`) | Vacía |
| Módulos del gateway | `headers` habilitado; `rewrite` **no** |
| `/var/www/html/index.html` del gateway | Página por defecto de Apache |
| Otros Kanboard en el cluster | `CAR-KANBOARD` y `PFR-KANBOARD-DR` (`car.1`, sin IP) |

## Paso 1 — Kanboard responde también en `/kanboard/` (aplicado 2026-10-26)

Cambios en `PFR-KANBOARD-TEST`, sin impacto: el gateway todavía no usa la ruta nueva y la raíz sigue igual.

| Archivo | Cambio | Backup |
|---|---|---|
| `/etc/apache2/sites-available/kanboard.conf` | `Alias /kanboard /var/www/kanboard` debajo del `DocumentRoot` | `/root/kanboard.conf.bak-20261026` (`9b2221f7…`) |
| `/var/www/kanboard/.htaccess` | `RewriteCond %{REQUEST_FILENAME} !-d` antes del `RewriteRule` | `/root/kanboard.htaccess.bak-20261026` (`950b50a0…`) |

**Por qué el cambio en `.htaccess`:** la regla original reescribe todo lo que no es archivo (incluido el directorio `/kanboard/`) a `index.php`. Dentro de un `Alias` y sin `RewriteBase`, Apache termina ejecutando `/index.php`. Kanboard calcula su ruta base con `dirname(PHP_SELF)` (`app/Helper/UrlHelper.php`), creía estar en `/` y generaba enlaces sin el prefijo. Con `!-d` los directorios los resuelve `DirectoryIndex` y `PHP_SELF` queda `/kanboard/index.php`.

> **Advertencia:** `.htaccess` es un archivo de Kanboard. Una actualización de versión lo pisa y hay que volver a aplicar este cambio (el mismo cambio está en la copia local `C:\Users\alfonzel\Documents\GitHub\kanboard`).

**Verificación (desde el contenedor):**

| Ruta | `/` | `/kanboard/` |
|---|---|---|
| Inicio | 302 → `/?controller=AuthController…` | 302 → `/kanboard/?controller=AuthController…` |
| Login | 200 | 200 |
| `data/db.sqlite` | 403 | 403 |
| CSS | 200 | 200 |
| `jsonrpc.php` | 200 | 200 |
| Enlaces del login | `/?controller=…` | `/kanboard/?controller=…` |

Desde `PFR-GW-SRV`: `http://192.168.0.106/kanboard/` → 302 (correcto).

**Rollback:**
```bash
lxc exec PFR-KANBOARD-TEST --project default -n -- sh -c 'cp -p /root/kanboard.conf.bak-20261026 /etc/apache2/sites-available/kanboard.conf && cp -p /root/kanboard.htaccess.bak-20261026 /var/www/kanboard/.htaccess && apache2ctl configtest && systemctl reload apache2' < /dev/null
```

## Paso 2 — Gateway: Kanboard en `/kanboard/`, raíz libre (aplicado 2026-10-26)

✅ Aplicado con OK del usuario, sin el portal (se hace después).

| Elemento | Valor |
|---|---|
| Backup | `/root/LB.conf.bak-20261026` (SHA-256 `5058d432…72fd635`) |
| Archivo nuevo | SHA-256 `dee8de49…5bdb0755`, CRLF conservado |
| Módulo | `a2enmod rewrite` |
| Aplicación | `configtest` OK, `systemctl reload apache2` (sin cortar conexiones) |

**Resultado real (desde 10.150.60.85):**

| Ruta | Antes | Después |
|---|---|---|
| `/` | 302 → login de Kanboard | **200** (página por defecto de Apache, hasta que esté el portal) |
| `/?controller=…`, `/index.php?controller=…` | 200 / 302 | **302 → `/kanboard/?controller=…`** |
| `/kanboard`, `/kamboard` | 302 → `/` | **302 → `/kanboard/`** |
| `/kanboard/` | 302 → `//` | **302 → login en `/kanboard/`** |
| Login, CSS bajo `/kanboard/` | 302 | **200** (27 de 27 enlaces con prefijo `/kanboard/`) |
| `/kanboard/data/db.sqlite`, `/kanboard/web.config`, `/web.config` | — / — / 403 | **403** |
| `/jsonrpc.php`, `/kanboard/jsonrpc.php` | 200 / 302 | **200 / 200** |
| `/vulnapp/`, `/adm`, `/adm/`, `/ntf`, HTTP→HTTPS | 302 / 302 / 200 / 403 / 302 | **Sin cambios** |

**Rollback:**
```bash
lxc exec PFR-GW-SRV --project PRJ-OSS -n -- sh -c 'cat /root/LB.conf.bak-20261026 > /etc/apache2/sites-available/LB.conf && apache2ctl configtest && systemctl reload apache2' < /dev/null
```

### Cambio aplicado

Procedimiento: [Modificar el LB.conf de un gateway de forma controlada](../../docs/06_Operacion.md#modificar-el-lbconf-de-un-gateway-de-forma-controlada). El archivo usa fines de línea CRLF.

**Prerrequisito:** `a2enmod rewrite` en `PFR-GW-SRV` (se carga con el reload).

**Se quitan:**
```apache
    ProxyPass /kanboard !
    ProxyPass /kamboard !
    ProxyPass / http://192.168.0.106:80/
    ProxyPassReverse / http://192.168.0.106:80/
    Redirect /kanboard /
    Redirect /kamboard /
```

**Se agrega** (en el lugar de `ProxyPass /kanboard !`, antes del bloque ADM-TECH):
```apache
    # Kanboard en /kanboard/ (PFR-KANBOARD-TEST 192.168.0.106); la raíz queda para el portal
    RedirectMatch ^/(kanboard|kamboard)$ /kanboard/
    RedirectMatch ^/kamboard/(.*)$ /kanboard/$1
    ProxyPass /kanboard/web.config !
    ProxyPass        /kanboard/ http://192.168.0.106/kanboard/
    ProxyPassReverse /kanboard/ http://192.168.0.106/kanboard/
    # Compatibilidad con enlaces viejos (correos, Telegram, favoritos) y con la API anterior
    RewriteEngine On
    RewriteCond %{QUERY_STRING} (^|&)controller=
    RewriteRule ^/(index\.php)?$ /kanboard/ [R=302,L]
    ProxyPass /jsonrpc.php http://192.168.0.106/kanboard/jsonrpc.php
```

Y el bloqueo de `web.config` (Nessus 121479) se extiende a la ruta nueva, dentro del mismo bloque (antes del `ProxyPass /kanboard/`):
```apache
    ProxyPass /kanboard/web.config !
    <Location "/kanboard/web.config">
      Require all denied
    </Location>
```

| Decisión | Motivo |
|---|---|
| Redirección **302** y no 301 | Los navegadores guardan las 301. Con 302 el rollback no deja redirecciones cacheadas. |
| `ProxyPass /jsonrpc.php` temporal | Los clientes de la API (colección de Postman, scripts) siguen funcionando hasta que se actualicen. Retirarlo después de avisar. |
| Bloqueo de `/kanboard/web.config` | Sin él se reabre el hallazgo Nessus 121479 por la ruta nueva. |
| Sin `ProxyPass /` | La raíz la sirve el propio gateway (`DocumentRoot /var/www/html`), donde va el portal. |

**Resultado esperado:**

| Ruta | Después |
|---|---|
| `/` | Página del gateway (portal) |
| `/kanboard`, `/kamboard` | 302 → `/kanboard/` |
| `/kanboard/` | Kanboard (302 al login) |
| `/?controller=…`, `/index.php?controller=…` | 302 → `/kanboard/?controller=…` |
| `/jsonrpc.php` | API de Kanboard |
| `/web.config`, `/kanboard/web.config` | 403 |
| `/vulnapp/`, `/adm/`, `/ntf`, HTTP→HTTPS | Sin cambios |

**Efectos para los usuarios:** tienen que iniciar sesión una vez (la cookie pasa a ruta `/kanboard/`).

**Rollback:** restaurar el backup del `LB.conf` y recargar. `mod_rewrite` puede quedar habilitado sin efecto.

## Pendientes

- ✅ Portal en la raíz publicado el 26/10 en los 3 gateways: [`proyectos/portal-oss/`](../../proyectos/portal-oss/).
- Prueba funcional de un usuario: login, tableros, tareas, adjuntos, plugins (Calendar, TeamWorkload).
- Pasar el estado final a `docs/` (rutas del gateway en Configuración, ficha de Kanboard) cuando esté el portal.
- Cargar la URL de la aplicación en Kanboard (`https://oss.personal.com.py/kanboard/`) cuando el certificado esté instalado.
- Actualizar la colección de Postman de [`recursos/kanboard-api/`](../../recursos/kanboard-api/) a `/kanboard/jsonrpc.php`.
- Replicar en los gateways de Carpinelli y Fernando dentro de la Etapa 2, antes de sumar sus IPs al DNS.
