from pathlib import Path
import re
R=Path(__file__).resolve().parent
report='''# Verificación de backup ADM-TECH — reanudación

**Estado final: NO LISTO.** Verificaciones reanudadas el 16/09/2026 a las 11:02:50–11:02:52 -0300, más comprobación HEAD posterior. El impedimento de acceso quedó resuelto: root confirmado, AUTH_RC=0 y SCHEMA_RC=0. Sigue pendiente preparar el destino y verificar su escritura, y confirmar el horario sin colisión. No se creó ningún directorio, script, cron ni respaldo remoto; no se utilizó contraseña PostgreSQL ni contraseña sudo.

## Resultado de las verificaciones pendientes

| Control | Estado | Resultado |
|---|---|---|
| Identidad y acceso root | LISTO | sudo -n su -c: tec-calidad05, uid=0, whoami=root |
| Conexión como Linux postgres | LISTO | postgres\u007cpostgres\u007cf\u007c58432647; AUTH_RC=0 |
| Sin credenciales heredadas ni pgpass | LISTO | Misma consulta con PGPASSFILE=/dev/null y variables retiradas: AUTH_SIN_CREDENCIALES_RC=0 |
| Servidor primario | LISTO | pg_is_in_recovery() = f |
| pg_dump --schema-only | LISTO | SCHEMA_RC=0, salida a /dev/null; sin respaldo persistido |
| Clientes PostgreSQL compatibles | LISTO | 10.12, evidencia anterior reutilizada |
| Usuario Linux postgres | LISTO | Usuario existente UID/GID 26; ejecución real comprobada |
| Directorio final disponible y escribible | BLOQUEADO | /var/backups/postgresql/admtech no existe; DEST_WRITE_RC=1 |
| Espacio e inodos | LISTO | Evidencia previa: 82.46 GiB disponibles y 173053757 inodos libres |
| Protección de extensiones Apache | LISTO | FilesMatch con sql, sql.gz y dump, Require all denied; ver interpretación HTTP abajo |
| Protección integral del destino final | NO VERIFICABLE | Fuera de DocumentRoot propuesto; ruta aún inexistente y permisos efectivos pendientes |
| Cron activo | LISTO | active/enabled, evidencia anterior |
| Horario sin colisión | NO VERIFICABLE | raid-check domingo 01:00, duración no medida; 01:30 sigue provisional |
| Retención de 30 días | REQUIERE AJUSTE | Viable en destino separado; incompatible con limpieza heredada si se usa backup_pg/admtech |
| Ausencia de secretos existentes | BLOQUEADO | Hallazgo previo en cron/script Infrawork; pendiente tratamiento y rotación |
| flock y pg_restore | LISTO | Disponibles; propuesta usa bloqueo y verificación de catálogo |

Se comprobó el comando de esquema solicitado tras AUTH_RC=0. No produjo advertencias en la ejecución observada. La prueba adicional sin archivo de claves emitió una advertencia de libpq porque /dev/null no es archivo plano, pero finalizó con código 0; confirma conexión sin usar un archivo de credenciales. No se afirma un método peer específico porque no se leyó pg_hba.conf.

## Ubicación final recomendada y limpieza de Infrawork

**Alternativa 1: /var/backups/postgresql/admtech, recomendada.** Mantiene el mismo filesystem aceptado por el responsable, conserva 30 días, queda fuera del árbol web y del alcance de la limpieza de Infrawork. No requiere modificar el backup actual para evitar que elimine archivos de ADM-TECH. El directorio padre /var/backups existe root:root 755, contexto var_t; /var/backups/postgresql y el destino aún no existen.

Alternativa 2: /var/www/html/backup_pg/admtech solo sería admisible después de corregir y verificar la limpieza de Infrawork, restringiéndola al primer nivel y al patrón backup_Infraestructura_*.sql. Además requiere permisos adecuados y protección web comprobada. Introduce dependencia de un script ajeno y mantiene copias en DocumentRoot; es menos segura. No se modificó esa limpieza.

Alternativa 3: retención efectiva de siete u ocho días no cumple el objetivo de 30 días; no recomendada.

La evidencia previa del script /opt/backup_potsgres.sh confirma `find "$BACKUP_DIR" -type f -mtime +7 -delete`, con BACKUP_DIR=/var/www/html/backup_pg. Es recursivo y sin filtro de nombres: alcanzaría archivos del subdirectorio admtech. Por el redondeo de -mtime, +7 selecciona archivos con al menos ocho días completos; la ejecución diaria añade variación. No es una política de 30 días. Se reutilizó la lectura ya realizada, sin volver a exponer el script ni sus credenciales.

## Seguridad web: archivo frente a página de error

La regla confirmada en /etc/httpd/conf.d/zz-hardening-personal.conf contiene:

```apache
<FilesMatch "\\.(bak|backup|old|orig|save|swp|tmp|sql|sql\\.gz|dump|tar|tar\\.gz|tgz|zip)$">
    Require all denied
</FilesMatch>
ErrorDocument 403 /INFRAWORK/main.php
ErrorDocument 404 /INFRAWORK/error404.php
```

Todas las solicitudes fueron HEAD, sin cuerpo, con SNI/Host infra.personal.com.py resuelto a 127.0.0.1 y validación TLS habilitada.

1. Archivo real /backup_pg/backup_Infraestructura_20260916_000001.sql: **302 Found**, Location /INFRAWORK/error.php.
2. Se siguió manualmente esa ruta exacta mediante otra solicitud HEAD: **200 OK** de /INFRAWORK/error.php.
3. El 200 corresponde a la página de error, no al dump. No se obtuvo 200/206 del respaldo real ni se descargó su contenido.

Existe una denegación explícita por extensión, y ErrorDocument 403 deriva al manejador de la aplicación. La cadena observada es compatible con esa denegación y posterior redirección del manejador. No se capturó el 403 interno ni se inspeccionó código de la aplicación, por lo que no se presenta la causalidad interna como demostrada. Tampoco se declara seguridad completa para todas las variantes/vhosts solo a partir de esta solicitud. El destino fuera de web sigue siendo la opción preferida.

## Contexto reutilizado, sin repetir relevamiento

Infrawork: cron root a medianoche ejecuta /opt/backup_potsgres.sh, SQL plano de Infraestructura en /var/www/html/backup_pg. Nueve dumps del 08 al 16/09, aproximadamente 6.10 GiB; archivos root:root 644. Primer tamaño 726628571 bytes y último 729730812: aumento de 3102241 bytes en ocho días, aproximadamente 0.37 MiB diarios por dump. Script sin bloqueo, checksum, validación ni publicación atómica observados. Autenticación existente contiene secreto, no reproducido.

También hay jobs de postgres: 22:00 lunes a viernes, backup sábado 05:00 y restauración de Infra_restore sábado 06:00. No se ejecutaron. Hay envío de correo cada minuto, sysstat cada diez minutos y raid-check domingos 01:00. Cron activo; zona del servidor America/Argentina/Buenos_Aires, UTC-03. No se vuelve a medir duración de tareas ni se infiere que hayan finalizado antes de 01:30.

Clientes /usr/pgsql-10/bin/pg_dump y pg_restore 10.12 compatibles. flock, sha256sum y logger disponibles. Filesystem raíz previamente al 89%, con espacio suficiente actualmente pero sujeto al crecimiento compartido.

## Estimación y propuesta local

30 × 58432647 / 1073741824 = **1.63 GiB** de referencia. Se basa en tamaño físico de la base, no en un dump custom medido; compresión, índices y crecimiento afectan el resultado. Añadir espacio de una copia en curso y mantener el control de al menos 5 GiB libres. Mismo filesystem aceptado; esta aceptación no aporta aislamiento frente a pérdida de ese filesystem.

propuesta_backup_admtech.sh conserva destino /var/backups/postgresql/admtech, usuario/base postgres, formato custom comprimido, umask 077, flock, temporal y movimiento atómico, pg_restore --list, checksum SHA-256, logs y retención de 30 días limitada a pares propios. Se actualizaron comentarios con las pruebas realizadas. No se instala ni ejecuta el script en esta fase.

El script ignora credenciales heredadas y usa PGPASSFILE=/dev/null; puede producir la advertencia inocua observada, sin tomar contraseña de ese dispositivo. pg_restore --list no sustituye una restauración completa de prueba. Dump y checksum se publican por separado: una interrupción entre ambos puede dejar una copia sin checksum; debe investigarse y no se informa éxito. La eliminación se hace después del nuevo respaldo verificado.

Cron local mantiene **01:30 provisional**. Debe confirmarse fin de raid-check dominical y otras tareas antes de activarlo. No se propone otro horario como libre sin evidencia.

## Próximos pasos exactos, sujetos a nueva aprobación

1. Confirmar duración/fin de las tareas nocturnas y aprobar horario; resolver el hallazgo de credenciales existentes por el procedimiento autorizado.
2. Después de aprobación explícita, crear /var/backups/postgresql/admtech con propietario postgres:postgres y modo 700; comprobar permisos de traversal, contexto SELinux adecuado y escritura efectiva como postgres. No desactivar SELinux.
3. Verificar que no exista Alias/exposición web del destino y mantener separadas las limpiezas de Infrawork y ADM-TECH. No hace falta alterar Infrawork para usar la alternativa 1.
4. Instalar script como /usr/local/sbin/backup_admtech.sh root:root 0755 solo tras la aprobación. Ejecutar primer respaldo completo en fase aprobada, comprobar checksum y logs; realizar restauración en entorno aislado autorizado, nunca sobre producción para probar.
5. Instalar cron root:root 0644 en /etc/cron.d/backup-admtech después de resolver el horario y validar primera ejecución. Confirmar alertas y monitoreo de edad del último backup y espacio.

El acceso root y PostgreSQL ya no son bloqueos. **No se cambia a LISTO PARA IMPLEMENTAR** porque la condición anterior exige destino escribible y horario sin colisión: ambos siguen pendientes. El usuario prohibió crear el directorio en esta etapa, y se respetó.

## Seguridad y validación local

No se solicitó ni utilizó contraseña sudo, al funcionar sudo -n su. No se usó contraseña PostgreSQL. Helper SSH local eliminado mediante trap; proceso y variables portadoras de la credencial SSH finalizados. No se generó .pgpass ni otro archivo remoto. Se verificó sintaxis del script local con bash -n, sin ejecutar respaldos ni borrados.

Permanece documentado el incidente previo: un filtro inicial dejó visible una credencial DB_PASS en una salida de herramienta; se saneó el archivo local y corrigió el filtro, pero no puede retirarse del historial. Corresponde rotación autorizada. No se repite el valor en estos entregables.

Un comando compuesto adicional fue rechazado por revisión automática sin razón específica visible. Se completó la revisión HTTP con solicitudes HEAD simples y lecturas específicas de reglas; no se requirió ampliar permisos ni modificar el servidor.

## Evidencias nuevas y comandos ejecutados
'''
for name in ['escalation_check','pending_root','web_pending']:
    report+='\n### '+name+'\n\n```bash\n'+(R/(name+'.sh')).read_text(encoding='utf-8')+'\n```\n\n```text\n'+(R/(name+'.txt')).read_text(encoding='utf-8')+'\n```\n'
(R/'verificacion_backup_admtech.md').write_text(report,encoding='utf-8')
secret=re.search(r'temporal:\s*(\S+)',Path(r'C:\Users\alfonzel\.codex\attachments\7051e76f-5c0e-45ac-b02a-64713544988a\pasted-text.txt').read_text(encoding='utf-8-sig')).group(1)
for name in ['verificacion_backup_admtech.md','propuesta_backup_admtech.sh','propuesta_backup_admtech.cron']:
    content=(R/name).read_text(encoding='utf-8')
    assert secret not in content
    assert not re.search(r'DB_PASS\s*=\s*(?!\[SECRETO)[^\s]+',content)
secret=None
print('Tres entregables actualizados; credencial SSH ausente; no se incluyen valores de claves PostgreSQL.')
