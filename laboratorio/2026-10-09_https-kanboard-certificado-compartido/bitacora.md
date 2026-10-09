# Bitácora — HTTPS para Kanboard con el certificado compartido

Ver contexto y resultado en [README.md](README.md).

---

## Paso 1 — Verificar si ya había DNS pedido (solo lectura)

```bash
host 10.143.11.8
host 192.168.91.117
host 10.11.11.12
host oss.personal.com.py
getent hosts 10.143.11.8 192.168.91.117 10.11.11.12
```

Resultado: los 4 `host` devolvieron `NXDOMAIN` (no existe registro, ni directo ni inverso), incluyendo el nombre que ya tiene el certificado. `getent hosts` no devolvió nada. Confirmado: no hay DNS pedido para nada de esto.

## Paso 2 — Confirmar que el certificado ya existe y es el mismo en los 3 gateways

```bash
lxc exec CAR-GW-SRV --project PRJ-OSS -- openssl x509 -in /etc/ssl/certs/server.crt -noout -subject -issuer -dates -ext subjectAltName
lxc exec FDO-GW-SRV --project PRJ-OSS -- openssl x509 -in /etc/ssl/certs/server.crt -noout -subject -issuer -dates -ext subjectAltName
lxc exec PFR-GW-SRV --project PRJ-OSS -- md5sum /etc/ssl/certs/server.crt
lxc exec CAR-GW-SRV --project PRJ-OSS -- md5sum /etc/ssl/certs/server.crt
lxc exec FDO-GW-SRV --project PRJ-OSS -- md5sum /etc/ssl/certs/server.crt
```

Resultado: mismo `subject=CN=oss.personal.com.py`, mismo `issuer=CN=AutoridadOSS`, mismas fechas (2026-09-03 a 2027-09-03), **mismo hash MD5 (`29d054e93d6ea62d66e2052c4d49242a`) en los 3 gateways** — es literalmente el mismo archivo, desplegado idéntico en los 3 sitios.

## Paso 3 — Primer intento (falló en tiempo de ejecución, no en sintaxis)

Backup:
```bash
lxc exec PFR-GW-SRV --project PRJ-OSS -- cp /etc/apache2/sites-available/LB.conf /etc/apache2/sites-available/LB.conf.bak-20261009-https
```

Reemplazo de la línea rota vieja (`ProxyPass /kanboard http://CAR-kanboard-1/`, dentro del `VirtualHost *:443`) por un bloque `<Location "/">` con las reglas de Kanboard adentro:

```bash
lxc exec PFR-GW-SRV --project PRJ-OSS -- sed -i 's|    ProxyPass /kanboard http://CAR-kanboard-1/|    <Location "/">\n      SSLVerifyClient none\n      ProxyPass /kanboard !\n      ProxyPass /kamboard !\n      ProxyPass / http://192.168.0.106:80/\n      ProxyPassReverse / http://192.168.0.106:80/\n      Redirect /kanboard /\n      Redirect /kamboard /\n    </Location>|' /etc/apache2/sites-available/LB.conf

lxc exec PFR-GW-SRV --project PRJ-OSS -- sed -i "s|    <Location '/ntf'>|    <Location '/ntf'>\n      SSLVerifyClient require|" /etc/apache2/sites-available/LB.conf
```

```bash
lxc exec PFR-GW-SRV --project PRJ-OSS -- apache2ctl configtest
```
```
AH00526: Syntax error on line 80 of /etc/apache2/sites-enabled/LB.conf:
ProxyPass|ProxyPassMatch can not have a path when defined in a location.
```

**Causa del error de sintaxis:** `ProxyPass`/`ProxyPassMatch` no pueden llevar un argumento de path explícito cuando están **dentro** de un bloque `<Location>` — el path ya lo da el propio `<Location>`. Había mezclado la sintaxis de "vhost top-level" (con path explícito, la que sí funciona en el puerto 80) con la de "dentro de Location" (sin path).

### Verificación de que el servicio no se cayó

```bash
lxc exec PFR-GW-SRV --project PRJ-OSS -- systemctl is-active apache2
```
```
active
```
Apache quedó sirviendo con la configuración anterior (válida) durante todo este intento fallido — el `reload` rechazado no tumba el servicio.

### Rollback a estado conocido-bueno

```bash
lxc exec PFR-GW-SRV --project PRJ-OSS -- cp /etc/apache2/sites-available/LB.conf.bak-20261009-https /etc/apache2/sites-available/LB.conf
lxc exec PFR-GW-SRV --project PRJ-OSS -- apache2ctl configtest
lxc exec PFR-GW-SRV --project PRJ-OSS -- systemctl reload apache2
```
```
Syntax OK
```

## Paso 4 — Segundo intento: sintaxis corregida, pero falla funcional

Se sacaron los `ProxyPass`/`Redirect` de adentro del `<Location>` (quedaron a nivel de vhost, con su path explícito, igual que en el puerto 80), dejando el `<Location "/">` solo con `SSLVerifyClient none`:

```bash
lxc exec PFR-GW-SRV --project PRJ-OSS -- sed -i 's|    ProxyPass /kanboard http://CAR-kanboard-1/|    <Location "/">\n      SSLVerifyClient none\n    </Location>\n    ProxyPass /kanboard !\n    ProxyPass /kamboard !\n    ProxyPass / http://192.168.0.106:80/\n    ProxyPassReverse / http://192.168.0.106:80/\n    Redirect /kanboard /\n    Redirect /kamboard /|' /etc/apache2/sites-available/LB.conf

lxc exec PFR-GW-SRV --project PRJ-OSS -- sed -i "s|    <Location '/ntf'>|    <Location '/ntf'>\n      SSLVerifyClient require|" /etc/apache2/sites-available/LB.conf

lxc exec PFR-GW-SRV --project PRJ-OSS -- apache2ctl configtest
```
```
Syntax OK
```

```bash
lxc exec PFR-GW-SRV --project PRJ-OSS -- systemctl reload apache2
lxc exec PFR-GW-SRV --project PRJ-OSS -- curl -k -sI https://localhost/ --max-time 5
```

Resultado: **sin salida** (conexión fallando silenciosamente). Diagnóstico con `curl -kv`:

```bash
lxc exec PFR-GW-SRV --project PRJ-OSS -- curl -kv https://localhost/ --max-time 5 2>&1 | tail -30
```
```
* SSL connection using TLSv1.3 / TLS_AES_256_GCM_SHA384 / X25519MLKEM768 / RSASSA-PSS
* Server certificate: subject: CN=oss.personal.com.py ...
> GET / HTTP/1.1
* TLSv1.3 (IN), TLS alert, unknown (628):
* OpenSSL SSL_read: OpenSSL/3.5.5: error:0A00045C:SSL routines::tlsv13 alert certificate required, errno 0
curl: (56) OpenSSL SSL_read: OpenSSL/3.5.5: error:0A00045C:SSL routines::tlsv13 alert certificate required, errno 0
```

**Confirmado:** el servidor sigue exigiendo certificado incluso para `/`. La sintaxis era válida pero el comportamiento en runtime no — ver la explicación de la causa (orden de evaluación de `SSLVerifyClient` vs. el saludo TLS) en [README.md](README.md).

## Paso 5 — Fix real: invertir la lógica (vhost en `optional`, `/ntf` sube a `require`)

```bash
lxc exec PFR-GW-SRV --project PRJ-OSS -- sed -i '0,/SSLVerifyClient require/s//SSLVerifyClient optional/' /etc/apache2/sites-available/LB.conf
```

(el `0,/patron/s//.../ ` limita el reemplazo a la **primera** ocurrencia — la del `VirtualHost`, no la que ya estaba dentro de `/ntf`)

Verificación de que quedaron las 3 líneas correctas:
```bash
lxc exec PFR-GW-SRV --project PRJ-OSS -- grep -n "SSLVerifyClient" /etc/apache2/sites-available/LB.conf
```
```
62:     SSLVerifyClient optional
79:      SSLVerifyClient none
89:      SSLVerifyClient require
```

```bash
lxc exec PFR-GW-SRV --project PRJ-OSS -- apache2ctl configtest
lxc exec PFR-GW-SRV --project PRJ-OSS -- systemctl reload apache2

lxc exec PFR-GW-SRV --project PRJ-OSS -- curl -k -sI https://localhost/ --max-time 5
lxc exec PFR-GW-SRV --project PRJ-OSS -- curl -k -sI https://localhost/ntf --max-time 5
```

**Resultado — funcionó:**
```
HTTP/1.1 302 Found
Location: /?controller=AuthController&action=login
Set-Cookie: KB_SID=...
                                                    <- Kanboard, SIN pedir certificado

HTTP/1.1 403 Forbidden                             <- NTF, SIGUE exigiendo certificado
```

Confirmado también desde el navegador real del usuario (`https://10.143.11.8/`): carga el tablero completo de Kanboard, con la advertencia de certificado esperada (nombre/CA no reconocidos todavía por el navegador, sin DNS).

## Paso 6 — Forzar HTTP → HTTPS para todo excepto Loki

Backup:
```bash
lxc exec PFR-GW-SRV --project PRJ-OSS -- cp /etc/apache2/sites-available/LB.conf /etc/apache2/sites-available/LB.conf.bak-20261009-redirect80
```

Se sacaron las reglas de Kanboard del `VirtualHost *:80` (ya no hace falta servirlo ahí, solo redirigir), con cada operación **limitada a la primera ocurrencia** (el rango `1,/<\/VirtualHost>/`) para no tocar por error las reglas equivalentes que ya estaban en el `VirtualHost *:443`:

```bash
lxc exec PFR-GW-SRV --project PRJ-OSS -- sed -i '1,/<\/VirtualHost>/{/^    ProxyPass \/kanboard !$/d}' /etc/apache2/sites-available/LB.conf
lxc exec PFR-GW-SRV --project PRJ-OSS -- sed -i '1,/<\/VirtualHost>/{/^    ProxyPass \/kamboard !$/d}' /etc/apache2/sites-available/LB.conf
lxc exec PFR-GW-SRV --project PRJ-OSS -- sed -i '1,/<\/VirtualHost>/{/^    ProxyPass \/ http:\/\/192.168.0.106:80\/$/d}' /etc/apache2/sites-available/LB.conf
lxc exec PFR-GW-SRV --project PRJ-OSS -- sed -i '1,/<\/VirtualHost>/{/^    ProxyPassReverse \/ http:\/\/192.168.0.106:80\/$/d}' /etc/apache2/sites-available/LB.conf
lxc exec PFR-GW-SRV --project PRJ-OSS -- sed -i '1,/<\/VirtualHost>/{/^    Redirect \/kanboard \/$/d}' /etc/apache2/sites-available/LB.conf
lxc exec PFR-GW-SRV --project PRJ-OSS -- sed -i '1,/<\/VirtualHost>/{s|^    Redirect /kamboard /$|    Redirect / https://10.143.11.8/|}' /etc/apache2/sites-available/LB.conf
```

Verificación del archivo completo antes de aplicar (confirmado manualmente: Loki intacto en `:80`, bloque `:443` sin tocar) — ver el archivo completo en el historial de la sesión, omitido acá por extensión.

```bash
lxc exec PFR-GW-SRV --project PRJ-OSS -- apache2ctl configtest
lxc exec PFR-GW-SRV --project PRJ-OSS -- systemctl reload apache2
```
```
Syntax OK
```

### Verificación final — los 4 casos

```bash
lxc exec PFR-GW-SRV --project PRJ-OSS -- curl -sI http://localhost/loki/loki/api/v1/status/buildinfo
lxc exec PFR-GW-SRV --project PRJ-OSS -- curl -sI http://localhost/ --max-time 5
lxc exec PFR-GW-SRV --project PRJ-OSS -- curl -k -sI https://localhost/ --max-time 5
lxc exec PFR-GW-SRV --project PRJ-OSS -- curl -k -sI https://localhost/ntf --max-time 5
```

```
HTTP/1.1 403 Forbidden                                    <- Loki HTTP, sin cambios

HTTP/1.1 302 Found
Location: https://10.143.11.8/                             <- Kanboard HTTP, redirige a HTTPS

HTTP/1.1 302 Found
Location: /?controller=AuthController&action=login         <- Kanboard HTTPS, funciona sin cert

HTTP/1.1 403 Forbidden                                     <- NTF HTTPS sin cert, sigue protegido
```

✅ Los 4 casos dieron el resultado esperado. Confirmado también desde el navegador: `http://10.143.11.8/` rebota solo a la versión HTTPS.
