# Certificado Let's Encrypt para `oss.personal.com.py` (ticket #1078719)

## Objetivo

Reemplazar el certificado de los 3 gateways de servicio (`PFR-GW-SRV`, `CAR-GW-SRV`, `FDO-GW-SRV`), hoy emitido por la CA interna `AutoridadOSS` y marcado por Nessus como no confiable (plugins 51192 y 57582). Ver [RIE-019](../../docs/11_Riesgos.md#rie-019--certificados-tls-no-confiables-y-configuración-tls-heredada-en-gateways-y-hosts).

## Ticket 451 — Solicitud de certificados digitales, #1078719

✅ Datos tomados de la copia impresa del ticket (`Ticket-1078719 (1).pdf`, en las descargas del usuario; no está en el repositorio).

| Campo | Valor |
|---|---|
| Certificado | Nuevo |
| Dominio | `oss.personal.com.py` |
| Servidor declarado | `PFR-GW-SRV` (en el uso se listan los 3 gateways: `10.143.11.8`, `192.168.91.117`, `10.11.11.12`) |
| Dónde se instala | Apache 2.4 (`mod_ssl`) sobre Ubuntu 26.04, en los contenedores gateway de los sitios Franco, Carpinelli y Fernando. El mismo certificado en los tres |
| Entidad certificadora pedida | Let's Encrypt |
| Tipo | Standard |
| Creado | 2026-10-16 13:27 |
| Estado | **Resuelto** |

**Historial:**

| Fecha | Quién | Qué |
|---|---|---|
| 2026-10-16 13:28 | Sistema | Circuito de aprobación: 1) Julio César Acosta, 2) Seguridad de la Información |
| 2026-10-19 08:44 | Julio César Acosta | Aprobó ("OK, proceder con la solicitud") |
| 2026-10-19 08:46 | Sistema | Asignado a Seguridad de la Información |
| 2026-10-20 09:54 | Natalia Cardozo | Pidió los nombres/IP de los activos y los servicios que usan el certificado |
| 2026-10-20 10:26 | Elías Alfonzo | Respondió: los 3 gateways con sus IP; servicios Kanboard (`/kanboard`) y VulnApp NG (`/vulnapp`) en 443/TCP; el 80/TCP solo redirige; DNS round-robin pedido en #1079305; pidió `oss.personal.com.py` en el SAN |
| 2026-10-22 14:41 | Sistema | Reasignado a Natalia Cardozo (`u995315`) |
| 2026-10-22 15:19 | Sistema | "Fue renovado el certificado". Registro: `https://ciberseg.personal.com.py/certificados/oss.personal.com.py`. Vencimiento registrado: **2027-01-20** |
| 2026-10-22 15:22 | Natalia Cardozo | "El certificado solicitado fue generado y registrado correctamente." **Cierre** |

## Archivos recibidos

Ubicación en la PC del usuario: `C:\Users\alfonzel\Documents\certificado digital\ocutubre 2026\LXD\`.

> **Advertencia:** `privkey.pem` es la clave privada, sin cifrar (`BEGIN PRIVATE KEY`). **Nunca** se copia a este repositorio, a un ticket ni a un chat. Si se pierde o se expone, hay que revocar y pedir otro certificado.

| Archivo | Contenido |
|---|---|
| `cert.pem` | Certificado del servidor |
| `chain.pem` | Intermedios: `Let's Encrypt YR1` y `ISRG Root YR` (firmado cruzado por `ISRG Root X1`) |
| `privkey.pem` | Clave privada RSA 2048 |

**Verificación local (2026-10-26, `openssl` 3.5.5, solo partes públicas):**

| Comprobación | Resultado |
|---|---|
| Sujeto | `CN=oss.personal.com.py` |
| SAN | `DNS:oss.personal.com.py` ✅ (lo pedido) |
| Emisor | `C=US, O=Let's Encrypt, CN=YR1` |
| Vigencia | 2026-10-22 17:20:36 UTC → **2027-01-20 17:20:35 UTC** (90 días, el estándar de Let's Encrypt) |
| Serie | `05AF8BA53240C0D5E7B6E60AC6FCF4A4FCC9` |
| SHA-256 | `12:0F:95:FE:2B:7F:D4:43:8B:76:75:E3:75:18:81:AA:2F:A8:C6:C5:C1:67:8A:6C:08:71:3D:33:74:58:F1:14` |
| Uso | Digital Signature, Key Encipherment; TLS Web Server Authentication |
| Cadena | `openssl verify -untrusted chain.pem cert.pem` → **OK** |
| Clave ↔ certificado | Hash de la clave pública idéntico en ambos → **coinciden** |
| DNS | `oss.personal.com.py` resuelve a `10.143.11.8` (solo Franco; ver #1079305) |

## Instalación aplicada (2026-10-26, ~17:26-17:28 UTC)

✅ Aplicada por Elías Alfonzo con Daniel Medina presente para probar Tembiapó.

**Chequeos previos:** `lxc exec` respondió en los 3 gateways. Los archivos precargados estaban presentes y los 3 servían `AutoridadOSS`. Se guardó un baseline de rutas de PFR. **SMS real desde Tembiapó, ya con `ntf-ca.crt` y antes del cambio: llegó.**

**Cambio en cada `LB.conf`** (PFR conserva sus fines de línea CRLF):

```apache
	SSLCipherSuite HIGH:!aNULL:!MD5:!RC4
	SSLProtocol -all +TLSv1.2 +TLSv1.3
	SSLCertificateFile      /etc/ssl/certs/oss.personal.com.py-20261022.fullchain.pem
	SSLCertificateKeyFile   /etc/ssl/private/oss.personal.com.py-20261022.key
```

`SSLCACertificateFile /etc/ssl/certs/ca.crt` y los `SSLVerifyClient` no se tocaron: los clientes de `/ntf` se siguen validando contra `AutoridadOSS`.

| Gateway | Backup (`/root/LB.conf.bak-20261026-cert`) | `LB.conf` nuevo | `configtest` / reload | Sirve |
|---|---|---|---|---|
| `PFR-GW-SRV` | `dee8de49…` | `caac1039…` | OK / `active` | Let's Encrypt YR1, vence 2027-01-20 |
| `CAR-GW-SRV` | `2487c9c7…` | `6cfa868d…` | OK / `active` | Let's Encrypt YR1, vence 2027-01-20 |
| `FDO-GW-SRV` | `9243b81b…` | `3bcbbdae…` | OK / `active` | Let's Encrypt YR1, vence 2027-01-20 |

**Verificación posterior:**

| Prueba | Resultado |
|---|---|
| `openssl s_client -verify_hostname oss.personal.com.py` contra las 3 IP | `Verify return code: 0 (ok)`, TLS 1.3 |
| TLS 1.0 y 1.1 contra PFR | Rechazados |
| `curl` sin `-k` a `https://oss.personal.com.py/kanboard/` y `/vulnapp/` | 302, `ssl_verify=0` |
| `/ntf` desde la PC del operador (sin certificado de cliente) | Rechazado (sigue exigiendo certificado de cliente) |
| Rutas de PFR antes/después (`rutas_kb.py`) | Sin diferencias |
| Log de `FDO-GW-SRV` | Reload 17:27:37; `POST /ntf` desde `10.11.11.24` a las 17:27:52 → **200** |
| SMS real desde Tembiapó | Ver confirmación de Daniel Medina |

**Rollback** (por gateway):
```bash
lxc exec <GW> --project PRJ-OSS -n -- sh -c 'cat /root/LB.conf.bak-20261026-cert > /etc/apache2/sites-available/LB.conf && apache2ctl configtest && systemctl reload apache2' < /dev/null
```

**Observación:** `FDO-GW-SRV` registra `AH01909 ... server certificate does NOT include an ID which matches the server name` porque el vhost no declara `ServerName` y Apache usa `fdo-gw-srv.lxd`. Es solo un aviso. Se corrige con `ServerName oss.personal.com.py` en los 3 gateways en un próximo cambio.

**Después del cambio:**
- [x] Hallazgos informados como **RESUELTO** en el ticket 778 **#1083298** (2026-10-26 14:59), con la evidencia `evidencia_certificado_oss_20261026.txt` (salida de `openssl s_client` contra las 3 IP: cadena válida, TLS 1.3, TLS 1.0/1.1 rechazados).

  | IP | Host (inventario) | ID Grafana | Hallazgo | Detectado |
  |---|---|---|---|---|
  | `10.143.11.8` | `fr-oss` | 41817 / 41818 | Certificado no confiable / CA no reconocida | 02/10/2026 |
  | `192.168.91.117` | `car-oss` | 40608 / 40609 | Certificado no confiable / CA no reconocida | 05/09/2026 |
  | `10.11.11.12` | `fdo-dns-lxd` | 41771 / 41772 | Certificado no confiable / CA no reconocida | 29/09/2026 |

- [ ] Seguir #1083298 hasta el cierre y la baja en el próximo escaneo. 🟡 Si el escaneo es por IP, puede aparecer "nombre de host incorrecto" (Nessus 45411): el servicio se publica como `oss.personal.com.py`.
- [ ] Cerrar la aceptación de riesgo del 16/10, haciendo referencia a #1083298.
- [ ] Quitar `AutoridadOSS` de `ntf-ca.crt` en Tembiapó (opcional; hoy no molesta).
- [x] Agregar `ServerName oss.personal.com.py` en los 3 gateways (hecho el 26/10 junto con las redirecciones, ver abajo).

## Redirección al nombre y de HTTP a HTTPS (aplicada 2026-10-26, ~17:36-17:37 UTC)

✅ Con OK del usuario.

**Problema:** el certificado es válido solo para `oss.personal.com.py`. Hoy:
- El puerto 80 de PFR redirigía a `https://10.143.11.8/`, la IP, así que cualquier acceso por `http://` terminaba en la advertencia de certificado.
- CAR publicaba Kanboard por HTTP sin cifrar, hacia `PFR-KANBOARD-DR`, que está detenido.
- FDO no redirigía el puerto 80.
- Por `https://<IP>/` el navegador avisa que el nombre no coincide. Esa advertencia aparece **antes** de que el servidor pueda responder y no se puede evitar; solo se puede llevar al usuario al nombre después.

**Clientes de máquina relevados antes del cambio (para excluirlos):**

| Cliente | Ruta | Puerto | Método |
|---|---|---|---|
| Grafana `10.11.11.23` (`Grafana/13.1.0`) | `/loki/...` | 80 | `GET` |
| `10.11.11.23` | `/supervisionge/...` | 443 (FDO) | `GET` |
| Tembiapó `10.11.11.24` | `/ntf` | 443 (FDO) | `POST` |
| Clientes de la API de Kanboard | `/jsonrpc.php`, `/kanboard/jsonrpc.php` | 443 (PFR) | `POST` |

**Cambio en los 3 `LB.conf`** (backup `/root/LB.conf.bak-20261026-redir`; `a2enmod rewrite` en CAR y FDO):

Puerto 80: se quitaron los `Redirect`/`ProxyPass` existentes, salvo el balanceador de Loki (PFR 1 línea, CAR 6, FDO 0), y se agregó:
```apache
    RedirectMatch 302 ^/(?!loki/)(.*)$ https://oss.personal.com.py/$1
```

Puerto 443, al inicio del `VirtualHost`:
```apache
    ServerName oss.personal.com.py
    RewriteEngine On
    RewriteCond %{HTTP_HOST} !^oss\.personal\.com\.py(:443)?$ [NC]
    RewriteCond %{REQUEST_METHOD} ^(GET|HEAD)$
    RewriteCond %{REQUEST_URI} !^/(ntf|loki|supervisionge|jsonrpc\.php|kanboard/jsonrpc\.php)
    RewriteRule ^/(.*)$ https://oss.personal.com.py/$1 [R=302,L]
```

| Decisión | Motivo |
|---|---|
| Solo `GET`/`HEAD` | Un `POST` redirigido rompe a los clientes de API |
| Excluir `/ntf`, `/loki`, `/supervisionge` y `jsonrpc` | Son clientes de máquina; algunos entran por IP |
| 302 y no 301 | No queda cacheado en los navegadores si hay rollback; se puede pasar a 301 más adelante |
| `ServerName oss.personal.com.py` | Las URL que arma Apache usan el nombre; además elimina el aviso `AH01909` |

| Gateway | `LB.conf` nuevo (SHA-256) | Resultado |
|---|---|---|
| `PFR-GW-SRV` | `ab1dd91d…` | OK / `active` |
| `CAR-GW-SRV` | `1d57afc0…` | OK / `active` |
| `FDO-GW-SRV` | `a70840b6…` | OK / `active` |

**Verificación:**

| Pedido | Resultado |
|---|---|
| `http://10.143.11.8/kanboard/`, `http://oss.personal.com.py/` | 302 → `https://oss.personal.com.py/...` |
| `http://oss.personal.com.py/kanboard/?controller=...&task_id=175` | 302 → `https://oss.personal.com.py/kanboard/?controller=...&task_id=175` (conserva la consulta) |
| `https://10.143.11.8/kanboard/`, `https://10.143.11.8/` | 302 → `https://oss.personal.com.py/...` |
| `http://192.168.91.117/`, `http://10.11.11.12/` | 302 → `https://oss.personal.com.py/` |
| `https://oss.personal.com.py/kanboard/`, `/vulnapp/`, `/?controller=...` | Igual que antes |
| `POST https://10.143.11.8/jsonrpc.php` | 200 (sin redirección) |
| `http://10.143.11.8/loki/...`, `https://oss.personal.com.py/web.config` | 403 (sin redirección) |
| FDO después de la recarga (17:37:29) | Grafana `/loki/loki` 200, `/loki/prometheus` 404 (igual que antes), `/supervisionge` 200, Tembiapó `/ntf` 200 |

**Rollback** (por gateway):
```bash
lxc exec <GW> --project PRJ-OSS -n -- sh -c 'cat /root/LB.conf.bak-20261026-redir > /etc/apache2/sites-available/LB.conf && apache2ctl configtest && systemctl reload apache2' < /dev/null
```

**Pendiente opcional:** HSTS (`Header always set Strict-Transport-Security "max-age=300"`, y subir el valor después de unos días) para que el navegador use siempre HTTPS con el nombre.

## Plan de instalación (✅ ejecutado el 2026-10-26, ver arriba)

Orden pactado en [PENDIENTES.md](../../PENDIENTES.md#2-certificado-y-dns-orden-obligatorio).

### 1. Coordinar la ventana antes de tocar nada

Con **Daniel Medina (Tembiapó)** y **Marcos Casco**. Tembiapó consume NTF por Fernando (`10.11.11.12`) y hoy confía en el certificado de `AutoridadOSS`.

✅ **Tembiapó es el único cliente de NTF.** Lo confirmó Norberto Núñez en la reunión del 24/10 (`reunion/2026-10-24_llamada-daniel-norberto-recursos-s3-certificado-ntf.vtt`, min. ~11:16-11:26): ante la pregunta de si alguien más usa NTF, respondió "este NTF dedicado es ese, sí". La IP `10.150.60.92` autorizada en `/ntf` es su equipo (`NBTECSVAASU18`), para pruebas. En la misma reunión (min. ~10:52-11:10) explicó que, con el certificado nuevo, del lado cliente "va a ser una petición HTTPS simple". 🟡 Se interpreta como validación del servidor con CA públicas; el certificado **de cliente** que exige `/ntf` se mantiene, porque quitarlo sería otra decisión de seguridad. Hay que confirmar que su cliente confía en las CA públicas (almacén del sistema). Si tiene fijado `AutoridadOSS` como única CA, se corta NTF al recargar Apache.

### 2. Qué cambia y qué no en cada gateway

| Elemento | Hoy | Después |
|---|---|---|
| `SSLCertificateFile` | `/etc/ssl/certs/server.crt` (`AutoridadOSS`) | `/etc/ssl/certs/oss.personal.com.py-20261022.fullchain.pem` (`cert.pem` + `chain.pem`) |
| `SSLCertificateKeyFile` | `/etc/ssl/certs/server.key` | `/etc/ssl/private/oss.personal.com.py-20261022.key` (`root:root`, `0600`) |
| `SSLCACertificateFile` | `/etc/ssl/certs/ca.crt` (`AutoridadOSS`) | **Sin cambios.** Valida el certificado **de cliente** de `/ntf`, no el del servidor |
| `SSLCipherSuite` | `ALL:!ADH:!EXPORT56:RC4+RSA:+HIGH:+MEDIUM:+LOW:+SSLv2:+EXP` | `HIGH:!aNULL:!MD5:!RC4` |
| `SSLProtocol` | No declarado | `-all +TLSv1.2 +TLSv1.3` |

Los archivos viejos (`server.crt`, `server.key`) se dejan donde están para el rollback.

> **Nota:** desde Apache 2.4.8, `SSLCertificateFile` acepta el certificado y los intermedios en un mismo archivo. Por eso se arma un `fullchain` y no se usa `SSLCertificateChainFile`.

### Precarga en los 3 gateways (aplicada el 2026-10-26, sin impacto)

✅ Con OK del usuario. Se copiaron los archivos sin tocar el `LB.conf`, así que Apache sigue sirviendo el certificado de `AutoridadOSS`. El día de la ventana solo cambian las líneas de configuración.

| Gateway | `fullchain` (`0644`) y clave (`0600`, `root:root`) | Clave ↔ certificado | Apache sirve | `LB.conf` (SHA-256, sin cambios) |
|---|---|---|---|---|
| `PFR-GW-SRV` | ✅ | Coinciden | `AutoridadOSS` | `dee8de49…` |
| `CAR-GW-SRV` | ✅ | Coinciden | `AutoridadOSS` | `2487c9c7…` |
| `FDO-GW-SRV` | ✅ | Coinciden | `AutoridadOSS` | `9243b81b…` |

- **Archivos:** `/etc/ssl/certs/oss.personal.com.py-20261022.fullchain.pem` (`cert.pem` + `chain.pem`, 3 certificados) y `/etc/ssl/private/oss.personal.com.py-20261022.key`.
- **Traslado de la clave:** PC → `/tmp/certlx` en `pfr-oss` (`umask 077`) → `lxc file push` a cada gateway → `shred -u` de los temporales. No quedan copias en `pfr-oss`.
- **Incidente transitorio:** en el primer intento, `lxc exec` hacia `CAR-GW-SRV` falló con `Error: Missing event connection with target cluster member`, con los 3 nodos `ONLINE` y el contenedor `RUNNING`. En el reintento, minutos después, funcionó. 🟡 Fue un corte momentáneo del canal de eventos entre `pfr.1` y `car.1`. No afecta el tráfico del gateway, pero conviene verificar `lxc exec` hacia los 3 antes de la ventana.

### 3. Pasos por gateway (los 3 en la misma ventana)

Procedimiento base: [Modificar el LB.conf de un gateway de forma controlada](../../docs/06_Operacion.md#modificar-el-lbconf-de-un-gateway-de-forma-controlada).

1. Baseline de rutas (`rutas_kb.py` / `rutas_check.py`) y huella del certificado actual.
2. `lxc file push` del `fullchain` y de la clave, con `--uid 0 --gid 0 --mode 0644` / `0600`.
3. Backup del `LB.conf` (`/root/LB.conf.bak-<fecha>`).
4. Cambiar las 4 líneas de la tabla (respetando CRLF en PFR).
5. `apache2ctl configtest` → `systemctl reload apache2`.
6. Verificar:
   ```bash
   openssl s_client -connect 10.143.11.8:443 -servername oss.personal.com.py </dev/null 2>/dev/null | openssl x509 -noout -issuer -enddate
   curl -sI https://oss.personal.com.py/kanboard/     # sin -k: debe validar el certificado
   ```
7. Comparar las rutas con el baseline. `/ntf` tiene que seguir exigiendo certificado de cliente.

**Rollback:** restaurar el backup del `LB.conf` y recargar. Los archivos viejos no se tocan.

### 4. Después del cambio

- Acceder siempre por nombre: `https://oss.personal.com.py/...`. Por IP (`https://10.143.11.8/`) el navegador va a avisar que el nombre no coincide.
- Cerrar la aceptación de riesgo de Gestión de Vulnerabilidades (778).
- Pedir un nuevo escaneo a Seguridad para que den de baja 51192 y 57582.

## Lado del cliente: Tembiapó (`10.11.11.24`), relevado el 2026-10-26

✅ Relevamiento de solo lectura con `alfonzel_opr` (el usuario también administra Tembiapó). Huella SSH del host aceptada en esa conexión: `ssh-ed25519 SHA256:4+rvJtc9Iq5lu4+F01XR7os62mJ2o3XCFWA+DUQnBs8`.

| Elemento | Valor |
|---|---|
| Host | `telegraf.1`, CentOS Linux 7, Apache (`httpd`), PHP 5.4.16, curl 7.29.0 con **NSS 3.44**, OpenSSL 1.0.2k |
| Código que llama a NTF | `/var/www/html/tembiapo/page/{ingresos,tcp,ticket_ate}/libs/enviar_sms.php` (función `enviarSMS`), `POST https://oss.personal.com.py/ntf` |
| Resolución del nombre | `/etc/hosts`: `10.11.11.12 oss.personal.com.py` (fija Fernando; el comentario del código explica que `CURLOPT_RESOLVE` no existe en esta versión) |
| Certificado de cliente | `CURLOPT_SSLCERT /etc/pki/tls/certs/client.crt` (`CN=Tembiapo`, emitido por `AutoridadOSS`, vence 2027-09-03) + `CURLOPT_SSLKEY /etc/pki/tls/private/tembiapo-client.key` |
| Validación del servidor | `CURLOPT_SSL_VERIFYPEER true`, `CURLOPT_SSL_VERIFYHOST 2` y **`CURLOPT_CAINFO /etc/pki/tls/certs/ca.crt`**, que contiene **solo** `CN=AutoridadOSS` |
| Almacén del sistema | `/etc/pki/tls/certs/ca-bundle.crt` (`ca-certificates-2020.2.41`, 188 CA), incluye `ISRG Root X1` |

**Prueba del certificado nuevo desde ese host** (`openssl verify`, enviando solo `cert.pem` y `chain.pem`, sin escribir archivos):

| Contra | Resultado |
|---|---|
| `ca-bundle.crt` (almacén del sistema) | **OK** |
| `ca.crt` (lo que usa hoy Tembiapó) | **Falla**: `unable to get local issuer certificate` |

**Conclusión:** ✅ con el código actual, **el cambio de certificado corta los SMS de Tembiapó**: la CA está fijada a `AutoridadOSS`. El sistema sí confía en Let's Encrypt; el problema es solo el `CURLOPT_CAINFO`.

**Lo que no cambia:** el certificado de cliente (`CN=Tembiapo`) sigue siendo válido, porque los gateways siguen validando clientes contra `AutoridadOSS` (`SSLCACertificateFile`). El `/etc/hosts` también sigue igual.

### Cambio propuesto en Tembiapó (🔴 no aplicado, antes del cambio en los gateways)

Un archivo de CA de transición que confía en **las dos** CA, así funciona con el certificado viejo y con el nuevo, y el orden de los cambios deja de importar:

```bash
# 1. Archivo nuevo: AutoridadOSS + ISRG Root X1 (del almacén del sistema)
cat /etc/pki/tls/certs/ca.crt <ISRG Root X1 extraído de ca-bundle.crt> > /etc/pki/tls/certs/ntf-ca.crt
# 2. En los 3 enviar_sms.php (con backup):
#    CURLOPT_CAINFO '/etc/pki/tls/certs/ca.crt'  →  '/etc/pki/tls/certs/ntf-ca.crt'
# 3. Probar contra el gateway actual con el mismo cliente (curl/NSS):
curl -s -o /dev/null -w '%{http_code}\n' --cacert /etc/pki/tls/certs/ntf-ca.crt \
     --cert /etc/pki/tls/certs/client.crt --key /etc/pki/tls/private/tembiapo-client.key \
     https://oss.personal.com.py/ntf
```

#### Avance 2026-10-26: `ntf-ca.crt` creado (aplicado por Elías Alfonzo, como root)

| Paso | Resultado |
|---|---|
| Estado previo | `ntf-ca.crt` no existía. `ca.crt`: `CN=AutoridadOSS`, dueño `apache:apache`, fines de línea CRLF y **sin salto de línea final** |
| Extracción de ISRG Root X1 | `awk` desde `# ISRG Root X1` en `ca-bundle.crt` → `CN=ISRG Root X1`, vence 2035-06-04 |
| Primer armado | ❌ `bad end line`: sin el salto de línea final de `ca.crt`, quedó `-----END CERTIFICATE-----# ISRG Root X1` en una sola línea |
| Armado corregido | `{ cat ca.crt; echo; cat isrg-root-x1.pem; } > ntf-ca.crt` → 2 CA (`AutoridadOSS`, `ISRG Root X1`), `root:root 0644`, SELinux `cert_t` |
| Prueba con curl/NSS + certificado de cliente, `POST []` a `https://oss.personal.com.py/ntf` (→ `10.11.11.12`) | ✅ **HTTP 200** con el certificado actual (`AutoridadOSS`) |

> **Lección:** al concatenar PEM, no dar por hecho que cada archivo termina con salto de línea. Usar `{ cat a; echo; cat b; }`.

#### Avance 2026-10-26: código de Tembiapó actualizado (Daniel Medina)

El repo de Tembiapó en GitHub no coincide con producción (faltan `ingresos/libs` y `tcp/libs`, y hay cambios hechos directo en el servidor). Por eso el cambio se aplicó **en el servidor** y no desde un commit del repo. Fueron **6 lugares**, no los 3 del relevamiento inicial:

| Archivo (`/var/www/html/tembiapo/page/`) | Línea | Valor |
|---|---|---|
| `ticket_ate/libs/enviar_sms.php` | 38 | `CURLOPT_CAINFO` → `ntf-ca.crt` |
| `tcp/libs/enviar_sms.php` | 38 | `CURLOPT_CAINFO` → `ntf-ca.crt` |
| `ingresos/libs/enviar_sms.php` | 53 | `CURLOPT_CAINFO` → `ntf-ca.crt` |
| `viaticos/libs/enviar_sms.php` | 84 | `CURLOPT_CAINFO` → `ntf-ca.crt` |
| `class/class_fs.php` | 27 | `'cainfo'` → `ntf-ca.crt` |
| `class/class_ingreso.php` | 21 | `'cainfo'` → `ntf-ca.crt` |

Verificado (solo lectura): ya no queda ninguna referencia a `tls/certs/ca.crt` en Tembiapó; `php -l` sin errores en los 6; dueños originales conservados; sin errores de SMS/cURL en los logs de Apache.

🔴 Pendiente: un SMS real de prueba antes de la ventana. 🟡 Sincronizar el repo de Tembiapó con producción (tarea de Daniel; el commit `b232d9a` de la PC del usuario quedó sin push y no se usa).

- **Por qué no se toca `ca.crt`:** puede tenerlo en uso otra configuración del servidor. Un archivo nuevo deja el cambio acotado a NTF.
- **Por qué un archivo de transición:** con las dos CA, no hay que coordinar al minuto el cambio en los gateways con el de Tembiapó. Cuando el certificado de los 3 gateways sea el de Let's Encrypt, se puede quitar `AutoridadOSS` de `ntf-ca.crt`.
- 🟡 La validación con NSS (la librería que usa PHP/curl en este host) se confirma recién con una conexión real contra un gateway con el certificado nuevo. `openssl verify` lo dio por bueno, pero NSS arma la cadena por su cuenta.
- **Relación con la Etapa 2:** si `FDO-GW-SRV` pasa a pedir el certificado de cliente solo en `/ntf` (renegociación en TLS 1.2), este es el cliente a probar ([RIE-020](../../docs/11_Riesgos.md#rie-020--gateways-de-car-y-fdo-no-homogéneos-con-pfr-bloquean-el-dns-compartido)).

> **Nota:** el host corre CentOS 7 y PHP 5.4, ambos sin soporte. Queda fuera de este cambio, pero conviene registrarlo para Tembiapó.

## Renovación (riesgo nuevo)

El certificado dura **90 días** y no hay renovación automática hacia los gateways. Ver [RIE-022](../../docs/11_Riesgos.md#rie-022--certificado-lets-encrypt-de-90-días-sin-renovación-automática). ✅ Ciberseguridad **reabre el ticket de Jerure cada 3 meses** con el certificado renovado (confirmado por el usuario el 2026-10-26). Al llegar, se repite la precarga y el cambio de líneas de esta bitácora.

## Pendientes

- [ ] Coordinar la ventana con Daniel Medina y Marcos Casco.
- [ ] Instalar en los 3 gateways a la vez.
- [x] Renovación: Ciberseguridad reabre el ticket de Jerure cada 3 meses (confirmado por el usuario el 2026-10-26).
- [ ] Definir dónde se guarda la clave privada fuera de la PC (¿PasswordSafe?).
- [ ] El certificado solo cubre `oss.personal.com.py`. Un nombre propio de Fernando para Comap ([ADR-0009](../../docs/adr/ADR-0009-dns-fqdn-compartido-y-nombres-por-sitio.md)) necesitaría otro certificado o la próxima emisión con ese SAN.
