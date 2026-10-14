PYTHONIOENCODING=utf-8 python - <<'PY'
import subprocess,re,glob,os
def inspect(label,args,cron=False):
 p=subprocess.Popen(args,stdout=subprocess.PIPE,stderr=subprocess.PIPE);out,err=p.communicate()
 print('\n=== '+label+' RC='+str(p.returncode)+' ===')
 if p.returncode: print('Sin acceso para verificacion');return
 for line in out.decode('utf-8','replace').splitlines():
  line=line.strip()
  if not line or line.startswith('#'):continue
  if cron:
   fields=line.split()
   if len(fields)>=6:print('Horario: '+' '.join(fields[:5]))
  secret=bool(re.search(r'(?i)pass|secret|token|://[^\s]+:[^\s]+@',line))
  if secret:print('[SECRETO REDACTADO] posible credencial o mecanismo de autenticacion en linea; no se imprime su valor')
  paths=re.findall(r'(?<![\w])/(?:usr|bin|sbin|var|opt|home|root|etc)/[A-Za-z0-9_./-]+',line)
  print('Rutas: '+ ' '.join(paths))
  print('Indicadores: '+','.join(x for x in ['pg_dump','Infraestructura','postgres','flock','find','mtime','delete','logger','pg_restore','sha256sum','set -e','pipefail'] if x in line))
  if not secret: print('Linea: '+line)
for path in ['/opt/backup_potsgres.sh','/var/lib/pgsql/10/backups/backup_infra.sh','/var/lib/pgsql/10/backups/restore.sh','/etc/cron.d/sysstat','/etc/anacrontab']:
 inspect(path,['sudo','-n','cat',path])
PY
printf '\n=== HTTPS SNI LOCAL ===\n'
for path in /backup_pg/ /backup_pg/backup_Infraestructura_20260916_000001.sql; do
printf '%s ' "$path"
curl --silent --show-error --max-time 10 --output /dev/null --write-out '%{http_code}\n' --head --resolve infra.personal.com.py:443:127.0.0.1 "https://infra.personal.com.py$path"
printf 'CURL_RC=%s\n' "$?"
done
printf '\n=== DEFAULT CLIENT ===\n'
/usr/bin/pg_dump --version
/usr/bin/pg_restore --version
/usr/sbin/getenforce

printf '\n=== HEAD REDIRECT METADATA ===\n'
curl --silent --show-error --max-time 10 --head --resolve infra.personal.com.py:443:127.0.0.1 'https://infra.personal.com.py/backup_pg/backup_Infraestructura_20260916_000001.sql' | awk 'tolower($1)=="location:" {split($2,a,"?");print "Location:",a[1]} /^HTTP\// {print}'
printf '\n=== ACCESS MATCH RULES ===\n'
grep -Ei '^[[:space:]]*(</?(LocationMatch|FilesMatch|DirectoryMatch)|Require|AuthType|AuthName)' /etc/httpd/conf.d/zz-hardening-personal.conf
