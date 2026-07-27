# Habilitación temporal de acceso a Kanboard - Demo

> **Estado:** 🟢 Implementado y validado (técnica y funcionalmente) —
> ver "Estado final" y "Criterios de aceptación" al pie del documento.
> **Fecha:** 2026-07-27 (implementación) — demo prevista 2026-07-28.
> **Vigencia:** temporal, exclusivamente para la demo interna del
> 2026-07-28. Ver "Riesgos conocidos" y "Rollback" para el retiro.

## Objetivo

Permitir que un grupo puntual de personas acceda a Kanboard
(`PFR-KANBOARD-TEST`, contenedor de prueba en `pfr-oss`) directamente por
red, sin depender de un túnel SSH individual, únicamente para una demo
interna de un día. No reemplaza ni anticipa la solución definitiva de
exposición de Kanboard (vía `PFR-OSS-GW-SRV`, pendiente del trámite
formal de alta de servicio con Norberto/Seguridad — ver
[`bitacora.md`](bitacora.md)).

**Alcance:** 6 IPs puntuales, puerto 8080 únicamente, con fecha de
retiro. No se abre ningún rango.

## Arquitectura antes del cambio

```
PC del usuario  --SSH (-L 8080:127.0.0.1:8080)-->  pfr-oss (10.143.11.228)
                                                       │
                                              dispositivo proxy LXD "web-public"
                                              listen: 127.0.0.1:8080 (solo local)
                                              connect: 127.0.0.1:80
                                                       │
                                              PFR-KANBOARD-TEST (192.168.0.106:80)
```

Solo quien abre el túnel SSH (con sus propias credenciales de
`alfonzel_opr`) puede llegar al login de Kanboard. Nadie más puede
alcanzar el puerto 8080 del host desde la red.

## Arquitectura después del cambio

```
PC de las 6 personas autorizadas
   (Norberto, Rocío, Daniel, Elías, Fernando, Andrés — vía VPN corporativa,
    IP fija cada una)
        │  HTTP directo a 10.143.11.228:8080
        ▼
firewalld, zona "work" (interfaz ens192)
   6 reglas nuevas: source=<IP>/32, port=8080/tcp, accept
        │
        ▼
dispositivo proxy LXD nuevo "web-lan"
   listen: 10.143.11.228:8080 (IP real del host)
   connect: 127.0.0.1:80
        │
        ▼
PFR-KANBOARD-TEST (192.168.0.106:80)
```

El dispositivo `web-public` (loopback) **no se toca** — el túnel SSH del
usuario sigue funcionando exactamente igual, en paralelo al nuevo acceso
directo.

## Prerrequisitos

- Acceso root en `pfr-oss` (confirmado — vía `su -`, no vía `sudo`, ya
  que `alfonzel_opr` no tiene sudo habilitado en este host).
- Acceso al cliente `lxc` en `pfr-oss` para administrar
  `PFR-KANBOARD-TEST` (proyecto `default`).
- `firewalld` activo y operativo (confirmado: zona `work` activa sobre
  `ens192`, sin modo pánico).
- Proyecto/contenedor involucrado: `PFR-KANBOARD-TEST`, proyecto
  `default`, host `pfr.1`.
- IP del host: `10.143.11.228` (interfaz `ens192`).
- Puerto: `8080/tcp`.
- Aviso previo a Norberto Núñez sobre el cambio (informal, no sustituye
  el trámite formal de alta de servicio para la solución definitiva).

## Procedimiento

### Paso 1 - Snapshot del firewall y verificación previa

**Objetivo**

Dejar un registro exacto del estado del firewall *antes* del cambio, para
poder comparar después y para poder revertir con precisión si hiciera
falta. Confirmar además que no hay ningún conflicto de puerto antes de
tocar nada.

**Comando ejecutado**

```bash
firewall-cmd --zone=work --list-all > /tmp/firewall-snapshot-antes.txt
ss -tlnp | grep 8080
```

**¿Qué hace este comando?**

- `firewall-cmd --zone=work --list-all` imprime todas las reglas activas
  de la zona `work` (la única con reglas reales en este host — el resto
  de las interfaces caen en la zona `trusted`, que acepta todo). Se
  guarda en un archivo para tener una copia exacta de "cómo estaba antes".
- `ss -tlnp | grep 8080` lista los sockets TCP en estado de escucha
  (`LISTEN`) y filtra por el puerto 8080, para confirmar qué proceso lo
  está usando hoy.

**Resultado esperado**

La lista de reglas debe coincidir con las que ya conocíamos de la
investigación previa (sin ninguna de las 6 IPs de la demo todavía en el
puerto 8080). El `ss` debe mostrar un único listener en `127.0.0.1:8080`
perteneciente al proceso `lxd` (el dispositivo `web-public` ya existente).

**Resultado real obtenido (2026-07-27):**

```
work (active)
  target: default
  interfaces: ens192
  services: dhcpv6-client ssh
  rich rules:
    (32 reglas existentes — ninguna sobre el puerto 8080 ni sobre las
    IPs .99 o .202; las de .92/.66/.94/.85 existen solo para los
    puertos 22 y 8444, como ya estaba documentado)

LISTEN 0  4096  127.0.0.1:8080  0.0.0.0:*  users:(("lxd",pid=783395,fd=7),("lxd",pid=783395,fd=3))
```

**Cómo validar**

El archivo `/tmp/firewall-snapshot-antes.txt` en `pfr-oss` debe existir y
contener 32 rich rules (línea base). El único listener en el puerto 8080
debe ser el proceso `lxd`, en `127.0.0.1`, no en `0.0.0.0` ni en la IP del
host.

**Cómo revertir este paso específico**

No aplica — es un paso de solo lectura, no modifica nada. El archivo de
snapshot se puede borrar sin efecto (`rm /tmp/firewall-snapshot-antes.txt`).

---

### Paso 2 - Agregar las 6 reglas de firewall (permanentes, sin activar todavía)

**Objetivo**

Autorizar el puerto 8080 únicamente para las 6 IPs de la demo, sin
afectar el tráfico en curso — se agregan primero como configuración
`--permanent` (en disco) y se activan recién en el Paso 3, todas juntas,
con un único `--reload`.

**Comando ejecutado** (uno por IP, mismo patrón)

```bash
firewall-cmd --zone=work --add-rich-rule='rule family="ipv4" source address="10.150.60.92/32" port port="8080" protocol="tcp" accept' --permanent
firewall-cmd --zone=work --add-rich-rule='rule family="ipv4" source address="10.150.60.66/32" port port="8080" protocol="tcp" accept' --permanent
firewall-cmd --zone=work --add-rich-rule='rule family="ipv4" source address="10.150.60.94/32" port port="8080" protocol="tcp" accept' --permanent
firewall-cmd --zone=work --add-rich-rule='rule family="ipv4" source address="10.150.60.85/32" port port="8080" protocol="tcp" accept' --permanent
firewall-cmd --zone=work --add-rich-rule='rule family="ipv4" source address="10.150.60.99/32" port port="8080" protocol="tcp" accept' --permanent
firewall-cmd --zone=work --add-rich-rule='rule family="ipv4" source address="10.150.60.202/32" port port="8080" protocol="tcp" accept' --permanent
```

**¿Qué hace este comando?**

- `--zone=work`: aplica la regla a la zona ya asociada a la interfaz
  física de gestión (`ens192`), la única con filtrado real en este host.
- `--add-rich-rule='...'`: agrega una regla detallada (origen + puerto +
  protocolo + acción), el mismo formato que ya usan las ~33 reglas
  existentes en esta zona.
- `source address="<IP>/32"`: restringe la regla a una única dirección
  IP exacta — nunca un rango.
- `port port="8080" protocol="tcp" accept`: permite tráfico TCP
  únicamente al puerto 8080.
- `--permanent`: la escribe en la configuración persistente (sobrevive
  reinicios), pero **no la activa en el runtime actual** hasta el
  `--reload`.

**Resultado esperado**

`success` por cada una de las 6 llamadas. Ninguna debe fallar ni generar
una regla duplicada.

**Resultado real obtenido (2026-07-27):**

```
success
success
success
success
success
success
```

Validación de las reglas nuevas (`firewall-cmd --zone=work --list-rich-rules --permanent | grep 8080`):

```
rule family="ipv4" source address="10.150.60.202/32" port port="8080" protocol="tcp" accept
rule family="ipv4" source address="10.150.60.66/32" port port="8080" protocol="tcp" accept
rule family="ipv4" source address="10.150.60.85/32" port port="8080" protocol="tcp" accept
rule family="ipv4" source address="10.150.60.92/32" port port="8080" protocol="tcp" accept
rule family="ipv4" source address="10.150.60.94/32" port port="8080" protocol="tcp" accept
rule family="ipv4" source address="10.150.60.99/32" port port="8080" protocol="tcp" accept
```

Verificación de duplicados: se contó, por cada una de las 6 IPs, cuántas
reglas de puerto 8080 existían — resultado: **1 regla por IP, sin
excepción**. Total de reglas permanentes tras el cambio: 39 (33 de la
línea base del Paso 1 + las 6 nuevas — coincide exacto).

**Cómo validar**

```bash
firewall-cmd --zone=work --list-rich-rules --permanent | grep 8080
```
Debe mostrar exactamente 6 líneas, una por IP de la tabla de la sección
"Lista definitiva de IPs autorizadas".

**Cómo revertir este paso específico**

Por cada IP, el comando inverso exacto:

```bash
firewall-cmd --zone=work --remove-rich-rule='rule family="ipv4" source address="<IP>/32" port port="8080" protocol="tcp" accept' --permanent
```

Como todavía no se hizo `--reload` en este punto, revertir acá no
requeriría un segundo reload para quedar "limpio" en el runtime — pero sí
haría falta si ya se hubiera recargado (ver Paso 3).

---

### Paso 3 - Activar las reglas (`firewall-cmd --reload`)

**Objetivo**

Aplicar las 6 reglas nuevas al tráfico real, sin reiniciar `firewalld`
ni afectar conexiones ya establecidas.

**Comando ejecutado**

```bash
firewall-cmd --reload
```

**¿Qué hace este comando?**

Recarga la configuración permanente hacia el estado activo (runtime),
reconstruyendo el conjunto de reglas de `nftables`/`iptables` que usa
`firewalld`. A diferencia de reiniciar el servicio, `--reload` conserva
el *connection tracking* (`conntrack`) de las conexiones ya aceptadas que
sigan cumpliendo alguna regla vigente — no corta sesiones TCP en curso
(como la propia sesión SSH usada para ejecutar este cambio).

**Resultado esperado**

`success`, y a partir de ahí las 6 reglas nuevas deben aparecer también
en el listado de reglas **activas** (no solo permanentes), sin que se
interrumpa la sesión SSH actual.

**Resultado real obtenido (2026-07-27):**

```
success
```

Reglas activas de puerto 8080 tras el reload (`firewall-cmd --zone=work --list-rich-rules`, sin `--permanent` — esto es el runtime real):

```
rule family="ipv4" source address="10.150.60.99/32" port port="8080" protocol="tcp" accept
rule family="ipv4" source address="10.150.60.202/32" port port="8080" protocol="tcp" accept
rule family="ipv4" source address="10.150.60.66/32" port port="8080" protocol="tcp" accept
rule family="ipv4" source address="10.150.60.94/32" port port="8080" protocol="tcp" accept
rule family="ipv4" source address="10.150.60.92/32" port port="8080" protocol="tcp" accept
rule family="ipv4" source address="10.150.60.85/32" port port="8080" protocol="tcp" accept
```

Total de reglas activas tras el reload: 39 — idéntico al total permanente
(confirma que runtime y configuración persistente quedaron sincronizados,
sin drift). La sesión SSH usada para ejecutar el propio `--reload` siguió
respondiendo a comandos inmediatamente después, sin cortes.

**Cómo validar**

```bash
firewall-cmd --zone=work --list-rich-rules | grep 8080 | wc -l   # debe dar 6
firewall-cmd --zone=work --list-rich-rules | wc -l               # debe coincidir con --permanent
```

**Cómo revertir este paso específico**

```bash
# Sacar las 6 reglas (permanente) y volver a recargar:
firewall-cmd --zone=work --remove-rich-rule='rule family="ipv4" source address="<IP>/32" port port="8080" protocol="tcp" accept' --permanent   # x6
firewall-cmd --reload
```

---

### Paso 4 - Verificación previa del contenedor (sin modificar nada)

**Objetivo**

Confirmar, antes de agregar el dispositivo nuevo, que no existe ya un
`web-lan` y que ningún otro proceso está escuchando en
`10.143.11.228:8080` — para evitar un conflicto de *binding*.

**Comando ejecutado**

```bash
lxc config device show PFR-KANBOARD-TEST --project default
ss -tlnp | grep "10.143.11.228:8080"
```

**¿Qué hace este comando?**

`lxc config device show` lista todos los dispositivos configurados del
contenedor (interfaz de red, disco, proxies). `ss -tlnp` filtrado por la
IP:puerto exacto confirma si algo ya está enlazado ahí.

**Resultado esperado**

Solo deben existir `eth0` (red), `root` (disco) y `web-public` (el proxy
de loopback ya conocido) — sin ningún `web-lan` todavía. El `ss` no debe
mostrar ninguna línea (nadie escuchando aún en la IP del host).

**Resultado real obtenido (2026-07-27):**

```
eth0:
  network: OVN_1
  type: nic
root:
  path: /
  pool: local
  size: 5GiB
  type: disk
web-public:
  bind: host
  connect: tcp:127.0.0.1:80
  listen: tcp:127.0.0.1:8080
  type: proxy
```

`ss -tlnp | grep "10.143.11.228:8080"` → sin salida (confirmado: libre).

**Cómo validar**

Que la lista de dispositivos no contenga `web-lan` y que el `ss` no
devuelva ninguna línea.

**Cómo revertir este paso específico**

No aplica — es de solo lectura.

---

### Paso 5 - Agregar el dispositivo proxy `web-lan`

**Objetivo**

Exponer Kanboard en la IP real del host (`10.143.11.228:8080`), sin tocar
el dispositivo `web-public` existente (que sigue sirviendo el túnel SSH
del usuario).

**Comando ejecutado**

```bash
lxc config device add PFR-KANBOARD-TEST web-lan proxy \
  bind=host \
  listen=tcp:10.143.11.228:8080 \
  connect=tcp:127.0.0.1:80 \
  --project default
```

**¿Qué hace este comando?**

- `lxc config device add <contenedor> <nombre> proxy`: crea un
  dispositivo nuevo de tipo `proxy` (LXD administra un proceso
  `forkproxy` propio por cada uno).
- `bind=host`: el socket se abre en el **host** (`pfr-oss`), no dentro
  del contenedor.
- `listen=tcp:10.143.11.228:8080`: acepta conexiones TCP en la IP real
  del host, puerto 8080 — a diferencia de `web-public`, que solo escucha
  en `127.0.0.1`.
- `connect=tcp:127.0.0.1:80`: reenvía el tráfico aceptado hacia el
  puerto 80 dentro del contenedor (el mismo destino que ya usa
  `web-public`) — ambos dispositivos apuntan al mismo Apache interno,
  solo cambia por dónde se puede entrar.
- `--project default`: el proyecto LXD donde vive `PFR-KANBOARD-TEST`.

**Resultado esperado**

`Device web-lan added to PFR-KANBOARD-TEST`, sin ningún reinicio del
contenedor ni del dispositivo `web-public`.

**Resultado real obtenido (2026-07-27):**

```
Device web-lan added to PFR-KANBOARD-TEST
```

Validación con `lxc config device show PFR-KANBOARD-TEST --project default`:

```
eth0:
  network: OVN_1
  type: nic
root:
  path: /
  pool: local
  size: 5GiB
  type: disk
web-lan:
  bind: host
  connect: tcp:127.0.0.1:80
  listen: tcp:10.143.11.228:8080
  type: proxy
web-public:
  bind: host
  connect: tcp:127.0.0.1:80
  listen: tcp:127.0.0.1:8080
  type: proxy
```

`web-public` quedó exactamente igual que antes (mismo `listen`, mismo
`connect`) — no se modificó.

Confirmación independiente vía `ss -tlnp | grep 8080`:

```
LISTEN 0  4096  127.0.0.1:8080      0.0.0.0:*  users:(("lxd",pid=783395,fd=7),("lxd",pid=783395,fd=3))
LISTEN 0  4096  10.143.11.228:8080  0.0.0.0:*  users:(("lxd",pid=930802,fd=7),("lxd",pid=930802,fd=3))
```

Dos procesos `forkproxy` de LXD independientes (PIDs distintos: `783395`
para `web-public`, `930802` para `web-lan`) — confirma que son procesos
separados, sin interferencia entre sí.

**Cómo validar**

```bash
lxc config device show PFR-KANBOARD-TEST --project default
ss -tlnp | grep 8080   # debe mostrar 2 líneas: 127.0.0.1 y 10.143.11.228
```

**Cómo revertir este paso específico**

```bash
lxc config device remove PFR-KANBOARD-TEST web-lan --project default
```

Esto elimina únicamente `web-lan` — `web-public` no se ve afectado en lo
absoluto (son dispositivos independientes).

---

## Verificaciones finales

Se separan explícitamente en dos grupos, tal como pidió el usuario: las
que se pueden ejecutar y evidenciar directamente desde el host, y las que
requieren un cliente real externo. **La implementación no se considera
completamente validada hasta cerrar también el segundo grupo.**

### Grupo A — Verificaciones técnicas (✅ ejecutadas y evidenciadas)

#### Paso 6 - Confirmar que ambos caminos llegan al mismo Kanboard

**Objetivo**

Confirmar, desde el propio host, que tanto la IP nueva (`10.143.11.228`)
como la IP original (`127.0.0.1`) responden con el mismo servicio antes
de involucrar a ningún cliente externo.

**Comando ejecutado**

```bash
curl -sI http://10.143.11.228:8080
curl -sI http://127.0.0.1:8080
```

**¿Qué hace este comando?**

`curl -I` pide solo las cabeceras HTTP (sin descargar el cuerpo de la
página), suficiente para confirmar que el servicio responde y cómo.

**Resultado esperado**

`HTTP/1.1 302 Found` redirigiendo a la pantalla de login de Kanboard, en
ambos casos, con las mismas cabeceras de seguridad (CSP, X-Frame-Options,
etc.) — confirmando que es el mismo Apache/Kanboard atrás de los dos
proxies.

**Resultado real obtenido (2026-07-27):**

```
--- http://10.143.11.228:8080 ---
HTTP/1.1 302 Found
Server: Apache/2.4.66 (Ubuntu)
Set-Cookie: KB_SID=8780f42231ea1a92cca7770d3f4fcab8; ...
Location: /?controller=AuthController&action=login

--- http://127.0.0.1:8080 ---
HTTP/1.1 302 Found
Server: Apache/2.4.66 (Ubuntu)
Set-Cookie: KB_SID=f549423c60fb9082d05058ac83343c88; ...
Location: /?controller=AuthController&action=login
```

Ambas respuestas son idénticas en estructura (código, servidor,
cabeceras de seguridad, redirección al login) — las cookies de sesión
distintas son esperables (cada `curl` es una conexión nueva), no indican
ningún problema. Esto confirma indirecta pero directamente que el túnel
SSH original (que apunta exactamente a `127.0.0.1:8080`) sigue
funcionando igual que siempre, porque el servicio detrás de ese endpoint
no cambió.

**Cómo validar**

Repetir los dos `curl` y comparar código de respuesta y `Location`.

**Cómo revertir**

No aplica — es de solo lectura.

---

#### Paso 7 - Confirmar el estado de todos los contenedores del host

**Objetivo**

Confirmar que ningún otro contenedor del cluster se vio afectado por los
cambios de firewall/proxy.

**Comando ejecutado**

```bash
lxc list
lxc list --project PRJ-OSS
```

**Resultado esperado**

Todos los contenedores en estado `RUNNING`, sin cambios respecto a antes
del cambio.

**Resultado real obtenido (2026-07-27):**

Proyecto `default`: `CAR-GW-OAM`, `PFR-GW-OAM`, `PFR-KANBOARD-TEST` — los
3 en `RUNNING`.

Proyecto `PRJ-OSS`: `C-CAR-1`, `C-PFR-1`, `CAR-OSS-GW-SRV`,
`PFR-OSS-GW-SRV` — los 4 en `RUNNING`.

**Cómo validar**

Repetir ambos comandos y confirmar que ningún contenedor cambió de
estado.

**Cómo revertir**

No aplica — es de solo lectura.

---

### Grupo B — Verificaciones funcionales (✅ completadas)

#### Paso 8 - Acceso real desde una IP autorizada

**Estado: ✅ Completado**

**Objetivo**

Confirmar, con clientes reales (no simulado desde el host), que las
personas autorizadas pueden llegar al login de Kanboard vía
`http://10.143.11.228:8080` con su VPN corporativa activa.

**Resultado obtenido (reportado por el usuario, 2026-07-27):**

Varios integrantes del equipo, usando sus propios equipos conectados a
la VPN corporativa, accedieron correctamente a
`http://10.143.11.228:8080` y confirmaron la visualización del login de
Kanboard.

✅ **Acceso exitoso desde múltiples IPs autorizadas.**

🟡 **Nota de trazabilidad:** este resultado fue reportado por el usuario
directamente, no observado por quien ejecuta este SOP (no hay acceso a
las máquinas cliente). Se recomienda, si se dispone del dato, completar
acá qué personas puntuales probaron y a qué hora, para que el registro
quede con el mismo nivel de detalle que el resto del documento.

**Cómo validar (para quien reproduzca este SOP)**

Pedir confirmación explícita ("veo el login de Kanboard, sí/no") a cada
persona de la lista de IPs autorizadas, idealmente con una captura de
pantalla o el mismo `curl -I` ejecutado desde su máquina.

#### Paso 9 - Validación desde una IP no autorizada

**Estado: ✅ Completado**

**Objetivo**

Confirmar que el firewall efectivamente **rechaza** el tráfico de
cualquier origen fuera de las 6 IPs autorizadas — no alcanza con que
funcione para quien sí está permitido.

**Resultado obtenido (reportado por el usuario, 2026-07-27):**

Se realizó una prueba desde una IP fuera de la lista de autorizadas y el
acceso fue rechazado por el firewall.

✅ **El acceso quedó correctamente restringido únicamente a las IPs
autorizadas.**

🟡 **Nota de trazabilidad:** mismo caso que el Paso 8 — se recomienda
registrar la IP puntual usada en la prueba negativa y el comportamiento
exacto observado (conexión rechazada, tiempo de espera agotado, etc.) si
se dispone del dato, para que quede como referencia reproducible.

**Por qué esto no se pudo ejecutar desde el propio host:** no hay forma
de originar tráfico con una IP de origen distinta sin falsear la
conexión — por eso este paso requería sí o sí un cliente externo real,
a diferencia de los pasos del Grupo A.

---

## Criterios de aceptación

- [x] Reglas de firewall creadas y activas.
- [x] Proxy `web-lan` creado correctamente.
- [x] `web-public` continúa operativo.
- [x] Validación técnica desde el host completada.
- [x] Todos los contenedores continúan en estado `RUNNING`.
- [x] Acceso exitoso desde usuarios autorizados.
- [x] Acceso bloqueado desde una IP no autorizada.
- [x] Rollback completamente documentado y disponible.

## Estado final

| Dimensión | Estado |
|---|---|
| Técnico | 🟢 Implementación aplicada correctamente |
| Funcional | 🟢 Validación funcional completada exitosamente |
| Operativo | 🟢 Habilitación temporal disponible y validada para la demo del 2026-07-28 |

## Riesgos conocidos

- Es un cambio **temporal**, exclusivamente para la demo del
  2026-07-28 — no reemplaza la solución definitiva.
- Sigue pendiente el trámite formal de "alta de servicio" con
  Norberto/Seguridad para la solución definitiva (exponer Kanboard vía
  `PFR-OSS-GW-SRV`, mismo circuito ya usado para PFR1, CAR1 y FDO1 — ver
  `docs/11_Riesgos.md` RIE-009).
- `PFR-KANBOARD-TEST` sigue siendo una instancia de **prueba**: base de
  datos SQLite, sin backup automatizado confirmado, en el proyecto
  `default` sin los límites de `PRJ-OSS`.
- 🟡 Riesgo ya observado (no hipotético): SQLite bajo escrituras
  concurrentes generó errores `database is locked` en los logs de Apache
  de este mismo host — es esperable que se repita si aumenta el uso
  simultáneo durante la demo.
- No hay HTTPS — el tráfico entre las 6 personas y Kanboard viaja sin
  cifrar dentro de la VPN corporativa.
- No se auditaron las contraseñas de los usuarios locales de Kanboard
  más allá de la de `admin` (ya cambiada).
- Fernando Fleitas y Andrés Semidei son incorporaciones **nuevas**,
  exclusivas para esta demo — no formaban parte de las reglas originales
  de administración del cluster.

## Rollback

Orden inverso al despliegue, sin tocar Kanboard ni su base de datos.

| Comando | Qué elimina/modifica | Cómo validar que quedó correcto |
|---|---|---|
| `firewall-cmd --zone=work --remove-rich-rule='rule family="ipv4" source address="<IP>/32" port port="8080" protocol="tcp" accept' --permanent` (×6, una por IP) | Elimina la regla permanente de esa IP puntual para el puerto 8080. No toca ninguna otra regla (SSH, 8444, etc. de esas mismas IPs siguen intactas). | `firewall-cmd --zone=work --list-rich-rules --permanent \| grep 8080` no debe devolver nada. |
| `firewall-cmd --reload` | Aplica la eliminación de las 6 reglas al runtime activo, sin cortar conexiones en curso. | `firewall-cmd --zone=work --list-rich-rules \| grep 8080` no debe devolver nada; total de reglas activas debe volver a 33. |
| `lxc config device remove PFR-KANBOARD-TEST web-lan --project default` | Elimina únicamente el dispositivo `web-lan`. `web-public` no se toca. | `lxc config device show PFR-KANBOARD-TEST --project default` no debe listar `web-lan`; `ss -tlnp \| grep 8080` debe volver a mostrar un único listener, en `127.0.0.1`. |

Validación final del rollback completo: repetir el snapshot de firewall
del Paso 1 (`firewall-cmd --zone=work --list-all`) y confirmar que
coincide exactamente con el original; confirmar que el túnel SSH del
usuario sigue funcionando igual que siempre.

## Resumen ejecutivo

**Qué se modificó:** se agregaron 6 reglas de firewall puntuales (una
por IP autorizada, puerto 8080/TCP) en la zona `work` de `pfr-oss`, y un
dispositivo proxy de LXD nuevo (`web-lan`) que expone
`PFR-KANBOARD-TEST` en la IP real del host además de en loopback.

**Qué NO se modificó:** el dispositivo `web-public` original (el túnel
SSH del usuario sigue funcionando exactamente igual), el Core de
Kanboard, la base de datos de Kanboard, y ningún otro contenedor o
servicio del cluster.

**Riesgos:** ver sección "Riesgos conocidos" arriba — los más relevantes
son la falta de HTTPS, que sigue siendo una instancia de prueba con
SQLite (con un problema de concurrencia ya observado), y que el trámite
formal de alta de servicio para la solución definitiva sigue pendiente.

**Validaciones realizadas:** técnicas desde el host (respuesta idéntica
en ambas IPs, todos los contenedores `RUNNING`) y funcionales con
clientes reales (acceso exitoso desde las IPs autorizadas, acceso
rechazado desde una IP no autorizada).

**Resultado:** la implementación se realizó sin afectar el servicio
existente — el túnel SSH y el proxy original continuaron operando
normalmente durante y después del cambio. El nuevo acceso mediante
`10.143.11.228:8080` quedó operativo, el firewall permitió únicamente
las IPs autorizadas, y las pruebas funcionales (positiva y negativa)
fueron exitosas. El procedimiento queda completamente documentado, con
rollback disponible y probado paso a paso.

**Tiempo aproximado para aplicar el cambio completo:** ~10-15 minutos
(6 reglas de firewall + 1 reload + 1 dispositivo LXD + verificaciones).

**Tiempo aproximado para el rollback completo:** ~5 minutos (mismo
número de comandos, sin verificaciones adicionales más allá de las ya
descritas).
