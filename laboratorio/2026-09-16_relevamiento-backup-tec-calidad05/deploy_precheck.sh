hostname
whoami
sudo -n su -c 'id; whoami; for p in /var/backups/postgresql/admtech /usr/local/sbin/backup_admtech.sh /etc/cron.d/backup-admtech; do if test -e "$p" || test -L "$p"; then printf "EXISTE %s\n" "$p"; else printf "AUSENTE %s\n" "$p"; fi; done; df -B1 -P /var/backups; date --iso-8601=seconds'
