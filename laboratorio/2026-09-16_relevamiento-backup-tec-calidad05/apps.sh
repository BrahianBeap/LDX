printf '\n=== FECHA ===\n'
date --iso-8601=seconds
printf '\n=== SERVICIOS APLICACION ===\n'
systemctl show vulnapp httpd mariadb postgresql-10 -p Id -p MainPID -p WorkingDirectory -p ControlGroup -p FragmentPath -p MemoryAccounting -p MemoryCurrent -p CPUAccounting -p CPUUsageNSec
systemctl list-unit-files --type=service --no-pager | grep -Ei 'adm|infra|vuln|python|flask|httpd|php|postgres|maria'
printf '\n=== APACHE ===\n'
/usr/sbin/httpd -S
printf '\n=== PUERTOS ===\n'
/usr/sbin/ss -lnt
printf '\n=== RUTAS ===\n'
find /var/www/html/adm /var/www/html/INFRAWORK /var/www/html/vulnapp -maxdepth 2 -type d
printf '\n=== INDICIOS TECNOLOGIA (SOLO NOMBRES) ===\n'
find /var/www/html/adm /var/www/html/INFRAWORK /var/www/html/vulnapp -maxdepth 1 -type f -printf '%p\n'
printf '\n=== TAMANOS ===\n'
du -x -B1 --max-depth=1 /var/www/html/adm /var/www/html/INFRAWORK /var/www/html/vulnapp
printf '\n=== DATOS Y LOGS ===\n'
ls -ld /var/lib/mysql /var/lib/pgsql /var/lib/pgsql/10/data /var/log/httpd /var/log/mariadb
du -x -s -B1 /var/lib/mysql /var/lib/pgsql /var/log/httpd /var/log/mariadb
printf '\n=== MONTAJES APPS ===\n'
df -B1 -P /var/www/html/adm /var/www/html/INFRAWORK /var/www/html/vulnapp
printf '\n=== PAQUETES ===\n'
rpm -q httpd php php-cli mariadb-server postgresql10-server python python-flask
printf '\n=== CPU PROCESOS INTERVALO ===\n'
if command -v pidstat >/dev/null 2>&1; then pidstat -u -r -C 'python|httpd|mysqld|postmaster' 1 3; fi
