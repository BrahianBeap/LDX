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
printf '\n=== READONLY ===\n'
query postgres "SELECT current_setting('default_transaction_read_only'), current_setting('transaction_read_only'), current_setting('statement_timeout');" || exit 1
printf '\n=== NOMBRES ===\n'
query postgres "SELECT datname FROM pg_database WHERE lower(datname) IN (lower('Infraestructura'),lower('Infra_restore'),lower('postgres'),lower('vulnerabilidad')) ORDER BY datname;" || exit 1
printf '\n=== TAMANOS ===\n'
query postgres "SELECT datname AS base_datos, pg_database_size(datname) AS bytes, round(pg_database_size(datname)::numeric / 1073741824,2) AS gib FROM pg_database WHERE lower(datname) IN (lower('Infraestructura'),lower('Infra_restore'),lower('postgres'),lower('vulnerabilidad')) ORDER BY datname;" || exit 1
