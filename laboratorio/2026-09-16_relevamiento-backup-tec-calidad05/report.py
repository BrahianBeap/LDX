import csv, pathlib, re
R=pathlib.Path(__file__).resolve().parent
B=1073741824
g=lambda n:f'{n/B:.2f}'
p=lambda n:f'{n:.1f}'
date='2026-09-16T09:25:10-0300'
host='tec-calidad05'
base=(R/'base.txt').read_text(encoding='utf-8')
apps=(R/'apps.txt').read_text(encoding='utf-8')
final=(R/'final_checks.txt').read_text(encoding='utf-8')
def write(name, header, rows):
    with (R/name).open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.writer(f,delimiter=';'); w.writerow(header.split(';')); w.writerows(rows)
    with (R/name).open(encoding='utf-8-sig',newline='') as f:
        contents=list(csv.reader(f,delimiter=';'))
        assert all(len(row)==len(contents[0]) for row in contents)
total=800996720640+1063256064
used=712104357888+301240320
free=88892362752+762015744
write('01_resumen_servidores.csv','Servidor;IP;Aplicaciones_identificadas;Sistema_operativo;Virtualizacion;vCPU;Modelo_CPU;CPU_actual_porcentaje;CPU_historica_porcentaje;Carga_1m;Carga_5m;Carga_15m;RAM_total_GiB;RAM_usada_GiB;RAM_disponible_GiB;RAM_usada_porcentaje;Swap_total_GiB;Swap_usada_GiB;Disco_FS_total_GiB;Disco_FS_usado_GiB;Disco_FS_libre_GiB;Disco_FS_usado_porcentaje;Uptime;Fecha_medicion;Observaciones',[[host,'10.129.2.165','Infrawork | VulnApp','CentOS Linux 7.7.1908 (Core)','VMware',4,'Intel Xeon E5-2698 v4 @ 2.20GHz','0.9','0.6','0.05','0.05','0.05',g(8201240576),g(2015776768),g(5266776064),p(2015776768/8201240576*100),g(2147479552),g(228974592),g(total),g(used),g(free),p(used/total*100),'65 días 16:01',date,'ALERTA /: 88.9%. CPU actual: mpstat 3 s. Histórico: sar del 16/09 00:00:01–09:20:01. RAM usada según free (excluye buff/cache). ADM-TECH pendiente: candidato /var/www/html/adm. IP adicional 192.168.122.1.']])
diskrows=[]
for dev,typ,mount,cap,use,avail,ino in [('/dev/mapper/centos-root','lvm','/',800996720640,712104357888,88892362752,2),('/dev/sda1','part','/boot',1063256064,301240320,762015744,1)]:
    diskrows.append([host,dev,typ,'xfs',mount,g(cap),g(use),g(avail),p(use/cap*100),p(ino),'Local','ALERTA' if use/cap>=.8 or ino>=80 else 'OK',date])
write('02_detalle_discos.csv','Servidor;Dispositivo;Tipo;Sistema_archivos;Punto_montaje;Capacidad_GiB;Usado_GiB;Libre_GiB;Uso_porcentaje;Inodos_uso_porcentaje;Local_o_remoto;Estado;Fecha_medicion',diskrows)
rows=[]
def app(name,state,path='N/D',service='N/D',tech='N/D',mount='N/D',code='N/D',docs='N/D',logs='N/D',db='N/D',cpu='N/D',ram='N/D',kind='No disponible',obs=''):
    rows.append([host,name,state,path,service,tech,mount,code,docs,logs,db,cpu,ram,kind,obs,'2026-09-16T09:25:41-0300'])
app('ADM-TECH','No identificada en este servidor; ubicación pendiente de confirmación',obs='Existe /var/www/html/adm como candidato. No se confirmó su correspondencia con ADM-TECH.')
app('adm (candidato ADM-TECH)','Directorio identificado; identidad funcional pendiente','/var/www/html/adm','httpd.service (compartido; asociación por DocumentRoot)','PHP (archivos .php)','/',docs=g(7109476352),kind='Servicio compartido',obs=f'Total directorio {g(7177682944)} GiB. Documentos: subdirectorio archivos, clasificación por nombre. Backups {g(1150976)} GiB. Código puro no separable de otros archivos. BD no confirmada.')
app('Infrawork','Identificada por directorio de publicación','/var/www/html/INFRAWORK','httpd.service (compartido; asociación por DocumentRoot)','PHP (archivos .php)','/',logs=g(20480+5574656),kind='Servicio compartido',obs=f'Total directorio {g(41064361984)} GiB. Ejemplos_fileinput {g(40639614976)} GiB: contenido mixto no atribuible íntegramente a documentos. Logs_GiB suma logs y garbage-test/log (5595136 bytes). Código y documentos N/D por mezcla. BD no confirmada.')
app('VulnApp','Identificada por servicio activo y WorkingDirectory','/var/www/html/vulnapp','vulnapp.service','Python; Flask instalado, uso no confirmado','/',docs=g(470507520),cpu='0.0',ram=f'{155044/1024:.2f}',kind='Dedicada',obs=f'Total directorio {g(471416832)} GiB. uploads clasificado por nombre. PID 6366 confirmado. RSS y CPU medidos por pidstat entre 09:26:13 y 09:26:16. CPU 0.0% sobre un nucleo durante 3 segundos, no historica. Código puro N/D: resto incluye copias y configuraciones. BD no confirmada.')
app('infrafilerun','Directorio identificado','/var/www/html/infrafilerun',mount='/',obs=f'Total ocupado {g(634862866432)} GiB. No atribuido a Infrawork ni ADM-TECH. Existe documentos/ADM, pero su nombre no prueba propietario ni equivalencia. Separacion codigo/documentos N/D.')
app('backup_pg','Directorio identificado','/var/www/html/backup_pg',mount='/',obs=f'Total ocupado {g(6554636288)} GiB. Posibles copias por nombre; no equivale al tamano del motor PostgreSQL ni de una BD especifica.')
proc=base.split('=== PROCESOS ===')[1].split('=== PUERTOS ===')[0]
for name,comm,service,tech in [('Apache compartido','httpd','httpd.service','Apache 2.4.6 / PHP 5.6.40 instalado'),('MariaDB','mysqld','mariadb.service','MariaDB 5.5.64'),('PostgreSQL','postmaster','postgresql-10.service','PostgreSQL 10.12')]:
    matches=[line.split() for line in proc.splitlines() if len(line.split())==6 and line.split()[2]==comm]
    rss=sum(int(x[5]) for x in matches)
    app(name,'Servicio activo',service=service,tech=tech,ram=f'{rss/1024:.2f}',kind='Servicio compartido',obs='RSS agregado puntual; puede contar páginas compartidas varias veces. CPU actual del componente N/D. Sin reparto por aplicación. Tamaño de datos/logs: Sin acceso con alfonzel_opr. Bases específicas no confirmadas.')
write('03_detalle_aplicaciones.csv','Servidor;Aplicacion;Estado_identificacion;Ruta;Servicio;Tecnologia;Punto_montaje;Codigo_GiB;Documentos_GiB;Logs_GiB;Base_datos_GiB;CPU_porcentaje;RAM_MiB;Tipo_medicion;Observaciones;Fecha_medicion',rows)
intro=f'''# Evidencias de relevamiento: tec-calidad05

Fecha inicial del servidor: {date}. Las fechas de cada etapa figuran en las salidas. Lectura con alfonzel_opr, sin sudo, sin instalaciones, cambios de configuración ni archivos remotos.

## Identidad y acceso

Primer comando remoto: `hostname && whoami`. Resultado validado: `tec-calidad05` y `alfonzel_opr`. Hubo un intento previo rechazado por autenticación; se corrigió la construcción local del helper y se validó antes del relevamiento.
OpenSSH directo desde Git Bash, SSH_ASKPASS_REQUIRE=force, StrictHostKeyChecking=yes, ControlMaster=no y ControlPath=none. Contraseña recibida desde el adjunto en memoria, pasada por entorno al proceso de cada comando, nunca incluida en argumentos ni archivos. Helper askpass.sh en mktemp con modo 700, shebang y printf literal, eliminado por trap junto al directorio temporal. Los procesos locales que manejaron la variable terminaron.

## Resultados y cálculos

- VM VMware; kernel 3.10.0-1062.18.1.el7.x86_64. CPU expuesta al invitado: 4 sockets × 1 núcleo × 1 hilo = 4 vCPU. No describe la topología física del host VMware.
- CPU puntual: 100 − 99.08 idle = 0.92%, mostrado 0.9%, mpstat entre 09:25:14 y 09:25:17. Cargas 1/5/15 min: 0.05/0.05/0.05.
- CPU histórica accesible: sar del día 16/09/2026, intervalo 00:00:01–09:20:01, muestreo aproximadamente cada 10 minutos. 100 − 99.43 = 0.57%, mostrado 0.6%. No representa semanas, meses ni picos fuera de esa ventana.
- RAM visible al SO: 8201240576 bytes = {g(8201240576)} GiB. Usada según free: 2015776768 = {g(2015776768)} GiB ({p(2015776768/8201240576*100)}%). Disponible: 5266776064 = {g(5266776064)} GiB. Libre: 162037760 bytes. buff/cache: 6023426048 bytes. `used = total − free − buff/cache`; no sumar caché como uso exclusivo de aplicaciones. La métrica alternativa total−available da {p((8201240576-5266776064)/8201240576*100)}%, no se mezcla con used en el CSV. Capacidad física del host y DIMM: N/D.
- Swap: {g(2147479552)} GiB total, {g(228974592)} GiB usada ({p(228974592/2147479552*100)}%). vmstat no mostró actividad si/so en los intervalos observados; ocupación de swap no equivale a presión actual.
- GiB = bytes / 1073741824. RAM de procesos MiB = RSS KiB / 1024. Dos decimales para tamaños, un decimal para porcentajes. Valores menores de 0.005 GiB redondean a 0.00 y no implican ausencia de datos.
- Sistemas de archivos locales reales únicos: / y /boot. Total {g(total)} GiB, usado {g(used)} GiB, disponible {g(free)} GiB, uso {p(used/total*100)}%. Sin montajes remotos identificados. Pseudo FS y tmpfs excluidos del detalle y suma.
- ALERTA raíz: {p(712104357888/800996720640*100)}% ocupado, {g(88892362752)} GiB disponibles. df redondea a 89%; el CSV calcula usado/capacidad con bytes. /boot: {p(301240320/1063256064*100)}%. Inodos: 2% y 1% reportados por df (redondeados hacia arriba), sin alerta.
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
'''
for name in ['base','apps','final_checks']:
    intro+='\n### '+name+'\n\n```bash\n'+(R/(name+'.sh')).read_text(encoding='utf-8')+'```\n'
intro+='\n## Salidas relevantes depuradas\n'
# Keep resource evidence; remove unrelated process rows and repetitive file names.
safe_base=base.split('=== PROCESOS ===')[0]+'=== PROCESOS RELEVANTES ===\n'+'\n'.join(x for x in proc.splitlines() if any(c in x.split() for c in ['httpd','python','mysqld','postmaster']))+'\n'+base.split('=== PUERTOS ===')[1]
safe_apps=apps.split('=== RUTAS ===')[0]+'\n=== INDICIOS ===\n/var/www/html/adm/index.php\n/var/www/html/INFRAWORK/index.php\n/var/www/html/vulnapp/app.py\n'+apps.split('=== TAMANOS ===')[1]
for name,out in [('Base',safe_base),('Aplicaciones',safe_apps),('Comprobaciones finales',final)]:
    intro+='\n### '+name+'\n\n```text\n'+out+'\n```\n'
intro+='\n## Validación local\n\nCSV UTF-8 con BOM, delimitador punto y coma, encabezados solicitados y número de campos validado. Ausencia de la contraseña comprobada por comparación literal en todos los archivos generados. Se incluyen únicamente métricas, metadatos y nombres; no contenidos de configuraciones sensibles, datos o código de aplicaciones. Helper eliminado mediante trap y proceso con contraseña finalizado.\n'
(R/'04_evidencias_tec-calidad05.md').write_text(intro,encoding='utf-8')
secret=re.search(r'temporal:\s*(\S+)',pathlib.Path(r'C:\Users\alfonzel\.codex\attachments\7051e76f-5c0e-45ac-b02a-64713544988a\pasted-text.txt').read_text(encoding='utf-8-sig')).group(1)
for file in R.iterdir():
    if file.is_file():
        assert secret.encode() not in file.read_bytes(), 'Se encontró un secreto en un archivo generado'
secret=None
print('Validación OK: cuatro entregables, campos coherentes y contraseña ausente.')
print(f'Disco: {g(total)} GiB, {g(used)} GiB usados; RAM: {g(8201240576)} GiB.')
