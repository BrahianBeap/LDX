# Evidencias de relevamiento: tec-calidad05

Fecha inicial del servidor: 2026-09-16T09:25:10-0300. Las fechas de cada etapa figuran en las salidas. Lectura con alfonzel_opr, sin sudo, sin instalaciones, cambios de configuración ni archivos remotos.

## Identidad y acceso

Primer comando remoto: `hostname && whoami`. Resultado validado: `tec-calidad05` y `alfonzel_opr`. Hubo un intento previo rechazado por autenticación; se corrigió la construcción local del helper y se validó antes del relevamiento.
OpenSSH directo desde Git Bash, SSH_ASKPASS_REQUIRE=force, StrictHostKeyChecking=yes, ControlMaster=no y ControlPath=none. Contraseña recibida desde el adjunto en memoria, pasada por entorno al proceso de cada comando, nunca incluida en argumentos ni archivos. Helper askpass.sh en mktemp con modo 700, shebang y printf literal, eliminado por trap junto al directorio temporal. Los procesos locales que manejaron la variable terminaron.

## Resultados y cálculos

- VM VMware; kernel 3.10.0-1062.18.1.el7.x86_64. CPU expuesta al invitado: 4 sockets × 1 núcleo × 1 hilo = 4 vCPU. No describe la topología física del host VMware.
- CPU puntual: 100 − 99.08 idle = 0.92%, mostrado 0.9%, mpstat entre 09:25:14 y 09:25:17. Cargas 1/5/15 min: 0.05/0.05/0.05.
- CPU histórica accesible: sar del día 16/09/2026, intervalo 00:00:01–09:20:01, muestreo aproximadamente cada 10 minutos. 100 − 99.43 = 0.57%, mostrado 0.6%. No representa semanas, meses ni picos fuera de esa ventana.
- RAM visible al SO: 8201240576 bytes = 7.64 GiB. Usada según free: 2015776768 = 1.88 GiB (24.6%). Disponible: 5266776064 = 4.91 GiB. Libre: 162037760 bytes. buff/cache: 6023426048 bytes. `used = total − free − buff/cache`; no sumar caché como uso exclusivo de aplicaciones. La métrica alternativa total−available da 35.8%, no se mezcla con used en el CSV. Capacidad física del host y DIMM: N/D.
- Swap: 2.00 GiB total, 0.21 GiB usada (10.7%). vmstat no mostró actividad si/so en los intervalos observados; ocupación de swap no equivale a presión actual.
- GiB = bytes / 1073741824. RAM de procesos MiB = RSS KiB / 1024. Dos decimales para tamaños, un decimal para porcentajes. Valores menores de 0.005 GiB redondean a 0.00 y no implican ausencia de datos.
- Sistemas de archivos locales reales únicos: / y /boot. Total 746.98 GiB, usado 663.48 GiB, disponible 83.50 GiB, uso 88.8%. Sin montajes remotos identificados. Pseudo FS y tmpfs excluidos del detalle y suma.
- ALERTA raíz: 88.9% ocupado, 82.79 GiB disponibles. df redondea a 89%; el CSV calcula usado/capacidad con bytes. /boot: 28.3%. Inodos: 2% y 1% reportados por df (redondeados hacia arriba), sin alerta.
- Discos virtuales sda: 750.00 GiB; sdb: 260.00 GiB. Total discos principales provisionados: 1010.00 GiB. No se suma con particiones/LVM. LV raíz: 746.00 GiB; LV swap: 2.00 GiB; /boot: partición 1.00 GiB. La diferencia respecto a discos no demuestra espacio libre del VG: estado de PV/VG no comprobado. fd0 y sr0 son dispositivos auxiliares, excluidos del total principal.

## Aplicaciones y límites de atribución

Infrawork: directorio /var/www/html/INFRAWORK con archivos PHP. VulnApp: servicio activo, PID 6366 Python y WorkingDirectory /var/www/html/vulnapp. Flask está instalado, pero no se leyó código ni configuración para confirmar su uso por ese proceso.

ADM-TECH: **No identificada en este servidor; ubicación pendiente de confirmación**. /var/www/html/adm es candidato; el nombre abreviado no prueba equivalencia. Se incluye como componente separado, sin atribución definitiva.

Apache activo con virtual host infra.personal.com.py en 80/443 y DocumentRoot principal /var/www/html. Las asociaciones de directorios PHP con Apache son inferencias por ubicación, no pruebas de rutas HTTP individuales. No se hicieron solicitudes a las aplicaciones. Apache es compartido: no se distribuye RAM/CPU entre aplicaciones.

Tamaños du: bloques ocupados, sin seguir enlaces, restringidos al mismo filesystem (-x). Totales de aplicaciones incluyen código, dependencias, archivos, configuraciones y copias; no equivalen a código puro ni a consumo de RAM/CPU. Clasificación de archivos/uploads por nombres de directorios, no inspección de datos. INFRAWORK/Ejemplos_fileinput contiene componentes mixtos, por lo que no se declara como documentos puros. No sumar totales de directorios con sus subdirectorios.

MariaDB y PostgreSQL están activos; no se pudo confirmar relación con bases específicas de las aplicaciones sin leer configuraciones sensibles. No se accedió a ninguna BD. Tamaños de motores, datos y logs restringidos: **Sin acceso con alfonzel_opr**. Las cifras parciales emitidas por du en /var/lib/mysql, /var/lib/pgsql, /var/log/httpd y /var/log/mariadb se descartan, no son totales válidos. MemoryAccounting/CPUAccounting de VulnApp desactivados: el valor centinela MemoryCurrent no es RAM usada. RSS de procesos compartidos puede duplicar páginas compartidas; no es PSS. %CPU de ps es promedio durante vida del proceso y no se utiliza como CPU puntual.

## Recomendaciones para completar la planilla

Priorizar revisión autorizada del crecimiento y retención de archivos en / por superar 80%; este relevamiento no elimina nada. Confirmar con el responsable si /adm corresponde a ADM-TECH. Solicitar al DBA tamaños por base y asociaciones, y a administradores totales de directorios restringidos. Separar inventario de código, adjuntos, logs y copias con responsables; no inferirlo solo por tamaño. Complementar con historial representativo de días/semanas y horas pico antes de dimensionar. Capacidad asignada, consumo puntual e histórico son magnitudes distintas.

## Comandos remotos ejecutados

Se enviaron como texto por SSH, sin crear scripts en el servidor. ss/httpd inicialmente no estaban en PATH: se ejecutaron después con /usr/sbin. No se leyeron fuentes, credenciales, unidades completas ni archivos de conexión.

### base

```bash
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
```

### apps

```bash
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
```

### final_checks

```bash
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
```

## Salidas relevantes depuradas

### Base

```text
tec-calidad05
alfonzel_opr

=== IDENTIDAD ===
tec-calidad05
10.129.2.165 192.168.122.1 
2026-09-16T09:25:10-0300
CentOS Linux release 7.7.1908 (Core)
3.10.0-1062.18.1.el7.x86_64
 09:25:10 up 65 days, 16:01,  2 users,  load average: 0,05, 0,05, 0,05
vmware

=== CPU ===
Architecture:          x86_64
CPU op-mode(s):        32-bit, 64-bit
Byte Order:            Little Endian
CPU(s):                4
On-line CPU(s) list:   0-3
Thread(s) per core:    1
Core(s) per socket:    1
Socket(s):             4
NUMA node(s):          1
Vendor ID:             GenuineIntel
CPU family:            6
Model:                 37
Model name:            Intel(R) Xeon(R) CPU E5-2698 v4 @ 2.20GHz
Stepping:              1
CPU MHz:               2197.454
BogoMIPS:              4394.90
Hypervisor vendor:     VMware
Virtualization type:   full
L1d cache:             32K
L1i cache:             32K
L2 cache:              256K
L3 cache:              51200K
NUMA node0 CPU(s):     0-3
Flags:                 fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pat pse36 clflush mmx fxsr sse sse2 ss syscall nx rdtscp lm constant_tsc arch_perfmon nopl xtopology tsc_reliable nonstop_tsc eagerfpu pni pclmulqdq ssse3 cx16 sse4_1 sse4_2 x2apic popcnt tsc_deadline_timer aes hypervisor lahf_lm ssbd ibrs ibpb stibp tsc_adjust arat spec_ctrl intel_stibp flush_l1d arch_capabilities
4
procs -----------memory---------- ---swap-- -----io---- -system-- ------cpu-----
 r  b   swpd   free   buff  cache   si   so    bi    bo   in   cs us sy id wa st
 1  0 223608 160592      0 5880416    0    0    33    19    2    1  1  0 99  0  0
 0  0 223608 160812      0 5880664    0    0     0     0  532  561  2  1 97  0  0
 0  0 223608 160896      0 5880664    0    0     0     0  310  281  0  0 100  0  0
 0  0 223608 159404      0 5882200    0    0  1452   756  726  358  0  1 98  0  0
 0  0 223608 159404      0 5882196    0    0     0     0  181  207  0  0 100  0  0
Linux 3.10.0-1062.18.1.el7.x86_64 (tec-calidad05) 	16/09/26 	_x86_64_	(4 CPU)

09:25:14     CPU    %usr   %nice    %sys %iowait    %irq   %soft  %steal  %guest  %gnice   %idle
09:25:15     all    1,25    0,00    0,00    0,00    0,00    0,00    0,00    0,00    0,00   98,75
09:25:16     all    0,00    0,00    0,25    0,00    0,00    0,00    0,00    0,00    0,00   99,75
09:25:17     all    1,00    0,00    0,25    0,00    0,00    0,00    0,00    0,00    0,00   98,75
Media:       all    0,75    0,00    0,17    0,00    0,00    0,00    0,00    0,00    0,00   99,08

=== HISTORIAL ===
Linux 3.10.0-1062.18.1.el7.x86_64 (tec-calidad05) 	16/09/26 	_x86_64_	(4 CPU)

00:00:01        CPU     %user     %nice   %system   %iowait    %steal     %idle
00:10:01        all      5,71      0,00      0,42      0,00      0,00     93,87
00:20:01        all      0,20      0,00      0,12      0,00      0,00     99,68
00:30:01        all      0,19      0,00      0,11      0,00      0,00     99,69
00:40:01        all      0,20      0,00      0,12      0,00      0,00     99,68
00:50:01        all      0,20      0,00      0,12      0,00      0,00     99,68
01:00:01        all      0,19      0,00      0,11      0,00      0,00     99,69
01:10:01        all      0,20      0,00      0,12      0,00      0,00     99,68
01:20:01        all      0,20      0,00      0,11      0,00      0,00     99,68
01:30:01        all      0,20      0,00      0,12      0,00      0,00     99,69
01:40:01        all      0,20      0,00      0,12      0,00      0,00     99,68
01:50:01        all      0,20      0,00      0,12      0,00      0,00     99,68
02:00:01        all      0,19      0,00      0,12      0,00      0,00     99,69
02:10:01        all      0,20      0,00      0,13      0,00      0,00     99,67
02:20:01        all      0,20      0,00      0,11      0,00      0,00     99,69
02:30:01        all      0,19      0,00      0,11      0,00      0,00     99,70
02:40:01        all      0,20      0,00      0,12      0,00      0,00     99,68
02:50:01        all      0,20      0,00      0,11      0,00      0,00     99,69
03:00:01        all      0,20      0,00      0,12      0,00      0,00     99,69
03:10:01        all      0,20      0,00      0,13      0,00      0,00     99,67
03:20:01        all      0,20      0,00      0,11      0,00      0,00     99,69
03:30:01        all      0,19      0,16      1,81      0,00      0,00     97,84
03:40:01        all      0,21      0,00      0,13      0,00      0,00     99,66
03:50:01        all      0,20      0,00      0,12      0,00      0,00     99,69
04:00:02        all      0,20      0,00      0,11      0,00      0,00     99,69
04:10:01        all      0,21      0,00      0,13      0,00      0,00     99,65
04:20:01        all      0,20      0,00      0,12      0,00      0,00     99,69
04:30:01        all      0,20      0,00      0,12      0,00      0,00     99,68
04:40:01        all      0,20      0,00      0,12      0,00      0,00     99,68
04:50:01        all      0,20      0,00      0,11      0,00      0,00     99,69
05:00:01        all      0,19      0,00      0,11      0,00      0,00     99,69
05:10:01        all      0,21      0,00      0,12      0,00      0,00     99,67
05:20:01        all      0,20      0,00      0,11      0,00      0,00     99,69
05:30:01        all      0,21      0,00      0,13      0,00      0,00     99,66
05:40:02        all      0,34      0,00      0,18      0,00      0,00     99,48
05:50:02        all      0,20      0,00      0,11      0,00      0,00     99,69
06:00:02        all      0,19      0,00      0,11      0,00      0,00     99,69
06:10:02        all      0,20      0,00      0,12      0,00      0,00     99,68
06:20:01        all      0,20      0,00      0,12      0,00      0,00     99,68
06:30:01        all      0,20      0,00      0,12      0,00      0,00     99,69
06:40:01        all      0,20      0,00      0,12      0,00      0,00     99,68
06:50:01        all      0,20      0,00      0,12      0,00      0,00     99,69
07:00:01        all      0,20      0,00      0,12      0,00      0,00     99,68
07:10:01        all      0,21      0,00      0,14      0,00      0,00     99,65
07:20:01        all      0,20      0,00      0,12      0,00      0,00     99,69
07:30:01        all      0,20      0,00      0,12      0,00      0,00     99,68
07:40:01        all      0,79      0,00      0,16      0,00      0,00     99,05
07:50:01        all      0,20      0,00      0,12      0,00      0,00     99,68
08:00:01        all      0,69      0,00      0,19      0,00      0,00     99,13
08:10:01        all      0,44      0,00      0,16      0,00      0,00     99,40
08:20:01        all      0,88      0,00      0,20      0,01      0,00     98,91
08:30:01        all      0,23      0,00      0,14      0,00      0,00     99,64
08:40:01        all      0,58      0,00      0,28      0,01      0,00     99,14
08:50:01        all      0,31      0,00      0,16      0,00      0,00     99,53
09:00:01        all      1,78      0,00      0,67      0,05      0,00     97,49
09:10:02        all      0,67      0,00      0,23      0,00      0,00     99,10
09:20:01        all      0,72      0,00      0,25      0,00      0,00     99,02
Media:          all      0,39      0,00      0,18      0,00      0,00     99,43

=== MEMORIA ===
              total        used        free      shared  buff/cache   available
Mem:     8201240576  2015776768   162037760   605442048  6023426048  5266776064
Swap:    2147479552   228974592  1918504960
      8009024 K total memory
      1968940 K used memory
      2811944 K active memory
      2708276 K inactive memory
       157832 K free memory
            0 K buffer memory
      5882252 K swap cache
      2097148 K total swap
       223608 K used swap
      1873540 K free swap
     11917756 non-nice user cpu ticks
        22527 nice user cpu ticks
      4642681 system cpu ticks
   2250042777 idle cpu ticks
       280282 IO-wait cpu ticks
            0 IRQ cpu ticks
       404684 softirq cpu ticks
            0 stolen cpu ticks
    746586568 pages paged in
    430668845 pages paged out
         8489 pages swapped in
        78785 pages swapped out
   1239646147 interrupts
   1319599902 CPU context switches
   1783887816 boot time
      8990553 forks

=== DISCOS ===
NAME            TYPE         SIZE FSTYPE      MOUNTPOINT
fd0             disk         4096             
sda             disk 805306368000             
â”œâ”€sda1          part   1073741824 xfs         /boot
â”œâ”€sda2          part  20400046080 LVM2_member 
â”‚ â”œâ”€centos-root lvm  801007206400 xfs         /
â”‚ â””â”€centos-swap lvm    2147483648 swap        [SWAP]
â””â”€sda3          part 515396075520 LVM2_member 
  â””â”€centos-root lvm  801007206400 xfs         /
sdb             disk 279172874240 LVM2_member 
â””â”€centos-root   lvm  801007206400 xfs         /
sr0             rom    1073741312             
sysfs sysfs /sys
proc proc /proc
devtmpfs devtmpfs /dev
securityfs securityfs /sys/kernel/security
tmpfs tmpfs /dev/shm
devpts devpts /dev/pts
tmpfs tmpfs /run
tmpfs tmpfs /sys/fs/cgroup
cgroup cgroup /sys/fs/cgroup/systemd
pstore pstore /sys/fs/pstore
cgroup cgroup /sys/fs/cgroup/devices
cgroup cgroup /sys/fs/cgroup/memory
cgroup cgroup /sys/fs/cgroup/cpu,cpuacct
cgroup cgroup /sys/fs/cgroup/blkio
cgroup cgroup /sys/fs/cgroup/perf_event
cgroup cgroup /sys/fs/cgroup/pids
cgroup cgroup /sys/fs/cgroup/net_cls,net_prio
cgroup cgroup /sys/fs/cgroup/freezer
cgroup cgroup /sys/fs/cgroup/cpuset
cgroup cgroup /sys/fs/cgroup/hugetlb
configfs configfs /sys/kernel/config
/dev/mapper/centos-root xfs /
selinuxfs selinuxfs /sys/fs/selinux
systemd-1 autofs /proc/sys/fs/binfmt_misc
hugetlbfs hugetlbfs /dev/hugepages
debugfs debugfs /sys/kernel/debug
mqueue mqueue /dev/mqueue
/dev/sda1 xfs /boot
sunrpc rpc_pipefs /var/lib/nfs/rpc_pipefs
tmpfs tmpfs /run/user/42
binfmt_misc binfmt_misc /proc/sys/fs/binfmt_misc
tmpfs tmpfs /run/user/21563
tmpfs tmpfs /run/user/47861
S.ficheros              Tipo     bloques de 1       Usados Disponibles Capacidad Montado en
devtmpfs                devtmpfs   4083376128            0  4083376128        0% /dev
tmpfs                   tmpfs      4100620288         8192  4100612096        1% /dev/shm
tmpfs                   tmpfs      4100620288    421167104  3679453184       11% /run
tmpfs                   tmpfs      4100620288            0  4100620288        0% /sys/fs/cgroup
/dev/mapper/centos-root xfs      800996720640 712104357888 88892362752       89% /
/dev/sda1               xfs        1063256064    301240320   762015744       29% /boot
tmpfs                   tmpfs       820125696        12288   820113408        1% /run/user/42
tmpfs                   tmpfs       820125696            0   820125696        0% /run/user/21563
tmpfs                   tmpfs       820125696            0   820125696        0% /run/user/47861
S.ficheros                Nodos-i NUsados   NLibres NUso% Montado en
devtmpfs                   996918     371    996547    1% /dev
tmpfs                     1001128       2   1001126    1% /dev/shm
tmpfs                     1001128     767   1000361    1% /run
tmpfs                     1001128      16   1001112    1% /sys/fs/cgroup
/dev/mapper/centos-root 175914088 2171473 173742615    2% /
/dev/sda1                  524288     357    523931    1% /boot
tmpfs                     1001128       9   1001119    1% /run/user/42
tmpfs                     1001128       1   1001127    1% /run/user/21563
tmpfs                     1001128       1   1001127    1% /run/user/47861

=== SERVICIOS ===
abrt-oops.service        loaded active running ABRT kernel log watcher
abrt-xorg.service        loaded active running ABRT Xorg log watcher
abrtd.service            loaded active running ABRT Automated Bug Reporting Tool
accounts-daemon.service  loaded active running Accounts Service
atd.service              loaded active running Job spooling tools
auditd.service           loaded active running Security Auditing Service
bolt.service             loaded active running Thunderbolt system service
chronyd.service          loaded active running NTP client/server
colord.service           loaded active running Manage, Install and Generate Color Profiles
crond.service            loaded active running Command Scheduler
cups.service             loaded active running CUPS Printing Service
dbus.service             loaded active running D-Bus System Message Bus
firewalld.service        loaded active running firewalld - dynamic firewall daemon
gdm.service              loaded active running GNOME Display Manager
gssproxy.service         loaded active running GSSAPI Proxy Daemon
httpd.service            loaded active running The Apache HTTP Server
irqbalance.service       loaded active running irqbalance daemon
ksmtuned.service         loaded active running Kernel Samepage Merging (KSM) Tuning Daemon
libstoragemgmt.service   loaded active running libstoragemgmt plug-in server daemon
lvm2-lvmetad.service     loaded active running LVM2 metadata daemon
mariadb.service          loaded active running MariaDB database server
mcelog.service           loaded active running Machine Check Exception Logging Daemon
NetworkManager.service   loaded active running Network Manager
oddjobd.service          loaded active running privileged operations for unprivileged applications
packagekit.service       loaded active running PackageKit Daemon
polkit.service           loaded active running Authorization Manager
postfix.service          loaded active running Postfix Mail Transport Agent
postgresql-10.service    loaded active running PostgreSQL 10 database server
rngd.service             loaded active running Hardware RNG Entropy Gatherer Daemon
rpcbind.service          loaded active running RPC bind service
rsyslog.service          loaded active running System Logging Service
rtkit-daemon.service     loaded active running RealtimeKit Scheduling Policy Service
smartd.service           loaded active running Self Monitoring and Reporting Technology (SMART) Daemon
sshd.service             loaded active running OpenSSH server daemon
sssd.service             loaded active running System Security Services Daemon
systemd-journald.service loaded active running Journal Service
systemd-logind.service   loaded active running Login Service
systemd-machined.service loaded active running Virtual Machine and Container Registration Service
systemd-udevd.service    loaded active running udev Kernel Device Manager
tuned.service            loaded active running Dynamic System Tuning Daemon
upower.service           loaded active running Daemon for power management
vgauthd.service          loaded active running VGAuth Service for open-vm-tools
vmtoolsd.service         loaded active running Service for virtual machines hosted on VMware
vulnapp.service          loaded active running VulnApp
wpa_supplicant.service   loaded active running WPA Supplicant daemon

=== PROCESOS RELEVANTES ===
 1940 mysql    mysqld           0.2  2.9 232660
 6366 apache   python           0.0  1.9 155052
 3252 postgres postmaster       0.0  1.7 141800
 2133 postgres postmaster       0.0  1.7 140108
 2134 postgres postmaster       0.0  1.7 138524
15494 postgres postmaster       0.0  0.4 35816
 2232 postgres postmaster       0.0  0.3 29932
 1498 root     httpd            0.0  0.3 28040
29445 postgres postmaster       0.0  0.3 24844
19199 postgres postmaster       0.0  0.2 23176
24591 apache   httpd            0.6  0.2 22936
23170 apache   httpd            0.0  0.2 22548
23322 apache   httpd            0.0  0.2 21244
22532 apache   httpd            0.0  0.2 20364
23903 apache   httpd            0.0  0.2 18808
24520 apache   httpd            0.2  0.2 18124
 2231 postgres postmaster       0.0  0.2 17968
24607 apache   httpd            0.4  0.2 16224
24690 apache   httpd            0.5  0.2 16068
22626 apache   httpd            0.0  0.1 15704
 2653 postgres postmaster       0.0  0.1 15200
24655 apache   httpd            0.0  0.1 15132
23495 apache   httpd            0.0  0.1 14748
23843 apache   httpd            0.0  0.1 13672
 1491 postgres postmaster       0.0  0.1 11792
19492 postgres postmaster       0.0  0.1 10528
19302 postgres postmaster       0.0  0.1  9996
20452 postgres postmaster       0.0  0.0  6776
19254 postgres postmaster       0.0  0.0  6712
 2136 postgres postmaster       0.0  0.0  6136
 2135 postgres postmaster       0.0  0.0  5192
 2137 postgres postmaster       0.0  0.0  1592
 2139 postgres postmaster       0.0  0.0  1532
 1595 postgres postmaster       0.0  0.0  1064


=== APACHE ===

=== DIRECTORIOS ===
/var/www
/var/www/cgi-bin
/var/www/html
/var/www/html/Sistema
/var/www/html/Proyecto
/var/www/html/portafoox-lite
/var/www/html/subirArchivos
/var/www/html/supportix
/var/www/html/webalizer
/var/www/html/xampp
/var/www/html/INFRAWORK
/var/www/html/test
/var/www/html/quill-1.3.6
/var/www/html/infrafilerun
/var/www/html/adm
/var/www/html/sorteo
/var/www/html/RuletaNucleo
/var/www/html/backup_pg
/var/www/html/vulnapp
/opt
/opt/rh
/opt/sublime_text
/opt/sublime_text/Icon
/opt/sublime_text/Packages
/opt/remi
/opt/remi/php56
/srv

STDERR
** WARNING: connection is not using a post-quantum key exchange algorithm.
** This session may be vulnerable to "store now, decrypt later" attacks.
** The server may need to be upgraded. See https://openssh.com/pq.html
bash: ss: command not found
bash: httpd: command not found

```

### Aplicaciones

```text

=== FECHA ===
2026-09-16T09:25:41-0300

=== SERVICIOS APLICACION ===
MainPID=6366
ControlGroup=/system.slice/vulnapp.service
MemoryCurrent=18446744073709551615
CPUAccounting=no
MemoryAccounting=no
WorkingDirectory=/var/www/html/vulnapp
Id=vulnapp.service
FragmentPath=/etc/systemd/system/vulnapp.service
httpd.service                                 enabled 
initrd-udevadm-cleanup-db.service             static  
mariadb.service                               enabled 
mdadm-grow-continue@.service                  static  
mdadm-last-resort@.service                    static  
postgresql-10.service                         enabled 
rhel-loadmodules.service                      enabled 
vulnapp.service                               enabled 

=== APACHE ===
VirtualHost configuration:
*:80                   infra.personal.com.py (/etc/httpd/conf.d/infra.personal.com.py.conf:1)
*:443                  is a NameVirtualHost
         default server infra.personal.com.py (/etc/httpd/conf.d/infra.personal.com.py.conf:16)
         port 443 namevhost infra.personal.com.py (/etc/httpd/conf.d/infra.personal.com.py.conf:16)
         port 443 namevhost infra.personal.com.py (/etc/httpd/conf.d/ssl.conf:56)
ServerRoot: "/etc/httpd"
Main DocumentRoot: "/var/www/html"
Main ErrorLog: "/etc/httpd/logs/error_log"
Mutex proxy-balancer-shm: using_defaults
Mutex rewrite-map: using_defaults
Mutex authdigest-client: using_defaults
Mutex ssl-stapling: using_defaults
Mutex proxy: using_defaults
Mutex authn-socache: using_defaults
Mutex ssl-cache: using_defaults
Mutex default: dir="/run/httpd/" mechanism=default 
Mutex mpm-accept: using_defaults
Mutex authdigest-opaque: using_defaults
PidFile: "/run/httpd/httpd.pid"
Define: _RH_HAS_HTTPPROTOCOLOPTIONS
Define: DUMP_VHOSTS
Define: DUMP_RUN_CFG
User: name="apache" id=48 not_used
Group: name="apache" id=48 not_used

=== PUERTOS ===
State      Recv-Q Send-Q Local Address:Port               Peer Address:Port              
LISTEN     0      128          *:22                       *:*                  
LISTEN     0      128    127.0.0.1:631                      *:*                  
LISTEN     0      128          *:5432                     *:*                  
LISTEN     0      100    127.0.0.1:25                       *:*                  
LISTEN     0      128    127.0.0.1:6010                     *:*                  
LISTEN     0      128    127.0.0.1:6011                     *:*                  
LISTEN     0      128          *:5000                     *:*                  
LISTEN     0      50           *:3306                     *:*                  
LISTEN     0      128          *:111                      *:*                  
LISTEN     0      5      192.168.122.1:53                       *:*                  
LISTEN     0      128       [::]:22                    [::]:*                  
LISTEN     0      128      [::1]:631                   [::]:*                  
LISTEN     0      128       [::]:5432                  [::]:*                  
LISTEN     0      100      [::1]:25                    [::]:*                  
LISTEN     0      128      [::1]:6010                  [::]:*                  
LISTEN     0      128      [::1]:6011                  [::]:*                  
LISTEN     0      128       [::]:443                   [::]:*                  
LISTEN     0      128       [::]:111                   [::]:*                  
LISTEN     0      128       [::]:80                    [::]:*                  


=== INDICIOS ===
/var/www/html/adm/index.php
/var/www/html/INFRAWORK/index.php
/var/www/html/vulnapp/app.py

299008	/var/www/html/adm/img
48185344	/var/www/html/adm/assets
15880192	/var/www/html/adm/vendor
7109476352	/var/www/html/adm/archivos
77824	/var/www/html/adm/migo_notificacion
24576	/var/www/html/adm/certificados
139264	/var/www/html/adm/db
1150976	/var/www/html/adm/backups
7177682944	/var/www/html/adm
8069120	/var/www/html/INFRAWORK/PHPMailer
520192	/var/www/html/INFRAWORK/PHPMailer-master
770048	/var/www/html/INFRAWORK/sweetalert
9109504	/var/www/html/INFRAWORK/email
667648	/var/www/html/INFRAWORK/energia
221184	/var/www/html/INFRAWORK/proceso_carga_grilla
577536	/var/www/html/INFRAWORK/presupuesto-pago
1036288	/var/www/html/INFRAWORK/jquery-ui-1.12.1
4096	/var/www/html/INFRAWORK/sms
20480	/var/www/html/INFRAWORK/configuracion
1458176	/var/www/html/INFRAWORK/gestion
0	/var/www/html/INFRAWORK/api
6520832	/var/www/html/INFRAWORK/garbage-test
106496	/var/www/html/INFRAWORK/informes
20480	/var/www/html/INFRAWORK/logs
487424	/var/www/html/INFRAWORK/PHPMailer-master_old
15880192	/var/www/html/INFRAWORK/vendor
1028096	/var/www/html/INFRAWORK/pruebas
1732608	/var/www/html/INFRAWORK/bootstrap-3.4.1
163840	/var/www/html/INFRAWORK/stock_estructura
3596288	/var/www/html/INFRAWORK/alquiler
266240	/var/www/html/INFRAWORK/reporte
864256	/var/www/html/INFRAWORK/crono
40960	/var/www/html/INFRAWORK/notificaciones
277209088	/var/www/html/INFRAWORK/certificado_trabajo
311296	/var/www/html/INFRAWORK/solped
40639614976	/var/www/html/INFRAWORK/Ejemplos_fileinput
1081344	/var/www/html/INFRAWORK/acciones
1019904	/var/www/html/INFRAWORK/css
1470464	/var/www/html/INFRAWORK/fonts
798720	/var/www/html/INFRAWORK/fpdf
274432	/var/www/html/INFRAWORK/FusionCharts
18706432	/var/www/html/INFRAWORK/graficos
16252928	/var/www/html/INFRAWORK/html2
1908736	/var/www/html/INFRAWORK/images
6787072	/var/www/html/INFRAWORK/img
593920	/var/www/html/INFRAWORK/javascript
21708800	/var/www/html/INFRAWORK/js
57344	/var/www/html/INFRAWORK/popup
11472896	/var/www/html/INFRAWORK/examples
1794048	/var/www/html/INFRAWORK/imagen_fileupload
0	/var/www/html/INFRAWORK/tmp_file_upload
200704	/var/www/html/INFRAWORK/fileinput
327680	/var/www/html/INFRAWORK/ticket_ABM
41064361984	/var/www/html/INFRAWORK
470507520	/var/www/html/vulnapp/uploads
286720	/var/www/html/vulnapp/templates
57344	/var/www/html/vulnapp/templates.bak
16384	/var/www/html/vulnapp/static
471416832	/var/www/html/vulnapp

=== DATOS Y LOGS ===
drwxr-xr-x. 5 mysql    mysql     215 jul 12 17:26 /var/lib/mysql
drwx------. 5 postgres postgres  181 feb 11  2020 /var/lib/pgsql
drwx------. 2 root     root     4096 sep 13 03:12 /var/log/httpd
drwxr-x---. 2 mysql    mysql      25 ago  8  2019 /var/log/mariadb
62951424	/var/lib/mysql
0	/var/lib/pgsql
4096	/var/log/httpd
0	/var/log/mariadb

=== MONTAJES APPS ===
S.ficheros              bloques de 1       Usados Disponibles Capacidad Montado en
/dev/mapper/centos-root 800996720640 712104275968 88892444672       89% /
/dev/mapper/centos-root 800996720640 712104275968 88892444672       89% /
/dev/mapper/centos-root 800996720640 712104275968 88892444672       89% /

=== PAQUETES ===
httpd-2.4.6-97.el7.centos.x86_64
php-5.6.40-41.el7.remi.x86_64
php-cli-5.6.40-41.el7.remi.x86_64
mariadb-server-5.5.64-1.el7.x86_64
postgresql10-server-10.12-1PGDG.rhel7.x86_64
python-2.7.5-86.el7.x86_64
python-flask-0.10.1-4.el7.noarch

=== CPU PROCESOS INTERVALO ===
Linux 3.10.0-1062.18.1.el7.x86_64 (tec-calidad05) 	16/09/26 	_x86_64_	(4 CPU)

09:25:50      UID       PID    %usr %system  %guest    %CPU   CPU  Command

09:25:50      UID       PID  minflt/s  majflt/s     VSZ    RSS   %MEM  Command
09:25:51       48     24855      2,88      0,00  592368  10364   0,13  httpd
09:25:51       48     24856      2,88      0,00  592368  10364   0,13  httpd

09:25:51      UID       PID    %usr %system  %guest    %CPU   CPU  Command
09:25:52        0      1498    0,00    1,00    0,00    1,00     3  httpd
09:25:52       48     23903    1,00    0,00    0,00    1,00     1  httpd

09:25:51      UID       PID  minflt/s  majflt/s     VSZ    RSS   %MEM  Command
09:25:52       48     23903   1466,00      0,00       0      0   0,00  httpd

09:25:52      UID       PID    %usr %system  %guest    %CPU   CPU  Command
09:25:53       48     24591    1,00    1,00    0,00    2,00     1  httpd

09:25:52      UID       PID  minflt/s  majflt/s     VSZ    RSS   %MEM  Command
09:25:53       48     24591   1392,00      0,00       0      0   0,00  httpd

Media:        UID       PID    %usr %system  %guest    %CPU   CPU  Command
Media:          0      1498    0,00    0,33    0,00    0,33     -  httpd
Media:         48     24591    0,33    0,33    0,00    0,66     -  httpd

Media:        UID       PID  minflt/s  majflt/s     VSZ    RSS   %MEM  Command
Media:         48     24591    457,89      0,00  454832  15456   0,19  httpd
Media:         48     24855      0,99      0,00  592368  10364   0,13  httpd
Media:         48     24856      0,99      0,00  592368  10364   0,13  httpd

STDERR
** WARNING: connection is not using a post-quantum key exchange algorithm.
** This session may be vulnerable to "store now, decrypt later" attacks.
** The server may need to be upgraded. See https://openssh.com/pq.html
ls: no se puede acceder a /var/lib/pgsql/10/data: Permiso denegado
du: no se puede leer el directorio Â«/var/lib/mysql/mysqlÂ»: Permiso denegado
du: no se puede leer el directorio Â«/var/lib/mysql/performance_schemaÂ»: Permiso denegado
du: no se puede leer el directorio Â«/var/lib/mysql/infrafilerunÂ»: Permiso denegado
du: no se puede leer el directorio Â«/var/lib/pgsqlÂ»: Permiso denegado
du: no se puede leer el directorio Â«/var/log/httpdÂ»: Permiso denegado
du: no se puede leer el directorio Â«/var/log/mariadbÂ»: Permiso denegado

```

### Comprobaciones finales

```text
2026-09-16T09:26:13-0300

=== VULNAPP INTERVALO ===
Linux 3.10.0-1062.18.1.el7.x86_64 (tec-calidad05) 	16/09/26 	_x86_64_	(4 CPU)

09:26:13      UID       PID    %usr %system  %guest    %CPU   CPU  Command
09:26:14       48      6366    0,00    0,00    0,00    0,00     1  python

09:26:13      UID       PID  minflt/s  majflt/s     VSZ    RSS   %MEM  Command
09:26:14       48      6366      0,00      0,00  499976 155044   1,94  python

09:26:14      UID       PID    %usr %system  %guest    %CPU   CPU  Command
09:26:15       48      6366    0,00    0,00    0,00    0,00     1  python

09:26:14      UID       PID  minflt/s  majflt/s     VSZ    RSS   %MEM  Command
09:26:15       48      6366      0,00      0,00  499976 155044   1,94  python

09:26:15      UID       PID    %usr %system  %guest    %CPU   CPU  Command
09:26:16       48      6366    0,00    0,00    0,00    0,00     1  python

09:26:15      UID       PID  minflt/s  majflt/s     VSZ    RSS   %MEM  Command
09:26:16       48      6366      0,00      0,00  499976 155044   1,94  python

Media:        UID       PID    %usr %system  %guest    %CPU   CPU  Command
Media:         48      6366    0,00    0,00    0,00    0,00     -  python

Media:        UID       PID  minflt/s  majflt/s     VSZ    RSS   %MEM  Command
Media:         48      6366      0,00      0,00  499976 155044   1,94  python

=== OTROS DIRECTORIOS IDENTIFICADOS ===
6554636288	/var/www/html/backup_pg
634862866432	/var/www/html/infrafilerun
1978368	/var/www/html/subirArchivos

=== LOGS CONCRETOS ===
20480	/var/www/html/INFRAWORK/logs
5574656	/var/www/html/INFRAWORK/garbage-test/log

=== SERVICIOS ===
MainPID=1498
ControlGroup=/system.slice/httpd.service
WorkingDirectory=
Id=httpd.service
MainPID=1591
ControlGroup=/system.slice/mariadb.service
WorkingDirectory=
Id=mariadb.service
MainPID=1491
ControlGroup=/system.slice/postgresql-10.service
WorkingDirectory=
Id=postgresql-10.service

=== NOMBRES APLICACIONES ===
/var/www/html/portafoox-lite/admin
/var/www/html/INFRAWORK
/var/www/html/infrafilerun
/var/www/html/infrafilerun/documentos/ADM
/var/www/html/adm
/var/www/html/vulnapp

=== FECHA FIN ===
2026-09-16T09:28:03-0300

STDERR
** WARNING: connection is not using a post-quantum key exchange algorithm.
** This session may be vulnerable to "store now, decrypt later" attacks.
** The server may need to be upgraded. See https://openssh.com/pq.html

```

## Validación local

CSV UTF-8 con BOM, delimitador punto y coma, encabezados solicitados y número de campos validado. Ausencia de la contraseña comprobada por comparación literal en todos los archivos generados. Se incluyen únicamente métricas, metadatos y nombres; no contenidos de configuraciones sensibles, datos o código de aplicaciones. Helper eliminado mediante trap y proceso con contraseña finalizado.
