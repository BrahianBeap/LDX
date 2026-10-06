# Bitácora — Verificación en vivo del cluster (2026-10-06)

Ver contexto y resumen en [`README.md`](README.md). Esta bitácora contiene la salida relevante capturada de cada host, en modo solo lectura.

---

## pfr-oss (10.143.11.228, `pfr.1`)

```
$ hostname && uptime
pfr-oss
 18:01:14 up 93 days, 19:17,  3 users,  load average: 0.04, 0.04, 0.00

$ cat /etc/os-release | head -5
PRETTY_NAME="Ubuntu 26.04 LTS"
VERSION_ID="26.04"
VERSION_CODENAME=resolute

$ snap list | grep -Ei 'lxd|microovn|core'
lxd       5.21.6-78b046a          40361  5.21/stable    canonical**  in-cohort,held
microovn  24.03.6+snap77a702704c  1088   24.03/stable   canonical**  -
```

### `lxc cluster list`

```
+-------+-----------------------------+-----------------+--------------+----------------+-------------+--------+-------------------+
| NAME  |             URL             |      ROLES      | ARCHITECTURE | FAILURE DOMAIN | DESCRIPTION | STATE  |      MESSAGE      |
+-------+-----------------------------+-----------------+--------------+----------------+-------------+--------+-------------------+
| car.1 | https://192.168.91.116:8443 | database        | x86_64       | default        |             | ONLINE | Fully operational |
| fdo.1 | https://10.150.32.101:8443  | database        | x86_64       | default        |             | ONLINE | Fully operational |
| pfr.1 | https://10.143.11.228:8443  | database-leader | x86_64       | default        |             | ONLINE | Fully operational |
|       |                             | database        |              |                |             |        |                   |
+-------+-----------------------------+-----------------+--------------+----------------+-------------+--------+-------------------+
```

✅ Los 3 nodos ONLINE — quórum de 3/3 parece completo. Ver [RIE-002](../../docs/11_Riesgos.md#rie-002--dos-de-tres-nodos-activos-alta-disponibilidad-de-base-de-datos-incompleta-🟡-posiblemente-resuelto--ver-verificación-en-vivo).

### `lxc list` (proyecto `default`)

```
PFR-GW-OAM         RUNNING   192.168.0.6 / 10.231.193.114   pfr.1
CAR-GW-OAM         RUNNING   192.168.0.8 / 10.231.193.180   car.1
FDO-GW-OAM         RUNNING   192.168.0.9 / 10.231.193.107   fdo.1
PFR-KANBOARD-TEST  RUNNING   192.168.0.106                  pfr.1
```

### `lxc list --project PRJ-OSS` (vista de cluster, igual desde cualquier nodo)

```
C-Colector-1   RUNNING  192.168.0.11 (eth1)    car.1
C-Grafana-1    STOPPED                         car.1
C-Loki-1       RUNNING  192.168.0.12 (eth0)    pfr.1
C-Mimir-1      STOPPED                         fdo.1
CAR-GW-SRV     RUNNING  192.168.91.117/192.168.0.2   car.1
CAR-KANBOARD   STOPPED                         car.1
FDO-GW-SRV     RUNNING  192.168.0.4/10.11.11.12      fdo.1
FDO-WS-1       RUNNING  192.168.0.110 (eth0)   fdo.1
I-GW-SRV       STOPPED                         fdo.1
Minio-1        STOPPED                         car.1
PFR-GW-SRV     RUNNING  192.168.0.1/10.143.11.8      pfr.1
PFR-WS-1       RUNNING  192.168.0.111 (eth0)   pfr.1
```

✅ `FDO-WS-1` (servicio NTF, ver [03_Componentes.md — balanceador embebido](../../docs/03_Componentes.md#variante-balanceador-embebido-en-el-gateway-cuando-se-necesita-la-ip-real-de-origen)) corre en `fdo.1` con IP en `OVN_1` → evidencia de que OVN funciona en Fernando. Ver [RIE-013](../../docs/11_Riesgos.md#rie-013--interfaz-ovn-bloqueada-en-fernando-causa-raíz-no-identificada-🟡-posiblemente-resuelto--ver-verificación-en-vivo).

🔴 `CAR-KANBOARD` y `C-Mimir-1` no están documentados en ningún lado — pendiente de validación con el equipo.

### `lxc network list` / `--project PRJ-OSS`

Red `OVN_1` (`192.168.0.254/24`) y `UplinkOvn1` presentes y `CREATED` en los 3 nodos. `lxc network list --target fdo.1` (corrido desde `fdo-oss`) devuelve la misma lista, incluyendo `OVN_1` — no distingue si el chassis de Fernando está realmente activo a nivel de OVN (ver limitación abajo).

### `lxc project list`

```
PRJ-OSS             YES  YES  YES  YES  NO   YES  Servicios OSS         38
default (current)   YES  YES  YES  YES  YES  YES  Default LXD project   30
```

### Disco

`/dev/sda3` (raíz) 15% usado (6.7G/49G). Sin alertas.

---

## car-oss (192.168.91.116, `car.1`)

Mismos resultados de cluster/red/proyecto que `pfr-oss` (es información replicada del cluster). Datos propios del nodo:

```
$ hostname && uptime
car-oss
 18:01:14 up 94 days,  5:32,  3 users

$ cat /etc/os-release | head -3
PRETTY_NAME="Ubuntu 26.04 LTS"
VERSION_ID="26.04"

$ df -h /
/dev/mapper/ubuntu--vg-ubuntu--lv   98G   12G   82G  13% /
```

LXD 5.21.6 y MicroOVN 24.03.6 — mismas versiones que `pfr-oss` (consistentes, buena práctica ya documentada en [12_Lecciones_Aprendidas.md](../../docs/12_Lecciones_Aprendidas.md)).

---

## fdo-oss (10.150.32.101, `fdo.1`, hostname real `fdo-oss1`)

```
$ hostname && uptime
fdo-oss1
 18:01:29 up 62 days, 23:53,  4 users

$ cat /etc/os-release | head -3
PRETTY_NAME="Ubuntu 26.04 LTS"
VERSION_ID="26.04"

$ df -h /
/dev/mapper/ubuntu--vg-ubuntu--lv   98G   12G   82G  13% /

$ ip -4 -brief addr
lo               UNKNOWN        127.0.0.1/8
nic_oam          UP             10.150.32.101/24
UplinkOvn1       UP             169.254.1.1/24
lxdbr_OAM        UP             10.231.193.1/24
wg0              UNKNOWN        169.254.0.2/32
```

LXD 5.21.6 y MicroOVN 24.03.6 — mismas versiones que los otros dos nodos.

### Intento de verificar MicroOVN directamente

```
$ sudo -n microovn status
sudo: a password is required

$ microovn status
Error: failed listing services: Get "http://control.socket/1.0/services":
dial unix /var/snap/microovn/common/state/control.socket: connect: permission denied
```

🔴 **Limitación de esta verificación:** la cuenta `alfonzel_opr` no tiene `sudo` sin contraseña ni pertenece al grupo con acceso al socket de control de MicroOVN. No se pudo confirmar el estado interno del chassis OVN en Fernando — solo la evidencia indirecta de que hay un contenedor corriendo sobre la red `OVN_1` en ese nodo (`FDO-WS-1`, ver arriba). Repetir esta verificación con acceso a `sudo` para cerrar la duda de causa raíz en [TRB-012](../../docs/07_Troubleshooting.md#trb-012--la-interfaz-ovn-no-levanta-en-un-nodo-nuevo-aunque-los-servicios-de-microovn-estén-running-🟡-posiblemente-resuelto--ver-nota-2026-10-06).

### `lxc network list --target fdo.1`

```
OVN_1       ovn      YES  192.168.0.254/24   25  CREATED
UplinkOvn1  bridge   YES  169.254.1.1/24      1  CREATED
br-int      bridge   NO                       0
lxdbr_OAM   bridge   YES  10.231.193.1/24      4  CREATED
lxdovn43    bridge   NO                        0
nic_oam     physical NO                        0
nic_srv1    physical NO                        9
```

> **Nota metodológica:** este comando lista las definiciones de red del cluster (replicadas vía la base de datos distribuida), no necesariamente el estado de salud del chassis OVN *local* a `fdo.1`. La confirmación real de que OVN funciona ahí es indirecta: el contenedor `FDO-WS-1` está `RUNNING` con una IP de `OVN_1` asignada, lo cual no sería posible si el chassis no estuviera operativo.
