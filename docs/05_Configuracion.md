# 05 — Configuración del sistema

> **Audiencia:** Ingenieros de infraestructura y operadores del cluster.
> **Propósito:** Documentar todos los parámetros y configuraciones del sistema: proxy, cloud-init, perfiles, dispositivos y firewall. No incluye instalación (ver [04_Instalacion.md](04_Instalacion.md)).

---

## Proxy HTTP de LXD

### ¿Qué controla?
El proxy HTTP que LXD usa para comunicarse con internet: descargar imágenes de contenedores, actualizaciones, etc.

### Parámetros

| Parámetro | Archivo/Comando | Función | Ejemplo |
|---|---|---|---|
| `core.http_proxy` | `lxc config set` | Proxy para tráfico HTTP de LXD | `http://32.x.x.x:3128` |
| `core.https_proxy` | `lxc config set` | Proxy para tráfico HTTPS de LXD | `http://32.x.x.x:3128` |
| `core.proxy_ignore_hosts` | `lxc config set` | Hosts sin proxy (acceso directo) | `127.0.0.1,localhost` |

> **Nota:** La IP del proxy (🔴 Pendiente de validación) debe confirmarse con Nicolás (equipo de seguridad). En la reunión se mencionó `32.x.x.x:3128`.

### Ver la configuración actual
```bash
lxc config show
# Buscar las claves core.http_proxy, core.https_proxy, core.proxy_ignore_hosts
```

### Impacto de configuración incorrecta
Sin el proxy configurado correctamente, LXD no puede descargar imágenes de contenedores ni el cloud-init puede instalar paquetes via APT.

---

## Perfiles (profiles)

Los perfiles agrupan configuración reutilizable: cloud-init, dispositivos y variables. Un contenedor puede asociarse a uno o múltiples perfiles.

### Ver perfiles existentes
```bash
lxc profile list
lxc profile show NOMBRE_PERFIL
```

### Editar un perfil
```bash
lxc profile edit NOMBRE_PERFIL
# Abre el perfil en el editor de texto configurado ($EDITOR)
```

### Estructura de un perfil con cloud-init y dispositivo proxy

```yaml
config:
  cloud-init.user-data: |
    #cloud-config
    package_update: true
    package_upgrade: true
    packages:
      - apache2
      - php8.5
devices:
  proxy1:
    bind: instance
    connect: tcp:IP_PROXY:3128
    listen: tcp:127.0.0.1:3128
    type: proxy
description: Perfil base con cloud-init y acceso a internet via proxy
name: nombre-perfil
```

> **Advertencia:** El bloque `user-data` **debe comenzar exactamente con `#cloud-config`** en la primera línea. Sin este header, cloud-init falla con error `unhandled not multipart text`. Ver [07_Troubleshooting.md](07_Troubleshooting.md).

---

## Configuración cloud-init (user-data)

### ¿Qué es?
La sección `user-data` del perfil define qué hace cloud-init en el primer arranque del contenedor.

### Campos principales

| Campo | Tipo | Descripción | Ejemplo |
|---|---|---|---|
| `package_update` | boolean | Actualizar la lista de paquetes APT antes de instalar | `true` |
| `package_upgrade` | boolean | Actualizar los paquetes instalados a sus últimas versiones | `true` |
| `packages` | lista | Lista de paquetes APT a instalar | `- apache2` |
| `write_files` | lista | Archivos a escribir en el filesystem | Ver documentación cloud-init |
| `runcmd` | lista | Comandos a ejecutar al finalizar la inicialización | `- systemctl restart apache2` |

### Ejemplo completo

```yaml
#cloud-config
package_update: true
package_upgrade: true
packages:
  - apache2
  - php8.5
```

### Verificar que cloud-init ejecutó correctamente
```bash
# Dentro del contenedor:
cloud-init status
# Resultado esperado: status: done

# Verificar servicios instalados:
ss -ntlp
# Debe mostrar puerto 80 escuchando (si apache2 está instalado)
```

### Limitación importante
✅ Cloud-init se ejecuta **solo en el primer arranque** del contenedor. Si se modifica el perfil y se reinicia el contenedor, los cambios en cloud-init **no se aplican**. Para re-ejecutar cloud-init, hay que **eliminar y recrear** el contenedor.

---

## Secciones de cloud-init en LXD

LXD expone tres secciones de cloud-init para los perfiles:

| Sección | Clave del perfil | Uso |
|---|---|---|
| User data | `cloud-init.user-data` | Paquetes, usuarios, archivos, comandos |
| Network config | `cloud-init.network-config` | Configuración de red estática (IPs fijas al contenedor) |
| Vendor data | `cloud-init.vendor-data` | Configuración del proveedor de infraestructura |

---

## Dispositivo proxy LXD (salida a internet)

### ¿Qué es?
Un dispositivo proxy LXD crea un socket de red dentro del contenedor que traduce tráfico hacia el host. Se usó como workaround temporal para que los contenedores accedan al proxy HTTP mientras OVN no estaba disponible.

> **Actualización (segunda reunión):** en PFR1 y CAR1, donde OVN ya está funcional (ver [ADR-0006](adr/ADR-0006-wireguard-underlay-ovn-multisitio.md)), este workaround fue reemplazado por un **contenedor gateway dedicado a operación y mantenimiento**: un segundo contenedor gateway (similar al gateway de servicios, ver [02_Arquitectura.md](02_Arquitectura.md)) conectado a la interfaz de gestión del host — la única que tiene permiso de salida hacia el proxy corporativo. Los demás contenedores del sitio enrutan su tráfico de salida (`apt`, descarga de imágenes, etc.) hacia este gateway a través de la red OVN interna, en lugar de tener cada uno su propio dispositivo proxy individual. Este patrón sigue siendo temporal en los sitios donde OVN todavía no está disponible (ej. FDO1), donde el dispositivo proxy por contenedor descrito abajo sigue siendo necesario.

### Configuración (en el perfil o en el contenedor)

```yaml
devices:
  proxy-salida:
    type: proxy
    bind: instance
    listen: tcp:127.0.0.1:3128
    connect: tcp:IP_PROXY:3128
```

| Parámetro | Descripción |
|---|---|
| `type: proxy` | Tipo de dispositivo: proxy de red |
| `bind: instance` | El socket `listen` está dentro del contenedor |
| `listen: tcp:127.0.0.1:3128` | El contenedor escucha en esta dirección |
| `connect: tcp:IP_PROXY:3128` | El host conecta esta dirección al exterior |

> **Confusión frecuente:** `bind: instance` significa que el lado `listen` (la dirección que escucha) es el **interior del contenedor**. `bind: host` significa que el lado `listen` es el **host**. Norberto lo invirtió durante la demostración y tuvo que corregirlo.

---

## Dispositivo proxy LXD (exposición de servicios sin OVN)

### ¿Cuándo usar?
Cuando se necesita exponer un servicio del contenedor hacia el exterior antes de que OVN esté disponible. Redirige tráfico de la interfaz de gestión del host hacia el contenedor.

> **Importante:** Workaround temporal. No es la solución de producción.

### Configuración

```yaml
devices:
  web-public:
    type: proxy
    bind: host
    listen: tcp:IP_GESTION_VM:80
    connect: tcp:127.0.0.1:80
```

| Parámetro | Descripción |
|---|---|
| `bind: host` | El socket `listen` está en el host (interfaz de gestión) |
| `listen: tcp:IP_GESTION_VM:80` | El host escucha en esta IP/puerto |
| `connect: tcp:127.0.0.1:80` | Conectar al servicio del contenedor en localhost:80 |

---

## Configuración de firewall (firewalld)

### Rich rules para acceso a Web UI

```bash
# Agregar IP de operador:
firewall-cmd --add-rich-rule='rule family=ipv4 source address=IP_OPERADOR port port=8443-8444 protocol=tcp accept'

# Hacer permanente:
firewall-cmd --runtime-to-permanent

# Ver reglas activas:
firewall-cmd --list-rich-rules

# Ver estado del firewall:
firewall-cmd --state
```

### Impacto de configuración incorrecta
Si falta la rich rule para la IP de un operador, ese operador no puede acceder a la Web UI aunque el servicio LXD esté funcionando.

---

## Interfaz de red del contenedor "gateway de servicios" (driver IPVLAN)

### ¿Qué es?
Dispositivo de red que conecta un contenedor directamente a una interfaz física del host, reutilizando su misma dirección MAC. Se usa exclusivamente en los contenedores que actúan como gateway de servicios de un sitio o proyecto (ver [02_Arquitectura.md](02_Arquitectura.md) y [03_Componentes.md](03_Componentes.md)).

### Configuración (en el perfil)

```yaml
devices:
  eth-ovn:
    type: nic
    network: ovn-red-interna     # Pata hacia la red virtualizada del cluster (este-oeste)
  eth-servicio:
    type: nic
    nictype: ipvlan
    parent: nicsrv1               # Interfaz física de servicio del host (norte-sur)
    mode: l2
```

| Parámetro | Descripción |
|---|---|
| `nictype: ipvlan` | Selecciona el driver IPVLAN en lugar del bridge por defecto |
| `parent: nicsrv1` | Interfaz física del host a la que se conecta (debe tener el mismo nombre en todos los nodos — ver [04_Instalacion.md — Paso 0](04_Instalacion.md)) |
| `mode: l2` | Modo de operación de IPVLAN a nivel de Capa 2 |

> **Por qué IPVLAN:** una política de seguridad de VMware bloquea tráfico saliente con una MAC distinta de la asignada a la VM. IPVLAN reutiliza la MAC del host para todo el tráfico de los contenedores, evitando ese bloqueo sin tener que solicitar una excepción a VMware. Ver el detalle completo en [03_Componentes.md](03_Componentes.md).

---

## Perfil del contenedor "gateway de servicios"

### ¿Qué controla?
La configuración estándar aplicada a cada contenedor que actúa como router/gateway de entrada y salida de servicios de un sitio o proyecto (ver [02_Arquitectura.md](02_Arquitectura.md)).

### Elementos del perfil

| Elemento | Configuración | Por qué |
|---|---|---|
| Interfaces | Una hacia la red OVN (`type: nic`), otra `ipvlan` hacia `nicsrv1` (ver sección anterior) | El contenedor enruta entre la red interna del cluster y la red de servicio del sitio |
| SSH | Deshabilitado (`systemctl disable --now ssh`, dentro del contenedor) | La administración se hace exclusivamente vía `lxc exec`. Reduce la superficie de movimiento lateral si algún contenedor del cluster estuviera comprometido |
| Firewall | Habilitado y configurado para actuar como router (reenvío de paquetes entre sus dos interfaces) | Es su única función — no aloja aplicaciones |
| `journald` | Límite de 100 MB (`SystemMaxUse=100M` en `/etc/systemd/journald.conf`, o `limits.kernel.journald.systemmaxuse` en el perfil) | Por defecto `journald` puede acumular hasta 4 GB de logs. Este contenedor no genera logs de aplicación — 100 MB es más que suficiente |
| NTP | `systemd-timesyncd` configurado igual que el host (ver [04_Instalacion.md — Paso 10](04_Instalacion.md)) | Evita desincronización de reloj entre el contenedor y el cluster |

### Ejemplo — límite de journald en el perfil

```yaml
config:
  limits.kernel.journald.systemmaxuse: "100MB"
```

### Cómo verificar
```bash
lxc exec CONTENEDOR -- systemctl status ssh
# Debe mostrar "inactive (dead)"

lxc exec CONTENEDOR -- journalctl --disk-usage
# Debe mostrar un uso cercano o menor a 100 MB
```

---

## Variable de entorno de proxy para APT y snap

### ¿Qué controla?
Que las herramientas de línea de comandos dentro de un contenedor o host (`apt`, `snap`) usen el proxy HTTP corporativo, además de la configuración nativa de LXD (`core.http_proxy`, ver arriba).

### Configuración

```bash
export http_proxy=http://IP_PROXY:3128
export https_proxy=http://IP_PROXY:3128
```

> **Nota:** Esta variable debe adaptarse al contexto donde se use: exportarla en la sesión de shell interactiva, agregarla a `/etc/environment` para que aplique a todos los procesos del sistema, o configurarla específicamente para `apt` (`/etc/apt/apt.conf.d/`) y para `snap` (variables de entorno del servicio `snapd`) según corresponda.

### Impacto de configuración incorrecta
Sin esta variable (o con una IP de proxy incorrecta), comandos como `apt update` o `snap install` fallan por falta de acceso a internet, incluso si `core.http_proxy` de LXD está bien configurado — son mecanismos independientes.

---

## Reenvío de logs del host a Loki (rsyslog)

### ¿Qué controla?
Que los logs del sistema operativo de cada host del cluster se envíen a un servidor Loki centralizado, ubicado en **otra infraestructura** (no en el propio cluster LXD).

### Configuración (rsyslog)

Agregar en la configuración de `rsyslog` (ej. `/etc/rsyslog.d/`) una directiva de reenvío hacia el endpoint de Loki correspondiente. 🔴 Sintaxis exacta y endpoint: Pendiente de validación — se instaló el paquete pero la directiva de reenvío no quedó documentada en la sesión.

### Por qué un Loki externo al cluster
Si los hosts del cluster LXD apuntaran a un Loki alojado dentro del mismo cluster, una falla del cluster dejaría al equipo sin logs justo en el momento en que más se necesitan para diagnosticar. Ver [12_Lecciones_Aprendidas.md](12_Lecciones_Aprendidas.md).

### Cómo verificar
🔴 Pendiente de validación — confirmar recepción de logs en el Loki destino.

---

## Proyectos LXD (multi-tenancy)

### ¿Qué controla?
El aislamiento de recursos y de acceso entre distintos equipos/áreas que comparten el cluster. Ver la decisión completa en [ADR-0007](adr/ADR-0007-proyectos-lxd-multitenancy.md).

### Crear un proyecto nuevo

```bash
lxc project create PRJ-CODIGO_AREA
lxc project switch PRJ-CODIGO_AREA
```

### Definir límites del proyecto

```bash
lxc project set PRJ-CODIGO_AREA limits.networks 2
lxc project set PRJ-CODIGO_AREA limits.cpu 5
lxc project set PRJ-CODIGO_AREA limits.memory 16GB
lxc project set PRJ-CODIGO_AREA limits.instances 5
lxc project set PRJ-CODIGO_AREA limits.containers 4
lxc project set PRJ-CODIGO_AREA limits.virtual-machines 1
```

| Parámetro | Función | Valor por defecto | Impacto de cambiar el valor |
|---|---|---|---|
| `limits.networks` | Cantidad máxima de redes que el proyecto puede referenciar | Sin límite | Limita cuántas redes (ej. OVN + servicio) puede usar el proyecto |
| `limits.cpu` | Cantidad máxima de vCPUs que puede consumir la suma de instancias del proyecto | Sin límite | Evita que el proyecto agote la CPU disponible del cluster |
| `limits.memory` | Memoria RAM máxima total del proyecto | Sin límite | Evita que el proyecto agote la RAM disponible del cluster |
| `limits.instances` | Cantidad máxima de instancias (contenedores + VMs) | Sin límite | Limita el crecimiento descontrolado de instancias |
| `limits.containers` | Cantidad máxima de contenedores | Sin límite | Subconjunto de `limits.instances`, específico para contenedores |
| `limits.virtual-machines` | Cantidad máxima de VMs | Sin límite | Subconjunto de `limits.instances`, específico para VMs |

> **Riesgo de configuración incorrecta:** si un proyecto se crea **sin** definir estos límites explícitamente, hereda un comportamiento sin restricciones — el mismo riesgo que compartir el proyecto `default`. Definir límites es un paso obligatorio, no opcional, al dar de alta un proyecto nuevo.

### Crear un grupo de acceso restringido al proyecto

```bash
lxc auth group create NOMBRE_GRUPO
lxc auth group permission add NOMBRE_GRUPO project PRJ-CODIGO_AREA operator
lxc auth identity group add NOMBRE_USUARIO NOMBRE_GRUPO
```

Los usuarios del grupo solo ven y pueden operar los recursos del proyecto al que el grupo tiene permiso — no ven el proyecto `default` ni los de otros equipos.

### Cómo verificar

```bash
lxc project list
# Debe mostrar el proyecto nuevo con sus límites

lxc project show PRJ-CODIGO_AREA
# Muestra la configuración completa, incluidos los límites definidos

lxc auth group list
# Debe mostrar el grupo y su permiso restringido al proyecto
```

### Recomendación del equipo

✅ A partir de esta reunión, **todo trabajo nuevo de un equipo/área se hace en un proyecto dedicado**, no en `default`. Ver [ADR-0007](adr/ADR-0007-proyectos-lxd-multitenancy.md).

---

## Documentos relacionados

| Tema | Documento |
|---|---|
| Instalación previa | [04_Instalacion.md](04_Instalacion.md) |
| Operación con contenedores y proyectos | [06_Operacion.md](06_Operacion.md) |
| Troubleshooting de configuración | [07_Troubleshooting.md](07_Troubleshooting.md) |
| Decisión sobre dispositivo proxy | [10_Decisiones.md](10_Decisiones.md) |
| Decisión sobre WireGuard como underlay | [ADR-0006](adr/ADR-0006-wireguard-underlay-ovn-multisitio.md) |
| Decisión sobre proyectos LXD | [ADR-0007](adr/ADR-0007-proyectos-lxd-multitenancy.md) |
