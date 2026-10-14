from pathlib import Path
import hashlib,re,shlex
R=Path(__file__).resolve().parent
script=R/'propuesta_backup_admtech(1).sh'
digest=hashlib.sha256(script.read_bytes()).hexdigest()
cron_digest=hashlib.sha256((R/'propuesta_backup_admtech.cron').read_bytes()).hexdigest()
assert digest=='178f1a52f26ff35ef4e2b1e561cd138749f61ebb34613788eabccffc1459d174'
results={n:(R/(n+'.txt')).read_text(encoding='utf-8') for n in ['deploy_precheck','deploy_install','deploy_first_backup','deploy_cron']}
assert all(x in results['deploy_first_backup'] for x in ['BACKUP_RC=0','CHECKSUM_RC=0','PG_RESTORE_LIST_RC=0'])
assert digest in results['deploy_install'] and digest in results['deploy_cron']
assert cron_digest in results['deploy_cron']
report=f'''# Implementación del backup nocturno ADM-TECH

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
{digest}
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

Instalación realizada solo después de las comprobaciones exitosas y de confirmar nuevamente capacidad libre superior a 5 GiB. Cron root:root 0644 con contexto predeterminado aplicado. SHA-256 local/remoto del cron: `{cron_digest}`.

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
'''
for name,out in results.items():
    command=(R/(name+'.sh')).read_text(encoding='utf-8')
    if name!='deploy_precheck':
        command=shlex.split(shlex.split(command)[-1])[-1]
        command=re.sub(r"printf '%s' '[A-Za-z0-9+/=]+' \| base64 -d", "printf '%s' '<BASE64_DEL_ARCHIVO_LOCAL>' | base64 -d",command)
        command='# Cuerpo ejecutado como root mediante sudo -n su -c (bash -c):\n'+command
    report+='\n### '+name+'\n\n```bash\n'+command+'\n```\n\n```text\n'+out+'\n```\n'
(R/'implementacion_backup_admtech.md').write_text(report,encoding='utf-8')
secret=re.search(r'temporal:\s*(\S+)',Path(r'C:\Users\alfonzel\.codex\attachments\7051e76f-5c0e-45ac-b02a-64713544988a\pasted-text.txt').read_text(encoding='utf-8-sig')).group(1)
for file in [R/'implementacion_backup_admtech.md',script,R/'propuesta_backup_admtech.cron']:
    assert secret not in file.read_text(encoding='utf-8')
assert 'export PGPASSFILE=' not in script.read_text(encoding='utf-8')
secret=None
print('Documentación generada. Hashes coincidentes, tres validaciones RC=0 y entregables sin credencial SSH.')
