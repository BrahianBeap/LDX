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

## Plan de instalación (🔴 no aplicado)

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

Pendiente: desplegar los 3 `enviar_sms.php` con `CURLOPT_CAINFO` → `ntf-ca.crt` (commit en el repo de Tembiapó) y enviar un SMS real.

- **Por qué no se toca `ca.crt`:** puede tenerlo en uso otra configuración del servidor. Un archivo nuevo deja el cambio acotado a NTF.
- **Por qué un archivo de transición:** con las dos CA, no hay que coordinar al minuto el cambio en los gateways con el de Tembiapó. Cuando el certificado de los 3 gateways sea el de Let's Encrypt, se puede quitar `AutoridadOSS` de `ntf-ca.crt`.
- 🟡 La validación con NSS (la librería que usa PHP/curl en este host) se confirma recién con una conexión real contra un gateway con el certificado nuevo. `openssl verify` lo dio por bueno, pero NSS arma la cadena por su cuenta.
- **Relación con la Etapa 2:** si `FDO-GW-SRV` pasa a pedir el certificado de cliente solo en `/ntf` (renegociación en TLS 1.2), este es el cliente a probar ([RIE-020](../../docs/11_Riesgos.md#rie-020--gateways-de-car-y-fdo-no-homogéneos-con-pfr-bloquean-el-dns-compartido)).

> **Nota:** el host corre CentOS 7 y PHP 5.4, ambos sin soporte. Queda fuera de este cambio, pero conviene registrarlo para Tembiapó.

## Renovación (riesgo nuevo)

El certificado dura **90 días** y no hay renovación automática hacia los gateways. Ver [RIE-022](../../docs/11_Riesgos.md#rie-022--certificado-lets-encrypt-de-90-días-sin-renovación-automática). 🔴 Falta confirmar con Natalia Cardozo cómo y cuándo entrega Ciberseguridad el certificado renovado.

## Pendientes

- [ ] Coordinar la ventana con Daniel Medina y Marcos Casco.
- [ ] Instalar en los 3 gateways a la vez.
- [ ] Preguntar a Natalia Cardozo por la renovación (¿la inicia Ciberseguridad?, ¿con cuánta anticipación?, ¿por qué canal llegan los archivos?).
- [ ] Definir dónde se guarda la clave privada fuera de la PC (¿PasswordSafe?).
- [ ] El certificado solo cubre `oss.personal.com.py`. Un nombre propio de Fernando para Comap ([ADR-0009](../../docs/adr/ADR-0009-dns-fqdn-compartido-y-nombres-por-sitio.md)) necesitaría otro certificado o la próxima emisión con ese SAN.
