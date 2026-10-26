# Bitácora — Alta Jerure de `PFR-GW-SRV`

Relevamiento **estrictamente de solo lectura**, ejecutado desde `pfr-oss` con `lxc exec ... --project PRJ-OSS`. No se modificó ninguna configuración.

## 1. Datos cargados en el ticket #1076072 (tema 447)

| Campo | Valor cargado | Origen |
|---|---|---|
| Nombre del equipo / Hostname | `PFR-GW-SRV` | ✅ `hostnamectl` |
| IP | `10.143.11.8` | ✅ `ip -br addr` (eth1, `/26`) |
| VLAN | 411 | 🟡 De [02_Arquitectura.md](../../docs/02_Arquitectura.md). No se ve desde el contenedor (ipvlan no expone el tag) |
| ¿Crear registro DNS? | NO (por ahora) | El FQDN compartido se pedirá aparte, ver [02_Arquitectura.md](../../docs/02_Arquitectura.md#nombre-de-dominio-compartido-entre-sitios-fqdn--dns-round-robin) |
| Solicitante / Responsable (BPO) / Área | `alfonzel` / `cascoma` / AK402 | Datos administrativos, aportados por el usuario |
| Entorno / Criticidad | Producción / Crítica | Datos administrativos, aportados por el usuario |
| Ubicación | `pfr.1` | ✅ `lxc info` |
| Sistema operativo | Ubuntu 26.04 LTS | ✅ `/etc/os-release` |
| Memoria / CPU / Disco | 1 GiB / 1 vCPU / 5 GiB | ✅ Perfil `PFR-GW-SRV` (`limits.memory`, `limits.cpu`, `root.size`) |
| Backup / Monitoreo | NO / NO | ✅ Sin snapshots ni agentes |

Circuito de aprobación del ticket: Julio César Acosta → Marcos Casco (BPO) → Verificación Acceso SDI a Activo → Salvador Deu → Seguridad de la Información.

## 2. Servicios y puertos publicados (zona `external`, eth1)

| Protocolo/puerto | Servicio | Alcance |
|---|---|---|
| tcp/80 | Apache: redirige a HTTPS (excepto `/loki/loki/api/v1`) | Externo |
| tcp/443 | Apache: Kanboard (`/`), VulnApp NG (`/vulnapp`), NTF (`/ntf`, mTLS + IP) | Externo |
| udp/162 | Reenvío de traps SNMP → Loki `192.168.0.12:162` | Externo |
| tcp+udp/514 | rsyslog | Externo |
| tcp/8080 | Reenvío heredado → `192.168.0.106:80` (Kanboard, esquema anterior) | Externo, sin uso confirmado |

Zona `internal` (eth0, `OVN_1`): solo tcp/80.

## 3. Verificación de IP propia (447 vs 857)

```bash
lxc exec PFR-GW-SRV --project PRJ-OSS -- ip -d link show eth1   # ipvlan mode l2
lxc profile show PFR-GW-SRV --project PRJ-OSS                  # eth1: nictype=ipvlan, parent=nic_srv1; cloud-init: 10.143.11.8/26 estático
```

No hay NAT, VIP ni otro contenedor con esa dirección: corresponde el **447**.

## 4. DNS

```bash
nslookup oss.personal.com.py 10.129.4.176   # NXDOMAIN
nslookup 10.143.11.8 10.129.4.176           # NXDOMAIN (también contra .177)
```

`nslookup` no está instalado dentro del contenedor: se consultó desde el host, apuntando explícitamente a los DNS configurados en el cloud-init del contenedor.

## 5. Respuesta a la verificación de SDI (16/10)

Abel Díaz probó `ssh u998524_opr@10.143.11.8` → *connection refused*. Respuesta acordada: el contenedor no tiene SSH en ninguna interfaz. La verificación se hace desde el servidor de gestión `10.143.11.228` con `lxc exec PFR-GW-SRV --project PRJ-OSS -- <comando>`, lo que requiere permisos de LXD en ese host. Ver [TRB-018](../../docs/07_Troubleshooting.md#trb-018--la-verificación-de-acceso-de-sdi-por-ssh-a-la-ip-de-servicio-de-un-gateway-falla-con-connection-refused).
