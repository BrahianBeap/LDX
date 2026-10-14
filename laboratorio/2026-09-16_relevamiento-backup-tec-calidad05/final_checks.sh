date --iso-8601=seconds
printf '\n=== VULNAPP INTERVALO ===\n'
pidstat -u -r -p 6366 1 3
printf '\n=== OTROS DIRECTORIOS IDENTIFICADOS ===\n'
du -x -s -B1 /var/www/html/backup_pg /var/www/html/infrafilerun /var/www/html/subirArchivos
printf '\n=== LOGS CONCRETOS ===\n'
du -x -s -B1 /var/www/html/INFRAWORK/logs /var/www/html/INFRAWORK/garbage-test/log
printf '\n=== SERVICIOS ===\n'
for unit in httpd.service mariadb.service postgresql-10.service; do systemctl show "$unit" -p Id -p MainPID -p WorkingDirectory -p ControlGroup; done
printf '\n=== NOMBRES APLICACIONES ===\n'
find /var/www /opt /srv -maxdepth 4 -type d \( -iname '*adm*' -o -iname '*infra*' -o -iname '*vuln*' \)
printf '\n=== FECHA FIN ===\n'
date --iso-8601=seconds
