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

### bootstrap
Proceso de inicialización de un componente que no tiene dependencias previas. En MicroOVN, `microovn cluster bootstrap` configura el primer nodo OVN del cluster. Solo se ejecuta una vez, en el primer nodo.

---

## C

### CAR (Carpinelli)
Uno de los tres sitios geográficos del cluster LXD. Prefijo para los nodos de ese sitio: `CAR1`, `CAR2`, etc. El nodo CAR1 está pendiente de instalación al momento de la primera reunión.

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

---

## E

### EOL (End of Life)
Estado de un software cuando su desarrollador deja de publicar actualizaciones y parches de seguridad. CentOS 7 alcanzó EOL, lo que motiva la migración a Ubuntu LXD.

---

## F

### FDO (Fernando)
Uno de los tres sitios geográficos del cluster LXD. Prefijo para los nodos de ese sitio: `FDO1`, `FDO2`, etc. El nodo FDO1 está pendiente de instalación al momento de la primera reunión.

### firewalld
Sistema de gestión del firewall en Linux basado en zonas y reglas. Permite agregar reglas en tiempo real (`--runtime`) y hacerlas permanentes (`--permanent`) o usar `--runtime-to-permanent` para promover todas las reglas activas.

### Franco / PFR
Sitio geográfico donde se instaló el primer nodo del cluster (PFR1). Es el nodo de referencia para replicar la instalación en otros sitios.

---

## I

### InfraFileRoom
Servicio productivo actualmente corriendo en CentOS 7. Contiene aproximadamente 800 GB de datos. Es una de las migraciones prioritarias al cluster LXD.

---

## L

### lxc
Herramienta de línea de comandos (CLI) para interactuar con LXD. Permite crear, iniciar, detener, eliminar y configurar contenedores e imágenes. Es el cliente del servicio `lxd`.

### LXD
Sistema de gestión de contenedores de sistema desarrollado por Canonical. Expone una API REST que puede ser usada tanto por el CLI (`lxc`) como por la Web UI. Version usada en este proyecto: 5.21. Se instala via snap.

### lxd init
Wizard interactivo de inicialización de LXD. Configura: clustering, storage pool, networking, métricas y puertos. Se ejecuta una sola vez por nodo, inmediatamente después de instalar LXD.

### live migration
Migración de un contenedor en ejecución de un nodo del cluster a otro sin detenerlo previamente. LXD soporta live migration, pero su configuración y comportamiento en este entorno 🔴 Pendiente de validación. La migración estándar (offline) requiere detener el contenedor antes de moverlo con `lxc move CONTENEDOR --target NODO`.

---

## M

### MicroOVN
Distribución de OVN gestionada por Canonical, instalada via snap. Simplifica la configuración de OVN al proveer comandos propios (`microovn cluster bootstrap`, etc.). Es la capa que LXD usa para gestionar la red OVN.

### migrate (LXD)
Operación que mueve un contenedor de un nodo del cluster a otro. El contenedor debe estar detenido. Desde la UI: seleccionar contenedor → Migrate → seleccionar nodo destino.

---

## N

### nodo
Cada VM que corre LXD y pertenece al cluster. Un cluster tiene múltiples nodos. Cada nodo tiene su propio almacenamiento ZFS pero comparten la base de datos del cluster.

---

## O

### OVN (Open Virtual Network)
Capa de red definida por software (SDN) que permite crear redes virtuales que atraviesan múltiples hosts físicos o VMs. En este proyecto, OVN conecta los contenedores de distintos sitios geográficos como si estuvieran en la misma red.

---

## P

### perfil (profile)
Objeto LXD que agrupa configuraciones reutilizables: cloud-init, dispositivos, variables de configuración. Al asociar un perfil a un contenedor, este hereda todas las configuraciones del perfil. Un contenedor puede usar múltiples perfiles.

### PFR (Franco)
Ver [Franco / PFR](#franco--pfr).

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

### snap
Gestor de paquetes universal de Canonical para Linux. LXD y MicroOVN se instalan como snaps. Los snaps son autocontenidos y actualizan automáticamente.

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
VLAN de red dedicada para el tráfico de contenedores (separada de la interfaz de gestión). Debe ser habilitada por Cristian (administrador VMware) en cada VM que forme parte del cluster. Es prerequisito para que OVN funcione correctamente.

### VTT
Formato de archivo de subtítulos web (WebVTT). En este proyecto, las grabaciones de reuniones se almacenan como archivos `.vtt` en [`reunion/`](../reunion/).

---

## Z

### ZFS (Zettabyte File System)
Sistema de archivos avanzado con capacidades de storage pool, snapshots y checksums integrados. Elegido como driver de almacenamiento para LXD en este proyecto. Ver [10_Decisiones.md](10_Decisiones.md).
