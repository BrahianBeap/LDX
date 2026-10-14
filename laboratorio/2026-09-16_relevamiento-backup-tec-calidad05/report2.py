import pathlib,csv,re,hashlib
R=pathlib.Path(__file__).resolve().parent
G=1073741824
fmt=lambda n:f'{n/G:.2f}'
old=list(R.glob('0[1-4]_*'))
hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in old}
ev=(R/'04_evidencias_tec-calidad05.md').read_text(encoding='utf-8')
db=(R/'db2_verified.txt').read_text(encoding='utf-8')
detail=(R/'db_details.txt').read_text(encoding='utf-8')
storage=(R/'storage2.txt').read_text(encoding='utf-8')
identity=(R/'identity2.txt').read_text(encoding='utf-8')
assert identity.startswith('tec-calidad05\nalfonzel_opr\n')
assert 'on|on|30s' in db and 'PGPASS_ELIMINADO=SI' in db and 'PGPASS_ELIMINADO=SI' in detail
sizes={name:int(b) for name,b,g in re.findall(r'^(Infra_restore|Infraestructura|postgres|vulnerabilidad)\|(\d+)\|([0-9.]+)$',db,re.M)}
stamp='2026-09-16T09:59:19-0300'
def measured(path):
    return int(re.search(r'^(\d+)\s+'+re.escape(path)+r'$',ev,re.M).group(1))
folders={a:measured('/var/www/html/'+p) for a,p in [('Infrawork','INFRAWORK'),('ADM-TECH','adm'),('VulnApp','vulnapp')]}
allocated=sum(int(line.split('|')[2])*512 for line in storage.splitlines() if line.startswith('f|'))
assert allocated+4096==measured('/var/www/html/backup_pg')
assert all('backup_Infraestructura_' in line for line in storage.splitlines() if line.startswith('f|'))
repo=measured('/var/www/html/infrafilerun')
backup=allocated+4096
ops={a:folders[a]+sizes[b] for a,b in [('Infrawork','Infraestructura'),('ADM-TECH','postgres'),('VulnApp','vulnerabilidad')]}
alltot={a:n+(sizes['Infra_restore']+backup if a=='Infrawork' else 0) for a,n in ops.items()}
def csvfile(name,header,rows):
    with (R/name).open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.writer(f,delimiter=';');w.writerow(header.split(';'));w.writerows(rows)
    with (R/name).open(encoding='utf-8-sig',newline='') as f:
        data=list(csv.reader(f,delimiter=';'))
    assert all(len(x)==len(data[0]) for x in data)
rows=[]
for app,path,b,docs,logs in [('Infrawork','INFRAWORK','Infraestructura','N/D',fmt(5595136)),('ADM-TECH','adm','postgres',fmt(7109476352),'N/D'),('VulnApp','vulnapp','vulnerabilidad',fmt(470507520),'N/D')]:
    infra=app=='Infrawork';vuln=app=='VulnApp'
    obs='Totales del alcance medido y atribuido; no son inventario exhaustivo. Carpetas/CPU/RAM reutilizadas del 16/09 09:25–09:28; BD 09:58–09:59. Repositorio externo 0.00 significa ninguno atribuido, no ausencia. Logs externos sin acceso: excluidos, total parcial. '
    if infra:obs+='Ejemplos_fileinput 37.85 GiB mixtos incluidos en carpeta; no se declaran adjuntos puros. Nueve backups por nombre de base, 6.10 GiB incluyendo 4096 bytes del directorio. Infra_restore solo en respaldos.'
    elif vuln:obs+='CPU 0.0% durante 3 s y RSS 151.41 MiB dedicados; no históricos. Sin BD de respaldo informada ni archivos externos atribuidos: se suma 0, existencia no descartada.'
    else:obs+='Mapeo /adm y postgres confirmado por responsable; postgres usa el nombre habitual de la base de mantenimiento. Sin BD de respaldo informada ni archivos externos atribuidos. Copias internas de /adm/backups ya incluidas en carpeta, no se suman de nuevo.'
    rows.append(['tec-calidad05',app,'/var/www/html/'+path,fmt(folders[app]),docs,logs,'0.00',b,fmt(sizes[b]),'Infra_restore' if infra else 'No informada',fmt(sizes['Infra_restore']) if infra else 'N/D',fmt(backup) if infra else '0.00',fmt(ops[app]),fmt(alltot[app]),'0.0' if vuln else 'N/D — servicio Apache compartido','151.41' if vuln else 'N/D — servicio Apache compartido','Dedicada' if vuln else 'Servicio compartido',obs,stamp])
rows.append(['tec-calidad05','Repositorios compartidos pendientes','/var/www/html/infrafilerun','N/D','N/D','N/D',fmt(repo),'N/D','N/D','N/D','N/D','N/D',fmt(repo),fmt(repo),'N/D','N/D','No disponible','Repositorio compartido pendiente de atribución. Total único del repositorio, no sumar sus subdirectorios. documentos/ADM = 0 bytes; sin volumen positivo atribuible. Totales de esta fila solo reflejan repositorio.',stamp])
rows.append(['tec-calidad05','Backups compartidos pendientes','/var/www/html/backup_pg','N/D','N/D','N/D','N/D','N/D','N/D','N/D','N/D','0.00','0.00','0.00','N/D','N/D','No disponible','Sin saldo pendiente en backup_pg: todos los archivos y 4096 bytes del directorio atribuidos a Infrawork por nombres. No volver a sumar 6.10 GiB.',stamp])
csvfile('05_consumo_aplicaciones.csv','Servidor;Aplicacion;Ruta_principal;Carpeta_total_GiB;Adjuntos_incluidos_GiB;Logs_incluidos_GiB;Repositorio_externo_GiB;BD_principal;BD_principal_GiB;BD_respaldo;BD_respaldo_GiB;Backups_archivos_GiB;Total_operativo_GiB;Total_con_respaldos_GiB;CPU_porcentaje;RAM_MiB;Tipo_medicion;Observaciones;Fecha_medicion',rows)
dbrows=[]
for app,b in [('Infrawork','Infraestructura'),('ADM-TECH','postgres'),('VulnApp','vulnerabilidad')]:
    sec=detail.split('=== DATABASE '+b+' ===')[1].split('=== DATABASE')[0]
    t,i=map(int,re.search(r'tablas_bytes\|indices_bytes\n(\d+)\|(\d+)',sec).groups())
    dbrows.append([app,'Principal',b,fmt(sizes[b]),fmt(t),fmt(i),'Verificada; solo lectura; tablas e índices de esquemas de usuario','2026-09-16T09:59:16-0300'])
dbrows.append(['Infrawork','Respaldo','Infra_restore',fmt(sizes['Infra_restore']),'N/D','N/D','Verificada; desglose no solicitado para respaldo','2026-09-16T09:58:47-0300'])
csvfile('06_detalle_bases_postgresql.csv','Aplicacion;Tipo_base;Base_datos;Tamano_total_GiB;Tablas_GiB;Indices_GiB;Estado;Fecha_medicion',dbrows)
summary='''# Consumo para planilla

GiB, dos decimales. Carpetas reutilizadas del 16/09/2026 09:25–09:28 -0300; bases y desglose complementario del mismo día 09:58–09:59 -0300. Totales **parciales del alcance medido y atribuido**: logs externos sin acceso y repositorios sin atribución quedan fuera de los totales por aplicación. No es una fotografía simultánea ni un promedio histórico.

| Aplicación | Código/carpetas | Adjuntos incluidos | Base principal | Respaldo BD | Total operativo | Total con respaldos | Observaciones |
|---|---:|---:|---:|---:|---:|---:|---|
'''
for row in rows[:3]:
    app=row[1]
    note={'Infrawork':'Incluye logs 0.01 GiB y contenido mixto Ejemplos_fileinput 37.85 GiB. Total con respaldos añade 6.10 GiB de archivos y 1.71 GiB de Infra_restore.','ADM-TECH':'Mapeo confirmado. Base postgres con nombre habitual de mantenimiento. Sin respaldo BD informado; copias internas ya incluidas en carpeta.','VulnApp':'RAM dedicada 151.41 MiB; CPU puntual 0.0%. Sin respaldo BD informado.'}[app]
    summary+=f'| {app} | {row[3]} | {row[4]} | {row[8]} | {row[10]} | {row[12]} | {row[13]} | {note} |\n'
summary+=f'| Repositorios compartidos pendientes | {fmt(repo)} | N/D | N/D | N/D | {fmt(repo)} | {fmt(repo)} | infrafilerun; separado de las aplicaciones. |\n| Backups compartidos pendientes | 0.00 | N/D | N/D | N/D | 0.00 | 0.00 | Todo backup_pg atribuido a Infrawork; no duplicar. |\n'
summary+='''
«Código/carpetas» es la carpeta completa, no código puro. Adjuntos y logs internos ya están incluidos y no se suman otra vez. N/D no equivale a cero. Los respaldos no informados y logs externos desconocidos no se han estimado; los totales solo suman componentes comprobados. Las copias internas permanecen en el total operativo porque la fórmula solicitada usa la carpeta completa.

Infrawork y ADM-TECH: CPU y RAM **N/D — servicio Apache compartido**. RSS compartido reutilizado: Apache 237.90 MiB, PostgreSQL 613.95 MiB y MariaDB 227.21 MiB. No se reparte entre aplicaciones ni bases.
'''
(R/'08_resumen_para_planilla.md').write_text(summary,encoding='utf-8')
evidence='''# Evidencias complementarias de consumo por aplicación

## Alcance y mapeo recibido

Infrawork → Infraestructura (principal), Infra_restore (respaldo), /var/www/html/INFRAWORK.
ADM-TECH → postgres (principal), /var/www/html/adm. Mapeo confirmado por responsable; postgres utiliza el nombre habitual de la base de mantenimiento PostgreSQL.
VulnApp → vulnerabilidad (principal), /var/www/html/vulnapp. Respaldos BD de ADM-TECH y VulnApp no informados.

Se leyeron y reutilizaron 01, 02, 03 y 04 sin modificarlos. No se repitieron CPU, RAM, disco ni du de carpetas principales. Se conservaron bytes de las evidencias previas para calcular antes del redondeo. Mediciones nuevas: 2026-09-16 09:58:47–09:59:19 -0300.

## Identidad y credenciales temporales

Primer comando remoto: hostname && whoami. Resultado tec-calidad05 y alfonzel_opr validado antes de continuar. SSH directo con host key estricta, askpass forzado, sin multiplexación. Se reutilizó la credencial SSH vigente del pedido anterior; el nuevo adjunto tenía un marcador sin completar.

La credencial PostgreSQL se obtuvo del adjunto en memoria y viajó únicamente por stdin del canal SSH cifrado, como línea pgpass con escape de dos puntos y barras. No se incluyó en argumentos, historial ni archivos locales. El archivo remoto .pgpass se creó en mktemp con umask 077 y modo 600. Cada consulta recibió PGPASSFILE y PGOPTIONS con default_transaction_read_only=on y statement_timeout=30000; psql -X -w -v ON_ERROR_STOP=1.

Un intento inicial falló por extracción local incorrecta del campo de credencial; se corrigió sin modificar PostgreSQL. Su temporal también fue eliminado. Las sesiones exitosas confirmaron on y 30s; solo se ejecutaron SELECT sobre catálogos y funciones de tamaño. No se consultaron filas funcionales. Los traps eliminaron .pgpass y su directorio, con comprobación PGPASS_ELIMINADO=SI en cada sesión. Helper SSH eliminado por trap. Procesos locales portadores de credenciales finalizados.

## Criterios de tamaño y totales

GiB = bytes / 1073741824. Los totales se calculan con bytes y se redondean al final. Carpetas: bloques ocupados de du -x. PostgreSQL: tamaño informado por pg_database_size; no incluye todo el clúster, WAL global ni logs externos. No se debe exigir igualdad exacta entre ambas métricas y df.

Tablas_GiB suma pg_table_size de tablas ordinarias y vistas materializadas en esquemas de usuario, incluyendo TOAST y estructuras auxiliares según PostgreSQL. Indices_GiB suma pg_indexes_size de esas relaciones. Se excluyen catálogos, information_schema, pg_toast como esquema separado y esquemas temporales para evitar contar TOAST dos veces. No son el desglose completo de todos los objetos de la base; tablas + índices puede diferir del total por catálogos, secuencias y otros archivos. Los totales por esquema y top diez aplican ese mismo alcance; top incluye vistas materializadas y tamaño con índices. No se desglosó el respaldo porque solo se solicitó para principales.

Total_operativo = carpeta completa + repositorios externos atribuidos + BD principal + logs externos medidos y atribuidos.
Total_con_respaldos = total operativo + BD respaldo + backups externos en archivos atribuidos.
Adjuntos y logs internos se muestran como subconjuntos, nunca se suman otra vez. Infra_restore se suma solo al total con respaldos. Copias internas de carpetas ya están incluidas en el primer sumando y no se duplican. No se inventa un tamaño para logs externos: no hubo acceso en el relevamiento previo y los totales se etiquetan como parciales del alcance conocido.

## Desglose y atribución

infrafilerun mantiene 591.26 GiB. documentos/ADM mide 0 bytes y no aporta volumen. OBRAS y los otros nombres describen áreas o contenidos, no demuestran aplicación propietaria: se conserva el total como Repositorio compartido pendiente de atribución. No sumar documento padre e hijos.

backup_pg contiene nueve archivos backup_Infraestructura_YYYYMMDD_000001.sql, del 08 al 16 de septiembre. Se atribuyen a Infrawork por coincidencia inequívoca con la base. Se sumaron bloques de 512 bytes de archivos únicos (todos nlink=1) y 4096 bytes de metadatos del directorio, conciliando exactamente con el total previo de 6554636288 bytes (6.10 GiB). Nombres/fechas/tamaños visibles, sin abrir contenido. No se verificó integridad ni restaurabilidad. Saldo compartido pendiente en esa ruta: cero.

Infrawork/Ejemplos_fileinput es mixto: adjuntos puros N/D. Logs internos 5595136 bytes. ADM-TECH/archivos 7109476352 bytes; VulnApp/uploads 470507520 bytes, ambos incluidos. Los 1150976 bytes de /adm/backups ya están en carpeta y no se añaden a Backups_archivos_GiB, que aquí representa respaldos externos incrementales.

## Comandos y SQL ejecutados
'''
for name in ['db','db_details','storage2']:
    evidence+='\n### '+name+'\n\n```bash\n'+(R/(name+'.sh')).read_text(encoding='utf-8')+'\n```\n'
evidence+='\n## Resultados verificables\n'
for name,out in [('Identidad',identity),('Bases y modo de lectura',db),('Tablas, índices, esquemas y top diez',detail),('Repositorio y metadatos de respaldos',storage)]:
    evidence+='\n### '+name+'\n\n```text\n'+out.split('STDERR')[0]+'\n```\n'
evidence+='\n## Resumen y validación\n\n'+summary.split('# Consumo para planilla\n',1)[1]
evidence+='\nSe validaron encabezados, cantidad de columnas, consistencia de bytes de respaldos, fórmulas sin duplicados, separación de Infra_restore y ausencia de las dos credenciales en los nuevos entregables. Archivos 01–04 sin cambios, verificados mediante SHA-256. Sin .pgpass local generado; remotos eliminados y comprobados por la propia sesión.\n'
(R/'07_evidencias_consumo_aplicaciones.md').write_text(evidence,encoding='utf-8')
sshsecret=re.search(r'temporal:\s*(\S+)',pathlib.Path(r'C:\Users\alfonzel\.codex\attachments\7051e76f-5c0e-45ac-b02a-64713544988a\pasted-text.txt').read_text(encoding='utf-8-sig')).group(1)
pgsecret=re.search(r'temporal de PostgreSQL:\s*(\S+)',pathlib.Path(r'C:\Users\alfonzel\.codex\attachments\0f2462b0-f1aa-42d5-885e-c8e477c8d458\pasted-text.txt').read_text(encoding='utf-8-sig')).group(1)
for file in list(R.glob('0[5-8]_*')):
    text=file.read_text(encoding='utf-8-sig')
    assert sshsecret not in text and pgsecret not in text, 'Credencial encontrada'
assert all(hashlib.sha256(p.read_bytes()).hexdigest()==hashes[p.name] for p in old)
assert not list(R.rglob('.pgpass'))
sshsecret=pgsecret=None
print('Validación correcta. Archivos 01–04 intactos. Nuevos entregables sin credenciales.')
for a in ops:print(a,fmt(ops[a]),fmt(alltot[a]))
