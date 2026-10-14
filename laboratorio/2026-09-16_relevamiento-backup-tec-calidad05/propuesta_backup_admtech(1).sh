#!/bin/bash
# Backup ADM-TECH autorizado 2026-09-16; ejecucion diaria 02:30 local.
# Destino separado de backup_pg para conservar 30 dias sin limpieza ajena.
set -Eeuo pipefail
umask 077
PATH=/usr/pgsql-10/bin:/usr/bin:/bin
export PATH
readonly DEST=/var/backups/postgresql/admtech
readonly PGDUMP=/usr/pgsql-10/bin/pg_dump
readonly PGRESTORE=/usr/pgsql-10/bin/pg_restore
readonly MIN_FREE=5368709120
readonly RETENTION_MINUTES=43200
tmp=''
checksum_tmp=''
log() { /usr/bin/logger -t backup-admtech -- "$*"; }
cleanup() {
    local rc=$?
    trap - EXIT
    [[ -z "$tmp" ]] || rm -f -- "$tmp"
    [[ -z "$checksum_tmp" ]] || rm -f -- "$checksum_tmp"
    if (( rc != 0 )); then log "ERROR backup incompleto; codigo=$rc" || true; fi
    exit "$rc"
}
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM HUP
[[ $(id -un) == postgres ]] || { log 'ERROR requiere usuario Linux postgres'; exit 1; }
[[ -d "$DEST" && ! -L "$DEST" && -w "$DEST" ]] || { log 'ERROR destino ausente o no escribible'; exit 1; }
[[ $(stat -c %U "$DEST") == postgres && $(stat -c %a "$DEST") == 700 ]] || { log 'ERROR destino requiere propietario postgres y modo 700'; exit 1; }
# Retirar variables PostgreSQL heredadas; autenticacion local validada.
unset PGPASSWORD PGPASSFILE PGSERVICE PGSERVICEFILE
unset PGHOST PGHOSTADDR PGPORT PGDATABASE PGUSER PGOPTIONS
exec 9>"$DEST/.backup_admtech.lock"
if ! /usr/bin/flock -n 9; then log 'OMITIDO otra instancia mantiene el bloqueo'; exit 1; fi
free_bytes=$(df -B1 --output=avail "$DEST" | tail -n 1)
[[ "$free_bytes" =~ ^[[:space:]]*[0-9]+[[:space:]]*$ ]] || exit 1
(( free_bytes >= MIN_FREE )) || { log 'ERROR menos de 5 GiB disponibles'; exit 1; }
stamp=$(date -u +%Y%m%dT%H%M%SZ)
name="admtech_postgres_${stamp}.dump"
[[ ! -e "$DEST/$name" && ! -e "$DEST/$name.sha256" ]] || exit 1
tmp=$(mktemp "$DEST/.admtech_dump.XXXXXXXX")
checksum_tmp=$(mktemp "$DEST/.admtech_sha256.XXXXXXXX")
log "INICIO base=postgres archivo=$name"
"$PGDUMP" --no-password --username=postgres --dbname=postgres --port=5432 \
    --format=custom --compress=6 --lock-wait-timeout=60s --file="$tmp"
[[ -s "$tmp" ]] || { log 'ERROR dump vacio'; exit 1; }
"$PGRESTORE" --list "$tmp" >/dev/null
digest=$(/usr/bin/sha256sum "$tmp")
digest=${digest%% *}
printf '%s  %s\n' "$digest" "$name" > "$checksum_tmp"
# Cada archivo se publica atómicamente en el mismo sistema de archivos.
mv -- "$tmp" "$DEST/$name"
tmp=''
mv -- "$checksum_tmp" "$DEST/$name.sha256"
checksum_tmp=''
(cd "$DEST" && /usr/bin/sha256sum --check --status "$name.sha256")
# Limpiar solo pares propios, después de publicar y verificar un nuevo respaldo.
while IFS= read -r -d '' expired; do
    base=${expired##*/}
    [[ "$base" =~ ^admtech_postgres_[0-9]{8}T[0-9]{6}Z\.dump$ ]] || continue
    [[ -f "$expired.sha256" && ! -L "$expired.sha256" ]] || continue
    rm -- "$expired" "$expired.sha256"
done < <(find "$DEST" -maxdepth 1 -type f -name 'admtech_postgres_*.dump' -mmin +"$RETENTION_MINUTES" -print0)
log "OK base=postgres archivo=$name bytes=$(stat -c %s "$DEST/$name")"
