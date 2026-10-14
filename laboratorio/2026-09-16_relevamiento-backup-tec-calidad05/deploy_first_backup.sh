sudo -n su -c 'bash -c '"'"'set -u
date --iso-8601=seconds
printf '"'"'"'"'"'"'"'"'FILES_BEFORE='"'"'"'"'"'"'"'"'
find /var/backups/postgresql/admtech -maxdepth 1 -type f -printf '"'"'"'"'"'"'"'"'.'"'"'"'"'"'"'"'"' | wc -c
su - postgres -c '"'"'"'"'"'"'"'"'/usr/local/sbin/backup_admtech.sh'"'"'"'"'"'"'"'"'
rc=$?
printf '"'"'"'"'"'"'"'"'BACKUP_RC=%s\n'"'"'"'"'"'"'"'"' "$rc"
test "$rc" = 0 || exit "$rc"
su - postgres -c '"'"'"'"'"'"'"'"'cd /var/backups/postgresql/admtech && sha256sum --check --status admtech_postgres_*.dump.sha256'"'"'"'"'"'"'"'"'
rc=$?
printf '"'"'"'"'"'"'"'"'CHECKSUM_RC=%s\n'"'"'"'"'"'"'"'"' "$rc"
test "$rc" = 0 || exit "$rc"
su - postgres -c '"'"'"'"'"'"'"'"'for archivo in /var/backups/postgresql/admtech/admtech_postgres_*.dump; do test -s "$archivo" && /usr/pgsql-10/bin/pg_restore --list "$archivo" >/dev/null || exit 1; done'"'"'"'"'"'"'"'"'
rc=$?
printf '"'"'"'"'"'"'"'"'PG_RESTORE_LIST_RC=%s\n'"'"'"'"'"'"'"'"' "$rc"
test "$rc" = 0 || exit "$rc"
printf '"'"'"'"'"'"'"'"'FILES_AFTER='"'"'"'"'"'"'"'"'
find /var/backups/postgresql/admtech -maxdepth 1 -type f -printf '"'"'"'"'"'"'"'"'.'"'"'"'"'"'"'"'"' | wc -c
find /var/backups/postgresql/admtech -maxdepth 1 -type f -printf '"'"'"'"'"'"'"'"'%f|%s|%u|%g|%m|%TY-%Tm-%TdT%TH:%TM:%TS\n'"'"'"'"'"'"'"'"'
date --iso-8601=seconds
'"'"''
