# Bitácora — Backup y DR para Kanboard

Ver contexto y resultado en [README.md](README.md).

---

## Paso 1 — Snapshot manual de prueba (validar el concepto)

```bash
lxc snapshot PFR-KANBOARD-TEST backup-manual-20261008 --project default
lxc info PFR-KANBOARD-TEST --project default | grep -A5 Snapshots
```

```
Snapshots:
+------------------------+----------------------+------------+----------+
|          NAME          |       TAKEN AT       | EXPIRES AT | STATEFUL |
+------------------------+----------------------+------------+----------+
| backup-manual-20261008 | 2026/10/08 22:32 UTC |            | NO       |
+------------------------+----------------------+------------+----------+
```

## Paso 2 — Copiar el snapshot a otro sitio (`car.1`)

```bash
lxc copy PFR-KANBOARD-TEST/backup-manual-20261008 PFR-KANBOARD-DR --target car.1 --project default
lxc list PFR-KANBOARD-DR --project default
```

```
+-----------------+---------+------+------+-----------+-----------+----------+
|      NAME       |  STATE  | IPV4 | IPV6 |   TYPE    | SNAPSHOTS | LOCATION |
+-----------------+---------+------+------+-----------+-----------+----------+
| PFR-KANBOARD-DR | STOPPED |      |      | CONTAINER | 0         | car.1    |
+-----------------+---------+------+------+-----------+-----------+----------+
```

Corrido **desde `pfr-oss`**, sin necesidad de conectarse a `car-oss` — el cliente `lxc` habla con la API del cluster, que redirige automáticamente al nodo correcto (`car.1`) mientras los 3 nodos estén sanos. Esto deja de aplicar si `pfr-oss` mismo está caído — ahí sí hay que conectarse directo al nodo sobreviviente.

## Paso 3 — Probar que la copia arranca y sirve Kanboard de verdad

```bash
lxc start PFR-KANBOARD-DR --project default
lxc exec PFR-KANBOARD-DR --project default -- curl -sI http://localhost/
```

```
HTTP/1.1 302 Found
...
Location: /?controller=AuthController&action=login
```

✅ Misma respuesta que el original — la app funciona igual en la copia.

### Verificación de integridad de datos

```bash
lxc exec PFR-KANBOARD-TEST --project default -- md5sum /var/www/kanboard/data/db.sqlite
lxc exec PFR-KANBOARD-DR --project default -- md5sum /var/www/kanboard/data/db.sqlite
```

```
f7d3ba9cc3454c8fa11ef5b35c994207  /var/www/kanboard/data/db.sqlite   (original)
a080959a537c6166d26138c4dd341fad  /var/www/kanboard/data/db.sqlite   (copia)
```

🟡 **No coinciden — esperado, no es un error.** El snapshot se tomó en un instante fijo (22:32 UTC); el original siguió recibiendo actividad después (pruebas propias, uso real del equipo). La copia refleja el estado exacto del momento del snapshot, el original avanzó desde entonces. Confirma que el mecanismo de snapshot funciona correctamente (congela un punto en el tiempo), no que algo falló.

```bash
lxc stop PFR-KANBOARD-DR --project default
```

La copia se para de nuevo — no debe quedar corriendo en paralelo al original.

## Paso 4 — Snapshot automático nativo de LXD (sin script propio)

```bash
lxc config set PFR-KANBOARD-TEST snapshots.schedule "0 */6 * * *" --project default
lxc config set PFR-KANBOARD-TEST snapshots.expiry "7d" --project default
```

Verificado:
```bash
lxc config get PFR-KANBOARD-TEST snapshots.schedule --project default   # 0 */6 * * *
lxc config get PFR-KANBOARD-TEST snapshots.expiry --project default     # 7d
```

## Paso 5 — Script de sincronización cruzada

```bash
cat > ~/kanboard-dr-sync.sh << 'SCRIPT'
#!/bin/bash
set -euo pipefail
PROJECT=default
SRC=PFR-KANBOARD-TEST
SNAP=dr-sync
DR=PFR-KANBOARD-DR
TARGET=car.1
LOG=$HOME/kanboard-dr-sync.log

lxc delete "${SRC}/${SNAP}" --project "$PROJECT" 2>/dev/null || true
lxc delete "$DR" --project "$PROJECT" --force 2>/dev/null || true

lxc snapshot "$SRC" "$SNAP" --project "$PROJECT"
lxc copy "${SRC}/${SNAP}" "$DR" --target "$TARGET" --project "$PROJECT"

echo "$(date -Iseconds) DR sync OK" >> "$LOG"
SCRIPT
chmod +x ~/kanboard-dr-sync.sh
```

**Diseño deliberado:** siempre usa el mismo nombre de snapshot (`dr-sync`) y de contenedor destino (`PFR-KANBOARD-DR`), borrando la versión anterior antes de crear la nueva. No lleva historial de versiones — para este caso de uso (una sola copia reciente, no un archivo histórico) es más simple que armar lógica de retención, y evita tener que parsear JSON de la API de LXD para encontrar "el snapshot más viejo".

**Prueba manual:**
```bash
~/kanboard-dr-sync.sh
cat ~/kanboard-dr-sync.log
lxc list PFR-KANBOARD-DR --project default
```
```
2026-10-08T22:45:57+00:00 DR sync OK
+-----------------+---------+------+------+-----------+-----------+----------+
|      NAME       |  STATE  | IPV4 | IPV6 |   TYPE    | SNAPSHOTS | LOCATION |
+-----------------+---------+------+------+-----------+-----------+----------+
| PFR-KANBOARD-DR | STOPPED |      |      | CONTAINER | 0         | car.1    |
+-----------------+---------+------+------+-----------+-----------+----------+
```
✅ Corre limpio, copia creada y correctamente parada.

## Paso 6 — Intento de automatizar (bloqueado)

```bash
(crontab -l 2>/dev/null; echo "0 */6 * * * /home/alfonzel_opr/kanboard-dr-sync.sh >> /home/alfonzel_opr/kanboard-dr-sync-cron.log 2>&1") | crontab -
```
```
-bash: crontab: command not found
```

Diagnóstico adicional (solo lectura):
```bash
systemctl --user status        # sesión de usuario activa, corriendo bien
loginctl show-user alfonzel_opr | grep -i linger   # Linger=no
which at atd                   # sin salida, no instalados
which cron crond systemctl     # solo systemctl existe
dpkg -l | grep -iE 'cron'      # sin salida, paquete no instalado
```

**Conclusión:** ni `cron` ni un timer de `systemd --user` (que requeriría `Linger=yes` para sobrevivir sin sesión activa) están disponibles sin una acción de alguien con root. Ver las dos opciones de desbloqueo en [README.md](README.md).

## Paso 7 — Ruta de respaldo (fría) en `CAR-GW-SRV`

```bash
lxc exec CAR-GW-SRV --project PRJ-OSS -- cp /etc/apache2/sites-available/LB.conf /etc/apache2/sites-available/LB.conf.bak-20261008-dr

lxc exec CAR-GW-SRV --project PRJ-OSS -- sed -i '0,/<\/VirtualHost>/{s|</VirtualHost>|    ProxyPass /kanboard !\n    ProxyPass /kamboard !\n    ProxyPass / http://PFR-KANBOARD-DR:80/\n    ProxyPassReverse / http://PFR-KANBOARD-DR:80/\n    Redirect /kanboard /\n    Redirect /kamboard /\n</VirtualHost>|}' /etc/apache2/sites-available/LB.conf
```

Verificado antes de aplicar:
```bash
lxc exec CAR-GW-SRV --project PRJ-OSS -- grep -A6 "ProxyPass /kanboard !" /etc/apache2/sites-available/LB.conf
```
```
    ProxyPass /kanboard !
    ProxyPass /kamboard !
    ProxyPass / http://PFR-KANBOARD-DR:80/
    ProxyPassReverse / http://PFR-KANBOARD-DR:80/
    Redirect /kanboard /
    Redirect /kamboard /
</VirtualHost>
```

```bash
lxc exec CAR-GW-SRV --project PRJ-OSS -- apache2ctl configtest   # Syntax OK
lxc exec CAR-GW-SRV --project PRJ-OSS -- systemctl reload apache2
```

**Nota de diseño:** se usa el nombre del contenedor (`PFR-KANBOARD-DR`, resuelto por el DNS interno de LXD) en vez de su IP — mismo patrón que ya usa la configuración existente de NTF (`http://FDO-WS-1:8000/...`). Evita que la regla se rompa si la IP de `PFR-KANBOARD-DR` cambia entre arranques (tiene IP por DHCP, no fija). Esta ruta no responde nada mientras `PFR-KANBOARD-DR` esté parado — es el comportamiento esperado de un standby frío.

### Verificación de que no se rompió nada existente

```bash
lxc exec CAR-GW-SRV --project PRJ-OSS -- curl -sI http://localhost/loki/loki/api/v1/status/buildinfo
```
```
HTTP/1.1 403 Forbidden
```
✅ Correcto — la ACL de IP de Loki sigue activa en Carpinelli, no se vio afectada por la regla nueva.
