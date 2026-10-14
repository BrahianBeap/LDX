sudo -n su -c 'bash -c '"'"'set -euo pipefail
test ! -e /etc/cron.d/backup-admtech
test ! -L /etc/cron.d/backup-admtech
test "$(find /var/backups/postgresql/admtech -maxdepth 1 -type f -name '"'"'"'"'"'"'"'"'admtech_postgres_*.dump'"'"'"'"'"'"'"'"' -printf '"'"'"'"'"'"'"'"'.'"'"'"'"'"'"'"'"' | wc -c)" = 1
test "$(find /var/backups/postgresql/admtech -maxdepth 1 -type f -name '"'"'"'"'"'"'"'"'admtech_postgres_*.dump.sha256'"'"'"'"'"'"'"'"' -printf '"'"'"'"'"'"'"'"'.'"'"'"'"'"'"'"'"' | wc -c)" = 1
test "$(stat -c '"'"'"'"'"'"'"'"'%U:%G:%a'"'"'"'"'"'"'"'"' /var/backups/postgresql/admtech/admtech_postgres_20260916T141126Z.dump)" = postgres:postgres:600
test "$(stat -c '"'"'"'"'"'"'"'"'%U:%G:%a'"'"'"'"'"'"'"'"' /var/backups/postgresql/admtech/admtech_postgres_20260916T141126Z.dump.sha256)" = postgres:postgres:600
test "$(df -B1 --output=avail /var/backups/postgresql/admtech | tail -n 1)" -ge 5368709120
systemctl is-active crond
systemctl is-enabled crond
umask 077
cron_tmp=$(mktemp /etc/cron.d/.backup-admtech.XXXXXXXX)
trap '"'"'"'"'"'"'"'"'rm -f -- "$cron_tmp"'"'"'"'"'"'"'"'"' EXIT
printf '"'"'"'"'"'"'"'"'%s'"'"'"'"'"'"'"'"' '"'"'"'"'"'"'"'"'U0hFTEw9L2Jpbi9iYXNoClBBVEg9L3Vzci9wZ3NxbC0xMC9iaW46L3Vzci9sb2NhbC9zYmluOi91c3IvYmluOi9iaW4KTUFJTFRPPXJvb3QKCjMwIDIgKiAqICogcG9zdGdyZXMgL3Vzci9sb2NhbC9zYmluL2JhY2t1cF9hZG10ZWNoLnNoCg=='"'"'"'"'"'"'"'"' | base64 -d > "$cron_tmp"
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
printf '"'"'"'"'"'"'"'"'NEXT_RUN_LOCAL='"'"'"'"'"'"'"'"'
date -d '"'"'"'"'"'"'"'"'tomorrow 02:30'"'"'"'"'"'"'"'"' --iso-8601=seconds
timedatectl
printf '"'"'"'"'"'"'"'"'\n=== BACKUP LOG ===\n'"'"'"'"'"'"'"'"'
journalctl -t backup-admtech --since '"'"'"'"'"'"'"'"'2026-09-16 11:11:00'"'"'"'"'"'"'"'"' --no-pager -o short-iso
'"'"''
