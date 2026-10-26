# Tratamiento del escaneo Nessus y preparación de gateways para el FQDN compartido (2026-10-16)

## Objetivo

1. Tratar las detecciones del escaneo Nessus que adjuntó Seguridad de la Información al cerrar el ticket Jerure #1076134 (escaneo del 16/10/2026 09:30, sobre `10.143.11.8` y `10.143.11.228`).
2. Preparar a CAR-GW-SRV y FDO-GW-SRV para que, igual que PFR-GW-SRV, publiquen Kanboard y VulnApp NG. Es requisito antes de pedir el DNS compartido `oss.personal.com.py` (round-robin a los 3 gateways).

## Resultado

### Detecciones de Nessus (13, todas de criticidad media)

| Host | Plugin | Detección | Tratamiento | Estado |
|---|---|---|---|---|
| `10.143.11.8` | 10114 | ICMP timestamp (CVE-1999-0524) | Bloqueo de `timestamp-request`/`timestamp-reply` en firewalld (zona `external`) de los **3 gateways** | ✅ Aplicado |
| `10.143.11.8` | 121479 | `/web.config` accesible (archivo de reglas IIS que trae Kanboard; sin datos sensibles) | `ProxyPass /web.config !` + `Require all denied` en `LB.conf` de PFR. CAR y FDO no estaban expuestos (exigen certificado de cliente) | ✅ Aplicado (200 → 403) |
| `10.143.11.8` | 51192, 57582 | Certificado de `AutoridadOSS` no confiable / autofirmado | CA corporativa + DNS, o aceptación de riesgo | 🟡 Pendiente, ver [RIE-019](../../docs/11_Riesgos.md#rie-019--certificados-tls-no-confiables-y-configuración-tls-heredada-en-gateways-y-hosts) |
| `10.143.11.228` | 51192, 57582, 45411 (×3 puertos) | Certificado propio de LXD en 8443/8444/8555 | Aceptación de riesgo: modelo de confianza por certificado registrado, propio de LXD | 🟡 Pendiente de formalizar, ver [RIE-019](../../docs/11_Riesgos.md#rie-019--certificados-tls-no-confiables-y-configuración-tls-heredada-en-gateways-y-hosts) |

**Hallazgo adicional (no informado por Nessus):** el endpoint de métricas de LXD (`8555`) no exige autenticación. Ver [RIE-018](../../docs/11_Riesgos.md#rie-018--métricas-de-lxd-sin-autenticación).

### Etapa 1: preparación de CAR/FDO para publicar VulnApp NG ✅

| Cambio | Dónde | Efecto |
|---|---|---|
| Regla nueva en `ACL-OVN-1`: `192.168.0.2,192.168.0.4 → 192.168.0.14:5000` | `OVN_1` | CAR y FDO alcanzan Gunicorn (antes solo PFR) |
| `--forwarded-allow-ips 192.168.0.1,192.168.0.2,192.168.0.4` | `vulnapp.service` en `PFR-VULNAPP-APP` | Gunicorn confía en `X-Forwarded-*` de los 3 gateways |
| `a2enmod headers` | CAR-GW-SRV, FDO-GW-SRV | Permite `RequestHeader set X-Forwarded-Proto` (ver [TRB-015](../../docs/07_Troubleshooting.md#trb-015--requestheader-falla-con-invalid-command-porque-mod_headers-no-está-habilitado)) |

Ningún cambio alteró el comportamiento visible. El reinicio de Gunicorn cortó VulnApp NG por unos segundos.

### Etapa 2: `LB.conf` de CAR y FDO 🔴 Pendiente, coordinar con Norberto Núñez

Estado actual, verificado el 16/10/2026:

| | PFR-GW-SRV | CAR-GW-SRV | FDO-GW-SRV |
|---|---|---|---|
| Certificado de cliente en 443 | `optional`; `/` sin certificado, `/ntf` lo exige | `require` en todo el vhost | `require` en todo el vhost |
| Kanboard | `/` → `192.168.0.106` | `/kanboard` → `CAR-kanboard-1` (inexistente; `CAR-KANBOARD` detenido) | `/kanboard` → `CAR-kanboard-1` (inexistente) |
| VulnApp NG | `/vulnapp` → `192.168.0.14:5000` | — | — |
| HTTP (80) | Redirige a `https://10.143.11.8/` (IP fija) | Proxy **HTTP sin cifrar** de `/` a `PFR-KANBOARD-DR` (detenido) | Solo Loki |
| Rutas propias | — | — | `/supervisionge` (Comap → Grafana) |

Cambios previstos: pasar CAR y FDO al modelo de PFR ([mTLS opcional por defecto](../../docs/05_Configuracion.md#mtls-opcional-por-defecto-obligatorio-solo-en-rutas-específicas)), con `require` explícito en `/ntf` y `/supervisionge`; Kanboard en `/` y VulnApp NG en `/vulnapp` hacia los contenedores de PFR; bloqueo de `web.config`; HTTP → HTTPS; y redirecciones a `https://oss.personal.com.py/` en lugar de IP fija.

> **Advertencia:** pasar de `require` (en el handshake) a `require` por ruta obliga a los clientes de NTF y `/supervisionge` a soportar autenticación posterior al handshake en TLS 1.3. Hay que probarlo con el cliente de Norberto Núñez antes de aplicarlo, porque NTF es productivo.

Comandos, salidas y rollback de cada paso en [`bitacora.md`](bitacora.md).
