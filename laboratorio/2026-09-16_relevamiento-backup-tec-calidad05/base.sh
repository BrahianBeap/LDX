hostname && whoami
printf '\n=== IDENTIDAD ===\n'
hostname -f
hostname -I
date --iso-8601=seconds
cat /etc/centos-release
uname -r
uptime
systemd-detect-virt
printf '\n=== CPU ===\n'
lscpu
nproc
vmstat 1 5
if command -v mpstat >/dev/null 2>&1; then mpstat 1 3; fi
printf '\n=== HISTORIAL ===\n'
if command -v sar >/dev/null 2>&1; then sar -u; else printf 'N/D: sar no instalado\n'; fi
printf '\n=== MEMORIA ===\n'
free -b
vmstat -s
printf '\n=== DISCOS ===\n'
lsblk -b -o NAME,TYPE,SIZE,FSTYPE,MOUNTPOINT
findmnt -rn -o SOURCE,FSTYPE,TARGET
df -B1 -P -T
df -Pi
printf '\n=== SERVICIOS ===\n'
systemctl list-units --type=service --state=running --no-pager --no-legend
printf '\n=== PROCESOS ===\n'
ps -eo pid,user,comm,%cpu,%mem,rss --sort=-rss
printf '\n=== PUERTOS ===\n'
ss -lnt
printf '\n=== APACHE ===\n'
httpd -S
printf '\n=== DIRECTORIOS ===\n'
find /var/www /opt /srv -maxdepth 2 -type d 2>&1
