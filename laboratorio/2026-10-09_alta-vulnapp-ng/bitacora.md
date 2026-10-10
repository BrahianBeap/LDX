# Bitácora — Alta de VulnApp NG (2026-10-09)

Todos los comandos se ejecutaron por SSH contra `pfr-oss` (`10.143.11.228`), con `lxc exec`/`lxc file push` hacia los contenedores del proyecto `PRJ-OSS`. Los perfiles, los contenedores y las 4 reglas de `ACL-OVN-1` (paso 0) se crearon en la sesión anterior a la que registra el resto de esta bitácora, antes de que se resumiera la conversación — se reconstruyen acá a partir del estado real del cluster (`lxc profile show`, `lxc config show`, `lxc network acl show`), re-verificado en vivo el 2026-10-10. El resto de la bitácora (pasos 1 en adelante) sí se registró en el momento.

---

## 0. Creación de la plataforma (perfiles, contenedores, ACL, snapshot)

### Perfiles

```bash
lxc profile create PRF-VULNAPP-DB --project PRJ-OSS
lxc profile create PRF-VULNAPP-APP --project PRJ-OSS
```

Contenido real aplicado con `lxc profile edit <nombre> --project PRJ-OSS` (confirmado con `lxc profile show`):

```yaml
name: PRF-VULNAPP-DB
description: Perfil PostgreSQL 18 para VulnApp NG
config:
  cloud-init.network-config: |
    #cloud-config
    version: 2
    ethernets:
      eth0:
        dhcp4: true
        dhcp6: false
        routes:
          - to: 10.150.32.100
            via: 192.168.0.6
        nameservers:
          addresses:
            - 192.168.0.254
  cloud-init.user-data: |
    #cloud-config
    apt:
      http_proxy: "http://10.150.32.100:3128"
      https_proxy: "http://10.150.32.100:3128"
    package_update: true
    package_upgrade: true
  limits.cpu: "2"
  limits.memory: 2GiB
  limits.processes: "500"
devices:
  eth0:
    ipv4.address: 192.168.0.13
    network: OVN_1
    type: nic
  root:
    path: /
    pool: local
    size: 20GiB
    type: disk
```

`PRF-VULNAPP-APP` es igual, salvo la IP (`192.168.0.14`) y una ruta extra hacia `10.150.0.0/16` (necesaria para llegar a la API de SDI y a la pasarela de SMS, ver paso 7 más abajo):

```yaml
name: PRF-VULNAPP-APP
description: Perfil aplicacion (Flask/Gunicorn) para VulnApp NG
config:
  cloud-init.network-config: |
    #cloud-config
    version: 2
    ethernets:
      eth0:
        dhcp4: true
        dhcp6: false
        routes:
          - to: 10.150.0.0/16
            via: 192.168.0.6
          - to: 10.150.32.100
            via: 192.168.0.6
        nameservers:
          addresses:
            - 192.168.0.254
  cloud-init.user-data: |
    #cloud-config
    apt:
      http_proxy: "http://10.150.32.100:3128"
      https_proxy: "http://10.150.32.100:3128"
    package_update: true
    package_upgrade: true
  limits.cpu: "2"
  limits.memory: 2GiB
  limits.processes: "500"
devices:
  eth0:
    ipv4.address: 192.168.0.14
    network: OVN_1
    type: nic
  root:
    path: /
    pool: local
    size: 20GiB
    type: disk
```

### Contenedores

Imagen usada: el fingerprint de una imagen ya cacheada localmente en el host (`40eba84d6225`, Ubuntu 26.04 LTS minimal, serial `20260618`), no el alias remoto `ubuntu-minimal:resolute` — evita depender de salida a internet desde el host en el momento de crear el contenedor, algo que este cluster restringe.

```bash
lxc launch 40eba84d6225 PFR-VULNAPP-DB --project PRJ-OSS --target pfr.1 --profile PRF-VULNAPP-DB
lxc launch 40eba84d6225 PFR-VULNAPP-APP --project PRJ-OSS --target pfr.1 --profile PRF-VULNAPP-APP
```

`--target pfr.1`: sitio Franco, el único donde vive VulnApp NG (sin alta disponibilidad, DEC-042). Confirmado con `lxc list --project PRJ-OSS`: los dos contenedores quedaron `RUNNING`, con las IP del perfil (`.13` y `.14`).

### ACL-OVN-1 (las 4 reglas nuevas)

```bash
lxc network acl rule add ACL-OVN-1 ingress \
    action=allow source=192.168.0.14 destination=192.168.0.13 \
    protocol=tcp destination_port=5432 \
    "description=vulnapp-app hacia Postgres de vulnapp-db"

lxc network acl rule add ACL-OVN-1 ingress \
    action=allow source=192.168.0.1 destination=192.168.0.14 \
    protocol=tcp destination_port=5000 \
    "description=Balanceador PFR hacia Gunicorn de vulnapp-app"

lxc network acl rule add ACL-OVN-1 ingress \
    action=allow source=192.168.0.14 destination=10.150.58.116 \
    protocol=tcp destination_port=443 \
    "description=vulnapp-app hacia API SDI (ciberseg3.sis.personal.net.py)"

lxc network acl rule add ACL-OVN-1 ingress \
    action=allow source=192.168.0.14 destination=10.150.31.68 \
    protocol=tcp destination_port=80 \
    "description=vulnapp-app hacia pasarela SMS /ntf"
```

Confirmado con `lxc network acl show ACL-OVN-1 --project default` — ver el listado completo (estas 4 más las preexistentes) en [05_Configuracion.md — Firewall de la red OVN_1](../../docs/05_Configuracion.md#firewall-de-la-red-ovn_1-lxc-network-acl).

### Snapshot de la base de datos

```bash
lxc config set PFR-VULNAPP-DB snapshots.schedule "0 */6 * * *" --project PRJ-OSS
lxc config set PFR-VULNAPP-DB snapshots.expiry "7d" --project PRJ-OSS
```

Mismo patrón que Kanboard (cada 6 horas, retiene 7 días).

### Hallazgo al re-verificar esto en vivo (2026-10-10)

`192.168.0.13` y `.14` cayeron en un tramo de `OVN_1` que [02_Arquitectura.md](../../docs/02_Arquitectura.md#direccionamiento-ip-confirmado) tenía documentado como "`.12`–`.99`, sin asignar todavía" — en los hechos, `.11` y `.12` ya estaban tomados (`C-Colector-1` y `C-Loki-1`, respectivamente) antes de este alta. Esa tabla quedó corregida el mismo día que se encontró esto — ver la actualización en ese documento.

---

## 1. Primer intento de `01_instalar_db.sh` — falla

```
lxc exec PFR-VULNAPP-DB --project PRJ-OSS --env VULNAPP_DB_PASSWORD='<clave>' -- \
    bash /root/vulnapp-ng-lxd/runbook/lxd/01_instalar_db.sh
```

Avanza hasta "5/6 Restauracion del dump" (`pg_restore` sin errores), y falla en el bloque siguiente que reasigna dueños:

```
ERROR:  cannot change owner of sequence "areas_id_seq"
DETAIL:  Sequence "areas_id_seq" is linked to table "areas".
CONTEXT:  SQL statement "ALTER SEQUENCE areas_id_seq OWNER TO vulnapp"
```

Causa: la secuencia está vinculada automáticamente a una columna `SERIAL`/`IDENTITY` de `areas` — PostgreSQL no permite reasignarle el dueño por separado (ver [TRB-014](../../docs/07_Troubleshooting.md#trb-014--no-se-puede-reasignar-el-dueño-de-una-secuencia-vinculada-a-una-columna-serial-o-identity)). Como el bloque es una única transacción, el `DROP`/`ALTER` previo se revirtió entero: la base quedó con todo a nombre de `postgres`, sin estado intermedio. Reportado sin tocar el script ni el contenedor, a la espera de un paquete corregido.

## 2. Paquete corregido y re-intento de `01_instalar_db.sh`

Paquete nuevo (`vulnapp-ng-lxd_20261009_1916.tar.gz`, sha256 verificado) subido al host por SFTP, paquete y carpeta `/root/vulnapp-ng-lxd` anteriores borrados en ambos contenedores, extraído y verificado (`sha256sum -c --quiet SHA256SUMS && echo integridad OK`) en los dos.

Re-ejecución **sin** `--reemplazar` (la base ya tenía datos de la corrida anterior):

```
== 5/6 Restauracion del dump
[19:23:38] OK  La base vulnapp ya tiene 25 tablas: NO se restaura. Para volver a restaurar: --reemplazar
[19:23:39] OK  Todas las tablas, vistas y secuencias son de vulnapp; estadisticas actualizadas

== 6/6 Conteos contra produccion
   igual     areas                        11
   ... (19 tablas, todas "igual")
[19:23:40] OK  Las 19 tablas coinciden con produccion
[19:23:40] Vistas: 6 | activas hoy: 26817
```

✅ Base de datos lista.

## 3. Primer intento de `02_instalar_app.sh` — falla

Pasos 1/7 a 5/7 OK (Python 3.14.4, código copiado, venv con Flask 3.1.3/psycopg 3.3.6/gunicorn 23.0.0, conexión a la base OK: `hosts activos=5070 | vulnerabilidades activas=26817`). Falla en 6/7 al arrancar `vulnapp.service`: los 30 renglones que el propio script muestra en el error no alcanzan a mostrar la causa. Se consultó `journalctl -u vulnapp -n 150 --no-pager` directamente (diagnóstico de solo lectura) para ver el traceback completo:

```
File "/opt/vulnapp/app/app.py", line 103, in <module>
    os.makedirs(UPLOAD_FOLDER)
PermissionError: [Errno 13] Permission denied: '/opt/vulnapp/app/uploads'
```

Causa: el paso 2/7 deja `/opt/vulnapp/app` en modo `u=rwX,g=rX,o=` (dueño `root:www-data`) — el grupo `www-data`, con el que corre Gunicorn, tiene lectura/ejecución pero no escritura, y `app.py` intenta crear `uploads/` al importarse. Reportado sin tocar nada.

## 4. Paquete corregido y re-intento de `02_instalar_app.sh`

Paquete nuevo (`vulnapp-ng-lxd_20261009_2025.tar.gz`, sha256 verificado), llevado **solo** a `PFR-VULNAPP-APP` (la base no necesitaba nada nuevo). Se limpiaron los paquetes/carpetas anteriores en el host, en `PFR-VULNAPP-DB` (que ya no necesitaba ningún paquete) y en `PFR-VULNAPP-APP`.

```
== 4/7 Configuracion (/opt/vulnapp/env.conf)
[20:27:35] Se conserva la SECRET_KEY existente.
== 5/7 Conexion a la base (192.168.0.13)
[20:27:35] OK  La aplicacion llega a la base
[20:27:35] OK  La aplicacion se importa como www-data
== 6/7 Servicio vulnapp.service (Gunicorn en 192.168.0.14:5000)
[20:27:39] OK  Servicio activo
== 7/7 Comprobacion
[20:27:39] OK  http://192.168.0.14:5000/vulnapp/login responde 200
[20:27:39] Redireccion sin sesion: /vulnapp/login
[20:27:39] OK  La aplicacion conserva el prefijo /vulnapp en sus redirecciones
```

✅ Aplicación instalada.

## 5. Publicar en el gateway (`LB.conf` de `PFR-GW-SRV`)

Backup previo: `cp LB.conf LB.conf.bak_20261009_antes-vulnapp`. Bloque agregado **antes** de la regla general de Kanboard:

```apache
RequestHeader set X-Forwarded-Proto "https"
ProxyPass        /vulnapp http://192.168.0.14:5000/vulnapp
ProxyPassReverse /vulnapp http://192.168.0.14:5000/vulnapp
```

**Primer intento de `apache2ctl configtest`:**

```
AH00526: Syntax error on line 79 of /etc/apache2/sites-enabled/LB.conf:
Invalid command 'RequestHeader', perhaps misspelled or defined by a module not included in the server configuration
```

`mod_headers` no estaba habilitado en este gateway (`ls /etc/apache2/mods-enabled/` no lo tenía). Se restauró el backup de inmediato — Apache siguió corriendo con la config original, Kanboard no se vio afectado en ningún momento. Ver [TRB-015](../../docs/07_Troubleshooting.md#trb-015--requestheader-falla-con-invalid-command-porque-mod_headers-no-está-habilitado).

Se habilitó el módulo (`a2enmod headers`) y se reintentó el mismo despliegue:

```
apache2ctl configtest → Syntax OK
systemctl reload apache2 → (sin salida, exit 0)
systemctl is-active apache2 → active
```

Nota del equipo (2026-10-09): la causa y la solución quedaron anotadas también como paso previo en el README del paquete de instalación (`DockerLab/vulnapp-ng`), para que una instalación futura en otro gateway no se tope con lo mismo sin aviso.

**Verificación de que Kanboard sigue respondiendo** (dentro del contenedor, loopback): `curl -sk https://127.0.0.1/` → `HTTP 302` (igual que antes del cambio).

**Prueba de `/vulnapp`** (loopback):

```
$ curl -sk -D - -o /dev/null https://127.0.0.1/vulnapp/login
HTTP/1.1 200 OK
Server: gunicorn

$ curl -sk -D - -o /dev/null https://127.0.0.1/vulnapp/dashboard
HTTP/1.1 302 FOUND
Location: /vulnapp/login
Set-Cookie: session=...; HttpOnly; Path=/vulnapp
```

## 6. Prueba externa (desde fuera del contenedor gateway, contra `10.143.11.8`)

```
$ curl -sk -D - -o /dev/null https://10.143.11.8/vulnapp/login
HTTP/1.1 200 OK
Server: gunicorn

$ curl -sk -D - -o /dev/null https://10.143.11.8/vulnapp/dashboard
HTTP/1.1 302 FOUND
Location: /vulnapp/login
Set-Cookie: session=...; HttpOnly; Path=/vulnapp

$ curl -sk -o /dev/null -w "HTTP %{http_code}\n" https://10.143.11.8/
HTTP 302   # Kanboard, sin cambios
```

✅ Confirmado desde afuera del contenedor, no solo en loopback.

## 7. Alcance hacia SDI y hacia la pasarela de SMS (sin ejecutar `03_instalar_carga.sh`)

Prueba de conexión TCP pura (sin enviar ni recibir datos de aplicación, sin ninguna clave) desde `PFR-VULNAPP-APP`:

```python
socket.connect(('10.150.58.116', 443))  # SDI
socket.connect(('10.150.31.68', 80))    # SMS
```

Resultado:

```
10.150.58.116:443 -> NO CONECTA ([Errno 113] No route to host)
10.150.31.68:80   -> CONECTA (TCP handshake OK), socket local: ('192.168.0.14', 55340)
```

`ip route get` muestra que **ambos** destinos usan la misma ruta dentro del contenedor (`via 192.168.0.6 dev eth0 src 192.168.0.14`) — el fallo no es de ruteo ni de `ACL-OVN-1` (la regla `192.168.0.14 → 10.150.58.116:443` existe y está `enabled`, confirmado con `lxc network acl show ACL-OVN-1`). El filtrado ocurre después de `192.168.0.6`, fuera de lo que administra este cluster LXD.

**Sobre qué IP ve el destino:** no se pudo determinar con certeza. `192.168.0.6` no es un contenedor de este cluster (no aparece en `lxc list`), y el host `pfr-oss` no tiene reglas NAT visibles sin privilegios de `root` (`sudo iptables -t nat -S` no autorizado para esta cuenta) ni una ruta propia hacia `10.150.0.0/16` — solo ve `192.168.0.0/24` como red local del uplink OVN. Es decir, `192.168.0.6` y lo que haya más allá son responsabilidad de Seguridad/Redes, no de este cluster. El README de la aplicación ya anotaba esto como una incógnita a confirmar ("probablemente `10.143.11.228`") — sigue sin confirmarse. Ver [RIE-015](../../docs/11_Riesgos.md#rie-015--conectividad-de-vulnapp-ng-hacia-la-api-de-sdi-bloqueada).

No se instaló ni se ejecutó `03_instalar_carga.sh` (paso 4 del runbook) — queda explícitamente pendiente de que Seguridad habilite el destino.

## 8. Snapshot programado de `PFR-VULNAPP-DB`

Se copió el patrón ya usado en Kanboard. Config real leída desde el contenedor que sirve Kanboard en producción (`PFR-KANBOARD-TEST`, proyecto `default` — el nombre es heredado de un despliegue de prueba que terminó siendo el real, ver [13_Linea_de_Tiempo.md](../../docs/13_Linea_de_Tiempo.md)):

```
snapshots.schedule = "0 */6 * * *"   (cada 6 horas)
snapshots.expiry   = "7d"            (retiene 7 días)
```

Aplicado igual en `PFR-VULNAPP-DB`:

```
lxc config set PFR-VULNAPP-DB snapshots.schedule '0 */6 * * *' --project PRJ-OSS
lxc config set PFR-VULNAPP-DB snapshots.expiry '7d' --project PRJ-OSS
```

Confirmado con `lxc config get` (ambos valores devueltos tal cual se escribieron).

> No se replicó el resto del patrón de Kanboard (copia cruzada a otro sitio vía `kanboard-dr-sync.sh`) porque no fue parte de lo pedido para este alta — VulnApp NG es explícitamente sin alta disponibilidad (DEC-042, repositorio de la aplicación). Si en el futuro se decide agregar DR, el script de Kanboard es la referencia directa.

## 9. Limpieza final

```
# PFR-VULNAPP-APP: paquete y carpeta extraída (incluye el dump de produccion) — ya no hace falta
lxc exec PFR-VULNAPP-APP --project PRJ-OSS -- sh -c \
  'find /root -maxdepth 1 -name "*.tar.gz" -print -delete; rm -rf /root/vulnapp-ng-lxd'

# Host: paquete remanente en el home
find /home/alfonzel_opr -maxdepth 1 -name "*.tar.gz" -print -delete
```

Confirmado por `ls -la` en ambos lugares: no queda ningún `.tar.gz` ni la carpeta `vulnapp-ng-lxd`. `PFR-VULNAPP-DB` ya había quedado limpio en un paso anterior (no necesitaba ningún paquete). El código de la aplicación vive en `/opt/vulnapp` dentro de `PFR-VULNAPP-APP`, no depende del paquete borrado.

---

## Diferencias respecto al README de la aplicación

1. **`mod_headers` no estaba habilitado en `PFR-GW-SRV`** — el README de la aplicación asume que `RequestHeader` ya funciona; en este gateway hubo que habilitar el módulo primero (`a2enmod headers` + reload). Ya anotado en el README de la aplicación como paso previo, por pedido del equipo.
2. **Los dos bugs de los scripts** (secuencia vinculada, permisos de `uploads/`) no son de la plataforma LXD — se detectaron ejecutando el runbook de la aplicación por primera vez contra datos reales, tal como anticipaba su propio README ("los scripts no se probaron todavía en LXD").
3. El paso 11 del plan original (confirmar la IP de origen hacia SDI) **no se pudo cerrar**: se confirmó que el bloqueo no es de este cluster, pero no se pudo determinar la IP exacta que ve el destino por falta de visibilidad más allá de `192.168.0.6`.
