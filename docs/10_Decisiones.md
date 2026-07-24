# 10 — Decisiones de arquitectura

> **Audiencia:** Arquitectos, ingenieros senior, futuros mantenedores del sistema.
> **Propósito:** Resumen ejecutivo de las decisiones técnicas más importantes y sus justificaciones. Cada decisión tiene un ADR completo en [`docs/adr/`](adr/).

---

## Resumen de decisiones

| # | Decisión | Elegido | Descartado | ADR |
|---|---|---|---|---|
| 1 | Red SDN para contenedores | OVN via MicroOVN | Ubuntu Fan | [ADR-0002](adr/ADR-0002-red-ovn-vs-ubuntu-fan.md) |
| 2 | Driver de storage | ZFS | LVM, btrfs | [ADR-0003](adr/ADR-0003-storage-zfs.md) |
| 3 | Autenticación Web UI | TLS tokens + certificados | 🔴 Pendiente de validación otras alternativas | [ADR-0004](adr/ADR-0004-autenticacion-tls-tokens.md) |
| 4 | Arquitectura de servicios | Un servicio por contenedor | Stack completo por contenedor | [ADR-0005](adr/ADR-0005-arquitectura-microservicios.md) |
| 5 | Transporte inter-sitio para OVN | WireGuard como underlay cifrado | Túnel nativo de OVN sobre backbone, VXLAN | [ADR-0006](adr/ADR-0006-wireguard-underlay-ovn-multisitio.md) |
| 6 | Aislamiento multi-tenant | Proyectos LXD con límites y grupos | Proyecto `default` único para todos | [ADR-0007](adr/ADR-0007-proyectos-lxd-multitenancy.md) |

---

## Decisión 1: OVN vs Ubuntu Fan

**Contexto:** El cluster necesita una red SDN que conecte contenedores entre nodos geográficamente distribuidos.

**Elección:** OVN (Open Virtual Network) via MicroOVN.

**Razón principal:** Ubuntu Fan requiere subred /24. La red de gestión de las VMs es /29 — incompatible.

**Estado actual:** ✅ OVN funcional entre Franco (PFR1) y Carpinelli (CAR1), corriendo sobre una malla WireGuard (ver Decisión 5). Pendiente extender a Fernando (FDO1).

Ver detalles completos: [ADR-0002](adr/ADR-0002-red-ovn-vs-ubuntu-fan.md)

---

## Decisión 2: ZFS como storage driver

**Contexto:** LXD necesita un driver de almacenamiento para los datos de los contenedores.

**Elección:** ZFS sobre disco dedicado `/dev/sda6` (315 GB en PFR1).

**Razón principal:** ZFS provee snapshots integrados, checksums de integridad de datos y mejor integración con las operaciones de LXD comparado con LVM o btrfs.

Ver detalles completos: [ADR-0003](adr/ADR-0003-storage-zfs.md)

---

## Decisión 3: Autenticación mediante TLS tokens + certificados de navegador

**Contexto:** Los operadores necesitan un mecanismo de autenticación para la Web UI de LXD.

**Elección:** Certificados TLS por usuario + token inicial para el primer acceso.

**Razón principal:** Es el mecanismo nativo de LXD. Cada usuario tiene su propio certificado, facilitando la revocación individual de acceso.

Ver detalles completos: [ADR-0004](adr/ADR-0004-autenticacion-tls-tokens.md)

---

## Decisión 4: Un servicio por contenedor (microservicios)

**Contexto:** Los servicios actuales corren en VMs monolíticas (Apache + PHP + base de datos en la misma VM).

**Elección:** Un contenedor por servicio: contenedor web (Apache/PHP), contenedor de base de datos (separado).

**Razón principal:** Permite actualizar, escalar y recuperar cada servicio de forma independiente. Si se cambia la versión de PHP, la base de datos no se toca.

Ver detalles completos: [ADR-0005](adr/ADR-0005-arquitectura-microservicios.md)

---

## Decisión 5: WireGuard como transporte underlay para OVN entre sitios

**Contexto:** El túnel de datos nativo de OVN, viajando directamente sobre la red corporativa, es bloqueado entre sitios en Capa 3 separada (confirmado en dos implementaciones independientes, con un año de diferencia).

**Elección:** WireGuard como capa de transporte underlay cifrada; el túnel de OVN corre encima de la malla WireGuard.

**Razón principal:** Es la única alternativa probada que atraviesa la red corporativa sin ser bloqueada, y de paso agrega cifrado en tránsito que el túnel nativo de OVN no provee.

**Estado actual:** ✅ Probado y funcional entre PFR1 y CAR1. 🔴 Configuración de IP de la interfaz WireGuard aún no persistida en `netplan` (se pierde al reiniciar el host).

Ver detalles completos: [ADR-0006](adr/ADR-0006-wireguard-underlay-ovn-multisitio.md)

---

## Decisión 6: Proyectos LXD para aislamiento multi-tenant

**Contexto:** El cluster es una plataforma compartida entre distintos equipos/áreas. Sin segmentación, cualquier usuario ve y puede modificar los recursos de todos los demás, sin límites de consumo.

**Elección:** Un proyecto LXD por equipo/área, con límites explícitos de recursos (redes, CPU, memoria, instancias) y un grupo de identidad restringido a ese proyecto.

**Razón principal:** Es la funcionalidad nativa de LXD diseñada para este propósito — resuelve aislamiento de visibilidad/acceso y control de consumo de recursos sin herramientas externas.

Ver detalles completos: [ADR-0007](adr/ADR-0007-proyectos-lxd-multitenancy.md)

---

## Decisiones pendientes / abiertas

| Decisión | Estado | Propietario |
|---|---|---|
| Configuración de VPN para acceso remoto | 🔴 No evaluada aún | Pendiente |
| Estrategia de monitoreo (configuración Prometheus externo) | 🔴 No evaluada aún | Pendiente |
| Procedimiento de live migration entre nodos | 🔴 No evaluada aún | Pendiente |
| Política de backup de contenedores (frecuencia, retención) | 🔴 No evaluada aún | Pendiente |
| Automatización de la malla WireGuard al escalar a más sitios | 🔴 No evaluada aún | Pendiente |
| Política estándar de límites de recursos por proyecto LXD | 🔴 No evaluada aún | Pendiente |

---

## Documentos relacionados

| Tema | Documento |
|---|---|
| Arquitectura completa | [02_Arquitectura.md](02_Arquitectura.md) |
| Riesgos de las decisiones | [11_Riesgos.md](11_Riesgos.md) |
| Directorio de ADRs | [adr/](adr/) |
