# Implementación del backup nocturno ADM-TECH

**IMPLEMENTADO Y VERIFICADO**

Servidor tec-calidad05 (10.129.2.165). Implementación autorizada del 16/09/2026, entre 11:10:17 y 11:12:00 -0300. Acceso SSH como alfonzel_opr; escalamiento exclusivamente mediante sudo -n su. Identidad root confirmada con id/whoami. No se solicitó ni utilizó contraseña PostgreSQL o sudo.

## Archivos y directorios

Las tres rutas finales estaban ausentes antes de modificar; no se sobrescribió una implementación ajena. Se creó el padre necesario /var/backups/postgresql (root:root 755) y el destino /var/backups/postgresql/admtech. Se aplicó restorecon solicitado sin cambiar políticas ni desactivar SELinux.

| Elemento | Propietario/grupo | Modo | Contexto SELinux |
|---|---|---|---|
| /var/backups/postgresql/admtech | postgres:postgres | 700 | unconfined_u:object_r:var_t:s0 |
| /usr/local/sbin/backup_admtech.sh | root:root | 755 | unconfined_u:object_r:bin_t:s0 |
| /etc/cron.d/backup-admtech | root:root | 644 | unconfined_u:object_r:system_cron_spool_t:s0 |

Prueba controlada de escritura como postgres: WRITE_TEST_RC=0; .write_test eliminado. Script ejecutable pero no modificable por postgres: SCRIPT_PERMISSIONS_RC=0. Sintaxis bash -n válida localmente y en servidor. Script y cron se publicaron desde temporales en sus respectivos directorios con movimiento sin sobrescritura; temporales limpiados mediante trap.

No se encontró inicialmente el archivo con sufijo (1). Se partió de propuesta_backup_admtech.sh ya verificado y se preparó localmente **propuesta_backup_admtech(1).sh** con el ajuste autorizado. Es el contenido exacto instalado. Las propuestas/informes previos representan etapas anteriores; este documento registra el estado vigente.

SHA-256 del script local e instalado, coincidentes:

```text
178f1a52f26ff35ef4e2b1e561cd138749f61ebb34613788eabccffc1459d174
```

El bloque de variables instalado es:

```bash
unset PGPASSWORD PGPASSFILE PGSERVICE PGSERVICEFILE
unset PGHOST PGHOSTADDR PGPORT PGDATABASE PGUSER PGOPTIONS
```

No se agregó contraseña ni archivo pgpass. Se conservaron formato custom, compresión 6, flock, umask 077, set -Eeuo pipefail, temporales, movimientos atómicos por archivo, pg_restore --list, checksum comprobado, umbral 5 GiB, logger y retención de 30 días restringida a pares propios. La limpieza de Infrawork no alcanza este destino, situado fuera de backup_pg y del DocumentRoot.

## Primer respaldo y comprobaciones

Ejecutado con `su - postgres -c '/usr/local/sbin/backup_admtech.sh'` el 16/09/2026 a las 11:11:26–11:11:28 -0300.

| Validación | Resultado |
|---|---|
| BACKUP_RC | 0 |
| CHECKSUM_RC | 0 |
| PG_RESTORE_LIST_RC | 0 |
| Archivos regulares antes | 0 |
| Archivos regulares después | 3: dump, checksum y bloqueo flock |
| Dump | admtech_postgres_20260916T141126Z.dump |
| Tamaño dump | 4638079 bytes (4.42 MiB; 0.00 GiB al redondear a dos decimales) |
| Propietario/grupo del dump | postgres:postgres |
| Permisos dump | 600 |
| Fecha final dump | 2026-09-16T11:11:28-0300 |
| Checksum | admtech_postgres_20260916T141126Z.dump.sha256, 105 bytes, postgres:postgres 600 |
| Bloqueo auxiliar | .backup_admtech.lock, 0 bytes, postgres:postgres 600 |

Se creó exactamente un par de respaldo. El tercer archivo es el bloqueo persistente previsto para flock, no otro respaldo; no debe borrarse durante una ejecución. No quedaron temporales del dump/checksum. Se verificaron archivo no vacío, cantidad del par, propietario/grupo y modos antes de instalar cron. El checksum y el catálogo se comprobaron dentro del script y nuevamente en comandos independientes. No se imprimió el catálogo ni datos internos del dump. El journal registra INICIO y OK con el nombre y tamaño indicados.

## Programación instalada

```cron
SHELL=/bin/bash
PATH=/usr/pgsql-10/bin:/usr/local/sbin:/usr/bin:/bin
MAILTO=root

30 2 * * * postgres /usr/local/sbin/backup_admtech.sh
```

Instalación realizada solo después de las comprobaciones exitosas y de confirmar nuevamente capacidad libre superior a 5 GiB. Cron root:root 0644 con contexto predeterminado aplicado. SHA-256 local/remoto del cron: `271db236ea9fdec78776308cf099ab3f2f24d46593085e28e7a0d0bd79ea7c58`.

crond: **active / enabled** antes y después. No se reinició el servicio. Horario aprobado: todos los días **02:30**, hora local del servidor **America/Argentina/Buenos_Aires (UTC-03)**, con NTP sincronizado.

**Próxima ejecución calculada: 17/09/2026 02:30 -0300 (05:30 UTC).** Es la próxima coincidencia del cron según fecha/zona verificadas, no una ejecución futura ya observada.

## Alcance y pendientes

- No se modificaron backup de Infrawork, /opt/backup_potsgres.sh, crontabs existentes, Apache, PostgreSQL, pg_hba.conf, bases, contraseñas ni otros servicios. Los únicos ajustes de contexto fueron los restorecon autorizados sobre la nueva ruta de respaldo y el nuevo cron.
- Primer backup manual verificado. Falta observar la primera ejecución automática, confirmar entrega de notificaciones MAILTO=root y supervisar espacio/antigüedad del último respaldo.
- pg_restore --list valida lectura de catálogo, no una restauración integral. Queda pendiente una restauración en entorno aislado bajo autorización; no se restauró producción.
- Retención configurada: más de 43200 minutos, con borrado únicamente de pares propios después de un nuevo respaldo verificado. No se forzó envejecimiento ni se borraron respaldos para probarla. El primer directorio estaba vacío, por lo que no había respaldos viejos que eliminar.
- Dump y checksum se publican atómicamente por separado; una interrupción entre ambos puede dejar una copia sin checksum y requiere investigación. No se declara transacción atómica del par.
- Permanecen los riesgos documentados de compartir filesystem y de credenciales antiguas del esquema Infrawork. No se cambiaron esas credenciales ni se amplió el alcance autorizado.

## Evidencias y comandos sin secretos

SSH utilizó askpass forzado, host key estricta y multiplexación desactivada; helper local temporal eliminado por trap. La credencial SSH solo estuvo en memoria/entorno limitado al proceso, sin incorporarse a los entregables. Ninguna contraseña forma parte de los comandos siguientes. Los payloads de script/cron son contenido no secreto del archivo local indicado.

### deploy_precheck

```bash
hostname
whoami
sudo -n su -c 'id; whoami; for p in /var/backups/postgresql/admtech /usr/local/sbin/backup_admtech.sh /etc/cron.d/backup-admtech; do if test -e "$p" || test -L "$p"; then printf "EXISTE %s\n" "$p"; else printf "AUSENTE %s\n" "$p"; fi; done; df -B1 -P /var/backups; date --iso-8601=seconds'

```

```text
tec-calidad05
alfonzel_opr
uid=0(root) gid=0(root) grupos=0(root) contexto=unconfined_u:unconfined_r:unconfined_t:s0-s0:c0.c1023
root
AUSENTE /var/backups/postgresql/admtech
AUSENTE /usr/local/sbin/backup_admtech.sh
AUSENTE /etc/cron.d/backup-admtech
S.ficheros              bloques de 1       Usados Disponibles Capacidad Montado en
/dev/mapper/centos-root 800996720640 712467566592 88529154048       89% /
2026-09-16T11:10:17-0300

STDERR
** WARNING: connection is not using a post-quantum key exchange algorithm.
** This session may be vulnerable to "store now, decrypt later" attacks.
** The server may need to be upgraded. See https://openssh.com/pq.html

```

### deploy_install

```bash
# Cuerpo ejecutado como root mediante sudo -n su -c (bash -c):
set -euo pipefail
test "$(hostname)" = tec-calidad05
test "$(id -u)" = 0
for p in /var/backups/postgresql/admtech /usr/local/sbin/backup_admtech.sh /etc/cron.d/backup-admtech; do
  if test -e "$p" || test -L "$p"; then printf 'STOP EXISTE %s\n' "$p"; exit 1; fi
done
free_bytes=$(df -B1 --output=avail /var/backups | tail -n 1)
test "$free_bytes" -ge 5368709120
install -d -o postgres -g postgres -m 0700 /var/backups/postgresql/admtech
restorecon -Rv /var/backups/postgresql
ls -ldZ /var/backups/postgresql /var/backups/postgresql/admtech
namei -om /var/backups/postgresql/admtech
su - postgres -c 'test -w /var/backups/postgresql/admtech && touch /var/backups/postgresql/admtech/.write_test && rm -f /var/backups/postgresql/admtech/.write_test'
printf 'WRITE_TEST_RC=0\n'
umask 077
tmp_script=$(mktemp /usr/local/sbin/.backup_admtech.XXXXXXXX)
trap 'rm -f -- "$tmp_script"' EXIT
printf '%s' '<BASE64_DEL_ARCHIVO_LOCAL>' | base64 -d > "$tmp_script"
bash -n "$tmp_script"
test "$(sha256sum "$tmp_script" | cut -d' ' -f1)" = '178f1a52f26ff35ef4e2b1e561cd138749f61ebb34613788eabccffc1459d174'
chown root:root "$tmp_script"
chmod 0755 "$tmp_script"
mv -n -- "$tmp_script" /usr/local/sbin/backup_admtech.sh
test ! -e "$tmp_script"
bash -n /usr/local/sbin/backup_admtech.sh
ls -lZ /usr/local/sbin/backup_admtech.sh
sha256sum /usr/local/sbin/backup_admtech.sh
su - postgres -c 'test -x /usr/local/sbin/backup_admtech.sh && test ! -w /usr/local/sbin/backup_admtech.sh'
printf 'SCRIPT_PERMISSIONS_RC=0\n'
date --iso-8601=seconds

```

```text
drwxr-xr-x. root     root     unconfined_u:object_r:var_t:s0   /var/backups/postgresql
drwx------. postgres postgres unconfined_u:object_r:var_t:s0   /var/backups/postgresql/admtech
f: /var/backups/postgresql/admtech
 dr-xr-xr-x root     root     /
 drwxr-xr-x root     root     var
 drwxr-xr-x root     root     backups
 drwxr-xr-x root     root     postgresql
 drwx------ postgres postgres admtech
WRITE_TEST_RC=0
-rwxr-xr-x. root root unconfined_u:object_r:bin_t:s0   /usr/local/sbin/backup_admtech.sh
178f1a52f26ff35ef4e2b1e561cd138749f61ebb34613788eabccffc1459d174  /usr/local/sbin/backup_admtech.sh
SCRIPT_PERMISSIONS_RC=0
2026-09-16T11:11:07-0300

STDERR
** WARNING: connection is not using a post-quantum key exchange algorithm.
** This session may be vulnerable to "store now, decrypt later" attacks.
** The server may need to be upgraded. See https://openssh.com/pq.html

```

### deploy_first_backup

```bash
# Cuerpo ejecutado como root mediante sudo -n su -c (bash -c):
set -u
date --iso-8601=seconds
printf 'FILES_BEFORE='
find /var/backups/postgresql/admtech -maxdepth 1 -type f -printf '.' | wc -c
su - postgres -c '/usr/local/sbin/backup_admtech.sh'
rc=$?
printf 'BACKUP_RC=%s\n' "$rc"
test "$rc" = 0 || exit "$rc"
su - postgres -c 'cd /var/backups/postgresql/admtech && sha256sum --check --status admtech_postgres_*.dump.sha256'
rc=$?
printf 'CHECKSUM_RC=%s\n' "$rc"
test "$rc" = 0 || exit "$rc"
su - postgres -c 'for archivo in /var/backups/postgresql/admtech/admtech_postgres_*.dump; do test -s "$archivo" && /usr/pgsql-10/bin/pg_restore --list "$archivo" >/dev/null || exit 1; done'
rc=$?
printf 'PG_RESTORE_LIST_RC=%s\n' "$rc"
test "$rc" = 0 || exit "$rc"
printf 'FILES_AFTER='
find /var/backups/postgresql/admtech -maxdepth 1 -type f -printf '.' | wc -c
find /var/backups/postgresql/admtech -maxdepth 1 -type f -printf '%f|%s|%u|%g|%m|%TY-%Tm-%TdT%TH:%TM:%TS\n'
date --iso-8601=seconds

```

```text
2026-09-16T11:11:25-0300
FILES_BEFORE=0
BACKUP_RC=0
CHECKSUM_RC=0
PG_RESTORE_LIST_RC=0
FILES_AFTER=3
.backup_admtech.lock|0|postgres|postgres|600|2026-09-16T11:11:26.1658765530
admtech_postgres_20260916T141126Z.dump|4638079|postgres|postgres|600|2026-09-16T11:11:28.0289246560
admtech_postgres_20260916T141126Z.dump.sha256|105|postgres|postgres|600|2026-09-16T11:11:28.0769258960
2026-09-16T11:11:28-0300

STDERR
** WARNING: connection is not using a post-quantum key exchange algorithm.
** This session may be vulnerable to "store now, decrypt later" attacks.
** The server may need to be upgraded. See https://openssh.com/pq.html

```

### deploy_cron

```bash
# Cuerpo ejecutado como root mediante sudo -n su -c (bash -c):
set -euo pipefail
test ! -e /etc/cron.d/backup-admtech
test ! -L /etc/cron.d/backup-admtech
test "$(find /var/backups/postgresql/admtech -maxdepth 1 -type f -name 'admtech_postgres_*.dump' -printf '.' | wc -c)" = 1
test "$(find /var/backups/postgresql/admtech -maxdepth 1 -type f -name 'admtech_postgres_*.dump.sha256' -printf '.' | wc -c)" = 1
test "$(stat -c '%U:%G:%a' /var/backups/postgresql/admtech/admtech_postgres_20260916T141126Z.dump)" = postgres:postgres:600
test "$(stat -c '%U:%G:%a' /var/backups/postgresql/admtech/admtech_postgres_20260916T141126Z.dump.sha256)" = postgres:postgres:600
test "$(df -B1 --output=avail /var/backups/postgresql/admtech | tail -n 1)" -ge 5368709120
systemctl is-active crond
systemctl is-enabled crond
umask 077
cron_tmp=$(mktemp /etc/cron.d/.backup-admtech.XXXXXXXX)
trap 'rm -f -- "$cron_tmp"' EXIT
printf '%s' '<BASE64_DEL_ARCHIVO_LOCAL>' | base64 -d > "$cron_tmp"
chown root:root "$cron_tmp"
chmod 0644 "$cron_tmp"
mv -n -- "$cron_tmp" /etc/cron.d/backup-admtech
test ! -e "$cron_tmp"
restorecon -v /etc/cron.d/backup-admtech
cat /etc/cron.d/backup-admtech
ls -lZ /etc/cron.d/backup-admtech
sha256sum /etc/cron.d/backup-admtech /usr/local/sbin/backup_admtech.sh
systemctl is-active crond
systemctl is-enabled crond
date --iso-8601=seconds
printf 'NEXT_RUN_LOCAL='
date -d 'tomorrow 02:30' --iso-8601=seconds
timedatectl
printf '\n=== BACKUP LOG ===\n'
journalctl -t backup-admtech --since '2026-09-16 11:11:00' --no-pager -o short-iso

```

```text
active
enabled
SHELL=/bin/bash
PATH=/usr/pgsql-10/bin:/usr/local/sbin:/usr/bin:/bin
MAILTO=root

30 2 * * * postgres /usr/local/sbin/backup_admtech.sh
-rw-r--r--. root root unconfined_u:object_r:system_cron_spool_t:s0 /etc/cron.d/backup-admtech
271db236ea9fdec78776308cf099ab3f2f24d46593085e28e7a0d0bd79ea7c58  /etc/cron.d/backup-admtech
178f1a52f26ff35ef4e2b1e561cd138749f61ebb34613788eabccffc1459d174  /usr/local/sbin/backup_admtech.sh
active
enabled
2026-09-16T11:12:00-0300
NEXT_RUN_LOCAL=2026-09-17T02:30:00-0300
      Local time: miÃ© 2026-09-16 11:12:00 -03
  Universal time: miÃ© 2026-09-16 14:12:00 UTC
        RTC time: miÃ© 2026-09-16 14:12:00
       Time zone: America/Argentina/Buenos_Aires (-03, -0300)
     NTP enabled: yes
NTP synchronized: yes
 RTC in local TZ: no
      DST active: n/a

=== BACKUP LOG ===
-- Logs begin at mar 2026-09-01 14:06:01 -03, end at miÃ© 2026-09-16 11:12:00 -03. --
2026-09-16T11:11:26-0300 tec-calidad05 backup-admtech[5377]: INICIO base=postgres archivo=admtech_postgres_20260916T141126Z.dump
2026-09-16T11:11:28-0300 tec-calidad05 backup-admtech[5391]: OK base=postgres archivo=admtech_postgres_20260916T141126Z.dump bytes=4638079

STDERR
** WARNING: connection is not using a post-quantum key exchange algorithm.
** This session may be vulnerable to "store now, decrypt later" attacks.
** The server may need to be upgraded. See https://openssh.com/pq.html

```
