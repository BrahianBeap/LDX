date --iso-8601=seconds
printf '\n=== REPOSITORIO ===\n'
du -x -B1 --max-depth=2 /var/www/html/infrafilerun
printf '\n=== BACKUPS METADATOS ===\n'
find /var/www/html/backup_pg -xdev -printf '%y|%s|%b|%n|%D:%i|%TY-%Tm-%TdT%TH:%TM:%TS|%p\n'
date --iso-8601=seconds
