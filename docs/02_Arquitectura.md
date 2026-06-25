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
         │   │  └──────┘  │   │  └──────┘  │   │  └──────┘  │   │
         │   └───────────┘   └───────────┘   └───────────┘   │
         │         │                │                │         │
         │         └────────────────┴────────────────┘         │
         │                   Red OVN (VLAN 411)                │
         │              (pendiente de habilitación)            │
         └─────────────────────────────────────────────────────┘
```

> **Nota:** CAR1 y FDO1 están pendientes de instalación. La red OVN está pendiente de la habilitación de VLAN 411.

---

## Sitios y nodos

| Sitio | Nombre largo | Prefijo nodos | Estado |
|---|---|---|---|
| PFR | Franco | PFR1, PFR2, ... | ✅ PFR1 instalado |
| CAR | Carpinelli | CAR1, CAR2, ... | 🔴 Pendiente |
| FDO | Fernando | FDO1, FDO2, ... | 🔴 Pendiente |

✅ Convención de nombres: `SITIO` + número secuencial (PFR1, CAR1, FDO1).

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
  │  │  │  eth0   │  │  eth1  │  │  │
  │  │  │ Gestión │  │ VLAN   │  │  │
  │  │  │  /29    │  │  411   │  │  │
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
- ✅ Cada VM tiene al menos una interfaz de red de gestión (/29).
- 🔴 La segunda interfaz (VLAN 411) para tráfico de contenedores está **pendiente de habilitación** en todas las VMs.

---

## Redes del sistema

### Red de gestión (existente)

| Campo | Valor |
|---|---|
| Tipo | Subred IPv4 |
| Tamaño | /29 (6 IPs utilizables) |
| Uso | Acceso SSH a VMs, Web UI de LXD (puertos 8443/8444), proxy HTTP |
| Estado | ✅ Operativa |

### Red de contenedores — OVN (pendiente)

| Campo | Valor |
|---|---|
| Tecnología | OVN (Open Virtual Network) via MicroOVN |
| VLAN | 411 |
| Uso | Comunicación entre contenedores, incluso entre sitios distintos |
| Estado | 🔴 Pendiente de VLAN 411 en VMs |

> **Importante:** Mientras la red OVN no esté activa, los contenedores de distintos nodos del cluster **no pueden comunicarse directamente**. Ver [11_Riesgos.md](11_Riesgos.md) y [10_Decisiones.md](10_Decisiones.md).

### Solución temporal de red (dispositivo proxy)

Mientras OVN no está disponible, los contenedores acceden a internet y exponen servicios mediante **dispositivos proxy LXD** configurados sobre la interfaz de gestión. Ver [05_Configuracion.md](05_Configuracion.md).

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

- ✅ ZFS es local a cada nodo. Cada nodo tiene su propio pool.
- 🟡 Los contenedores de un nodo usan el pool ZFS de ese nodo.
- ✅ La migración de contenedores entre nodos transfiere los datos del pool origen al pool destino.

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
  │  │  │ Pool ZFS  │  │  OVN /   │  │  res    │  │  │
  │  │  │ /dev/sda6 │  │ (futuro) │  │         │  │  │
  │  │  └───────────┘  └──────────┘  └─────────┘  │  │
  │  └─────────────────────────────────────────────┘  │
  │                                                   │
  │  ┌──────────────┐  ┌────────────┐                 │
  │  │  MicroOVN    │  │  firewalld │                 │
  │  │  (snap)      │  │            │                 │
  │  └──────────────┘  └────────────┘                 │
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
