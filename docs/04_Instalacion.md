# 04 — Instalación del cluster LXD

> **Audiencia:** Ingenieros de infraestructura que instalarán nuevos nodos.
> **Propósito:** Procedimiento completo y reproducible para instalar y configurar un nodo LXD. Seguir este documento en orden estricto.

---

## Prerrequisitos

Antes de comenzar, verificar que se cumplen todos estos requisitos:

| Prerrequisito | Verificación | Responsable |
|---|---|---|
| VM con Ubuntu LTS disponible | `lsb_release -a` | SBA/AIT (Cristian) |
| Disco dedicado para ZFS (mínimo 100 GB, recomendado 300+ GB) | `lsblk` | SBA/AIT |
| Acceso SSH a la VM | `ssh usuario@IP` | SBA/AIT |
| Acceso a internet (proxy HTTP o directo) | `curl -I https://cloud-images.ubuntu.com` | Nicolás (seguridad) |
| IP de la VM en red de gestión (/29) | `ip addr` | SBA/AIT |
| Segunda interfaz de red dedicada a servicio de contenedores (VLAN local del sitio) | `ip addr` | Cristian |
| Reloj del sistema sincronizado (NTP) — ver Paso 10 | `timedatectl` | Equipo técnico |

> **Nota:** La VLAN de la interfaz de servicio **no necesita ser la misma** en todos los sitios — solo el **nombre** de la interfaz debe coincidir en todos los miembros del cluster (ver Paso 0). Ver [ADR-0006](adr/ADR-0006-wireguard-underlay-ovn-multisitio.md).

---

## Paso 0: Renombrar las interfaces de red con `netplan`

### Objetivo
Asegurar que la interfaz de gestión y la interfaz de servicio tengan **el mismo nombre en todos los nodos del cluster**, independientemente del nombre que el sistema operativo les haya asignado originalmente (ej. `NS35`, `NS37`).

### Explicación
LXD exige que las interfaces usadas por la red virtualizada del cluster tengan nombres idénticos en todos los miembros. Esto es necesario porque, cuando un contenedor migra de un nodo a otro, se lleva consigo su configuración de red (incluido el nombre de la interfaz a la que está asociado) — si el nodo destino no tiene una interfaz con ese mismo nombre, la migración queda inconsistente. Ver el detalle completo en [02_Arquitectura.md](02_Arquitectura.md) y [ADR-0006](adr/ADR-0006-wireguard-underlay-ovn-multisitio.md).

### Comando

Editar el archivo de `netplan` correspondiente (`/etc/netplan/*.yaml`) y usar `match` por dirección MAC junto con `set-name`:

```yaml
network:
  ethernets:
    nicsrv1:
      match:
        macaddress: "AA:BB:CC:DD:EE:FF"   # MAC real de la interfaz física de servicio
      set-name: nicsrv1                    # Nombre forzado, igual en todos los nodos
```

### Explicación de parámetros

| Parámetro | Descripción |
|---|---|
| `match.macaddress` | Dirección MAC real de la interfaz física (obtenida con `ip link`). Es el dato que identifica a la interfaz — no cambia entre reinicios. |
| `set-name` | Nombre lógico forzado para esa interfaz, independiente del nombre que le asignó el sistema operativo. Debe ser idéntico en todos los nodos del cluster que compartan esa función de red. |

### Cómo verificar
```bash
ip link
# La interfaz debe aparecer con el nombre forzado (ej. nicsrv1) en todos los nodos
```

> **Nota:** Este mismo criterio aplica a la interfaz de gestión (ej. `ns192`).

---

## Paso 1: Instalar LXD

### Objetivo
Instalar el daemon LXD en la VM. LXD se distribuye como snap, lo que garantiza versiones reproducibles y actualizaciones automáticas.

### Comando

```bash
snap install lxd
```

### Explicación
`snap install lxd` descarga e instala LXD desde el Snap Store de Canonical. La versión snap es la versión oficial y recomendada. No usar el paquete `lxd` de los repositorios deb del sistema operativo (es la versión antigua y discontinuada).

### Parámetros
Sin parámetros. El snap toma automáticamente la versión estable más reciente (5.21 al momento de la reunión).

### Resultado esperado
```
lxd 5.21 from Canonical✓ installed
```

### Cómo verificar
```bash
snap list lxd
# Debe mostrar: lxd  5.21  ...  stable  canonical✓
```

### Rollback
```bash
snap remove lxd
# No afecta datos hasta que se haya corrido lxd init
```

---

## Paso 1.5: Congelar actualizaciones automáticas de snap

### Objetivo
Evitar que `snapd` actualice LXD (o MicroOVN) automáticamente en un nodo sin que los demás nodos del cluster se actualicen al mismo tiempo.

### Comando

```bash
snap refresh --hold
```

### Explicación
Por defecto, `snapd` busca actualizaciones de todos los snaps instalados **una vez por día**. Si un nodo tiene acceso a internet (o al mismo repositorio de paquetes) y otro no, o si simplemente se actualizan en días distintos, terminan con versiones diferentes de LXD. Cuando eso ocurre, LXD **bloquea todas las operaciones de configuración en todo el cluster** (crear contenedores, modificar perfiles, etc.) hasta que todos los miembros vuelvan a tener la misma versión — aunque los contenedores ya en ejecución siguen funcionando con normalidad.

`snap refresh --hold` le indica a `snapd` que no busque más actualizaciones automáticas para ese snap. Las actualizaciones, de ahí en más, deben hacerse manualmente y de forma coordinada en todos los nodos del cluster al mismo tiempo.

### Resultado esperado
```
Hold refreshes for all snaps until [...]
```

### Cómo verificar
```bash
snap refresh --list
# El snap no debe aparecer en la lista de refrescos pendientes automáticos
```

### Errores frecuentes

| Error | Causa | Solución |
|---|---|---|
| Un nodo del cluster aparece bloqueado (icono/estado rojo) en `lxc cluster list` | Ese nodo tiene una versión de LXD distinta a la de los demás (se actualizó automáticamente porque no se aplicó `snap refresh --hold`) | Actualizar manualmente (`snap refresh lxd`) todos los nodos a la misma versión, de forma coordinada |

### Prevención
Aplicar `snap refresh --hold` inmediatamente después de instalar LXD y MicroOVN, en **todos** los nodos, antes de continuar con el resto de la instalación.

---

## Paso 2: Inicializar LXD (lxd init)

### Objetivo
Configurar el daemon LXD: storage pool, networking, clustering y métricas. Este es el paso más importante y no se puede deshacer fácilmente sin reinstalar.

### Comando

```bash
lxd init
```

### Explicación
`lxd init` es un wizard interactivo que hace preguntas sobre la configuración del nodo. Las respuestas determinan cómo LXD almacena datos, se comunica y se une al cluster.

> **Advertencia:** Ejecutar **una sola vez** por nodo. Si se necesita reconfigurar, hay que hacer reset completo.

### Respuestas recomendadas para el wizard

| Pregunta | Respuesta | Justificación |
|---|---|---|
| Clustering? | Yes | Este nodo formará parte del cluster distribuido |
| Create a new cluster? | Yes (solo en el primero, PFR1) | PFR1 es el nodo fundador |
| Join existing cluster? | Yes (para CAR1, FDO1, etc.) | Nodos adicionales se unen con token |
| Storage driver | ZFS | Ver [10_Decisiones.md](10_Decisiones.md) |
| Disk for ZFS pool | `/dev/sda6` (o el disco dedicado disponible) | Disco exclusivo para LXD |
| MAAS server? | No | No aplica a este entorno |
| Bridge for networking? | No | La red de contenedores es OVN (MicroOVN) |
| Prometheus metrics? | Yes | Habilitar métricas para observabilidad |
| Admin port | 8444 | Puerto de administración local |
| Cluster port | 8443 | Puerto de comunicación entre nodos y acceso a Web UI |

### Para nodos adicionales (CAR1, FDO1)

Al seleccionar "Join existing cluster", el wizard pedirá un **join token**. Este token se genera desde un nodo que ya sea miembro funcional del cluster (ej. PFR1):

```bash
# En el nodo existente (ej. PFR1):
lxc cluster add CAR1
# LXD muestra un token de un solo uso. Copiarlo y pegarlo cuando el wizard
# de lxd init en el nuevo nodo pregunte "Would you like to join an existing cluster?"
```

✅ Procedimiento confirmado al incorporar CAR1 (Carpinelli) como segundo miembro del cluster:

1. En PFR1: `lxc cluster add CAR1` → genera el token.
2. En CAR1: `lxd init` → responder `yes` a "Would you like to use LXD clustering?", `yes` a "Are you joining an existing cluster?" (a diferencia del primer nodo, donde se responde `no` porque inicia el cluster), y pegar el token generado en el paso anterior.
3. El wizard advierte que **todos los datos existentes en ese nodo se perderán** al unirse al cluster — confirmar solo si el nodo es nuevo y no tiene datos que conservar.
4. El wizard pide el disco/volumen a usar para el storage local de los contenedores (ver variante LVM más abajo).

> **Nota — variante de storage con LVM:** si el disco del nuevo nodo ya está particionado con LVM (a diferencia de un disco dedicado como `/dev/sda6` en PFR1), hay que crear un nuevo volumen lógico con el espacio libre restante antes de correr `lxd init`:
> ```bash
> # Ver espacio libre disponible en el grupo de volúmenes:
> vgs
> # Columna "VFree" muestra el espacio disponible, ej. 396 GB
>
> # Crear el volumen lógico nuevo con todo el espacio libre:
> lvcreate -n lxd -l 100%FREE NOMBRE_GRUPO_VOLUMENES
>
> # Confirmar que se creó:
> lsblk
> # Debe aparecer como /dev/mapper/NOMBRE_GRUPO_VOLUMENES-lxd
> ```
> Ese volumen lógico nuevo (`/dev/mapper/GRUPO-lxd`) es el que se indica como disco de storage cuando el wizard de `lxd init` lo solicita.

### Resultado esperado
```
LXD has been successfully configured.
```

### Cómo verificar
```bash
lxc cluster list
# Debe mostrar el nodo actual con estado ONLINE
```

### Errores frecuentes

| Error | Causa | Solución |
|---|---|---|
| `ZFS pool already exists` | El disco ya fue usado por ZFS antes | `zpool destroy NOMBRE_POOL` y volver a intentar |
| `Cannot connect to cluster` | Firewall bloqueando puerto 8443 | Ver Paso 5 (configuración de firewall) |

---

## Paso 3: Instalar MicroOVN

### Objetivo
Instalar el componente de red SDN que conectará los contenedores entre nodos y sitios.

### Comando

```bash
snap install microovn
```

### Explicación
MicroOVN es la distribución de OVN de Canonical, instalada como snap. Simplifica la configuración de OVN, que de otro modo requeriría instalar y configurar múltiples componentes manualmente.

### Resultado esperado
```
microovn X.Y.Z from Canonical✓ installed
```

### Cómo verificar
```bash
snap list microovn
```

---

## Paso 4: Configurar WireGuard como transporte underlay entre sitios

### Objetivo
Antes de unir un nuevo sitio al cluster OVN, establecer un túnel WireGuard cifrado entre ese sitio y los demás sitios ya activos. Este paso es específico de clusters distribuidos en Capa 3 separada — no es necesario si todos los nodos están bajo la misma Capa 2. Ver [ADR-0006](adr/ADR-0006-wireguard-underlay-ovn-multisitio.md).

> **Advertencia:** Este paso debe completarse y verificarse (tráfico bidireccional funcionando) **antes** de hacer `microovn cluster join` desde el nuevo sitio. Si el túnel de OVN se establece antes de que WireGuard esté funcionando, el resultado es el mismo problema original: plano de control sincronizado pero sin conectividad de datos entre contenedores.

### Comandos

```bash
# 1. Instalar herramientas de WireGuard:
apt install wireguard-tools

# 2. Generar el par de claves de este nodo:
wg genkey | tee privatekey | wg pubkey > publickey
# La clave pública (publickey) se comparte con los demás nodos.
# La clave privada (privatekey) NUNCA se comparte.

# 3. Dar permisos al servicio de red para leer la clave privada:
chown root:systemd-network privatekey
chmod 640 privatekey
```

### Configuración de la interfaz en `netplan`

```yaml
network:
  tunnels:
    wg0:
      mode: wireguard
      addresses: [169.254.X.0/32]        # IP interna no enrutable, única por nodo
      key: /ruta/a/privatekey
      peers:
        - keys:
            public: "CLAVE_PUBLICA_DEL_PEER"
          endpoint: IP_GESTION_DEL_PEER:PUERTO_WG
          allowed-ips: [169.254.X.0/32]
          keepalive: 25
  routes:
    - to: 169.254.Y.0/32                 # Ruta hacia la IP interna de cada peer
      via: 169.254.X.1                   # Gateway del túnel hacia ese peer
```

### Explicación de parámetros

| Parámetro | Descripción |
|---|---|
| `addresses` | Dirección IP interna de este nodo dentro de la malla WireGuard. Se usó un esquema numérico simple por sitio (Franco = `.0`, Carpinelli = `.1`, Fernando = `.2`, siguiente sitio = `.3`, y así sucesivamente). 🟡 Esquema de direccionamiento inferido de la demostración — formalizar antes de escalar a más sitios. |
| `key` | Ruta al archivo de clave privada generado en el paso anterior |
| `peers.keys.public` | Clave pública del nodo remoto con el que se establece el túnel |
| `peers.endpoint` | IP de gestión del nodo remoto y puerto UDP donde escucha WireGuard |
| `peers.allowed-ips` | Rango de IPs que se permite recibir a través de este peer |
| `routes` | Ruta estática necesaria para alcanzar la IP interna de cada peer adicional (se agrega una entrada por cada sitio remoto) |

> **Advertencia:** Configurar la IP siempre en `netplan` (como se muestra arriba), **no** solo con `ip addr add` en caliente. La configuración en caliente se pierde al reiniciar el host — es exactamente el pendiente abierto en [ADR-0006](adr/ADR-0006-wireguard-underlay-ovn-multisitio.md).

### Cuando se agrega un nuevo sitio al cluster

Hay que repetir este procedimiento y, además, **actualizar la configuración de todos los nodos existentes** para agregar al nuevo sitio como peer (nueva entrada en `peers` y en `routes`). WireGuard no tiene base de datos distribuida — no hay sincronización automática de esta configuración.

### Resultado esperado
```bash
wg show
# Debe mostrar el peer, con "latest handshake" reciente y "transfer" distinto de cero
```

### Cómo verificar
```bash
# Desde un contenedor de prueba en un sitio, hacer ping a un contenedor del otro sitio:
lxc exec CONTENEDOR_PRUEBA -- ping -c 3 IP_CONTENEDOR_OTRO_SITIO
```

### Errores frecuentes

| Error | Causa | Solución |
|---|---|---|
| `wg show` no muestra `latest handshake` | Clave pública incorrecta, endpoint incorrecto, o firewall bloqueando el puerto UDP de WireGuard | Verificar clave pública y endpoint en ambos extremos; verificar regla de firewall para el puerto UDP usado |
| El túnel funciona pero se pierde al reiniciar el host | La IP se configuró solo con `ip addr add`, no en `netplan` | Persistir la configuración en `netplan` como se muestra arriba |

---

## Paso 5: Bootstrap del cluster OVN (solo en el primer nodo del cluster)

### Objetivo
Inicializar el cluster OVN. Este comando solo se ejecuta en el primer nodo (PFR1). Los nodos siguientes se unen al cluster OVN mediante token, análogo al mecanismo de LXD.

### Comando (primer nodo)

```bash
microovn cluster bootstrap --address IP_GESTION:PUERTO
```

### Explicación
`microovn cluster bootstrap` configura este nodo como el nodo inicial del cluster OVN. Establece los servicios internos de OVN (ovsdb-server, ovn-northd, ovn-controller) y su propia base de datos distribuida (misma tecnología que usa LXD — Dqlite). Solo se ejecuta una vez en el clúster, en el nodo fundador.

> **Advertencia:** No ejecutar en nodos adicionales. Esos nodos se unen con el procedimiento de token descrito abajo.

### Para nodos adicionales (ej. CAR1)

```bash
# En el nodo existente (ej. PFR1), generar el token para el nuevo nodo:
microovn cluster add CAR1

# En el nuevo nodo (ej. CAR1), unirse al cluster con el token generado:
microovn cluster join TOKEN_GENERADO
```

✅ Confirmado al incorporar CAR1: una vez ejecutado `microovn cluster join`, los dos nodos se sincronizan automáticamente y la red OVN queda establecida entre ambos (siempre que la malla WireGuard del Paso 4 ya esté funcionando).

### Configuración de la interfaz northbound en LXD

Una sola vez por cluster (no por nodo, porque se replica vía la base de datos distribuida de LXD):

```bash
lxc config set network.ovn.northbound_connection_string "ssl:IP1:6641,ssl:IP2:6641"
```

Este parámetro le indica a LXD dónde encontrar la interfaz *northbound* de OVN (el punto de comandos por el cual LXD interactúa con OVN para crear switches, routers e interfaces virtualizadas).

### Resultado esperado
El comando `microovn cluster bootstrap`/`join` no produce output visible en caso de éxito.

### Cómo verificar
```bash
snap services microovn
# Todos los servicios deben estar en estado active/enabled

microovn cluster list
# Debe mostrar todos los miembros del cluster OVN
```

---

## Paso 6: Configurar firewall (firewalld)

### Objetivo
Permitir que los operadores del equipo accedan a la Web UI de LXD desde sus IPs.

### Comando

```bash
# Agregar regla para cada IP de operador:
firewall-cmd --add-rich-rule='rule family=ipv4 source address=IP_OPERADOR port port=8443-8444 protocol=tcp accept'

# Una vez agregadas todas las IPs, hacer las reglas permanentes:
firewall-cmd --runtime-to-permanent
```

### Explicación
firewalld gestiona el firewall del host. Las rich rules permiten especificar el origen (IP del operador), el protocolo y los puertos permitidos.

`--runtime-to-permanent` promueve todas las reglas activas en memoria a reglas persistentes que sobreviven reinicios del servicio. Sin este paso, las reglas se pierden al reiniciar firewalld o el sistema.

### Parámetros de la rich rule

| Parámetro | Descripción |
|---|---|
| `family=ipv4` | Aplica solo a tráfico IPv4 |
| `source address=IP` | IP de origen permitida |
| `port port=8443-8444` | Rango de puertos permitidos |
| `protocol=tcp` | Solo TCP |
| `accept` | Acción: permitir el tráfico |

### IPs a agregar

| Operador | IP | Estado |
|---|---|---|
| Daniel Medina | 🔴 Pendiente de validación (IP parcialmente capturada en reunión) | Pendiente |
| Rocío Duarte | 🔴 Pendiente de validación | Pendiente |
| Otros operadores | 🔴 Pendiente de validación | Pendiente |

> **Nota — CAR1 (Carpinelli):** el puerto de gestión de LXD (8444) para este nodo aún debe darse de alta formalmente como "alta de servicio" ante el equipo de seguridad, además de estar inventariado. La VPN corporativa ya reconoce el servidor, pero el puerto específico de LXD todavía no. Ver [11_Riesgos.md](11_Riesgos.md).

### Cómo verificar
```bash
firewall-cmd --list-rich-rules
# Deben aparecer las reglas agregadas
```

### Rollback
```bash
# Remover una regla específica:
firewall-cmd --remove-rich-rule='rule family=ipv4 source address=IP_OPERADOR port port=8443-8444 protocol=tcp accept'
firewall-cmd --runtime-to-permanent
```

---

## Paso 7: Configurar proxy HTTP en LXD

### Objetivo
Permitir que LXD (y los contenedores) descarguen imágenes y paquetes a través del proxy HTTP corporativo.

### Comandos

```bash
lxc config set core.http_proxy http://PROXY_IP:3128
lxc config set core.https_proxy http://PROXY_IP:3128
lxc config set core.proxy_ignore_hosts 127.0.0.1,localhost
```

> **Nota:** La IP exacta del proxy (🔴 Pendiente de validación — se mencionó `32.x.x.x:3128` en la reunión) debe ser confirmada con Nicolás (equipo de seguridad).

### Explicación

| Parámetro | Descripción |
|---|---|
| `core.http_proxy` | Proxy para tráfico HTTP saliente de LXD |
| `core.https_proxy` | Proxy para tráfico HTTPS saliente de LXD |
| `core.proxy_ignore_hosts` | Hosts que LXD debe acceder directamente sin proxy |

### Cómo verificar
```bash
lxc config get core.http_proxy
# Debe mostrar la URL del proxy
```

---

## Paso 8: Agregar usuarios al grupo lxd

### Objetivo
Permitir que los operadores usen `lxc` desde la línea de comandos sin necesidad de `sudo`.

### Comando

```bash
usermod -aG lxd NOMBRE_USUARIO
```

### Explicación
LXD usa un socket Unix (`/var/snap/lxd/common/lxd/unix.socket`) que solo puede ser accedido por `root` o miembros del grupo `lxd`. Agregar un usuario al grupo `lxd` le otorga acceso completo al cluster desde esa VM.

> **Advertencia:** El grupo `lxd` es equivalente a acceso root al host. Solo agregar usuarios de confianza.

### Cómo verificar
```bash
groups NOMBRE_USUARIO
# Debe incluir "lxd" en la lista
```

---

## Paso 9: Acceso a la Web UI

### Objetivo
Que cada operador pueda acceder a la Web UI de LXD desde su navegador.

### Procedimiento por operador

1. Abrir el navegador en modo incógnito.
2. Navegar a `https://IP_DEL_NODO:8443`.
3. El navegador advertirá sobre el certificado. Continuar.
4. En la UI: **Generate certificate** → descargar el archivo de certificado.
5. Instalar el certificado en el almacén del navegador (siguiente, siguiente, finalizar).
6. Cerrar la pestaña y abrir una nueva (en modo incógnito si el certificado fue rechazado antes).
7. Ingresar el **token** proporcionado por el administrador.

> **Nota:** Si el navegador rechazó el certificado anteriormente, usar modo incógnito para el primer acceso con el certificado nuevo.

### Cómo generar un token para un nuevo usuario

Desde la Web UI o CLI:

```bash
lxc config trust add NOMBRE_USUARIO
# LXD muestra el token. Compartirlo de forma segura con el usuario.
```

### Verificación
El usuario debe poder ver el dashboard del cluster al ingresar el token.

---

## Paso 10: Configurar NTP en el host

### Objetivo
Mantener el reloj del sistema sincronizado en todos los nodos del cluster. Es un prerrequisito silencioso pero crítico: la base de datos distribuida de LXD y de MicroOVN (Dqlite) usa la hora de cada nodo para coordinar la sincronización, y una diferencia de reloj — incluso de segundos — puede hacer que el cluster interprete que la sincronización está rota y bloquee operaciones de forma intermitente y difícil de diagnosticar.

### Comando

Ubuntu ya incluye `systemd-timesyncd` habilitado por defecto. Basta con verificar y, si es necesario, apuntar a los servidores NTP internos:

```bash
timedatectl set-ntp true
# Editar /etc/systemd/timesyncd.conf y definir NTP=SERVIDOR_NTP_1 SERVIDOR_NTP_2
systemctl restart systemd-timesyncd
```

### Resultado esperado
```bash
timedatectl
# "System clock synchronized: yes"
# "NTP service: active"
```

### Cómo verificar
```bash
timedatectl
```

### Errores frecuentes

Ver [TRB-009 en 07_Troubleshooting.md](07_Troubleshooting.md#trb-009) — comportamiento errático del cluster (bloqueos intermitentes de operaciones) causado por desincronización de reloj entre nodos.

### Prevención
Aplicar esta configuración en **todos** los hosts y también en todos los contenedores gateway de servicios (ver [05_Configuracion.md](05_Configuracion.md)), antes de unir el nodo al cluster.

---

## Resumen del procedimiento

```
Paso 0:  Renombrar interfaces de red con netplan (nombres iguales en todo el cluster)
Paso 1:  snap install lxd
Paso 1.5: snap refresh --hold (congelar actualizaciones automáticas)
Paso 2:  lxd init (wizard — responder según tabla; join token para nodos adicionales)
Paso 3:  snap install microovn
Paso 4:  Configurar WireGuard como transporte underlay entre sitios (nodos en Capa 3 separada)
Paso 5:  microovn cluster bootstrap / cluster add + cluster join
Paso 6:  Configurar firewall (rich rules por IP de operador)
Paso 7:  Configurar proxy HTTP (core.http_proxy, etc.)
Paso 8:  Agregar operadores al grupo lxd
Paso 9:  Guiar a cada operador en el acceso a Web UI
Paso 10: Configurar NTP
```

---

## Documentos relacionados

| Tema | Documento |
|---|---|
| Configuración posterior a la instalación | [05_Configuracion.md](05_Configuracion.md) |
| Operación diaria | [06_Operacion.md](06_Operacion.md) |
| Troubleshooting de instalación | [07_Troubleshooting.md](07_Troubleshooting.md) |
| Componentes instalados | [03_Componentes.md](03_Componentes.md) |
