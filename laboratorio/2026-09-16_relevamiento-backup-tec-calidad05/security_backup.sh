python - <<'PY'
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
inspect('CRON ROOT',['sudo','-n','crontab','-u','root','-l'],True)
inspect('CRON POSTGRES',['sudo','-n','crontab','-u','postgres','-l'],True)
inspect('SPOOL POSTGRES',['sudo','-n','cat','/var/spool/cron/postgres'],True)
for path in glob.glob('/etc/cron.d/*')+['/etc/crontab','/etc/anacrontab']:
 inspect(path,['cat',path],True)
print('\n=== REGLAS APACHE SELECCIONADAS ===')
for path in ['/etc/httpd/conf/httpd.conf']+glob.glob('/etc/httpd/conf.d/*.conf')+['/var/www/html/.htaccess','/var/www/html/backup_pg/.htaccess']:
 try:
  with open(path) as f:
   for num,line in enumerate(f,1):
    if re.match(r'^\s*(?:</?(?:Directory|Location|Files|VirtualHost)\b|DocumentRoot\b|Alias\b|Require\b|AllowOverride\b|Options\b|Order\b|Deny\b|Allow\b|Redirect\b)',line,re.I):
     if re.search(r'(?i)password|secret|token|://[^\s]+:[^\s]+@',line):line='[SECRETO REDACTADO]\n'
     print(path+':'+str(num)+': '+line.strip())
 except IOError as e:print(path+': No disponible ('+str(e.errno)+')')
PY
printf '\n=== HEAD HTTP ===\n'
for path in /backup_pg/ /backup_pg/backup_Infraestructura_20260916_000001.sql; do
printf '%s ' "$path"
curl --silent --show-error --max-time 10 --output /dev/null --write-out '%{http_code}\n' --head --header 'Host: infra.personal.com.py' "http://127.0.0.1$path"
printf 'CURL_RC=%s\n' "$?"
done
printf '\n=== HEAD HTTPS ===\n'
for path in /backup_pg/ /backup_pg/backup_Infraestructura_20260916_000001.sql; do
printf '%s ' "$path"
curl --silent --show-error --max-time 10 --output /dev/null --write-out '%{http_code}\n' --head --header 'Host: infra.personal.com.py' "https://127.0.0.1$path"
printf 'CURL_RC=%s\n' "$?"
done
printf '\n=== DAC APACHE ===\n'
id apache
namei -om /var/www/html/backup_pg/backup_Infraestructura_20260916_000001.sql
getenforce
