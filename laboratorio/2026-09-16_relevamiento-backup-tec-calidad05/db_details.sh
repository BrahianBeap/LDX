date --iso-8601=seconds
umask 077
pgdir=$(mktemp -d) || exit 1
cleanup() {
  rm -f -- "$pgdir/.pgpass"
  if test ! -e "$pgdir/.pgpass"; then printf '\nPGPASS_ELIMINADO=SI\n'; else printf '\nPGPASS_ELIMINADO=NO\n'; fi
  rmdir -- "$pgdir"
}
trap cleanup EXIT
trap 'exit 130' INT TERM HUP
IFS= read -r pgline || exit 1
printf '%s\n' "$pgline" > "$pgdir/.pgpass"
unset pgline
chmod 600 "$pgdir/.pgpass"
psqlbin=$(command -v psql)
if test -z "$psqlbin"; then psqlbin=/usr/pgsql-10/bin/psql; fi
query() {
  PGPASSFILE="$pgdir/.pgpass" PGOPTIONS='-c default_transaction_read_only=on -c statement_timeout=30000' "$psqlbin" -X -w -v ON_ERROR_STOP=1 -h 127.0.0.1 -p 5432 -U postgres -d "$1" -A -F '|' -c "$2"
}

for database in Infraestructura postgres vulnerabilidad; do
  printf '\n=== DATABASE %s ===\n' "$database"
  query "$database" "SELECT current_database(),current_setting('transaction_read_only'),current_setting('statement_timeout'),pg_database_size(current_database()) AS total_bytes;" || exit 1
  query "$database" "SELECT COALESCE(sum(pg_table_size(c.oid)),0) AS tablas_bytes,COALESCE(sum(pg_indexes_size(c.oid)),0) AS indices_bytes FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace WHERE c.relkind IN ('r','m') AND n.nspname NOT IN ('pg_catalog','information_schema') AND n.nspname !~ '^pg_toast' AND n.nspname !~ '^pg_temp';" || exit 1
  query "$database" "SELECT n.nspname AS esquema, sum(pg_table_size(c.oid)) AS tablas_bytes,sum(pg_indexes_size(c.oid)) AS indices_bytes,sum(pg_total_relation_size(c.oid)) AS total_bytes FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace WHERE c.relkind IN ('r','m') AND n.nspname NOT IN ('pg_catalog','information_schema') AND n.nspname !~ '^pg_toast' AND n.nspname !~ '^pg_temp' GROUP BY n.nspname ORDER BY total_bytes DESC;" || exit 1
  query "$database" "SELECT n.nspname AS esquema,c.relname AS tabla,pg_total_relation_size(c.oid) AS bytes FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace WHERE c.relkind IN ('r','m') AND n.nspname NOT IN ('pg_catalog','information_schema') AND n.nspname !~ '^pg_toast' AND n.nspname !~ '^pg_temp' ORDER BY bytes DESC,n.nspname,c.relname LIMIT 10;" || exit 1
done
date --iso-8601=seconds
