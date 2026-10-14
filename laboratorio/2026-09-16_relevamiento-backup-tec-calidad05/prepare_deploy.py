from pathlib import Path
import base64,hashlib,shlex
r=Path(__file__).resolve().parent
data=(r/'propuesta_backup_admtech(1).sh').read_bytes()
payload=base64.b64encode(data).decode()
digest=hashlib.sha256(data).hexdigest()
script=r'''set -euo pipefail
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
printf '%s' '__PAYLOAD__' | base64 -d > "$tmp_script"
bash -n "$tmp_script"
test "$(sha256sum "$tmp_script" | cut -d' ' -f1)" = '__DIGEST__'
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
'''.replace('__PAYLOAD__',payload).replace('__DIGEST__',digest)
(r/'deploy_install.sh').write_text('sudo -n su -c '+shlex.quote('bash -c '+shlex.quote(script))+'\n',encoding='utf-8')
print('SHA256 local:',digest)
