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
| **Responsabilidad** | Proveer la red SDN transversal entre nodos y sitios del cluster |
| **Dependencias** | snap, red IP entre nodos (para comunicación del plano de control OVN) |
| **Entradas** | Configuración del cluster OVN, interfaces de red (VLAN 411) |
| **Salidas** | Red virtual que conecta contenedores entre sitios |
| **Impacto si falla** | Los contenedores existentes pueden seguir corriendo, pero pierden conectividad de red entre sitios |
| **Cómo verificar** | `snap services microovn` |
| **Estado actual** | ✅ Instalado y bootstrapped en PFR1. 🔴 Sin red OVN funcional (falta VLAN 411) |

### Buenas prácticas

- `microovn cluster bootstrap` se ejecuta **solo una vez**, en el primer nodo (PFR1).
- Los nodos adicionales se agregan al cluster OVN durante el proceso de `lxd init` (usando join token).

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
