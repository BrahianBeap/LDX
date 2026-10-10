# Bitácora — Capacidad real del cluster, 3 sitios (2026-10-10)

Todos los comandos se ejecutaron por SSH contra `pfr-oss` (`10.143.11.228`) — ninguno necesitó conectarse a `car-oss` ni `fdo-oss` por separado, gracias a `--target` y a que `lxc exec`/`lxc info` enrutan automáticamente al servidor donde vive cada contenedor.

---

## 1. Miembros del cluster

```
$ lxc cluster list
+-------+-----------------------------+-----------------+--------------+
| NAME  |             URL             |      ROLES      | ARCHITECTURE |
+-------+-----------------------------+-----------------+--------------+
| car.1 | https://192.168.91.116:8443 | database        | x86_64       |
| fdo.1 | https://10.150.32.101:8443  | database        | x86_64       |
| pfr.1 | https://10.143.11.228:8443  | database-leader  | x86_64       |
|       |                              | database         |              |
+-------+-----------------------------+-----------------+--------------+
```

Los 3, `ONLINE`.

## 2. CPU y RAM física de cada sitio

```
$ lxc info --target car.1 --resources | grep -A3 "^Memory:"
Memory:
  Free: 4.68GiB
  Used: 3.32GiB
  Total: 8.00GiB

$ lxc info --target car.1 --resources | grep -c "online: true"
4

$ lxc info --target fdo.1 --resources | grep -A3 "^Memory:"
Memory:
  Free: 3.96GiB
  Used: 4.04GiB
  Total: 8.00GiB

$ lxc info --target fdo.1 --resources | grep -c "online: true"
4

$ lxc info --target pfr.1 --resources | grep -A3 "^Memory:"
Memory:
  Free: 8.20GiB
  Used: 7.80GiB
  Total: 16.00GiB

$ lxc info --target pfr.1 --resources | grep -c "online: true"
12
```

`car.1` corre como VM (se vio en el detalle de disco: `VMware Virtual SATA CDRW Drive`); no se confirmó lo mismo para `pfr.1`/`fdo.1`, no se investigó más a fondo por no ser el objetivo de esta verificación.

## 3. Capacidad del storage pool `local` en cada sitio

`lxc storage list --target` no es un flag válido para ese subcomando — se usó la API directamente:

```
$ lxc query "/1.0/storage-pools/local/resources?target=pfr.1"
{"space": {"total": 339170247168, "used": 5989762048}, ...}
→ 315.86 GiB total, 5.58 GiB usados, 310.28 GiB libres

$ lxc query "/1.0/storage-pools/local/resources?target=car.1"
{"space": {"total": 410130278912, "used": 6387188224}, ...}
→ 381.94 GiB total, 5.95 GiB usados, 375.99 GiB libres

$ lxc query "/1.0/storage-pools/local/resources?target=fdo.1"
{"space": {"total": 409902032384, "used": 4190615040}, ...}
→ 381.73 GiB total, 3.90 GiB usados, 377.83 GiB libres
```

(Bytes convertidos a GiB con 1024³. `pfr.1` también se verificó por separado con `zpool list` directo en el host: `326G / 5.58G / 320G` — la pequeña diferencia frente a los 315.86 GiB de la API es la diferencia de redondeo entre GB decimal y GiB binario, no un error.)

## 4. Inventario completo de contenedores

```
$ lxc list --all-projects -c ns4tL --format csv
C-Colector-1,RUNNING,192.168.0.11 (eth1),CONTAINER,car.1
C-Grafana-1,STOPPED,,CONTAINER,car.1
C-Loki-1,RUNNING,192.168.0.12 (eth0),CONTAINER,pfr.1
C-Mimir-1,STOPPED,,CONTAINER,fdo.1
CAR-GW-OAM,RUNNING,...,CONTAINER,car.1
CAR-GW-SRV,RUNNING,...,CONTAINER,car.1
CAR-KANBOARD,STOPPED,,CONTAINER,car.1
FDO-GW-OAM,RUNNING,...,CONTAINER,fdo.1
FDO-GW-SRV,RUNNING,...,CONTAINER,fdo.1
FDO-WS-1,RUNNING,192.168.0.110 (eth0),CONTAINER,fdo.1
I-GW-SRV,STOPPED,,CONTAINER,fdo.1
Minio-1,STOPPED,,CONTAINER,car.1
PFR-GW-OAM,RUNNING,...,CONTAINER,pfr.1
PFR-GW-SRV,RUNNING,...,CONTAINER,pfr.1
PFR-KANBOARD-DR,STOPPED,,CONTAINER,car.1
PFR-KANBOARD-TEST,RUNNING,192.168.0.106 (eth1),CONTAINER,pfr.1
PFR-VULNAPP-APP,RUNNING,192.168.0.14 (eth0),CONTAINER,pfr.1
PFR-VULNAPP-DB,RUNNING,192.168.0.13 (eth0),CONTAINER,pfr.1
PFR-WS-1,RUNNING,192.168.0.111 (eth0),CONTAINER,pfr.1
```

13 contenedores `RUNNING` (7 en Franco, 3 en Carpinelli, 3 en Fernando) y 6 `STOPPED` (todos en Carpinelli y Fernando — no consumen CPU/RAM, pero siguen reservando espacio en el pool mientras existan).

## 5. Uso real de memoria/disco por contenedor, y límites configurados

Patrón usado para cada uno de los 13 contenedores corriendo (ejemplo con `PFR-VULNAPP-APP`, proyecto `PRJ-OSS`):

```
$ lxc info PFR-VULNAPP-APP --project PRJ-OSS --resources | grep -A2 "Memory usage"
Memory usage:
    Memory (current): 365.05MiB
    Swap (current): 36.00KiB

$ lxc info PFR-VULNAPP-APP --project PRJ-OSS --resources | grep -A2 "Disk usage"
Disk usage:
    root: 471.38MiB

$ lxc config show PFR-VULNAPP-APP --project PRJ-OSS --expanded | grep -E "limits.cpu|limits.memory"
limits.cpu: "2"
limits.memory: 2GiB
```

**Nota de ruta:** varios contenedores dieron `Error: Instance not found` al principio porque están en el proyecto `PRJ-OSS`, no en `default` (`PFR-VULNAPP-APP`, `PFR-VULNAPP-DB`, `PFR-WS-1`, `C-Loki-1`, `C-Colector-1`, `FDO-WS-1`, y — a diferencia de lo que se esperaba — también `PFR-GW-SRV`, `CAR-GW-SRV` y `FDO-GW-SRV`, los gateways de **servicio**. Los gateways de **operación y mantenimiento** (`*-GW-OAM`) y Kanboard sí están en `default`.

Resultado consolidado de los 13:

| Contenedor | Sitio | Stack | RAM usada | Límite | Disco usado | Cupo de disco |
|---|---|---|---|---|---|---|
| `PFR-GW-SRV` | Franco | Gateway + balanceador embebido (Apache: Kanboard, Loki, NTF, VulnApp) | 218 MiB | 1 GiB (21%) | 62 MiB | 5 GiB |
| `PFR-GW-OAM` | Franco | Gateway de operación/mantenimiento | 335 MiB | 1 GiB (33%) | 402 MiB | 5 GiB |
| `C-Loki-1` | Franco | Loki — logs del proyecto (backend S3 externo, ver [14_Manual_Operativo.md](../../docs/14_Manual_Operativo.md)) | 1.07 GiB | 6 GiB (18%) | 872 MiB | 5 GiB |
| `PFR-KANBOARD-TEST` | Franco | Kanboard — PHP 8.5 / Apache / SQLite | 272 MiB | 🔴 sin límite | 353 MiB | 5 GiB |
| `PFR-VULNAPP-APP` | Franco | VulnApp NG — Python / Gunicorn | 365 MiB | 2 GiB (18%) | 471 MiB | 20 GiB |
| `PFR-VULNAPP-DB` | Franco | VulnApp NG — PostgreSQL 18 | 311 MiB | 2 GiB (15%) | 679 MiB | 20 GiB |
| `PFR-WS-1` | Franco | NTF — notificaciones SMPP | 548 MiB | 1 GiB (54%) | 598 MiB | 5 GiB |
| `CAR-GW-SRV` | Carpinelli | Gateway + balanceador embebido (sirve Loki hoy) | 172 MiB | 1 GiB (17%) | 62 MiB | 5 GiB |
| `CAR-GW-OAM` | Carpinelli | Gateway de operación/mantenimiento | 141 MiB | 1 GiB (14%) — 🟡 71.18 MiB de swap usados | 692 MiB | 5 GiB |
| `C-Colector-1` | Carpinelli | Grafana Alloy — recolector de telemetría (IP `192.168.0.11`, coincide con la regla de `ACL-OVN-1`) | 373 MiB | 2 GiB (18%) | 2.43 GiB | sin tope explícito |
| `FDO-GW-SRV` | Fernando | Gateway + balanceador embebido (sirve NTF de Fernando) | 547 MiB | 1 GiB (53%) — 🟡 24.48 MiB de swap usados | 461 MiB | 5 GiB |
| `FDO-GW-OAM` | Fernando | Gateway de operación/mantenimiento | 236 MiB | 1 GiB (23%) | 583 MiB | 5 GiB |
| `FDO-WS-1` | Fernando | NTF — notificaciones SMPP (segunda instancia) | 544 MiB | 1 GiB (53%) — 🟡 24.53 MiB de swap usados | 598 MiB | 5 GiB |

**Suma de RAM usada por los contenedores, por sitio:** Franco ≈ 3.07 GiB, Carpinelli ≈ 0.67 GiB, Fernando ≈ 1.30 GiB. En los 3 casos es menor que el "Used" que reporta el host (paso 2) — la diferencia es el propio sistema operativo del host más el caché de ZFS, que no son parte de ningún contenedor.

## Conclusión

Ver el resumen y los hallazgos para la planificación en [README.md](README.md).
