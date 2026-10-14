printf '\n=== ARCHIVO REAL ===\n'
curl --silent --show-error --max-time 10 --head --resolve infra.personal.com.py:443:127.0.0.1 'https://infra.personal.com.py/backup_pg/backup_Infraestructura_20260916_000001.sql' | awk '/^HTTP\// {print} tolower($1)=="location:" {split($2,a,"?");print "Location:",a[1]}'
printf '\n=== DESTINO DE REDIRECCION ===\n'
curl --silent --show-error --max-time 10 --head --resolve infra.personal.com.py:443:127.0.0.1 'https://infra.personal.com.py/INFRAWORK/error.php' | awk '/^HTTP\// {print} tolower($1)=="location:" {split($2,a,"?");print "Location:",a[1]}'
printf '\n=== ERROR DOCUMENT ===\n'
grep -E '^[[:space:]]*ErrorDocument[[:space:]]' /etc/httpd/conf/httpd.conf /etc/httpd/conf.d/*.conf
