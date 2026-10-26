# Bitácora — Tratamiento Nessus y Etapa 1 de gateways (2026-10-16)

Todo se ejecutó desde `pfr-oss` (`10.143.11.228`, usuario `alfonzel_opr`). Los cambios dentro de contenedores se hicieron con `lxc exec ... --project PRJ-OSS`. Cada cambio siguió el procedimiento de [06_Operacion.md — Modificar el LB.conf de un gateway de forma controlada](../../docs/06_Operacion.md#modificar-el-lbconf-de-un-gateway-de-forma-controlada): backup, cambio, validación, recarga sin corte, comparación de rutas y rollback si algo falla.

## 0. Verificación previa (solo lectura)

```bash
lxc config get core.https_address      # 10.143.11.228:8444  (API / Web UI)
lxc config get cluster.https_address   # 10.143.11.228:8443  (comunicación entre nodos)
lxc config get core.metrics_address    # 10.143.11.228:8555  (métricas)
lxc config get core.metrics_authentication   # false
```

| Prueba desde la red corporativa | Resultado |
|---|---|
| `https://10.143.11.228:8555/1.0/metrics` | Timeout (filtrado por firewall desde esa estación). Nessus sí llegó, por el acceso del escáner ([RIE-016](../../docs/11_Riesgos.md#rie-016--acceso-temporal-del-escáner-de-vulnerabilidades-por-lista-de-ips-sin-fecha-de-retiro)) |
| `https://10.143.11.228:8444/1.0` | 200: parte pública de la API de LXD (comportamiento normal sin certificado de confianza) |
| `https://10.143.11.8/web.config` | **200**, 793 bytes: archivo IIS de Kanboard (`<rewrite>` hacia `index.php`), sin secretos |
| `https://10.143.11.8/.htaccess` y `/data/` | 403 (la base SQLite de Kanboard ya estaba protegida) |
| `https://192.168.91.117/web.config`, `https://10.11.11.12/web.config` | `TLSV13_ALERT_CERTIFICATE_REQUIRED`: CAR y FDO no exponen nada sin certificado |

No se pudo leer el firewall del host `pfr-oss` porque `alfonzel_opr` necesita contraseña de sudo ahí.

## 1. ICMP timestamp, en los 3 gateways

Antes de aplicar, se comprobó que en los 3 gateways la configuración activa (runtime) y la guardada (permanent) de la zona `external` fueran iguales (solo difería la etiqueta `(active)`). Por eso se aplicó en las dos por separado, sin `--runtime-to-permanent`, que habría guardado cualquier otro cambio temporal.

```bash
for t in timestamp-request timestamp-reply; do
  firewall-cmd --zone=external --add-icmp-block=$t
  firewall-cmd --permanent --zone=external --add-icmp-block=$t
done
```

Verificación: `--list-icmp-blocks` muestra los dos tipos en runtime y permanent; `nft list ruleset` contiene 2 reglas `timestamp`; los puertos publicados no cambiaron.

**Rollback:** `firewall-cmd [--permanent] --zone=external --remove-icmp-block={timestamp-request,timestamp-reply}`.

## 2. `web.config`, solo en PFR-GW-SRV

Backup: `/root/LB.conf.bak-20261016` (SHA-256 `de69bc5f…a52497c`, igual al original). Bloque agregado justo antes de `ProxyPass /kanboard !`, respetando los fines de línea CRLF del archivo:

```apache
    # Bloquear web.config de Kanboard (Nessus 121479, 16/10/2026)
    ProxyPass /web.config !
    <Location "/web.config">
      Require all denied
    </Location>
```

El orden importa: las exclusiones con `ProxyPass ... !` tienen que ir **antes** de `ProxyPass / http://192.168.0.106:80/`.

Instalación: `apache2ctl configtest` (Syntax OK) → `systemctl reload apache2`. El archivo instalado tiene SHA-256 `f8dd2cb7…bb40eb2`, idéntico al revisado.

| Ruta | Antes | Después |
|---|---|---|
| `/web.config` | 200 | **403** |
| `/`, login de Kanboard, `/kanboard` | 302 / 200 / 302 | Sin cambios |
| `/vulnapp/` | 302 | Sin cambios |
| `/ntf` | 403 | Sin cambios |
| `http://` → `https://` | 302 | Sin cambios |

**Rollback:**
```bash
lxc exec PFR-GW-SRV --project PRJ-OSS -- sh -c 'cat /root/LB.conf.bak-20261016 > /etc/apache2/sites-available/LB.conf && apache2ctl configtest && systemctl reload apache2'
```

## 3. Etapa 1: VulnApp NG alcanzable desde CAR y FDO

Diagnóstico previo: CAR y FDO alcanzan `192.168.0.106:80` (Kanboard), porque la regla general de la ACL cubre el puerto 80, pero **no** `192.168.0.14:5000` (VulnApp NG), porque la regla de VulnApp solo permite `192.168.0.1`.

Backups:
- ACL: `~/backup-20261016/ACL-OVN-1.yaml` en `pfr-oss` (15 reglas).
- Unidad de systemd: `/root/vulnapp.service.bak-20261016` en `PFR-VULNAPP-APP`.

### 3.1 ACL (regla nueva, sin tocar la de PFR, para no cortar su acceso)

```bash
lxc network acl rule add ACL-OVN-1 ingress --project PRJ-OSS action=allow \
  source=192.168.0.2,192.168.0.4 destination=192.168.0.14 protocol=tcp destination_port=5000 \
  "description=Balanceadores CAR y FDO hacia Gunicorn de vulnapp-app" state=enabled
```

Resultado: 16 reglas. Los 3 gateways abren conexión TCP a `192.168.0.14:5000`.

**Rollback:** `lxc network acl rule remove ACL-OVN-1 ingress --project PRJ-OSS source=192.168.0.2,192.168.0.4 destination=192.168.0.14 destination_port=5000`.

### 3.2 Gunicorn

```bash
sed -i 's|--forwarded-allow-ips 192.168.0.1 |--forwarded-allow-ips 192.168.0.1,192.168.0.2,192.168.0.4 |' /etc/systemd/system/vulnapp.service
systemctl daemon-reload && systemctl restart vulnapp.service
```

Resultado: servicio activo con el parámetro nuevo y escuchando en `192.168.0.14:5000`; rutas de PFR sin cambios; `/vulnapp/` sigue redirigiendo a una ruta relativa (`/vulnapp/dashboard`).

> **Nota:** `vulnapp.service` la genera el instalador `02_instalar_app.sh` del paquete de VulnApp NG. Una reinstalación vuelve a dejar solo `192.168.0.1`. Hay que avisarle a quien mantiene el paquete.

**Rollback:** copiar `/root/vulnapp.service.bak-20261016` sobre la unidad, `systemctl daemon-reload` y reiniciar el servicio.

### 3.3 `mod_headers` en CAR y FDO

```bash
a2enmod headers && apache2ctl configtest && systemctl reload apache2
```

Resultado: módulo cargado; Apache activo en 80/443; ambos gateways siguen respondiendo `CERTIFICATE_REQUIRED` a clientes sin certificado.

La primera prueba sobre CAR, hecha durante la recarga, devolvió "conexión cerrada sin respuesta". Tres pruebas posteriores dieron el comportamiento normal y el log de errores no registró nada nuevo: fue momentáneo, mientras Apache renovaba sus procesos.

**Rollback:** `a2dismod headers && systemctl reload apache2`.
