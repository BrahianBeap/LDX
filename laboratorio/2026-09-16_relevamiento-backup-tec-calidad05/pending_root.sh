date --iso-8601=seconds
sudo -n su -c 'su - postgres -c "/usr/pgsql-10/bin/psql -X --no-password --dbname=postgres --tuples-only --no-align --command=\"SELECT current_database(), current_user, pg_is_in_recovery(), pg_database_size(current_database());\""'
auth_rc=$?
printf 'AUTH_RC=%s\n' "$auth_rc"
if test "$auth_rc" = 0; then
sudo -n su -c 'su - postgres -c "/usr/pgsql-10/bin/pg_dump --no-password --username=postgres --dbname=postgres --schema-only --lock-wait-timeout=60s --file=/dev/null"'
printf 'SCHEMA_RC=%s\n' "$?"
fi
printf '\n=== SIN PGPASS NI CREDENCIALES HEREDADAS ===\n'
sudo -n su -c 'su - postgres -c "unset PGPASSWORD PGSERVICE PGSERVICEFILE PGHOST PGHOSTADDR PGPORT PGDATABASE PGUSER PGOPTIONS; PGPASSFILE=/dev/null /usr/pgsql-10/bin/psql -X --no-password --port=5432 --username=postgres --dbname=postgres --tuples-only --no-align --command=\"SELECT current_database(), current_user, pg_is_in_recovery(), pg_database_size(current_database());\""'
printf 'AUTH_SIN_CREDENCIALES_RC=%s\n' "$?"
printf '\n=== DESTINO ===\n'
sudo -n su -c 'ls -ldZ /var/backups /var/backups/postgresql /var/backups/postgresql/admtech; su - postgres -c "test -w /var/backups/postgresql/admtech"; printf "DEST_WRITE_RC=%s\n" "$?"'
printf '\n=== REGLAS Y LIMPIEZA (SOLO LINEAS ESPECIFICAS) ===\n'
sudo -n su -c 'grep -E "^[[:space:]]*(<FilesMatch|</FilesMatch>|Require all denied)" /etc/httpd/conf.d/zz-hardening-personal.conf; grep -E "^[[:space:]]*(ErrorDocument[[:space:]]|Redirect[[:space:]])" /etc/httpd/conf/httpd.conf /etc/httpd/conf.d/infra.personal.com.py.conf'
date --iso-8601=seconds
