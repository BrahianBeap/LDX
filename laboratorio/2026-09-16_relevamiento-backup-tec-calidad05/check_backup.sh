date --iso-8601=seconds
printf '\n=== LOCALIZAR ===\n'
sudo -n grep -RIlE 'pg_dump|backup_Infraestructura' /etc/cron.d /etc/cron.daily /usr/local/sbin /var/spool/cron 2>/dev/null
printf 'BUSQUEDA_RC=%s\n' "$?"
printf '\n=== HERRAMIENTAS ===\n'
for cmd in pg_dump pg_restore psql flock sha256sum logger; do command -v "$cmd"; done
/usr/pgsql-10/bin/pg_dump --version
/usr/pgsql-10/bin/pg_restore --version
/usr/pgsql-10/bin/psql --version
id postgres
getent passwd postgres
printf '\n=== AUTH ===\n'
sudo -n -u postgres /usr/pgsql-10/bin/psql -X --no-password --dbname=postgres --tuples-only --no-align --command="SELECT current_database(), current_user, pg_is_in_recovery(), pg_database_size(current_database());"
auth_rc=$?
printf 'AUTH_RC=%s\n' "$auth_rc"
if test "$auth_rc" = 0; then
sudo -n -u postgres /usr/pgsql-10/bin/pg_dump --no-password --username=postgres --dbname=postgres --schema-only --lock-wait-timeout=60s --file=/dev/null
printf 'SCHEMA_RC=%s\n' "$?"
fi
printf '\n=== DESTINO ===\n'
ls -ldZ /var/www/html/backup_pg /var/www/html/backup_pg/admtech /var/backups /var/backups/postgresql/admtech
namei -om /var/www/html/backup_pg/admtech
df -B1 -P /var/www/html/backup_pg
df -Pi /var/www/html/backup_pg
sudo -n -u postgres test -w /var/www/html/backup_pg
printf 'POSTGRES_PARENT_WRITE_RC=%s\n' "$?"
sudo -n -u postgres test -w /var/www/html/backup_pg/admtech
printf 'POSTGRES_DEST_WRITE_RC=%s\n' "$?"
find /var/www/html/backup_pg -maxdepth 1 -type f -printf '%f|%s|%TY-%Tm-%Td %TH:%TM:%TS|%u|%g|%m\n' | sort
printf '\n=== APACHE ===\n'
/usr/sbin/httpd -S
printf '\n=== CRON ===\n'
systemctl is-active crond
systemctl is-enabled crond
timedatectl
date --iso-8601=seconds
