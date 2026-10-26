# Alta en inventario (Jerure) de `PFR-GW-SRV` (2026-10-12 → 2026-10-16)

## Objetivo

Registrar formalmente el gateway de servicios del sitio Franco (`PFR-GW-SRV`, IP `10.143.11.8`) en el inventario de Ciberseguridad (Jerure). Es requisito para que SDI pueda aprobar reglas de firewall que involucren esa IP. En particular, destraba la conectividad de VulnApp NG con la API de SDI ([RIE-015](../../docs/11_Riesgos.md#rie-015--conectividad-de-vulnapp-ng-hacia-la-api-de-sdi-bloqueada)).

En el inventario ya existía el registro **632 | DNSv6-home-21** asociado a la misma IP. Por recomendación de Abel Díaz (SDI), se pidió un registro nuevo sin modificar el anterior.

## Resultado

| Ticket | Tema Jerure | Estado | Detalle |
|---|---|---|---|
| #1076072 | Ciberseguridad – Alta de servidores virtuales-447 | 🟡 En circuito: aprobado por Julio César Acosta y Marcos Casco (BPO); en "Verificación Acceso SDI a Activo" | Abel Díaz informó "Sin acceso": intentó SSH a `10.143.11.8:22` y recibió *connection refused*. Ver [TRB-018](../../docs/07_Troubleshooting.md#trb-018--la-verificación-de-acceso-de-sdi-por-ssh-a-la-ip-de-servicio-de-un-gateway-falla-con-connection-refused) |
| #1076134 | Inventario / Agregar IP a activo de red existente-939 | ✅ Resuelto 16/10/2026 (Abel Díaz) | Se agregó `10.143.11.8` al activo `fr-oss` (`10.143.11.228`). Seguridad adjuntó un escaneo Nessus de ambas IP: ver [`2026-10-16_hardening-gateways-nessus/`](../2026-10-16_hardening-gateways-nessus/) |

✅ **Conclusión técnica del relevamiento:** `10.143.11.8` es una **IP propia** del contenedor (asignada estáticamente a `eth1`, driver `ipvlan` en modo L2 sobre la NIC de servicio del host), no una IP flotante ni compartida. Por eso correspondía el tema **447** y no el 857.

## Hallazgos del relevamiento (solo lectura, 2026-10-12)

| Hallazgo | Estado |
|---|---|
| Sin SSH en el contenedor (`ssh` *inactive/masked*, nada escucha en el puerto 22). Se administra con `lxc exec` desde `pfr-oss` | ✅ Por diseño, ver [03_Componentes.md](../../docs/03_Componentes.md#contenedor-gateway-de-servicios) |
| Sin snapshots ni `snapshots.schedule`: el gateway no tiene backup | 🔴 Ver [RIE-021](../../docs/11_Riesgos.md#rie-021--pfr-gw-srv-sin-snapshots-ni-backup) |
| `oss.personal.com.py` y el reverso de `10.143.11.8` dan NXDOMAIN, también contra los DNS corporativos del propio contenedor (`10.129.4.176`/`.177`) | 🔴 DNS pendiente, ver [02_Arquitectura.md](../../docs/02_Arquitectura.md#nombre-de-dominio-compartido-entre-sitios-fqdn--dns-round-robin) |
| Certificado TLS `CN=oss.personal.com.py`, emitido por `AutoridadOSS`, válido 09/2026-09/2027, **sin SAN** | 🟡 Ver [RIE-019](../../docs/11_Riesgos.md#rie-019--certificados-tls-no-confiables-y-configuración-tls-heredada-en-gateways-y-hosts) |
| Zonas de firewalld reales: `external` (eth1) y `internal` (eth0). Reenvío heredado `8080/tcp → 192.168.0.106:80` (esquema viejo de Kanboard) todavía configurado | 🟡 Candidato a retirar, sin uso confirmado |
| Sin agente de monitoreo dentro del contenedor | 🟡 Solo métricas nativas de LXD |

Datos completos del formulario (27 campos), servicios y puertos en [`bitacora.md`](bitacora.md).
