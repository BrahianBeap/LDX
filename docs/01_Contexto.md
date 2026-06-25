# 01 — Contexto del proyecto

> **Audiencia:** Ingenieros nuevos, arquitectos, stakeholders técnicos.
> **Propósito:** Explicar el origen, la necesidad y los beneficios buscados. Sin este contexto, las decisiones técnicas carecen de justificación.

---

## ¿Por qué existe este proyecto?

### El problema de EOL

✅ **CentOS 7 llegó a su End of Life.** Esto significa que Red Hat (y la comunidad) dejó de publicar parches de seguridad para este sistema operativo. Cualquier vulnerabilidad descubierta a partir de esa fecha queda sin corrección oficial.

El equipo opera servidores corriendo CentOS 7 con servicios productivos activos, lo que representa:

- **Riesgo de seguridad:** vulnerabilidades sin parche.
- **Riesgo de cumplimiento:** muchas normativas exigen sistemas con soporte activo.
- **Riesgo operativo:** sin actualizaciones de paquetes estables.

✅ El servicio más urgente a migrar es **InfraFileRoom**, con aproximadamente **800 GB de datos**, actualmente corriendo en CentOS 7.

---

### El modelo monolítico anterior

🟡 Antes de este proyecto, el modelo predominante era: un servidor físico (o VM) = un stack completo de servicios. Esto genera:

- **Alta dependencia:** si cae la VM, caen todos los servicios que aloja.
- **Dificultad para actualizar:** actualizar PHP requiere detener Apache y la base de datos.
- **Sin portabilidad:** mover un servicio implica reinstalarlo desde cero.
- **Sin escalabilidad horizontal:** agregar capacidad significa agregar VMs completas.

---

## ¿Qué necesidad cubre?

| Necesidad | Descripción |
|---|---|
| Migración fuera de EOL | Reemplazar CentOS 7 con Ubuntu LTS en contenedores LXD |
| Aislamiento de servicios | Un contenedor por servicio — fallas aisladas |
| Portabilidad | Mover contenedores entre nodos y sitios sin reinstalar |
| Alta disponibilidad geográfica | Cluster en 3 sitios: Franco, Carpinelli, Fernando |
| Despliegue repetible | cloud-init automatiza la configuración de cada contenedor |

---

## ¿Qué beneficios aporta?

### Agilidad operativa

✅ Con LXD y cloud-init, un nuevo contenedor con servicios preconfigurados puede estar listo en minutos, sin intervención manual paso a paso. Ver [04_Instalacion.md](04_Instalacion.md) y [05_Configuracion.md](05_Configuracion.md).

### Microservicios

✅ El equipo adoptó el principio explícito: **un servicio por contenedor**. Esto permite:

- Actualizar PHP sin tocar la base de datos.
- Escalar solo el servicio que lo necesita.
- Aislar fallas a un único contenedor.

### Alta disponibilidad

🟡 Con el cluster funcionando en 3 sitios geográficos independientes (Franco, Carpinelli, Fernando), la caída de un sitio completo no elimina la disponibilidad del sistema.

> **Advertencia:** La HA real requiere que la red OVN esté funcional entre sitios. Mientras OVN no esté operativo, los contenedores de distintos sitios no pueden comunicarse directamente. Ver [11_Riesgos.md](11_Riesgos.md).

### Backup liviano

✅ Un contenedor LXD puede exportarse como imagen localmente en minutos. Adicionalmente, las VMs que hospedan LXD tienen backup a nivel VMware (gestionado por SBA/AIT). Ver [06_Operacion.md](06_Operacion.md).

---

## ¿Qué riesgos intenta resolver?

| Riesgo original | Mitigación implementada |
|---|---|
| CentOS 7 EOL sin parches | Migración a Ubuntu 24.04 LTS en contenedores |
| Falla de servidor = falla de todos sus servicios | Contenedores aislados y cluster distribuido |
| Imposibilidad de mover cargas de trabajo | Migración de contenedores entre nodos del cluster |
| Crecimiento desordenado de VMs | Modelo estandarizado de perfiles y cloud-init |

---

## Restricciones del entorno

✅ La red de gestión de las VMs utiliza una subred **/29** (solo 6 IPs utilizables). Esta restricción es determinante en la elección de tecnología de red para los contenedores — ver [10_Decisiones.md](10_Decisiones.md) (decisión OVN vs Ubuntu Fan).

🔴 Las VMs son administradas por el equipo de VMware (SBA/AIT). Agregar interfaces de red, solicitar backups o cambios de infraestructura requiere coordinar con ese equipo (contacto: Cristian).

---

## Equipos involucrados

| Rol | Persona/Equipo | Responsabilidad |
|---|---|---|
| Instructor/consultor LXD | Norberto Núñez | Guía técnica, instalación inicial, transferencia de conocimiento |
| Coordinación del proyecto | Marcos Casco | Gestión de accesos, comunicación con equipos externos |
| Equipo técnico | Daniel Medina, Elías Alfonzo, Rocío Duarte | Operación, configuración, administración |
| Administrador VMware | Cristian | Gestión de VMs, interfaces de red, recursos de hypervisor |
| Seguridad / Accesos | Nicolás (Nico) | Proxy HTTP, permisos de red, antivirus |
| Administrador de edificio | Gustavo García | Acceso físico a infraestructura |

---

## Documentos relacionados

| Tema | Documento |
|---|---|
| Resumen del proyecto | [00_Resumen_Ejecutivo.md](00_Resumen_Ejecutivo.md) |
| Arquitectura técnica | [02_Arquitectura.md](02_Arquitectura.md) |
| Decisiones tomadas | [10_Decisiones.md](10_Decisiones.md) |
| Riesgos identificados | [11_Riesgos.md](11_Riesgos.md) |
