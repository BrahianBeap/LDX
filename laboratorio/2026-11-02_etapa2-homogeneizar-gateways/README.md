# Etapa 2 — Homogeneizar CAR y FDO con PFR (handoff en curso)

> **Estado (2026-11-02):** CAR y FDO ✅ **aplicados** (ver [Parte A](#resultado-de-la-parte-a-2026-11-02) y [Parte B](#resultado-de-la-parte-b-2026-11-02)). `/adm` publicado en ambos. Falta de la Parte C: ingreso con AD por navegador en CAR y FDO, y HSTS. 
> **Para quien retoma:** esta bitácora es autocontenida. Leer primero el contexto, después ejecutar la Parte A.

---

## Contexto — por qué urge

El 02/11 se cargaron en el DNS las **3 IP** de `oss.personal.com.py` (`10.143.11.8` Franco, `10.11.11.12` Fernando, `192.168.91.117` Carpinelli) **antes de terminar la Etapa 2**. El plan era pedirlas recién después ([ADR-0008](../../docs/adr/ADR-0008-gateway-balanceador-dos-etapas.md), [PENDIENTES.md](../../PENDIENTES.md)).

Consecuencia = exactamente [RIE-020](../../docs/11_Riesgos.md#rie-020--gateways-de-car-y-fdo-no-homogéneos-con-pfr-bloquean-el-dns-compartido): **2 de cada 3 accesos a `oss.personal.com.py` fallan** porque solo PFR está configurado. CAR y FDO exigen certificado de cliente en todo el vhost y apuntan Kanboard a un backend muerto.

**Decisión mientras se completa la Etapa 2:** o se revierte el DNS a 1 IP (`10.143.11.8`), o se termina la Etapa 2 ya. Se eligió terminar la Etapa 2.

---

## Estado real de los 3 gateways (verificado 02/11, `grep` sobre `LB.conf`)

| Elemento | **PFR (modelo OK)** | **CAR** | **FDO** |
|---|---|---|---|
| `SSLVerifyClient` del vhost | `optional` | 🔴 `require` | 🔴 `require` |
| `<Location "/"> none` | ✅ | 🔴 falta | 🔴 falta |
| `require` propio en `/ntf` | ✅ | ⚠️ hereda del vhost | ⚠️ hereda del vhost |
| Kanboard → backend | `192.168.0.106` ✅ | 🔴 `CAR-kanboard-1` (muerto) | 🔴 `CAR-kanboard-1` (muerto) |
| `/vulnapp` → `192.168.0.14:5000` | ✅ | 🔴 falta | 🔴 falta |
| `/web.config` bloqueado | ✅ | 🔴 no | 🔴 no |
| `/supervisionge` | no | no | ✅ (`FDO-WS-1:8001`, solo FDO) |
| HSTS | ✅ | 🔴 no | 🔴 no |
| `<VirtualHost *:80>` (Loki + redirect) | — | ✅ igual a PFR | ✅ igual a PFR |
| `balancer://NTF` y `balancer://loki` | — | ✅ **idénticos a PFR** | (confirmar en el archivo completo) |

**Reachability confirmada (02/11):** desde `CAR-GW-SRV`, `192.168.0.106:80` → **OK** y `192.168.0.14:5000` → **OK**. No hay riesgo de 502 en CAR.

---

## Decisiones tomadas

- CAR y FDO **hacen proxy a los contenedores de Franco** (las apps viven solo ahí). Kanboard → `192.168.0.106`, VulnApp → `192.168.0.14:5000`. No se crean apps locales en CAR/FDO.
- **`/ntf` conserva `SSLVerifyClient require` propio** en el `<Location>` — imprescindible: al pasar el vhost a `optional`, sin esto `/ntf` quedaría abierto.
- **Fuera de CAR/FDO por ahora:** `/adm` (ADM-TECH dev) y `/kanboard-prueba` (dev, IP restringida). Son dev, en Franco. "Lo otro, como estaba planeado", en una pasada posterior.

---

## PARTE A — CAR-GW-SRV (listo para aplicar)

Config final: [`LB_car.conf`](LB_car.conf) (= el `LB.conf` de PFR sin los 2 bloques dev). Procedimiento controlado ([06_Operacion.md](../../docs/06_Operacion.md)): **el `reload` no se corre hasta ver `Syntax OK`**.

### A.1 — Baseline + backup + push + configtest (NO recarga)

```bash
# 0) Baseline: configtest actual de CAR (debe decir Syntax OK antes de tocar nada)
lxc exec CAR-GW-SRV --project PRJ-OSS -n -- apache2ctl configtest

# 1) Backup con fecha
lxc exec CAR-GW-SRV --project PRJ-OSS -n -- \
  cp /etc/apache2/sites-available/LB.conf /root/LB.conf.bak-20261102-etapa2
lxc exec CAR-GW-SRV --project PRJ-OSS -n -- ls -l /root/LB.conf.bak-20261102-etapa2

# 2) Empujar el LB.conf nuevo. Pegar el contenido de LB_car.conf entre las marcas EOF.
cat <<'EOF' | lxc file push - CAR-GW-SRV/etc/apache2/sites-available/LB.conf --project PRJ-OSS --uid 0 --gid 0 --mode 0644
<...  CONTENIDO COMPLETO DE LB_car.conf  ...>
EOF

# 3) Validar sintaxis (NO recarga todavia)
lxc exec CAR-GW-SRV --project PRJ-OSS -n -- apache2ctl configtest
```

> **Gate:** continuar al paso A.2 **solo si el paso 3 dice `Syntax OK`**. Si no, rollback (abajo).

### A.2 — Reload + verificación

```bash
# 4) Recargar Apache y confirmar que quedó activo
lxc exec CAR-GW-SRV --project PRJ-OSS -n -- systemctl reload apache2
lxc exec CAR-GW-SRV --project PRJ-OSS -n -- systemctl is-active apache2

# 5) Verificar comportamiento contra la IP de CAR (192.168.91.117), por nombre.
#    Ejecutar desde un host que tenga curl (pfr-oss o un contenedor); ajustar si no.
curl -sI --resolve oss.personal.com.py:443:192.168.91.117 https://oss.personal.com.py/           # portal  -> 200
curl -sI --resolve oss.personal.com.py:443:192.168.91.117 https://oss.personal.com.py/kanboard/  # Kanboard -> 302/200
curl -sI --resolve oss.personal.com.py:443:192.168.91.117 https://oss.personal.com.py/vulnapp/   # VulnApp  -> 302/200
curl -sI --resolve oss.personal.com.py:443:192.168.91.117 https://oss.personal.com.py/ntf         # /ntf sin cert -> 403 (sigue protegido)
```

Esperado: el navegador entra sin pedir certificado; Kanboard/VulnApp/portal responden; `/ntf` sigue exigiendo certificado de cliente. Las respuestas deben coincidir con las de PFR (`10.143.11.8`).

### A.3 — Rollback (si falla el configtest o la verificación)

```bash
lxc exec CAR-GW-SRV --project PRJ-OSS -n -- \
  cp /root/LB.conf.bak-20261102-etapa2 /etc/apache2/sites-available/LB.conf
lxc exec CAR-GW-SRV --project PRJ-OSS -n -- apache2ctl configtest
lxc exec CAR-GW-SRV --project PRJ-OSS -n -- systemctl reload apache2
```

### Resultado de la Parte A (2026-11-02)

✅ Aplicado comando por comando, ejecutado por el usuario en `pfr-oss`.

| Comprobación | Resultado |
|---|---|
| `configtest` antes y después del cambio | `Syntax OK` en ambos |
| Portal (`/var/www/html/index.html`) | Mismo tamaño y fecha en PFR y CAR; no hizo falta copiarlo |
| Uso de `/ntf` por CAR | ✅ 0 pedidos en `/access.log`, que cubre desde el 2026-09-06 |
| Backup | `/root/LB.conf.bak-20261102-etapa2`, SHA-256 `1d57afc0…a34b194`, idéntico al original |
| `LB.conf` nuevo | SHA-256 `bd5125f9…1148d02`, igual a [`LB_car.conf`](LB_car.conf) con fin de línea LF |
| `reload` | `apache2` queda `active` |

| Ruta (por nombre, contra cada IP) | CAR | PFR |
|---|---|---|
| `/` | 200 | 200 |
| `/kanboard/` | 302 | 302 |
| `/vulnapp/` | 302 | 302 |
| `/web.config` | 403 | 403 |
| `/ntf` sin certificado | 403 | 403 |

🔴 **Sin probar por CAR:** el ingreso completo con AD en un navegador y un envío a `/ntf` con certificado de cliente. Como nadie usó `/ntf` por CAR desde el 2026-09-06, lo segundo no afecta a clientes conocidos.

---

## PARTE B — FDO-GW-SRV (pendiente, con cuidados)

FDO es el **único con riesgo de producción**: **Tembiapó manda los SMS por `/ntf` a través de Fernando (`10.11.11.12`)** con un stack viejo (CentOS 7, PHP 5.4, **NSS 3.44**). Al pasar el certificado de cliente de "todo el vhost" a "solo `/ntf`", pasa a pedirse por **renegociación TLS post-handshake**, que ese cliente puede no soportar. El cambio de `ntf-ca.crt` en Tembiapó (26/10) resolvió el cert **del servidor**, no esto.

### Hallazgos del 2026-11-02 (solo lectura, no aplicar FDO todavía)

| Comprobación | Resultado |
|---|---|
| `LB.conf` completo de FDO | ✅ `NTF` y `loki` iguales a CAR. Lo único propio es `/supervisionge`, con `Require ip` para `10.150.60.92`, `10.11.11.24` y `10.11.11.23` |
| Alcance desde FDO | ✅ `192.168.0.106:80` y `192.168.0.14:5000` responden |
| Tráfico en `/access.log` (desde 18/08) | ✅ 38.536 `POST /ntf` con 200 desde Tembiapó (`10.11.11.24`), y 103.634 `GET /supervisionge/lsNE` con 200 desde `10.11.11.23` |
| Clientes | ✅ `10.11.11.23` usa `Go-http-client/1.1`. Tembiapó envía sin `User-Agent`, con un `curl/7.29.0` aislado |

🟡 **Grafana:** Go no soporta autenticación posterior al handshake en TLS 1.3 ni renegociación por defecto, según lo conocido de su biblioteca TLS (no probado acá). Por eso `SSLVerifyClient require` por ruta probablemente cortaría `/supervisionge`.

✅ **Tembiapó:** el SMS de prueba enviado por PFR llegó (confirmado por el usuario, 2026-11-02). PFR ya pide el certificado por ruta en `/ntf`, así que FDO puede usar el mismo esquema.

**Decisión para `/supervisionge`:** conservar el certificado sin pedirlo después de conectar. Con `SSLVerifyClient optional` en el vhost, Apache lo solicita durante la conexión inicial. La ruta mantiene `optional`, para que no haya una segunda solicitud, y exige `SSL_CLIENT_VERIFY == 'SUCCESS'` además de la IP. 🟡 Grafana debería seguir funcionando porque hoy ya presenta su certificado al conectar; se confirma en el log tras el `reload`. Se descarta el DNS con 2 IP: el responsable mantiene las 3.

Configuración final: [`LB_fdo.conf`](LB_fdo.conf).

### Pasos previos obligatorios antes de tocar FDO

1. **Traer el `LB.conf` completo de FDO** y confirmar los `BalancerMember` de `NTF`/`loki` y el contenido exacto de `<Location '/supervisionge'>`:
   ```bash
   lxc exec FDO-GW-SRV --project PRJ-OSS -n -- cat /etc/apache2/sites-available/LB.conf
   ```
2. **Confirmar reachability desde FDO** a los backends de Franco:
   ```bash
   for HP in 192.168.0.106:80 192.168.0.14:5000; do
     printf '%s -> ' "$HP"
     lxc exec FDO-GW-SRV --project PRJ-OSS -n -- timeout 5 bash -c ": < /dev/tcp/${HP%:*}/${HP#*:}" && echo OK || echo FALLA
   done
   ```
3. **Ventana con SMS de prueba de Tembiapó listo + rollback cargado.** Aplicar el mismo procedimiento que CAR (backup → push → configtest → reload) y **enseguida** disparar un SMS real desde Tembiapó. Si sale → cerrado. Si no → rollback inmediato.

### Config de FDO = la de CAR + el bloque `/supervisionge` (solo FDO)

Partir de `LB_car.conf` y **agregar**, en el `<VirtualHost *:443>`, el bloque de Comap/Grafana que hoy ya tiene FDO:

```apache
    # Supervisionge (Comap/Grafana) — solo Fernando
    <Location '/supervisionge'>
      ProxyPass http://FDO-WS-1:8001/api/1/supervisionge
      # NBTECSVAASU18 Norberto Nunez
      Require ip 10.150.60.92
      # Tembiapo
      Require ip 10.11.11.24
      # Grafana - Observabilidad
      Require ip 10.11.11.23
    </Location>
```

> **Advertencia:** los `Require ip` son obligatorios. Sin ellos, la ruta quedaría abierta al pasar el vhost a `optional`. Falta decidir el manejo del certificado: ver los [hallazgos del 2026-11-02](#hallazgos-del-2026-11-02-solo-lectura-no-aplicar-fdo-todavía).

### Resultado de la Parte B (2026-11-02)

✅ Aplicado comando por comando, ejecutado por el usuario en `pfr-oss`, con [`LB_fdo.conf`](LB_fdo.conf). `reload` a las **19:03:31 UTC**.

| Comprobación | Resultado |
|---|---|
| `configtest` antes y después del cambio | `Syntax OK` en ambos |
| Backup | `/root/LB.conf.bak-20261102-etapa2`, SHA-256 `a70840b6…23dcf1f`, idéntico al original |
| `LB.conf` nuevo | SHA-256 `8895d016…93ca3e66` |
| SMS real de Tembiapó después del cambio | ✅ Llegó (confirmado por el usuario); además `POST /ntf` con 200 a las 19:03:46 |
| Grafana | ✅ `GET /supervisionge/lsNE` con 200 a las 19:03:38 y 19:04:38 |

Rutas pedidas desde el propio gateway, porque `pfr-oss` no llega a `10.11.11.12`:

| Ruta | Código |
|---|---|
| `/` | 200 |
| `/kanboard/` | 302 |
| `/vulnapp/` | 302 |
| `/web.config` | 403 |
| `/ntf` sin certificado | 403 |
| `/supervisionge/lsNE` sin certificado | 403 |

🔴 **Sin probar:** que `/supervisionge` rechace una IP autorizada sin certificado. El 403 local también lo produce la restricción por IP, así que esa prueba no alcanza. Falta una prueba desde `10.150.60.92` sin certificado.

**Rollback:**

```bash
lxc exec FDO-GW-SRV --project PRJ-OSS -n -- cp -p /root/LB.conf.bak-20261102-etapa2 /etc/apache2/sites-available/LB.conf
lxc exec FDO-GW-SRV --project PRJ-OSS -n -- apache2ctl configtest
lxc exec FDO-GW-SRV --project PRJ-OSS -n -- systemctl reload apache2
```

---

## PARTE C — Cierre (cuando CAR y FDO estén homogéneos)

0. ✅ **`/adm` publicado en CAR y FDO (2026-11-02):** los accesos que caían en esos gateways daban `404`. Ambos hacen proxy a `192.168.0.19`, igual que PFR; no hizo falta regla de ACL porque ya llegaban. `LB_car.conf` y `LB_fdo.conf` incluyen el bloque, así que sus huellas pasan a ser `03d1ab3e…51abb37` y `6019a79d…351e784`. Backups previos: `/root/LB.conf.bak-20261102-adm`. En CAR, `/adm` da 302 y `/adm/` da 200, igual que PFR. En FDO se probó desde el gateway con el mismo resultado, y después del `reload` (19:15:59 UTC) Grafana y Tembiapó siguieron con 200. `/kanboard-prueba` queda solo en PFR por decisión: es una ruta de prueba con acceso por IP, y se entra por `10.143.11.8`.
1. Verificar que las **3 IP** sirven Kanboard/VulnApp/portal igual que PFR, y que `/ntf` sigue protegido en las 3. ✅ Rutas verificadas; 🔴 falta probar el ingreso con AD en un navegador por CAR y FDO.
2. Subir HSTS a `max-age=31536000` en los 3 (compromiso del ticket #1083416, ya vencido el plazo del 02/11).
3. Actualizar el repo:
   - [RIE-020](../../docs/11_Riesgos.md) → cerrado, con referencia a esta bitácora.
   - [PENDIENTES.md](../../PENDIENTES.md) sección 2 (Etapa 2) y la fila DNS #1079305.
   - Nota en la [bitácora del certificado](../2026-10-26_certificado-lets-encrypt/README.md) (HSTS en CAR/FDO).
4. Retomar lo diferido: `/adm` y `/kanboard-prueba` en CAR/FDO si se decide homogeneizar también el dev.

---

## Referencias

- [ADR-0008 — Gateway + balanceador en dos etapas](../../docs/adr/ADR-0008-gateway-balanceador-dos-etapas.md)
- [RIE-020](../../docs/11_Riesgos.md#rie-020--gateways-de-car-y-fdo-no-homogéneos-con-pfr-bloquean-el-dns-compartido)
- [Bitácora del certificado Let's Encrypt (26/10)](../2026-10-26_certificado-lets-encrypt/README.md)
- [06_Operacion.md — Modificar el LB.conf de un gateway de forma controlada](../../docs/06_Operacion.md)
