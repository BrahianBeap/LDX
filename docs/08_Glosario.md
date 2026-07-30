# 08 — Glosario de términos técnicos

> **Audiencia:** Todo el equipo, especialmente ingenieros nuevos.
> **Propósito:** Diccionario de referencia. Cada término se define una sola vez aquí. Los demás documentos referencian este glosario.

---

## A

### APT
Gestor de paquetes de Debian/Ubuntu. Permite instalar, actualizar y remover software del sistema. Se usa dentro de los contenedores Ubuntu. En cloud-init, `package_update` y `package_upgrade` invocan APT internamente.

### ADR (Architecture Decision Record)
Documento que registra una decisión técnica importante: qué se decidió, por qué, qué alternativas se evaluaron y qué consecuencias tiene. Formato estándar: Michael Nygard. Ver [`docs/adr/`](adr/).

---

## B

### balanceador (contenedor)
Patrón de diseño: contenedor que recibe el tráfico web reenviado por el [gateway de servicios](#gateway-de-servicios-contenedor) y lo enruta, por URL/path, hacia el contenedor de aplicación correspondiente, usando Apache (u otro servidor web) como proxy reverso. Centraliza el certificado TLS de todos los servicios web de un sitio en un único lugar. Ver [ADR-0008](adr/ADR-0008-gateway-balanceador-dos-etapas.md) y [03_Componentes.md](03_Componentes.md).

### bootstrap
Proceso de inicialización de un componente que no tiene dependencias previas. En MicroOVN, `microovn cluster bootstrap` configura el primer nodo OVN del cluster. Solo se ejecuta una vez, en el primer nodo.

---

## C

### CAR (Carpinelli)
Uno de los tres sitios geográficos del cluster LXD. Prefijo para los nodos de ese sitio: `CAR1`, `CAR2`, etc. CAR1 fue instalado y unido al cluster en la segunda reunión (rol `database-standby`). Ver [13_Linea_de_Tiempo.md](13_Linea_de_Tiempo.md).

### cloud-init
Framework de inicialización de instancias cloud. Permite especificar, en el momento de la creación de un contenedor o VM, qué paquetes instalar, qué usuarios crear, qué archivos escribir, etc. Se ejecuta **solo en el primer arranque** del contenedor. Si se necesita re-ejecutar, el contenedor debe ser eliminado y recreado.

### cluster
Conjunto de nodos LXD que comparten una base de datos de estado y pueden gestionar contenedores de forma coordinada. Los contenedores son visibles desde cualquier nodo del cluster.

### contenedor de sistema
A diferencia de los contenedores de aplicación (Docker), un contenedor de sistema LXD emula un sistema operativo completo con su propio init, servicios, red y filesystem. Permite correr múltiples servicios dentro del mismo contenedor, aunque la buena práctica es uno por contenedor.

---

## D

### dispositivo proxy (LXD)
Tipo especial de dispositivo LXD que crea un socket de red que traduce tráfico entre el contenedor y el host. Se usa para dar salida a internet a los contenedores (temporalmente, mientras OVN no está configurado) o para exponer servicios del contenedor hacia el exterior. No es lo mismo que un proxy HTTP.

### Dqlite
Base de datos distribuida basada en SQLite que LXD usa internamente para almacenar el estado del cluster: qué contenedores existen, sus configuraciones, perfiles, redes e imágenes. Dqlite requiere **quórum** para operaciones de escritura. Con 1 solo nodo activo (estado actual del cluster), la pérdida de ese nodo implica pérdida del estado completo del cluster. La corrupción de Dqlite es el escenario de recuperación más complejo del sistema.

### drop (zona de firewalld)
Zona predefinida de `firewalld` con el comportamiento más restrictivo: no responde ping y descarta en silencio cualquier paquete a un puerto no explícitamente abierto (sin enviar rechazo TCP), a diferencia de zonas como `external`/`work`. Usada como zona por defecto en los contenedores gateway y balanceador para minimizar la información visible ante un escaneo externo. Ver [05_Configuracion.md](05_Configuracion.md).

---

## E

### EOL (End of Life)
Estado de un software cuando su desarrollador deja de publicar actualizaciones y parches de seguridad. CentOS 7 alcanzó EOL, lo que motiva la migración a Ubuntu LXD.

---

## F

### FDO (Fernando)
Uno de los tres sitios geográficos del cluster LXD. Prefijo para los nodos de ese sitio: `FDO1`, `FDO2`, etc. El nodo FDO1 está pendiente de instalación — sería el tercer miembro, necesario para completar el quórum de alta disponibilidad de la base de datos del cluster. Ver [13_Linea_de_Tiempo.md](13_Linea_de_Tiempo.md).

### firewalld
Sistema de gestión del firewall en Linux basado en zonas y reglas. Permite agregar reglas en tiempo real (`--runtime`) y hacerlas permanentes (`--permanent`) o usar `--runtime-to-permanent` para promover todas las reglas activas.

### Franco / PFR
Sitio geográfico donde se instaló el primer nodo del cluster (PFR1). Es el nodo de referencia para replicar la instalación en otros sitios. Rol actual en la base de datos distribuida: `database-leader`.

---

## G

### gateway de servicios (contenedor)
Patrón de diseño usado en cada sitio/proyecto del cluster: un contenedor dedicado que actúa como router entre la red OVN interna (tráfico este-oeste, entre contenedores) y la interfaz física de servicio del host (tráfico norte-sur, hacia la red del sitio), usando el driver [IPVLAN](#ipvlan). Concentra la IP de servicio del sitio o proyecto. Ver [02_Arquitectura.md](02_Arquitectura.md) y [03_Componentes.md](03_Componentes.md).

### geneve
Protocolo de encapsulamiento de red usado por OVN para el túnel de datos que interconecta los distintos chassis/hosts entre los que se distribuye la red virtualizada. No cifra el tráfico por defecto — ver [WireGuard](#wireguard) y [ADR-0006](adr/ADR-0006-wireguard-underlay-ovn-multisitio.md).

---

## I

### IPVLAN
Driver de red de Linux que permite que un contenedor use directamente una interfaz física del host, reutilizando su misma dirección MAC pero con una IP propia del contenedor. Se usa en los contenedores [gateway de servicios](#gateway-de-servicios-contenedor) para evitar el bloqueo de VMware a tráfico con MACs distintas de la asignada a la VM. Ver [03_Componentes.md](03_Componentes.md).

### InfraFileRoom
Servicio productivo actualmente corriendo en CentOS 7. Contiene aproximadamente 800 GB de datos. Es una de las migraciones prioritarias al cluster LXD.

---

## L

### LDAP (Lightweight Directory Access Protocol)
Protocolo de directorio usado para centralizar identidades corporativas. En este proyecto, los hosts del cluster autentican operadores contra el LDAP corporativo (`ldap.sis.personal.net.py`) vía SSSD, en lugar de usar usuarios locales. Ver [SSSD](#sssd) y [03_Componentes.md](03_Componentes.md).

### lxc
Herramienta de línea de comandos (CLI) para interactuar con LXD. Permite crear, iniciar, detener, eliminar y configurar contenedores e imágenes. Es el cliente del servicio `lxd`.

### LXD
Sistema de gestión de contenedores de sistema desarrollado por Canonical. Expone una API REST que puede ser usada tanto por el CLI (`lxc`) como por la Web UI. Version usada en este proyecto: 5.21. Se instala via snap.

### lxd init
Wizard interactivo de inicialización de LXD. Configura: clustering, storage pool, networking, métricas y puertos. Se ejecuta una sola vez por nodo, inmediatamente después de instalar LXD.

### live migration
Migración de un contenedor en ejecución de un nodo del cluster a otro sin detenerlo previamente. LXD soporta live migration, pero su configuración y comportamiento en este entorno 🔴 Pendiente de validación. La migración estándar (offline) requiere detener el contenedor antes de moverlo con `lxc move CONTENEDOR --target NODO`.

### Loki
Sistema de agregación y almacenamiento centralizado de logs. Cada host del cluster LXD reenvía sus logs de sistema (vía `rsyslog`) a un Loki alojado deliberadamente en **otra infraestructura**, distinta del propio cluster — para no perder visibilidad de logs justo si el cluster LXD tuviera una falla. Ver [03_Componentes.md](03_Componentes.md).

---

## M

### MicroOVN
Distribución de OVN gestionada por Canonical, instalada via snap. Simplifica la configuración de OVN al proveer comandos propios (`microovn cluster bootstrap`, etc.). Es la capa que LXD usa para gestionar la red OVN.

### migrate (LXD)
Operación que mueve un contenedor de un nodo del cluster a otro. El contenedor debe estar detenido. Desde la UI: seleccionar contenedor → Migrate → seleccionar nodo destino.

---

## N

### nodo
Cada VM que corre LXD y pertenece al cluster. Un cluster tiene múltiples nodos. Cada nodo tiene su propio almacenamiento local (ZFS o LVM, según cómo se instaló) pero comparten la base de datos del cluster.

### northbound interface (OVN)
Interfaz de comandos por la cual LXD interactúa con OVN para crear switches, routers e interfaces virtualizadas. Se configura una sola vez por cluster LXD (`network.ovn.northbound_connection_string`) porque se replica automáticamente vía la base de datos distribuida de LXD a todos los nodos. Ver [04_Instalacion.md](04_Instalacion.md).

---

## O

### overlay / underlay
Modelo de capas usado para describir una red virtualizada construida sobre otra red física o lógica preexistente. El **underlay** es la red de transporte subyacente (en este proyecto: la red corporativa IP entre sitios, y sobre ella, la malla [WireGuard](#wireguard)). El **overlay** es la red virtual que corre encima (en este proyecto: [OVN](#ovn-open-virtual-network)). Ver [ADR-0006](adr/ADR-0006-wireguard-underlay-ovn-multisitio.md).

### OVN (Open Virtual Network)
Capa de red definida por software (SDN) que permite crear redes virtuales que atraviesan múltiples hosts físicos o VMs. En este proyecto, OVN conecta los contenedores de distintos sitios geográficos como si estuvieran en la misma red. Su túnel de datos nativo (protocolo [geneve](#geneve)) no cifra el tráfico y, en este entorno, resultó bloqueado al viajar directamente sobre la red corporativa entre sitios en Capa 3 separada — por eso corre sobre una malla [WireGuard](#wireguard) como transporte underlay. Ver [ADR-0006](adr/ADR-0006-wireguard-underlay-ovn-multisitio.md). Usa la misma tecnología de base de datos distribuida que LXD (Dqlite) para su plano de control.

---

## P

### perfil (profile)
Objeto LXD que agrupa configuraciones reutilizables: cloud-init, dispositivos, variables de configuración. Al asociar un perfil a un contenedor, este hereda todas las configuraciones del perfil. Un contenedor puede usar múltiples perfiles.

### PFR (Franco)
Ver [Franco / PFR](#franco--pfr).

### proyecto (LXD project)
Espacio de nombres aislado dentro del mismo cluster LXD: tiene su propio conjunto de contenedores, perfiles y, opcionalmente, redes. Permite definir límites de recursos (CPU, memoria, cantidad de instancias, redes) y restringir el acceso de un grupo de usuarios exclusivamente a ese proyecto. Es el mecanismo elegido por el equipo para dar aislamiento multi-tenant sobre la infraestructura compartida. Ver [ADR-0007](adr/ADR-0007-proyectos-lxd-multitenancy.md) y [05_Configuracion.md](05_Configuracion.md).

### proxy HTTP
Servidor intermediario que reenvía solicitudes HTTP/HTTPS hacia internet. En este proyecto, el equipo de seguridad habilitó un proxy HTTP para que los contenedores puedan descargar paquetes. Se configura en LXD mediante `core.http_proxy` y en cloud-init mediante la sección de proxy.

### puerto 8443
Puerto del cluster LXD (comunicación entre nodos y acceso de usuarios a la Web UI).

### puerto 8444
Puerto de administración de LXD (gestión del daemon local).

---

## Q

### quórum
Número mínimo de nodos que deben estar disponibles para que el cluster pueda realizar operaciones de escritura en su base de datos (Dqlite). Con 3 nodos, el quórum es 2 — el cluster puede perder 1 nodo y seguir operando. Con 1 nodo (estado actual), el quórum es 1 — cualquier falla del único nodo deja el cluster inoperativo. Ver también: [Dqlite](#dqlite), [split-brain](#split-brain).

---

## R

### replicación activo-standby / multimaestro
Patrones de replicación de bases de datos: en **activo-standby**, las escrituras van únicamente al nodo maestro y las lecturas pueden distribuirse hacia uno o más nodos standby (solo lectura), evitando cuello de botella entre lectura y escritura; el failover (promover un standby a maestro) es una maniobra planificada, típicamente usada durante mantenimiento del nodo activo. En **multimaestro**, más de un nodo acepta escrituras simultáneamente. LXD no gestiona ni provee replicación de datos de aplicación — es responsabilidad de quien diseña cada servicio, según lo que soporte la base de datos elegida. Ver [09_FAQ.md](09_FAQ.md).

### rich rule (firewalld)
Regla de firewall avanzada en firewalld que permite especificar origen, destino, protocolo, puerto y acción. Más expresiva que las reglas simples.

### rollback
Proceso de revertir un cambio o volver al estado anterior. En LXD, puede implicar restaurar un contenedor desde una imagen o solicitar la reversión de la VM a SBA/AIT.

### RPO (Recovery Point Objective)
Cantidad máxima de datos que una organización puede perder ante un incidente, medida en tiempo. Ejemplo: RPO de 24 horas significa que se acepta perder como máximo un día de datos. Define la frecuencia mínima necesaria de backups. 🔴 No definido para el cluster LXD en el estado actual.

### RTO (Recovery Time Objective)
Tiempo máximo tolerable que un servicio puede estar inactivo tras un incidente antes de que el impacto sea inaceptable. Ejemplo: RTO de 4 horas significa que el servicio debe estar restaurado en menos de 4 horas. 🔴 No definido para el cluster LXD en el estado actual. Ver [15_Revision_Arquitectonica.md](15_Revision_Arquitectonica.md).

---

## S

### SBA / AIT
Equipos responsables de la administración de la infraestructura VMware. Son quienes deben ser contactados para: crear VMs, agregar interfaces de red, configurar backup de VMs.

### SDN (Software Defined Networking)
Modelo de red donde la topología y el enrutamiento se gestionan por software en lugar de hardware físico. OVN es la implementación SDN elegida para este proyecto.

### SSSD (System Security Services Daemon)
Servicio que permite a los hosts Linux del cluster autenticar usuarios contra un directorio externo (en este proyecto, [LDAP](#ldap) corporativo) en lugar de usuarios locales. También gestiona la autorización de `sudo` (`sudo_provider = ldap`). Ver [03_Componentes.md](03_Componentes.md) y [LL-015 en 12_Lecciones_Aprendidas.md](12_Lecciones_Aprendidas.md).

### snap
Gestor de paquetes universal de Canonical para Linux. LXD y MicroOVN se instalan como snaps. Los snaps son autocontenidos y **actualizan automáticamente por defecto** (una revisión diaria). Ver `snap refresh --hold` en [04_Instalacion.md](04_Instalacion.md) — necesario para evitar desincronización de versiones entre nodos del cluster.

### snapshot (LXD)
Captura instantánea del estado de un contenedor en un momento dado, usada como punto de restauración rápido antes de un cambio riesgoso. Es por contenedor (si un servicio tiene frontend y base de datos en contenedores separados, cada uno necesita su propio snapshot) y, a diferencia de publicar una [imagen](#lxd) (`lxc publish`), no crea un artefacto reutilizable para clonar otros contenedores — solo permite revertir (`lxc restore`) el mismo contenedor a ese estado. Los snapshots **no son migrables entre proyectos LXD**. Ver [06_Operacion.md](06_Operacion.md) y [12_Lecciones_Aprendidas.md](12_Lecciones_Aprendidas.md).

### split-brain
Condición de error en un cluster distribuido donde dos o más grupos de nodos quedan aislados entre sí (por corte de red) y cada grupo cree ser el único activo, tomando decisiones conflictivas sobre el mismo estado. En un cluster LXD de 3 nodos en 3 sitios distintos, un corte de enlace puede provocar que el nodo aislado y los otros dos intenten mantener el liderazgo simultáneamente. Dqlite mitiga esto mediante quórum, pero el riesgo no desaparece completamente. Ver también: [quórum](#quórum), [Dqlite](#dqlite).

### storage pool
Volumen de almacenamiento dedicado para los datos de los contenedores en LXD. En este proyecto se usa ZFS sobre el disco `/dev/sda6` (315 GB en PFR1).

---

## T

### TLS (Transport Layer Security)
Protocolo de cifrado para comunicaciones en red. LXD usa TLS para autenticar a los usuarios que acceden a la Web UI. Cada usuario genera un certificado TLS en su navegador.

### token (LXD)
Credencial temporal generada por LXD para autenticar a un nuevo usuario en la Web UI o para que un nuevo nodo se una al cluster. Los tokens tienen tiempo de expiración.

---

## U

### Ubuntu Fan
Tecnología de red overlay de Canonical para conectar contenedores. Requiere una subred /24. **Descartada en este proyecto** porque la red de gestión es /29. Ver [10_Decisiones.md](10_Decisiones.md).

### user-data (cloud-init)
Sección de la configuración de cloud-init donde se definen las instrucciones que se ejecutarán al primer arranque: paquetes a instalar, usuarios a crear, scripts a ejecutar. **Requiere el header `#cloud-config`** al inicio del bloque YAML.

---

## V

### VLAN 411
VLAN de red dedicada al tráfico de contenedores en Franco (Carpinelli y Fernando usan su propia VLAN local, con un número distinto). Debe ser habilitada por Cristian (administrador VMware) en la VM correspondiente. 🟡 A diferencia de lo asumido inicialmente en [ADR-0002](adr/ADR-0002-red-ovn-vs-ubuntu-fan.md), **no es necesario que todos los sitios usen la misma VLAN** — cada sitio puede tener la suya. Lo que sí exige LXD es que el **nombre de la interfaz** de servicio sea idéntico en todos los nodos del cluster. Ver [ADR-0006](adr/ADR-0006-wireguard-underlay-ovn-multisitio.md).

### VTT
Formato de archivo de subtítulos web (WebVTT). En este proyecto, las grabaciones de reuniones se almacenan como archivos `.vtt` en [`reunion/`](../reunion/).

---

## W

### WireGuard
Tecnología de red overlay punto a punto (mesh), mucho más simple que OVN: no tiene plano de control ni base de datos distribuida, toda su configuración (claves, endpoints, rutas) es manual. Se adoptó como capa de transporte **underlay**, cifrada, para interconectar los sitios geográficos del cluster — el túnel de datos de OVN corre encima de la malla WireGuard. Ver [ADR-0006](adr/ADR-0006-wireguard-underlay-ovn-multisitio.md) y [03_Componentes.md](03_Componentes.md).

---

## Z

### ZFS (Zettabyte File System)
Sistema de archivos avanzado con capacidades de storage pool, snapshots y checksums integrados. Elegido como driver de almacenamiento para LXD en este proyecto. Ver [10_Decisiones.md](10_Decisiones.md).
