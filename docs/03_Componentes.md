# 03 — Componentes del sistema

> **Audiencia:** Ingenieros de infraestructura, SRE.
> **Propósito:** Descripción detallada de cada componente: función, dependencias, impacto de falla y verificación. No incluye instalación (ver [04_Instalacion.md](04_Instalacion.md)) ni configuración (ver [05_Configuracion.md](05_Configuracion.md)).

---

## LXD

| Campo | Valor |
|---|---|
| **Nombre** | LXD |
| **Versión** | 5.21 |
| **Función** | Gestión de contenedores de sistema Linux en el nodo |
| **Responsabilidad** | Ciclo de vida de contenedores, imágenes, perfiles, storage pools y redes |
| **Dependencias** | Sistema operativo Ubuntu, snap, ZFS (storage), MicroOVN (red) |
| **Entradas** | Comandos `lxc`, llamadas a la API REST (Web UI), configuración de cluster |
| **Salidas** | Contenedores en ejecución, métricas Prometheus, estado del cluster |
| **Impacto si falla** | Todos los contenedores del nodo quedan inaccesibles. El cluster puede seguir operando en otros nodos. |
| **Cómo verificar** | `snap services lxd` — debe mostrar `active` |
| **Puertos** | 8443 (cluster/usuarios), 8444 (admin local) |

### Buenas prácticas

- Instalar siempre via snap (`snap install lxd`). No usar el paquete deb del sistema.
- Ejecutar `lxd init` inmediatamente después de instalar, antes de cualquier otra configuración.
- Solicitar backup de la VM a SBA/AIT tan pronto el nodo esté configurado.
- ✅ Después de instalar, ejecutar `snap refresh --hold` para congelar las actualizaciones automáticas. Si un nodo del cluster se actualiza automáticamente y otro no, el cluster **bloquea todas las operaciones de configuración** hasta que todos los miembros tengan la misma versión. Ver [12_Lecciones_Aprendidas.md](12_Lecciones_Aprendidas.md) y [07_Troubleshooting.md](07_Troubleshooting.md).
- ✅ Todos los nodos deben tener la hora sincronizada (NTP). Diferencias de reloj entre nodos, aunque sean de segundos, pueden hacer que el cluster interprete que la sincronización de la base de datos distribuida está rota y bloquee operaciones. Ver [05_Configuracion.md](05_Configuracion.md).

---

## lxc (CLI)

| Campo | Valor |
|---|---|
| **Nombre** | lxc |
| **Función** | Cliente de línea de comandos para LXD |
| **Responsabilidad** | Interfaz de administración para crear, gestionar y monitorear contenedores desde terminal |
| **Dependencias** | LXD daemon en ejecución |
| **Entradas** | Comandos del operador |
| **Salidas** | Estado de contenedores, configuración, logs |
| **Impacto si falla** | Solo afecta la interfaz CLI. La Web UI sigue disponible. |
| **Cómo verificar** | `lxc list` — lista todos los contenedores del cluster |

---

## MicroOVN

| Campo | Valor |
|---|---|
| **Nombre** | MicroOVN |
| **Función** | Gestión simplificada de OVN para el cluster LXD |
| **Responsabilidad** | Proveer la red SDN transversal (overlay) entre nodos y sitios del cluster |
| **Dependencias** | snap, WireGuard (transporte underlay entre sitios — ver [ADR-0006](adr/ADR-0006-wireguard-underlay-ovn-multisitio.md)), red IP entre nodos para el plano de control |
| **Entradas** | Configuración del cluster OVN, interfaz de servicio local (`nicsrv1`) |
| **Salidas** | Red virtual que conecta contenedores entre sitios |
| **Impacto si falla** | Los contenedores existentes pueden seguir corriendo, pero pierden conectividad de red entre sitios |
| **Cómo verificar** | `snap services microovn`, `microovn cluster list` |
| **Estado actual** | ✅ Instalado, bootstrapped y funcional entre PFR1 y CAR1 (sobre WireGuard). 🔴 Pendiente extender a FDO1 |

### Base de datos distribuida de MicroOVN

MicroOVN usa la **misma tecnología de base de datos distribuida que LXD** (Dqlite — ver [08_Glosario.md](08_Glosario.md)) para sincronizar su plano de control entre los miembros del cluster OVN. Esto significa que el mecanismo para sumar un nuevo miembro es análogo al de LXD: se genera un token desde un nodo existente (`microovn cluster add HOSTNAME`) y se usa ese token en el nuevo nodo (`microovn cluster join TOKEN`). Ver el procedimiento completo en [04_Instalacion.md](04_Instalacion.md).

### Buenas prácticas

- `microovn cluster bootstrap` se ejecuta **solo una vez**, en el primer nodo (PFR1).
- Los nodos adicionales se agregan al cluster OVN con `microovn cluster add` / `microovn cluster join` (ver [04_Instalacion.md](04_Instalacion.md)), **después** de que la malla WireGuard hacia ese nodo esté configurada y probada.
- La configuración de la interfaz *northbound* de OVN dentro de LXD (`lxc config set network.ovn.northbound_connection_string`, o equivalente vía el wizard) solo necesita definirse **una vez** por cluster LXD — al ser una base de datos distribuida, se replica automáticamente a los demás nodos.

---

## WireGuard

| Campo | Valor |
|---|---|
| **Nombre** | WireGuard |
| **Función** | Red overlay punto a punto (mesh) cifrada, usada como transporte underlay entre sitios geográficos |
| **Responsabilidad** | Transportar de forma cifrada el tráfico del túnel de datos de OVN entre sitios en Capa 3 separada |
| **Dependencias** | Paquete `wireguard-tools`, conectividad IP básica (UDP) entre los hosts de cada sitio |
| **Entradas** | Configuración manual por nodo: clave privada/pública, endpoint del peer, rutas |
| **Salidas** | Túnel cifrado punto a punto entre dos hosts; sobre él corre el túnel de datos de OVN |
| **Impacto si falla** | Los contenedores del sitio afectado pierden conectividad OVN con los demás sitios. La gestión del cluster LXD (plano de control) no se ve afectada porque usa la red de gestión, no la malla WireGuard |
| **Cómo verificar** | `wg show` (en el host) — debe mostrar el peer con *handshake* reciente y tráfico (`transfer`) distinto de cero |
| **Estado actual** | ✅ Configurado y probado entre PFR1 y CAR1. 🔴 Configuración de IP de la interfaz no persistida en `netplan` (se pierde al reiniciar el host) |

### Buenas prácticas

- No tiene plano de control ni base de datos distribuida: **toda la configuración es manual**. Al agregar un nuevo sitio al cluster, hay que generar un nuevo par de claves y actualizar la configuración de `netplan` en **todos** los nodos existentes para agregar el nuevo peer.
- Persistir siempre la configuración (dirección IP, rutas, peers) en `netplan`, nunca solo en caliente (`ip addr`, `wg set`), para que sobreviva reinicios.
- Ver el detalle completo de la decisión en [ADR-0006](adr/ADR-0006-wireguard-underlay-ovn-multisitio.md) y la configuración paso a paso en [05_Configuracion.md](05_Configuracion.md).

---

## Driver de red IPVLAN

| Campo | Valor |
|---|---|
| **Nombre** | IPVLAN |
| **Función** | Driver de red de Linux que permite que un contenedor use directamente una interfaz física del host, reutilizando su misma dirección MAC pero con IP propia del contenedor |
| **Responsabilidad** | Conectar el contenedor "gateway de servicios" de cada sitio directamente a la interfaz de servicio del host (`nicsrv1`) |
| **Dependencias** | Interfaz física de servicio del host |
| **Entradas** | Configuración del dispositivo de red en el perfil LXD (`nictype: ipvlan`) |
| **Salidas** | El contenedor queda accesible directamente sobre la red de servicio del sitio, con su propia IP |
| **Impacto si falla** | El contenedor gateway de servicios pierde conectividad hacia/desde la red de servicio del sitio |
| **Cómo verificar** | `lxc config device show CONTENEDOR` — debe mostrar `nictype: ipvlan` sobre el `parent` correspondiente |

### ¿Por qué IPVLAN y no un bridge tradicional?

Una política de seguridad de VMware no permite que, por la interfaz virtual asignada a la VM, salga tráfico con una dirección MAC distinta de la que VMware le asignó a esa VM. Un bridge de Linux tradicional (`macvlan` o un bridge L2 estándar) generaría tráfico con MACs distintas por cada contenedor, lo que sería bloqueado por esa política. IPVLAN evita el problema: **reutiliza la misma MAC de la interfaz física del host** para todo el tráfico, diferenciando el tráfico de cada contenedor únicamente por IP. Esta restricción de VMware se puede solicitar levantar formalmente, pero se optó por IPVLAN para no depender de ese cambio y evitar efectos adversos no deseados.

---

## ZFS (Storage Pool)

| Campo | Valor |
|---|---|
| **Nombre** | ZFS storage pool |
| **Función** | Almacenamiento de datos de contenedores e imágenes |
| **Responsabilidad** | Proveer un filesystem eficiente con snapshots integrados para LXD |
| **Dependencias** | Disco dedicado (`/dev/sda6` en PFR1, 315 GB) |
| **Entradas** | Datos de contenedores e imágenes LXD |
| **Salidas** | Almacenamiento persistente de datos de contenedores |
| **Impacto si falla** | **Crítico:** todos los contenedores del nodo quedan inaccesibles o con datos corruptos |
| **Cómo verificar** | `zpool status` — debe mostrar el pool en estado `ONLINE` |

### Buenas prácticas

- El disco del pool ZFS debe ser **exclusivo para LXD**. No compartir con el sistema operativo.
- Solicitar backup de la VM a SBA/AIT para tener un punto de restauración ante pérdida del pool.

---

## firewalld

| Campo | Valor |
|---|---|
| **Nombre** | firewalld |
| **Función** | Gestión del firewall del host Linux |
| **Responsabilidad** | Controlar el acceso a los puertos de LXD (8443/8444) por IP de origen |
| **Dependencias** | Sistema operativo Ubuntu |
| **Entradas** | Reglas de zona, rich rules |
| **Salidas** | Tráfico de red permitido o denegado según las reglas |
| **Impacto si falla** | Si firewalld se detiene, el comportamiento depende de las políticas por defecto. Puede quedar sin restricciones o bloqueado. |
| **Cómo verificar** | `firewall-cmd --state` — debe mostrar `running` |

---

## SSSD (autenticación LDAP)

| Campo | Valor |
|---|---|
| **Nombre** | SSSD (System Security Services Daemon) + `sssd-ldap` |
| **Función** | Autenticación e identidad de sistema operativo (login SSH/consola y `sudo`) de los hosts del cluster contra el LDAP corporativo, en lugar de usuarios locales |
| **Responsabilidad** | Resolver identidad y grupos de los operadores contra `ldap.sis.personal.net.py`, y autorizar `sudo` vía `sudo_provider = ldap` |
| **Dependencias** | Certificado de la cadena CA del LDAP corporativo instalado en `/usr/local/share/ca-certificates/` (`update-ca-certificates`), paquetes `sssd sssd-ldap libsss-sudo oddjob-mkhomedir` |
| **Entradas** | `/etc/sssd/sssd.conf` (dominio, `ldap_search_base`, `simple_allow_groups`) |
| **Salidas** | Sesiones de usuario autenticadas contra LDAP; creación automática de `$HOME` vía `pam-auth-update --enable mkhomedir` |
| **Impacto si falla** | Los operadores no pueden iniciar sesión en el host por su cuenta LDAP (afecta acceso administrativo al SO, no al login de LXD vía TLS/tokens, que es independiente) |
| **Cómo verificar** | `systemctl status sssd` — debe estar `active (running)`. Login de prueba con un usuario del grupo permitido |
| **Restricción crítica (Ubuntu 26.04 LTS)** | Ejecutar `update-alternatives --config sudo` y elegir la implementación clásica de `sudo` (no `sudo-rs`) — ver [LL-015 en 12_Lecciones_Aprendidas.md](12_Lecciones_Aprendidas.md) |

### Grupos con acceso permitido

`simple_allow_groups` restringe el login a: `seguridad`, `css`, `SVA`, `sva_tec_ps`, `SegInf_ps`, `SegInf`, `nunezno_opr`, `AK402_opr`. Agregar un grupo nuevo a esta lista es la forma de dar acceso de sistema operativo (distinto del acceso al grupo `lxd`, ver [06_Operacion.md](06_Operacion.md)) a un equipo adicional.

Ver el procedimiento completo en [`onenote/Clúster-OSS/Clúster/SSSD.md`](../onenote/Clúster-OSS/Clúster/SSSD.md).

---

## cloud-init

| Campo | Valor |
|---|---|
| **Nombre** | cloud-init |
| **Función** | Inicialización automatizada de contenedores al primer arranque |
| **Responsabilidad** | Instalar paquetes, crear usuarios, escribir archivos y ejecutar scripts en el primer boot |
| **Dependencias** | Acceso a internet (APT) o proxy HTTP configurado |
| **Entradas** | Configuración `user-data` del perfil LXD |
| **Salidas** | Contenedor configurado con los servicios instalados |
| **Impacto si falla** | El contenedor arranca pero sin los paquetes/servicios especificados. Debe ser recreado. |
| **Cómo verificar** | Dentro del contenedor: `cloud-init status` — debe mostrar `done` |
| **Restricción crítica** | Se ejecuta **solo en el primer arranque**. Para re-ejecutar hay que eliminar y recrear el contenedor. |

### Buenas prácticas

- Siempre incluir el header `#cloud-config` al inicio del bloque `user-data`.
- Incluir `package_update: true` y `package_upgrade: true` para asegurar que el sistema esté actualizado.
- Verificar con `cloud-init status` antes de asumir que la instalación fue exitosa.

---

## Prometheus (métricas LXD)

| Campo | Valor |
|---|---|
| **Nombre** | Prometheus metrics endpoint |
| **Función** | Exposición de métricas del cluster LXD para monitoreo |
| **Responsabilidad** | Proveer datos de salud y rendimiento del nodo y sus contenedores |
| **Dependencias** | LXD daemon |
| **Entradas** | Estado interno de LXD |
| **Salidas** | Métricas en formato Prometheus (scrapeables por un servidor Prometheus externo) |
| **Impacto si falla** | Solo afecta la observabilidad, no la operación |
| **Cómo verificar** | 🔴 Endpoint y configuración Prometheus externos: Pendiente de validación |

---

## Grafana

| Campo | Valor |
|---|---|
| **Nombre** | Grafana |
| **Función** | Visualización de métricas del cluster |
| **Responsabilidad** | Dashboards de monitoreo para operadores |
| **Dependencias** | Servidor Prometheus configurado con el endpoint LXD |
| **Configuración** | 🟡 Dashboards importados desde Grafana Labs por ID |
| **Impacto si falla** | Solo afecta la visibilidad, no la operación del cluster |
| **Estado** | 🔴 Detalles de configuración: Pendiente de validación |

---

## Loki (logs centralizados)

| Campo | Valor |
|---|---|
| **Nombre** | Loki |
| **Función** | Agregador y almacén de logs centralizado |
| **Responsabilidad** | Recibir, vía `rsyslog`, los logs del sistema operativo de cada host del cluster LXD |
| **Dependencias** | `rsyslog` configurado en cada host para reenviar logs hacia Loki |
| **Entradas** | Logs de sistema (`syslog`) de cada nodo del cluster LXD |
| **Salidas** | Logs consultables centralizadamente (fuera del propio cluster que los genera) |
| **Impacto si falla** | Se pierde visibilidad centralizada de logs, pero no afecta la operación del cluster LXD |
| **Cómo verificar** | 🔴 Endpoint y validación de recepción de logs: Pendiente de validación |

> **Importante:** Este Loki vive en **otra infraestructura**, distinta del propio cluster LXD (se mencionó que está en SBA). La razón es deliberada: si los hosts del cluster LXD apuntaran a un Loki alojado dentro del mismo cluster, una falla del cluster dejaría sin logs justo en el momento en que más se necesitan para diagnosticar. Ver [12_Lecciones_Aprendidas.md](12_Lecciones_Aprendidas.md).

---

## Contenedor "gateway de servicios"

| Campo | Valor |
|---|---|
| **Nombre** | Contenedor gateway de servicios (patrón, no un paquete instalable) |
| **Función** | Concentrar y enrutar el tráfico de entrada/salida de servicios de un sitio o proyecto |
| **Responsabilidad** | Actuar como router entre la red OVN interna (este-oeste, entre contenedores) y la interfaz física de servicio del host (norte-sur, hacia la red del sitio), conservando la IP de servicio histórica cuando aplica |
| **Dependencias** | Perfil LXD con dos dispositivos de red: uno sobre OVN, otro `ipvlan` sobre `nicsrv1` |
| **Entradas** | Tráfico este-oeste desde/hacia otros contenedores del cluster; tráfico norte-sur desde/hacia la red del sitio |
| **Salidas** | Tráfico enrutado hacia el destino correspondiente |
| **Impacto si falla** | Los servicios de ese sitio/proyecto quedan inalcanzables desde la red del sitio, aunque los contenedores individuales sigan corriendo |
| **Cómo verificar** | `lxc exec CONTENEDOR -- ip addr` (debe mostrar ambas interfaces con IP) |

### Buenas prácticas (aplicadas por Norberto Núñez en la demostración)

- Deshabilitar SSH dentro de este contenedor. La administración se hace exclusivamente vía `lxc exec` / consola del daemon LXD, nunca por SSH directo — reduce la posibilidad de movimiento lateral si algún contenedor del cluster llegara a estar comprometido.
- Limitar el tamaño de `journald` a 100 MB (por defecto puede acumular hasta 4 GB de logs). Este contenedor actúa como router y no aloja aplicaciones, por lo que no necesita retener logs extensos.
- Configurar NTP (`systemd-timesyncd`) igual que en el host — ver [05_Configuracion.md](05_Configuracion.md).
- Un contenedor gateway de servicios distinto por cada sitio/proyecto (ej. `presidente-franco-ss-gw`, y su equivalente en Carpinelli), no compartido entre sitios.

Ver la configuración completa del perfil en [05_Configuracion.md](05_Configuracion.md).

---

## Contenedor "balanceador"

| Campo | Valor |
|---|---|
| **Nombre** | Contenedor balanceador (patrón, no un paquete instalable) — primer ejemplo: `PFR-LB` |
| **Función** | Recibir el tráfico web reenviado por el contenedor gateway de servicios y enrutarlo, por URL/path, hacia el contenedor de aplicación correspondiente |
| **Responsabilidad** | Centralizar el certificado TLS de todos los servicios web de un sitio en un único lugar; actuar como proxy reverso HTTP(S) |
| **Dependencias** | Contenedor gateway de servicios del mismo sitio (le reenvía el tráfico); Apache (u otro servidor web) instalado dentro |
| **Entradas** | Tráfico HTTP/HTTPS reenviado desde el contenedor gateway (ej. puerto 80/443) |
| **Salidas** | Tráfico enrutado hacia el contenedor de servicio correspondiente, según URL/path |
| **Impacto si falla** | Todos los servicios web publicados a través de este balanceador quedan inalcanzables desde afuera, aunque los contenedores de aplicación sigan corriendo — es un punto único de falla por sitio si no tiene réplicas |
| **Cómo verificar** | `lxc exec CONTENEDOR -- ss -ntlp` (debe mostrar el puerto 80/443 escuchando); `curl` contra la IP del balanceador |
| **IP fija** | Sí — requiere IP fija en `OVN_1` porque el gateway apunta directamente a él (ej. `.11` para `PFR-LB` en Franco, ver [02_Arquitectura.md](02_Arquitectura.md)) |

### Buenas prácticas

- Un balanceador por sitio, no compartido entre sitios (mismo criterio que el contenedor gateway de servicios).
- Instalar el certificado TLS únicamente en este contenedor — los contenedores de aplicación detrás del balanceador no necesitan certificado propio.
- No alojar aplicaciones dentro de este contenedor — su única función es enrutar, igual que el gateway no aloja aplicaciones (ver [Contenedor "gateway de servicios"](#contenedor-gateway-de-servicios) arriba).
- Servicios no-web (ej. bases de datos) no pasan por este contenedor — el gateway los redirige directamente. Ver [ADR-0008](adr/ADR-0008-gateway-balanceador-dos-etapas.md).

Ver la decisión completa en [ADR-0008](adr/ADR-0008-gateway-balanceador-dos-etapas.md), el diagrama en [02_Arquitectura.md](02_Arquitectura.md) y la configuración del perfil/Apache en [05_Configuracion.md](05_Configuracion.md).

---

## Proyectos LXD (multi-tenancy)

| Campo | Valor |
|---|---|
| **Nombre** | Proyecto LXD (`lxc project`) |
| **Función** | Espacio de nombres aislado dentro del mismo cluster LXD, con sus propios contenedores, perfiles y límites de recursos |
| **Responsabilidad** | Separar visibilidad y consumo de recursos entre distintos equipos/áreas que comparten la infraestructura |
| **Dependencias** | LXD (funcionalidad nativa, no requiere componentes adicionales) |
| **Entradas** | Definición de límites (redes, CPU, memoria, instancias) y grupo de identidad asociado |
| **Salidas** | Aislamiento de acceso: los usuarios de un grupo solo ven los recursos de su proyecto |
| **Impacto si falla** | No aplica falla en sentido de servicio — un proyecto mal configurado (sin límites) puede permitir que un equipo consuma recursos de más |
| **Cómo verificar** | `lxc project list`, `lxc project show NOMBRE_PROYECTO` |

Ver la decisión completa en [ADR-0007](adr/ADR-0007-proyectos-lxd-multitenancy.md) y la configuración en [05_Configuracion.md](05_Configuracion.md).

---

## Web UI (LXD)

| Campo | Valor |
|---|---|
| **Nombre** | LXD Web UI |
| **Función** | Interfaz gráfica para administración del cluster LXD |
| **Responsabilidad** | Gestión visual de contenedores, imágenes, perfiles, redes y storage |
| **Dependencias** | LXD daemon, acceso HTTPS al puerto 8443 |
| **Entradas** | Acciones del operador via navegador web |
| **Salidas** | Estado del cluster, configuración aplicada |
| **Impacto si falla** | Solo afecta el acceso gráfico. El CLI (`lxc`) sigue disponible. |
| **Acceso actual** | ✅ Red local únicamente. 🔴 VPN no configurada |

---

## Documentos relacionados

| Tema | Documento |
|---|---|
| Arquitectura del sistema | [02_Arquitectura.md](02_Arquitectura.md) |
| Instalación de los componentes | [04_Instalacion.md](04_Instalacion.md) |
| Configuración de cada componente | [05_Configuracion.md](05_Configuracion.md) |
| Monitoreo operativo | [14_Manual_Operativo.md](14_Manual_Operativo.md) |
| Glosario de términos | [08_Glosario.md](08_Glosario.md) |
