# Evidencias complementarias de consumo por aplicación

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

### db

```bash
date --iso-8601=seconds
umask 077
pgdir=$(mktemp -d) || exit 1
cleanup() {
  rm -f -- "$pgdir/.pgpass"
  if test ! -e "$pgdir/.pgpass"; then printf '\nPGPASS_ELIMINADO=SI\n'; else printf '\nPGPASS_ELIMINADO=NO\n'; fi
  rmdir -- "$pgdir"
}
trap cleanup EXIT
trap 'exit 130' INT TERM HUP
IFS= read -r pgline || exit 1
printf '%s\n' "$pgline" > "$pgdir/.pgpass"
unset pgline
chmod 600 "$pgdir/.pgpass"
psqlbin=$(command -v psql)
if test -z "$psqlbin"; then psqlbin=/usr/pgsql-10/bin/psql; fi
query() {
  PGPASSFILE="$pgdir/.pgpass" PGOPTIONS='-c default_transaction_read_only=on -c statement_timeout=30000' "$psqlbin" -X -w -v ON_ERROR_STOP=1 -h 127.0.0.1 -p 5432 -U postgres -d "$1" -A -F '|' -c "$2"
}
printf '\n=== READONLY ===\n'
query postgres "SELECT current_setting('default_transaction_read_only'), current_setting('transaction_read_only'), current_setting('statement_timeout');" || exit 1
printf '\n=== NOMBRES ===\n'
query postgres "SELECT datname FROM pg_database WHERE lower(datname) IN (lower('Infraestructura'),lower('Infra_restore'),lower('postgres'),lower('vulnerabilidad')) ORDER BY datname;" || exit 1
printf '\n=== TAMANOS ===\n'
query postgres "SELECT datname AS base_datos, pg_database_size(datname) AS bytes, round(pg_database_size(datname)::numeric / 1073741824,2) AS gib FROM pg_database WHERE lower(datname) IN (lower('Infraestructura'),lower('Infra_restore'),lower('postgres'),lower('vulnerabilidad')) ORDER BY datname;" || exit 1

```

### db_details

```bash
date --iso-8601=seconds
umask 077
pgdir=$(mktemp -d) || exit 1
cleanup() {
  rm -f -- "$pgdir/.pgpass"
  if test ! -e "$pgdir/.pgpass"; then printf '\nPGPASS_ELIMINADO=SI\n'; else printf '\nPGPASS_ELIMINADO=NO\n'; fi
  rmdir -- "$pgdir"
}
trap cleanup EXIT
trap 'exit 130' INT TERM HUP
IFS= read -r pgline || exit 1
printf '%s\n' "$pgline" > "$pgdir/.pgpass"
unset pgline
chmod 600 "$pgdir/.pgpass"
psqlbin=$(command -v psql)
if test -z "$psqlbin"; then psqlbin=/usr/pgsql-10/bin/psql; fi
query() {
  PGPASSFILE="$pgdir/.pgpass" PGOPTIONS='-c default_transaction_read_only=on -c statement_timeout=30000' "$psqlbin" -X -w -v ON_ERROR_STOP=1 -h 127.0.0.1 -p 5432 -U postgres -d "$1" -A -F '|' -c "$2"
}

for database in Infraestructura postgres vulnerabilidad; do
  printf '\n=== DATABASE %s ===\n' "$database"
  query "$database" "SELECT current_database(),current_setting('transaction_read_only'),current_setting('statement_timeout'),pg_database_size(current_database()) AS total_bytes;" || exit 1
  query "$database" "SELECT COALESCE(sum(pg_table_size(c.oid)),0) AS tablas_bytes,COALESCE(sum(pg_indexes_size(c.oid)),0) AS indices_bytes FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace WHERE c.relkind IN ('r','m') AND n.nspname NOT IN ('pg_catalog','information_schema') AND n.nspname !~ '^pg_toast' AND n.nspname !~ '^pg_temp';" || exit 1
  query "$database" "SELECT n.nspname AS esquema, sum(pg_table_size(c.oid)) AS tablas_bytes,sum(pg_indexes_size(c.oid)) AS indices_bytes,sum(pg_total_relation_size(c.oid)) AS total_bytes FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace WHERE c.relkind IN ('r','m') AND n.nspname NOT IN ('pg_catalog','information_schema') AND n.nspname !~ '^pg_toast' AND n.nspname !~ '^pg_temp' GROUP BY n.nspname ORDER BY total_bytes DESC;" || exit 1
  query "$database" "SELECT n.nspname AS esquema,c.relname AS tabla,pg_total_relation_size(c.oid) AS bytes FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace WHERE c.relkind IN ('r','m') AND n.nspname NOT IN ('pg_catalog','information_schema') AND n.nspname !~ '^pg_toast' AND n.nspname !~ '^pg_temp' ORDER BY bytes DESC,n.nspname,c.relname LIMIT 10;" || exit 1
done
date --iso-8601=seconds

```

### storage2

```bash
date --iso-8601=seconds
printf '\n=== REPOSITORIO ===\n'
du -x -B1 --max-depth=2 /var/www/html/infrafilerun
printf '\n=== BACKUPS METADATOS ===\n'
find /var/www/html/backup_pg -xdev -printf '%y|%s|%b|%n|%D:%i|%TY-%Tm-%TdT%TH:%TM:%TS|%p\n'
date --iso-8601=seconds

```

## Resultados verificables

### Identidad

```text
tec-calidad05
alfonzel_opr


```

### Bases y modo de lectura

```text
2026-09-16T09:58:47-0300

=== READONLY ===
current_setting|current_setting|current_setting
on|on|30s
(1 fila)

=== NOMBRES ===
datname
Infra_restore
Infraestructura
postgres
vulnerabilidad
(4 filas)

=== TAMANOS ===
base_datos|bytes|gib
Infra_restore|1840168071|1.71
Infraestructura|1921186951|1.79
postgres|58432647|0.05
vulnerabilidad|121412743|0.11
(4 filas)

PGPASS_ELIMINADO=SI


```

### Tablas, índices, esquemas y top diez

```text
2026-09-16T09:59:16-0300

=== DATABASE Infraestructura ===
current_database|current_setting|current_setting|total_bytes
Infraestructura|on|30s|1921186951
(1 fila)
tablas_bytes|indices_bytes
1554325504|348372992
(1 fila)
esquema|tablas_bytes|indices_bytes|total_bytes
public|1430306816|326475776|1756782592
gestion|67657728|11059200|78716928
energia|42688512|7323648|50012160
nota_acceso|6545408|1007616|7553024
auditoria|5373952|1769472|7143424
reserva|811008|606208|1417216
utilitario|761856|16384|778240
stock_estructura|180224|114688|294912
(8 filas)
esquema|tabla|bytes
public|mail_historial_backup|1105805312
public|control_ip_cant|434806784
public|presupuesto_item|138125312
energia|datos_consumo_ande|46006272
gestion|incidencia_historial|20242432
public|orden_trabajo|16441344
gestion|incidencia|16138240
public|grilla_item_precio|14090240
gestion|doc_adj|10502144
auditoria|audi_presupuesto|7086080
(10 filas)

=== DATABASE postgres ===
current_database|current_setting|current_setting|total_bytes
postgres|on|30s|58432647
(1 fila)
tablas_bytes|indices_bytes
34578432|13156352
(1 fila)
esquema|tablas_bytes|indices_bytes|total_bytes
reserva|34512896|13107200|47620096
aud|49152|32768|81920
public|16384|16384|32768
(3 filas)
esquema|tabla|bytes
reserva|historial|17276928
reserva|reserva_detalle|4366336
reserva|adm_inicial_detalle|3301376
reserva|deposito_inicial_detalle|3186688
reserva|requirente_inicial_detalle|2695168
reserva|reserva_estado_historial|2367488
reserva|deposito_salida_detalle|2301952
reserva|adjuntos|2072576
reserva|reserva|1974272
reserva|auditoria_eliminacion|1368064
(10 filas)

=== DATABASE vulnerabilidad ===
current_database|current_setting|current_setting|total_bytes
vulnerabilidad|on|30s|121412743
(1 fila)
tablas_bytes|indices_bytes
58589184|53559296
(1 fila)
esquema|tablas_bytes|indices_bytes|total_bytes
public|58589184|53559296|112148480
(1 fila)
esquema|tabla|bytes
public|vulnerabilidades|85360640
public|hosts|9887744
public|historial_vulnerabilidades|7741440
public|importacion_hosts|7258112
public|mv_resumen_hosts|1310720
public|historial_hosts|122880
public|auditoria_usuarios|65536
public|historial_areas|65536
public|operaciones_masivas|65536
public|areas|57344
(10 filas)
2026-09-16T09:59:17-0300

PGPASS_ELIMINADO=SI


```

### Repositorio y metadatos de respaldos

```text
2026-09-16T09:58:47-0300

=== REPOSITORIO ===
4096	/var/www/html/infrafilerun/oauth2/authorize
8192	/var/www/html/infrafilerun/oauth2/token
16384	/var/www/html/infrafilerun/oauth2
8192	/var/www/html/infrafilerun/ocs
4096	/var/www/html/infrafilerun/oembed
4096	/var/www/html/infrafilerun/panel
12288	/var/www/html/infrafilerun/sounds
4096	/var/www/html/infrafilerun/sso
15773696	/var/www/html/infrafilerun/system/classes
2158592	/var/www/html/infrafilerun/system/data
49152	/var/www/html/infrafilerun/system/functions
180224	/var/www/html/infrafilerun/system/includes
6488064	/var/www/html/infrafilerun/system/modules
24653824	/var/www/html/infrafilerun/system
8192	/var/www/html/infrafilerun/weblinks
24576	/var/www/html/infrafilerun/wl/css
8192	/var/www/html/infrafilerun/wl/img
57344	/var/www/html/infrafilerun/wl/js
98304	/var/www/html/infrafilerun/wl
8192	/var/www/html/infrafilerun/a
81920	/var/www/html/infrafilerun/cron
12288	/var/www/html/infrafilerun/css/ext-ux
176128	/var/www/html/infrafilerun/css/font-awesome
253952	/var/www/html/infrafilerun/css/roboto
581632	/var/www/html/infrafilerun/css
98304	/var/www/html/infrafilerun/customizables/auth
339968	/var/www/html/infrafilerun/customizables/emails
4096	/var/www/html/infrafilerun/customizables/events
11227136	/var/www/html/infrafilerun/customizables/plugins
11673600	/var/www/html/infrafilerun/customizables
339968	/var/www/html/infrafilerun/images/extjs
487424	/var/www/html/infrafilerun/images/fico
20480	/var/www/html/infrafilerun/images/generic
204800	/var/www/html/infrafilerun/images/icons
1060864	/var/www/html/infrafilerun/images
331776	/var/www/html/infrafilerun/js/cpanel
765952	/var/www/html/infrafilerun/js/ext
315392	/var/www/html/infrafilerun/js/fileman
16384	/var/www/html/infrafilerun/js/flow
155648	/var/www/html/infrafilerun/js/jquery
16384	/var/www/html/infrafilerun/js/swfobject
1671168	/var/www/html/infrafilerun/js
4096	/var/www/html/infrafilerun/logout
629142773760	/var/www/html/infrafilerun/documentos/OBRAS
252391424	/var/www/html/infrafilerun/documentos/GESTION
149106688	/var/www/html/infrafilerun/documentos/ESTABILIZADORES
237121536	/var/www/html/infrafilerun/documentos/FILTROS
211406848	/var/www/html/infrafilerun/documentos/PROYECTOS_PLANOS_2019
491008000	/var/www/html/infrafilerun/documentos/Relevamiento_Sitios_Proyecto_LTE
55386112	/var/www/html/infrafilerun/documentos/.filerun.trash
0	/var/www/html/infrafilerun/documentos/.filerun.thumbnails
620560384	/var/www/html/infrafilerun/documentos/VIATICO
0	/var/www/html/infrafilerun/documentos/ADM
3663118336	/var/www/html/infrafilerun/documentos/Baterias2025-Telrad
634822873088	/var/www/html/infrafilerun/documentos
634862866432	/var/www/html/infrafilerun

=== BACKUPS METADATOS ===
d|4096|8|2|64768:2315688321|2026-09-16T00:00:01.8078952260|/var/www/html/backup_pg
f|726628571|1419200|1|64768:2315543786|2026-09-08T00:02:01.4932789200|/var/www/html/backup_pg/backup_Infraestructura_20260908_000001.sql
f|727163692|1420248|1|64768:2315543791|2026-09-09T00:02:00.5236091450|/var/www/html/backup_pg/backup_Infraestructura_20260909_000001.sql
f|727692246|1421280|1|64768:2315543807|2026-09-10T00:02:00.9266707760|/var/www/html/backup_pg/backup_Infraestructura_20260910_000001.sql
f|728163749|1422200|1|64768:2315544394|2026-09-11T00:02:01.3599303370|/var/www/html/backup_pg/backup_Infraestructura_20260911_000001.sql
f|728635964|1423120|1|64768:2315544401|2026-09-12T00:02:02.5893422110|/var/www/html/backup_pg/backup_Infraestructura_20260912_000001.sql
f|728704985|1423256|1|64768:2315544403|2026-09-13T00:01:59.8238166680|/var/www/html/backup_pg/backup_Infraestructura_20260913_000001.sql
f|728707153|1423264|1|64768:2315544404|2026-09-14T00:02:02.1070570750|/var/www/html/backup_pg/backup_Infraestructura_20260914_000001.sql
f|729182934|1424192|1|64768:2315544407|2026-09-15T00:02:02.2973763840|/var/www/html/backup_pg/backup_Infraestructura_20260915_000001.sql
f|729730812|1425256|1|64768:2315544409|2026-09-16T00:02:00.0663119700|/var/www/html/backup_pg/backup_Infraestructura_20260916_000001.sql
2026-09-16T09:59:19-0300


```

## Resumen y validación


GiB, dos decimales. Carpetas reutilizadas del 16/09/2026 09:25–09:28 -0300; bases y desglose complementario del mismo día 09:58–09:59 -0300. Totales **parciales del alcance medido y atribuido**: logs externos sin acceso y repositorios sin atribución quedan fuera de los totales por aplicación. No es una fotografía simultánea ni un promedio histórico.

| Aplicación | Código/carpetas | Adjuntos incluidos | Base principal | Respaldo BD | Total operativo | Total con respaldos | Observaciones |
|---|---:|---:|---:|---:|---:|---:|---|
| Infrawork | 38.24 | N/D | 1.79 | 1.71 | 40.03 | 47.85 | Incluye logs 0.01 GiB y contenido mixto Ejemplos_fileinput 37.85 GiB. Total con respaldos añade 6.10 GiB de archivos y 1.71 GiB de Infra_restore. |
| ADM-TECH | 6.68 | 6.62 | 0.05 | N/D | 6.74 | 6.74 | Mapeo confirmado. Base postgres con nombre habitual de mantenimiento. Sin respaldo BD informado; copias internas ya incluidas en carpeta. |
| VulnApp | 0.44 | 0.44 | 0.11 | N/D | 0.55 | 0.55 | RAM dedicada 151.41 MiB; CPU puntual 0.0%. Sin respaldo BD informado. |
| Repositorios compartidos pendientes | 591.26 | N/D | N/D | N/D | 591.26 | 591.26 | infrafilerun; separado de las aplicaciones. |
| Backups compartidos pendientes | 0.00 | N/D | N/D | N/D | 0.00 | 0.00 | Todo backup_pg atribuido a Infrawork; no duplicar. |

«Código/carpetas» es la carpeta completa, no código puro. Adjuntos y logs internos ya están incluidos y no se suman otra vez. N/D no equivale a cero. Los respaldos no informados y logs externos desconocidos no se han estimado; los totales solo suman componentes comprobados. Las copias internas permanecen en el total operativo porque la fórmula solicitada usa la carpeta completa.

Infrawork y ADM-TECH: CPU y RAM **N/D — servicio Apache compartido**. RSS compartido reutilizado: Apache 237.90 MiB, PostgreSQL 613.95 MiB y MariaDB 227.21 MiB. No se reparte entre aplicaciones ni bases.

Se validaron encabezados, cantidad de columnas, consistencia de bytes de respaldos, fórmulas sin duplicados, separación de Infra_restore y ausencia de las dos credenciales en los nuevos entregables. Archivos 01–04 sin cambios, verificados mediante SHA-256. Sin .pgpass local generado; remotos eliminados y comprobados por la propia sesión.
