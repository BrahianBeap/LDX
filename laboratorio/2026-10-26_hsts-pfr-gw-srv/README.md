# HSTS en PFR-GW-SRV — ticket 1083324 (2026-10-26)

> **Estado:** ✅ Aplicado y verificado el 2026-10-26 19:27 UTC con `max-age=300`. 🔴 Pendiente subir a `31536000` tras unos días sin incidentes.

## Contexto

✅ El escaneo de vulnerabilidades (Sistema Jerure, ticket 1083324, scan 8154, publicado 26/10/2026 16:04) informó sobre `10.143.11.8:443`:

| Criticidad | ID | Plugin | Estado |
|---|---|---|---|
| Baja | 43743 | HSTS Missing From HTTPS Server (RFC 6797) | INFORMADO |

`10.143.11.8` es la IP de servicio de **`PFR-GW-SRV`**, el gateway de Franco (proyecto `PRJ-OSS`, nodo `pfr.1`). Ver [02_Arquitectura.md](../../docs/02_Arquitectura.md).

**Qué es HSTS:** el encabezado `Strict-Transport-Security` le indica al navegador que, durante `max-age` segundos, solo debe conectarse a ese sitio por HTTPS. Esto evita que un atacante en la red fuerce una conexión HTTP sin cifrar (*SSL stripping*) en la primera petición.

**Por qué faltaba:** el `LB.conf` redirige HTTP → HTTPS, pero no enviaba el encabezado. La redirección sola no protege la primera petición HTTP.

## Cambio

Dos líneas agregadas justo después de `<VirtualHost *:443>` en `/etc/apache2/sites-available/LB.conf`:

```apache
    # HSTS (ticket 1083324, Nessus 43743, 26/10/2026). max-age corto al inicio; subir a 31536000 tras unos dias
    Header always set Strict-Transport-Security "max-age=300"
```

| Decisión | Motivo |
|---|---|
| `max-age=300` (5 minutos) al inicio | ✅ Lo pactado en [PENDIENTES.md](../../PENDIENTES.md#2-certificado-y-dns-orden-obligatorio): si algo falla, los navegadores olvidan la regla enseguida. Decisión confirmada por Elías Alfonzo el 26/10 |
| Subir después a `31536000` (1 año) | Valor recomendado a largo plazo. ✅ El escáner de Jerure aceptó `max-age=300`: el reescaneo del 28/10 no informó nada. Igual se sube, porque es el compromiso registrado en el ticket #1083416 |
| Sin `includeSubDomains` | 🟡 No conocemos qué otros subdominios de `personal.com.py` existen ni si todos tienen HTTPS. Con esa opción, los navegadores dejarían de abrirlos por HTTP |
| Sin `preload` | Solo sirve para dominios públicos inscritos en la lista *preload* de los navegadores |
| `always` | El encabezado también sale en redirecciones, errores y respuestas que vienen del backend por el proxy (Kanboard, VulnApp NG, ADM-TECH) |
| Solo en el `VirtualHost` 443 | RFC 6797: los navegadores ignoran HSTS recibido por HTTP. El puerto 80 solo redirige |

> **Nota:** los navegadores ignoran HSTS cuando se accede por IP. La protección real aplica a quien entra por `oss.personal.com.py`. Al escáner, que entra por IP, le alcanza con ver el encabezado.

> **Advertencia:** HSTS es "pegajoso": un navegador que lo recibe recuerda la regla durante `max-age`, aunque luego se quite el encabezado. Por eso se empieza con un valor corto.

Se siguió el procedimiento general de [06_Operacion.md — Modificar el LB.conf de un gateway de forma controlada](../../docs/06_Operacion.md#modificar-el-lbconf-de-un-gateway-de-forma-controlada).

## Ejecución

Desde `pfr-oss` (`10.143.11.228`, usuario `alfonzel_opr`), con `lxc exec PFR-GW-SRV --project PRJ-OSS`.

### 0. Verificación previa (solo lectura)

| Comprobación | Resultado |
|---|---|
| `apache2ctl -M \| grep headers` | `headers_module (shared)` |
| `grep -n '<VirtualHost' LB.conf` | `1: *:80`, `50: *:443` (uno solo en 443) |
| `grep -rni strict-transport /etc/apache2/` | Sin coincidencias |
| Fin de línea | CRLF en las 141 líneas (`grep -c $'\r$'`; el contenedor no tiene `file`) |
| `apache2ctl -S` | `*:443 oss.personal.com.py (LB.conf:50)` |

> **Advertencia — trabajo concurrente:** el archivo se había modificado y recargado a las 19:11 UTC del mismo día, sin backup propio, y ya existían `/root/LB.conf.bak-20261026` y `/root/LB.conf.new` de otros trabajos. Se esperó a que esa edición terminara, se usaron nombres propios (`-hsts`) y el script abortaba si el hash del archivo no era el verificado (`edf024f7…863ed2`) o si el backup ya existía.

### 1–3. Backup, cambio e instalación

```bash
F=/etc/apache2/sites-available/LB.conf
B=/root/LB.conf.bak-20261026-hsts
N=/root/LB.conf.new-hsts
EXP=edf024f725551ed0da2fcb85256281798b3a6b0affd5c4cf0ee898fbcc863ed2
[ "$(sha256sum < "$F" | cut -d' ' -f1)" = "$EXP" ] || { echo "ABORTA: el archivo cambio"; exit 1; }
[ -e "$B" ] && { echo "ABORTA: $B ya existe"; exit 1; }
cp -p "$F" "$B" && chmod 444 "$B"
awk '{print} /<VirtualHost[^>]*:443>/{print "    # HSTS (...)\r"; print "    Header always set Strict-Transport-Security \"max-age=300\"\r"}' "$F" > "$N"
[ "$(diff "$B" "$N" | grep -c '^>')" = 2 ] || { echo "ABORTA: diff inesperado"; exit 1; }
cat "$N" > "$F"       # conserva dueño y permisos (root:root 444)
apache2ctl configtest && systemctl reload apache2 || { cat "$B" > "$F"; echo "ROLLBACK APLICADO"; }
```

| Paso | Resultado |
|---|---|
| Backup `LB.conf.bak-20261026-hsts` | SHA-256 `edf024f7…863ed2`, igual al original |
| `diff` | `50a51,52`: exactamente 2 líneas agregadas, con `^M` (CRLF) |
| `configtest` / `reload` | `Syntax OK`, recarga sin corte, `apache2` activo |
| Archivo instalado | SHA-256 `97320ad6…08f6cc`, igual al revisado; `root:root 444` |

### 4. Verificación

Rutas probadas por nombre (`curl --resolve oss.personal.com.py:443:10.143.11.8`) antes y después: **sin cambios**.

| Ruta | Antes y después |
|---|---|
| `https://oss.personal.com.py/` (portal) | 200 |
| `/kanboard/` | 302 → login de Kanboard |
| `/web.config`, `/kanboard/web.config` | 403 |
| `/vulnapp/` | 302 → `/vulnapp/dashboard` |
| `/adm/` | 200 |
| `/ntf` | 403 |
| `/supervisionge` | 404 (en PFR no existe; se publica solo hacia Fernando) |
| `POST /jsonrpc.php` | 200 |
| `https://10.143.11.8/`, `http://oss.personal.com.py/` | 302 → `https://oss.personal.com.py/` |

Encabezado, desde `pfr-oss` y desde una estación de la red corporativa:

```
$ curl -skI https://10.143.11.8/
HTTP/1.1 302 Found
Strict-Transport-Security: max-age=300
Location: https://oss.personal.com.py/

$ curl -sI http://10.143.11.8/
HTTP/1.1 302 Found          # sin HSTS por HTTP, como corresponde
```

### Rollback

```bash
lxc exec PFR-GW-SRV --project PRJ-OSS -- sh -c 'cat /root/LB.conf.bak-20261026-hsts > /etc/apache2/sites-available/LB.conf && apache2ctl configtest && systemctl reload apache2'
```

> **Nota:** restaurar este backup también revierte cualquier cambio posterior al 26/10 19:27 en el mismo archivo. Si hubo otros, quitar solo las dos líneas HSTS.

### Errores frecuentes

| Error | Causa | Solución |
|---|---|---|
| `Invalid command 'Header'` en `configtest` | `mod_headers` no está habilitado | `a2enmod headers` y repetir |
| `diff` no muestra 2 líneas agregadas | El `VirtualHost` usa otra sintaxis (ej. `_default_:443`) | Revisar `grep -n '<VirtualHost'` y ajustar el patrón del `awk` |
| El encabezado no aparece en `curl` | Responde otro `VirtualHost` | `apache2ctl -S` para ver cuál atiende el 443 |

## Pendientes

- [ ] **Subir `max-age` a `31536000`** después de unos días sin incidentes. Repetir el procedimiento con backup propio, cambiando solo el valor.
- [x] Hallazgo declarado RESUELTO en el ticket 778 #1083416 (26/10 16:49) y respondido en #1083324 (26/10 16:51). #1083324 quedó resuelto el 28/10. ✅ #1083416 resuelto el 28/10: el reescaneo de ese día (09:19) no detectó vulnerabilidades relevantes, por lo que `max-age=300` alcanzó para dar de baja el hallazgo.
- [ ] 🟡 `CAR-GW-SRV` y `FDO-GW-SRV` no tienen HSTS. Incluir la misma línea al reescribir su `LB.conf` (Etapa 2, [RIE-020](../../docs/11_Riesgos.md)), para que los 3 gateways queden iguales.
- [ ] Cuando esté en su valor final, documentar la línea HSTS como parte estándar del `LB.conf` en [05_Configuracion.md](../../docs/05_Configuracion.md).
- [ ] 🔴 Averiguar quién hizo el cambio de las 19:11 UTC del 26/10 en este `LB.conf`, que no tiene backup propio, y que lo registre.
