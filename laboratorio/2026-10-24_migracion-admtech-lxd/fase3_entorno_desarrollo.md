# Fase 3 — Entorno de desarrollo de ADM-TECH (comandos propuestos)

> 🟡 **Propuesto, no ejecutado.** Requiere OK explícito antes de correr cualquier paso. Cada paso indica si **crea**, **modifica** o solo **lee**.
> Todo se ejecuta desde `pfr-oss` (`10.143.11.228`), salvo donde se indica "en tu PC".

## Qué se crea

| Elemento | Nombre | Detalle |
|---|---|---|
| Base de prueba | `DEV-ADMTECH-DB` | `pfr.1`, `PRJ-OSS`, `192.168.0.18`, 1 vCPU / 1 GiB / raíz 10 GiB, PostgreSQL 18 |
| App de prueba | `DEV-ADMTECH-APP` | `pfr.1`, `PRJ-OSS`, `192.168.0.19`, 1 vCPU / 1 GiB / raíz 10 GiB, Apache + PHP 8.5 |
| Volumen de archivos | `admtech-archivos-dev` | Pool `local`, 10 GiB, con una **muestra** de los adjuntos (no los 7,2 GB) |
| ACL | 2 reglas nuevas | `.19 → .18:5432` y `.1 → .19:80` |
| Gateway (opcional) | Ruta `/adm-dev` en `PFR-GW-SRV` | Restringida a la IP de tu PC, para probar desde el navegador |

**Qué no se toca:** tec-calidad05 (solo se lee la base con `pg_dump`), la producción de ADM-TECH, ni los demás contenedores del clúster.

**Recursos:** +2 GiB de RAM sobre `pfr.1` (tiene ~8 GiB libres) y ~30 GiB de disco (tiene ~320 GB libres).

---

## Paso 1 — Perfiles (CREA)

Copian el patrón de `PRF-VULNAPP-DB/APP`: rutas por el gateway de operación `.6`, proxy de apt y SSH deshabilitado.

```bash
lxc profile create PRF-ADMTECH-DEV-DB --project PRJ-OSS
lxc profile create PRF-ADMTECH-DEV-APP --project PRJ-OSS
lxc profile edit PRF-ADMTECH-DEV-DB  --project PRJ-OSS < prf-admtech-dev-db.yaml
lxc profile edit PRF-ADMTECH-DEV-APP --project PRJ-OSS < prf-admtech-dev-app.yaml
```

`prf-admtech-dev-db.yaml` (el de APP es igual, con `192.168.0.19`, la descripción correspondiente y la ruta extra `10.150.0.0/16 via 192.168.0.6` para OAuth):

```yaml
description: Entorno de desarrollo ADM-TECH - PostgreSQL 18
config:
  cloud-init.network-config: |
    version: 2
    ethernets:
      eth0:
        dhcp4: true
        dhcp6: false
        routes:
          - to: 10.150.32.100
            via: 192.168.0.6
        nameservers:
          addresses: [192.168.0.254]
  cloud-init.user-data: |
    #cloud-config
    apt:
      http_proxy: "http://10.150.32.100:3128"
      https_proxy: "http://10.150.32.100:3128"
    package_update: true
    package_upgrade: true
    runcmd:
      - systemctl disable --now ssh.socket ssh
      - systemctl mask ssh.socket ssh
  limits.cpu: "1"
  limits.memory: 1GiB
  limits.processes: "500"
devices:
  eth0: {type: nic, network: OVN_1, ipv4.address: 192.168.0.18}
  root: {type: disk, path: /, pool: local, size: 10GiB}
```

## Paso 2 — Contenedores y volumen (CREA)

`< /dev/null` evita el cuelgue de [TRB-017](../../docs/07_Troubleshooting.md#trb-017--lxc-launchlxc-init-se-cuelgan-sin-error-al-ejecutarse-por-ssh-sin-terminal).

```bash
lxc launch ubuntu:26.04 DEV-ADMTECH-DB  --project PRJ-OSS --target pfr.1 -p PRF-ADMTECH-DEV-DB  < /dev/null
lxc launch ubuntu:26.04 DEV-ADMTECH-APP --project PRJ-OSS --target pfr.1 -p PRF-ADMTECH-DEV-APP < /dev/null

lxc storage volume create local admtech-archivos-dev size=10GiB --project PRJ-OSS --target pfr.1
lxc config device add DEV-ADMTECH-APP archivos disk pool=local source=admtech-archivos-dev \
    path=/var/www/adm/archivos --project PRJ-OSS
```

> **Nota:** la imagen local `ubuntu 26.04 LTS amd64 (release)` (`deafe0d30bd9`) ya está cacheada. Si el remoto `ubuntu:` no responde, usar ese fingerprint.

**Verificar:** `lxc list --project PRJ-OSS -c ns4L | grep DEV-ADMTECH` → ambos `RUNNING` con `.18` y `.19`; `cloud-init status` en cada uno → `done`.

## Paso 3 — ACL (MODIFICA `ACL-OVN-1`, solo agrega reglas)

```bash
lxc network acl show ACL-OVN-1 --project PRJ-OSS > ~/backup-AAAAMMDD/ACL-OVN-1.yaml   # backup
lxc network acl rule add ACL-OVN-1 ingress --project PRJ-OSS action=allow \
  source=192.168.0.19 destination=192.168.0.18 protocol=tcp destination_port=5432 \
  "description=DEV ADM-TECH: app hacia PostgreSQL" state=enabled
```

El acceso `.1 → .19:80` ya lo cubre la regla general "Desde LBs hacia los servicios web internos" (`.1,.2,.4 → 192.168.0.0/24`, puerto 80). No hace falta otra regla.

**Rollback:** `lxc network acl rule remove ...` con los mismos parámetros.

## Paso 4 — Software (CREA, dentro de los contenedores)

```bash
# Base
lxc exec DEV-ADMTECH-DB --project PRJ-OSS -n -- apt-get install -y postgresql-18
# Escuchar en la IP de OVN y aceptar solo a la app de prueba
#   postgresql.conf: listen_addresses = 'localhost,192.168.0.18'
#   pg_hba.conf:     host  admtech  admtech_app  192.168.0.19/32  scram-sha-256

# App
lxc exec DEV-ADMTECH-APP --project PRJ-OSS -n -- apt-get install -y \
  apache2 libapache2-mod-php php-pgsql php-gd php-zip php-mbstring php-xml php-curl php-ldap composer git unzip
```

> **Nota:** Ubuntu 26.04 trae PostgreSQL 18 en sus repositorios (es la misma vía que usó VulnApp NG). Para producción se evaluará el repositorio PGDG, que permite elegir la versión independientemente del SO.

## Paso 5 — Datos de prueba (LEE de tec-calidad05, CREA en el entorno de desarrollo)

**5a. Dump de la base, en tu PC** (pg_dump de pgAdmin; conexión de solo lectura, nada se escribe en tec-calidad05):

```powershell
& "C:\Program Files\pgAdmin 4\runtime\pg_dump.exe" -h 10.129.2.165 -U postgres -d postgres `
  -n reserva -n aud -Fc -f admtech_YYYYMMDD.dump
```

**5b. Muestra de archivos** (un mes reciente, unos cientos de MB): listado y copia con `tar` por SSH desde tec-calidad05, solo lectura.

**5c. Subir y restaurar** (desde `pfr-oss`):

```bash
lxc file push admtech_YYYYMMDD.dump DEV-ADMTECH-DB/tmp/ --project PRJ-OSS
lxc exec DEV-ADMTECH-DB --project PRJ-OSS -n -- sudo -u postgres sh -c '
  createuser admtech_app --pwprompt   # contraseña nueva, solo para desarrollo
  createdb admtech -O admtech_app -E UTF8
  pg_restore -d admtech --no-owner --role=admtech_app /tmp/admtech_YYYYMMDD.dump
  rm /tmp/admtech_YYYYMMDD.dump'
```

Se restaura en una base llamada **`admtech`** (no `postgres`), con dueño `admtech_app`. La aplicación queda sin superusuario desde el inicio.

> **Advertencia:** el dump tiene **datos reales** de producción. Queda solo dentro de `DEV-ADMTECH-DB`. La copia local en tu PC se borra después de subirla.

## Paso 6 — Código (CREA)

El código **no** se clona desde GitLab dentro del contenedor (no está confirmada la ruta de red). Se arma en tu PC desde la rama `feature/php85` y se sube:

```powershell
git -C C:\Users\alfonzel\Documents\GitHub\adm-tech archive --format=tar.gz -o adm-php85.tar.gz feature/php85
```
```bash
lxc file push adm-php85.tar.gz DEV-ADMTECH-APP/tmp/ --project PRJ-OSS
lxc exec DEV-ADMTECH-APP --project PRJ-OSS -n -- sh -c 'mkdir -p /var/www/adm && tar xzf /tmp/adm-php85.tar.gz -C /var/www/adm && rm /tmp/adm-php85.tar.gz'
```

Configuración: vhost propio con `SetEnv DB_HOST=192.168.0.18`, `DB_NAME=admtech`, `DB_USER=admtech_app`, y PHP desactivado en `/var/www/adm/archivos`. **Sin credenciales de producción.**

## Paso 7 — Acceso desde el navegador (MODIFICA `LB.conf` de PFR, opcional)

Ruta `/adm-dev` en `PFR-GW-SRV`, restringida a la IP de tu PC, con el procedimiento [Modificar el LB.conf de un gateway de forma controlada](../../docs/06_Operacion.md#modificar-el-lbconf-de-un-gateway-de-forma-controlada):

```apache
    <Location "/adm-dev">
      ProxyPass http://192.168.0.19/adm
      ProxyPassReverse http://192.168.0.19/adm
      Require ip IP_DE_TU_PC
    </Location>
```

> **Nota:** el login OAuth no va a funcionar en desarrollo (la URL de retorno registrada es la de producción). Se usa el login de respaldo usuario/clave de la aplicación.

## Para retirar todo el entorno de desarrollo

```bash
lxc delete --force DEV-ADMTECH-APP DEV-ADMTECH-DB --project PRJ-OSS
lxc storage volume delete local admtech-archivos-dev --project PRJ-OSS --target pfr.1
lxc profile delete PRF-ADMTECH-DEV-APP --project PRJ-OSS; lxc profile delete PRF-ADMTECH-DEV-DB --project PRJ-OSS
# + quitar la regla de la ACL y la ruta /adm-dev
```
