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

---

## Decisión 1: OVN vs Ubuntu Fan

**Contexto:** El cluster necesita una red SDN que conecte contenedores entre nodos geográficamente distribuidos.

**Elección:** OVN (Open Virtual Network) via MicroOVN.

**Razón principal:** Ubuntu Fan requiere subred /24. La red de gestión de las VMs es /29 — incompatible.

**Estado actual:** 🔴 OVN instalado y bootstrapped, pero no funcional aún. Requiere interfaz de red VLAN 411 en las VMs.

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

## Decisiones pendientes / abiertas

| Decisión | Estado | Propietario |
|---|---|---|
| Configuración de VPN para acceso remoto | 🔴 No evaluada aún | Pendiente |
| Estrategia de monitoreo (configuración Prometheus externo) | 🔴 No evaluada aún | Pendiente |
| Procedimiento de live migration entre nodos | 🔴 No evaluada aún | Pendiente |
| Política de backup de contenedores (frecuencia, retención) | 🔴 No evaluada aún | Pendiente |

---

## Documentos relacionados

| Tema | Documento |
|---|---|
| Arquitectura completa | [02_Arquitectura.md](02_Arquitectura.md) |
| Riesgos de las decisiones | [11_Riesgos.md](11_Riesgos.md) |
| Directorio de ADRs | [adr/](adr/) |
