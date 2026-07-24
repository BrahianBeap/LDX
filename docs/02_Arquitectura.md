# 02 — Arquitectura del sistema

> **Audiencia:** Ingenieros de infraestructura, arquitectos, SRE.
> **Propósito:** Visión completa de la arquitectura: sitios, componentes, redes, almacenamiento y relaciones entre ellos.

---

## Visión general

El sistema es un **cluster LXD distribuido en 3 sitios geográficos**. Cada sitio tiene una o más VMs ejecutando LXD. Todos los nodos comparten una base de datos de cluster unificada, lo que permite gestionar contenedores desde cualquier nodo y migrarlos entre sitios.

```
         ┌─────────────────────────────────────────────────────┐
         │                   CLUSTER LXD                       │
         │                                                     │
         │   ┌───────────┐   ┌───────────┐   ┌───────────┐   │
         │   │  Sitio PFR │   │  Sitio CAR │   │  Sitio FDO │   │
         │   │  (Franco)  │   │(Carpinelli)│   │ (Fernando) │   │
         │   │            │   │            │   │            │   │
         │   │  ┌──────┐  │   │  ┌──────┐  │   │  ┌──────┐  │   │
         │   │  │ PFR1 │  │   │  │ CAR1 │  │   │  │ FDO1 │  │   │
         │   │  │ (VM) │  │   │  │ (VM) │  │   │  │ (VM) │  │   │
         │   │  │ DB   │  │   │  │ DB   │  │   │  │ 🔴   │  │   │
         │   │  │ líder│  │   │  │standby│  │   │  │pend. │  │   │
         │   │  └──────┘  │   │  └──────┘  │   │  └──────┘  │   │
         │   └───────────┘   └───────────┘   └───────────┘   │
         │         │                │                │         │
         │         └────────────────┴────────────────┘         │
         │        Red OVN (overlay) sobre WireGuard (underlay)  │
         │        ✅ Funcional PFR1↔CAR1 · 🔴 FDO1 pendiente    │
         └─────────────────────────────────────────────────────┘
```

> **Nota:** CAR1 fue instalado y unido al cluster en la segunda reunión (`reunion/segunda_reunion LXD _ Implementacion.vtt`). El cluster tiene 2 de los 3 miembros necesarios para quórum de alta disponibilidad de la base de datos (ver [Dqlite en 08_Glosario.md](08_Glosario.md#dqlite)). FDO1 (Fernando) sigue pendiente de instalación. La red OVN entre PFR1 y CAR1 es funcional gracias al transporte WireGuard — ver [ADR-0006](adr/ADR-0006-wireguard-underlay-ovn-multisitio.md).

---

## Sitios y nodos

| Sitio | Nombre largo | Prefijo nodos | Estado |
|---|---|---|---|
| PFR | Franco | PFR1, PFR2, ... | ✅ PFR1 instalado — miembro fundador, database-leader |
| CAR | Carpinelli | CAR1, CAR2, ... | ✅ CAR1 instalado y unido al cluster — database-standby |
| FDO | Fernando | FDO1, FDO2, ... | 🔴 Pendiente — sería el tercer miembro (completaría quórum de HA de base de datos) |

✅ Convención de nombres: `SITIO` + número secuencial (PFR1, CAR1, FDO1).

🟡 El equipo previó, a futuro, sumar sitios adicionales fuera de los tres iniciales (mencionados como candidatos: IT y Ciudad del Este). No hay compromiso de fecha ni de cantidad final — marcado como planificación abierta, no como alcance confirmado.

---

## Infraestructura subyacente

```
  Infraestructura física / hypervisor
  ┌──────────────────────────────────┐
  │         VMware (SBA/AIT)         │
  │                                  │
  │  ┌────────────────────────────┐  │
  │  │  VM Ubuntu (ej: PFR1)      │  │
  │  │                            │  │
  │  │  ┌─────────┐  ┌────────┐  │  │
  │  │  │  ns192  │  │nicsrv1 │  │  │
  │  │  │ Gestión │  │Servicio│  │  │
  │  │  │  /29    │  │(VLAN   │  │  │
  │  │  │         │  │ local) │  │  │
  │  │  └─────────┘  └────────┘  │  │
  │  │       │            │       │  │
  │  │       ▼            ▼       │  │
  │  │  ┌──────────────────────┐  │  │
  │  │  │       LXD 5.21       │  │  │
  │  │  └──────────────────────┘  │  │
  │  └────────────────────────────┘  │
  └──────────────────────────────────┘
```

- ✅ Las VMs corren Ubuntu Linux y son gestionadas por el equipo VMware (contacto: Cristian).
- ✅ Cada VM tiene **dos interfaces de red**, cada una con un propósito exclusivo (ver [ADR-0006](adr/ADR-0006-wireguard-underlay-ovn-multisitio.md#aclaración-importante-sobre-vlan-411-actualiza-adr-0002)):
  - **Interfaz de gestión** (`ns192` en Franco): exclusiva para SSH y administración del host y de LXD (Web UI, puertos 8443/8444). No se usa para tráfico de contenedores.
  - **Interfaz de servicio** (`nicsrv1`): exclusiva para el tráfico de contenedores (OVN). Vive en una VLAN local propia de cada sitio — **no necesita ser la misma VLAN en los tres sitios**.
- ✅ **Convención obligatoria:** el nombre de la interfaz de servicio debe ser idéntico en todos los miembros del cluster (`nicsrv1` en Franco y en Carpinelli), independientemente del nombre original que le haya asignado el sistema operativo (ej. `NS35`, `NS37`). Se logra renombrando la interfaz por MAC en `netplan`. Esto es un requisito de LXD para que un contenedor migrado de un nodo a otro pueda conservar su configuración de red. Ver [05_Configuracion.md](05_Configuracion.md).

---

## Redes del sistema

### Red de gestión (existente)

| Campo | Valor |
|---|---|
| Tipo | Subred IPv4 |
| Tamaño | /29 (6 IPs utilizables) |
| Uso | Acceso SSH a VMs, Web UI de LXD (puertos 8443/8444), proxy HTTP |
| Estado | ✅ Operativa |

### Red de contenedores — OVN sobre WireGuard

| Campo | Valor |
|---|---|
| Tecnología overlay (Capa 3) | OVN (Open Virtual Network) via MicroOVN |
| Tecnología de transporte inter-sitio (underlay) | WireGuard (mesh cifrada) — ver [ADR-0006](adr/ADR-0006-wireguard-underlay-ovn-multisitio.md) |
| Interfaz de servicio local | `nicsrv1` (mismo nombre en todos los nodos, VLAN local propia de cada sitio) |
| Uso | Comunicación entre contenedores, incluso entre sitios distintos |
| Estado | ✅ Funcional entre PFR1 y CAR1 · 🔴 Pendiente extender a FDO1 |

**Por qué el túnel nativo de OVN no fue suficiente:** el túnel de datos de OVN, viajando directamente sobre la red corporativa entre sitios en Capa 3 separada, es bloqueado por un elemento de red intermedio no identificado (confirmado en dos implementaciones independientes). WireGuard se agregó como capa de transporte underlay cifrada, sobre la cual corre el túnel de OVN. Ver el análisis completo en [ADR-0006](adr/ADR-0006-wireguard-underlay-ovn-multisitio.md).

```
  Capa 3 — Red virtualizada del cluster (OVN)     ← contenedores, tráfico este-oeste
  Capa 2 — Malla WireGuard cifrada (underlay)      ← túnel punto a punto entre sitios
  Capa 1 — Red de transporte corporativa (backbone) ← red IP existente entre sitios
```

> **Importante:** Mientras un sitio no tenga la malla WireGuard configurada hacia los demás, sus contenedores **no pueden comunicarse** con contenedores de otros sitios. Ver [11_Riesgos.md](11_Riesgos.md) y [10_Decisiones.md](10_Decisiones.md).

### Patrón de contenedor "gateway de servicios"

Cada sitio/proyecto tiene un contenedor dedicado que actúa como **router/gateway de entrada y salida de servicios** para ese sitio (ejemplo: `presidente-franco-ss-gw` en Franco). Este contenedor:

- Tiene **dos interfaces**: una hacia la red OVN interna (comunicación este-oeste entre contenedores del cluster) y otra ligada directamente a la interfaz física de servicio del host (`nicsrv1`), mediante el driver **IPVLAN** (ver [03_Componentes.md](03_Componentes.md)).
- Concentra la(s) IP(s) pública(s)/de servicio de ese sitio — por ejemplo, la IP histórica de un servicio que se está migrando se asigna a este contenedor, no a cada contenedor individual, evitando mezclar la IP de un proyecto con la de otro.
- Se configura como **router**: firewall habilitado, SSH deshabilitado (la administración se hace exclusivamente vía `lxc exec`, nunca por SSH directo, para reducir superficie de movimiento lateral), y límites de `journald` bajos (100 MB) porque no aloja aplicaciones ni genera logs significativos.

Ver la configuración completa del perfil en [05_Configuracion.md](05_Configuracion.md).

### Modelo de multi-tenancy (proyectos LXD)

A partir de esta reunión, el equipo adoptó **proyectos LXD** (`lxc project`) como mecanismo de aislamiento entre equipos/áreas que comparten el cluster: cada proyecto tiene su propio conjunto de contenedores, perfiles, límites de recursos (CPU, memoria, redes, cantidad de instancias) y un grupo de identidad restringido a ese proyecto. Ver la decisión completa en [ADR-0007](adr/ADR-0007-proyectos-lxd-multitenancy.md) y la configuración en [05_Configuracion.md](05_Configuracion.md).

---

## Capa de almacenamiento

```
  ┌─────────────────────────────────┐
  │          LXD Storage Pool        │
  │                                  │
  │   Driver: ZFS                    │
  │   Disco: /dev/sda6               │
  │   Tamaño: 315 GB (en PFR1)       │
  │                                  │
  │   ┌──────────┐  ┌──────────┐    │
  │   │Contenedor│  │Contenedor│    │
  │   │  ubuntu1 │  │  ubuntu2 │    │
  │   └──────────┘  └──────────┘    │
  └─────────────────────────────────┘
```

- ✅ El almacenamiento es local a cada nodo. Cada nodo tiene su propio pool/volumen dedicado a LXD.
- 🟡 Los contenedores de un nodo usan el storage local de ese nodo.
- ✅ La migración de contenedores entre nodos transfiere los datos del storage origen al storage destino.
- 🟡 El particionamiento de disco puede variar levemente entre nodos según cómo se instaló cada VM: en PFR1 se usó un disco/partición dedicado (`/dev/sda6`, 315 GB) directamente para ZFS; en CAR1 el disco fue particionado con LVM, por lo que el volumen para LXD se creó como un nuevo volumen lógico (`lxd`) dentro del grupo de volúmenes existente, usando el espacio libre restante (ver [04_Instalacion.md](04_Instalacion.md)).

Ver decisión de ZFS en [10_Decisiones.md](10_Decisiones.md).

---

## Capa de acceso y autenticación

```
  Operador (navegador)
       │
       │ HTTPS:8443 / TLS
       ▼
  ┌──────────────────┐
  │   LXD Web UI     │
  │   (puerto 8443)  │
  │                  │
  │  Autenticación:  │
  │  Certificado TLS │
  │  + Token         │
  └──────────────────┘
       │
       ▼
  ┌──────────────────┐
  │   LXD daemon     │
  │   (lxd)          │
  │   puerto 8444    │
  └──────────────────┘
```

- ✅ Cada operador instala un certificado TLS en su navegador.
- ✅ El acceso a la Web UI es actualmente solo desde la red local (sin VPN).
- 🔴 Acceso VPN no configurado.

---

## Diagrama completo de componentes por nodo

```
  ┌──────────────────────────────────────────────────┐
  │                   VM (ej: PFR1)                   │
  │                                                   │
  │  ┌─────────────────────────────────────────────┐  │
  │  │                  LXD 5.21                   │  │
  │  │                                             │  │
  │  │  ┌───────────┐  ┌──────────┐  ┌─────────┐  │  │
  │  │  │  Storage  │  │ Network  │  │Contenedo│  │  │
  │  │  │ ZFS o LVM │  │   OVN    │  │  res    │  │  │
  │  │  │ (según    │  │          │  │         │  │  │
  │  │  │  nodo)    │  │          │  │         │  │  │
  │  │  └───────────┘  └──────────┘  └─────────┘  │  │
  │  └─────────────────────────────────────────────┘  │
  │                                                   │
  │  ┌──────────────┐  ┌────────────┐  ┌───────────┐  │
  │  │  MicroOVN    │  │  firewalld │  │ WireGuard │  │
  │  │  (snap)      │  │            │  │ (underlay)│  │
  │  └──────────────┘  └────────────┘  └───────────┘  │
  │                                                   │
  │  ┌──────────────────────────────────────────────┐  │
  │  │  Prometheus metrics endpoint (via LXD)        │  │
  │  └──────────────────────────────────────────────┘  │
  └──────────────────────────────────────────────────┘
```

---

## Flujo de despliegue de un nuevo contenedor

```
  1. Operador define perfil
     (cloud-init + dispositivos)
          │
          ▼
  2. Crea contenedor
     lxc launch ubuntu:24.04 nombre --profile perfil
          │
          ▼
  3. cloud-init ejecuta al primer boot
     (instala paquetes, configura servicios)
          │
          ▼
  4. Verifica estado
     cloud-init status → done
     ss -ntlp → puertos escuchando
          │
          ▼
  5. Opcional: crear imagen
     (para clonar este contenedor en el futuro)
```

---

## Documentos relacionados

| Tema | Documento |
|---|---|
| Descripción de cada componente | [03_Componentes.md](03_Componentes.md) |
| Procedimiento de instalación | [04_Instalacion.md](04_Instalacion.md) |
| Configuración de red y proxy | [05_Configuracion.md](05_Configuracion.md) |
| Decisión sobre OVN | [10_Decisiones.md](10_Decisiones.md) |
| Riesgos de red | [11_Riesgos.md](11_Riesgos.md) |
