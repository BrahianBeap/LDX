# 00 — Resumen Ejecutivo

> **Audiencia:** Ingenieros nuevos, líderes técnicos, stakeholders.
> **Propósito:** Orientación general. No reemplaza la documentación técnica detallada.

---

## ¿Qué es este proyecto?

Este proyecto implementa un **cluster LXD distribuido geográficamente** para virtualización de servidores mediante contenedores de sistema Linux.

**LXD** (Linux Containers, de Canonical) permite ejecutar sistemas operativos completos dentro de contenedores ligeros en lugar de máquinas virtuales pesadas. A diferencia de Docker (que virtualiza aplicaciones), LXD virtualiza el sistema operativo completo, incluyendo servicios, red y almacenamiento.

✅ El cluster gestiona contenedores a través de una API unificada, permitiendo que los contenedores sean visibles y migrables entre todos los nodos del cluster, independientemente del sitio geográfico donde residan.

---

## ¿Qué problema resuelve?

| Problema | Impacto | Solución |
|---|---|---|
| CentOS 7 llegó a End of Life (EOL) | Sin parches de seguridad, incumplimiento normativo | Migrar cargas de trabajo a contenedores Ubuntu LXD |
| InfraFileRoom (~800 GB) en CentOS 7 | Sistema productivo sin soporte activo | Migrar a contenedor LXD en cluster |
| Servidores físicos monolíticos | Un servidor = un servicio = un punto de falla | Un contenedor por servicio, múltiples nodos |
| Sin alta disponibilidad geográfica | Caída de un sitio = pérdida de todos los servicios del sitio | Cluster distribuido en 3 sitios independientes |

---

## Objetivos

1. ✅ Establecer un cluster LXD en al menos 3 sitios geográficos (Franco, Carpinelli, Fernando).
2. ✅ Implementar OVN como red transversal de contenedores entre sitios.
3. ✅ Adoptar arquitectura de microservicios: un servicio por contenedor.
4. ✅ Migrar cargas de trabajo existentes (CentOS 7) a contenedores Ubuntu.
5. 🟡 Implementar monitoreo con Prometheus y Grafana.
6. 🔴 Plazo exacto de producción: Pendiente de validación.

---

## Alcance de la primera reunión

| Tarea | Estado |
|---|---|
| Nodo PFR1 (Franco) instalado con LXD | ✅ Completado |
| MicroOVN bootstrapped en PFR1 | ✅ Completado |
| Web UI accesible en red local (PFR1) | ✅ Completado |
| Usuarios con acceso a la UI | ✅ Completado (Daniel, Rocío) |
| Proxy HTTP configurado para contenedores | ✅ Completado (temporal) |
| Cloud-init con instalación automática de paquetes | ✅ Demostrado |
| Nodo CAR1 (Carpinelli) instalado | ✅ Completado en la segunda reunión (ver abajo) |
| Nodo FDO1 (Fernando) instalado | 🔴 Pendiente |
| Red de contenedores dedicada habilitada por sitio | ✅ Completado en PFR1 y CAR1 |
| OVN funcional entre sitios | ✅ Completado entre PFR1 y CAR1 — ver [ADR-0006](adr/ADR-0006-wireguard-underlay-ovn-multisitio.md) |
| Servicios en producción | 🔴 Pendiente |

---

## Alcance de la segunda reunión (`reunion/segunda_reunion LXD _ Implementacion.vtt`)

| Tarea | Estado |
|---|---|
| Diagnóstico de la causa raíz del bloqueo de red entre sitios | ✅ Completado |
| WireGuard como transporte underlay para OVN entre sitios | ✅ Implementado y probado (PFR1↔CAR1) |
| CAR1 unido al cluster (segundo miembro, `database-standby`) | ✅ Completado |
| Contenedores gateway de servicios (patrón por sitio/proyecto) | ✅ Completado en PFR1 y CAR1 |
| Proyectos LXD para aislamiento multi-tenant | ✅ Adoptado como práctica estándar — ver [ADR-0007](adr/ADR-0007-proyectos-lxd-multitenancy.md) |
| Buenas prácticas operativas (`snap refresh --hold`, NTP, límites de journald, SSH deshabilitado) | ✅ Aplicadas |

Ver el detalle completo en [13_Linea_de_Tiempo.md](13_Linea_de_Tiempo.md).

---

## Estado actual del proyecto

🟡 El cluster está en **fase de implementación activa**, con 2 de 3 sitios iniciales instalados y unidos (PFR1 y CAR1). Falta FDO1 (Fernando) para completar el quórum de alta disponibilidad de la base de datos distribuida.

La red de contenedores (OVN) **es funcional entre PFR1 y CAR1**, corriendo sobre una malla WireGuard cifrada que sirve de transporte entre sitios geográficamente separados en Capa 3 (ver [ADR-0006](adr/ADR-0006-wireguard-underlay-ovn-multisitio.md)). El dispositivo de proxy reverso sobre la interfaz de gestión, usado como solución temporal en la primera reunión, sigue vigente únicamente en sitios donde OVN todavía no está disponible.

---

## Resultado esperado

Una vez completado el cluster, cualquier ingeniero podrá:

- Desplegar nuevos servicios en minutos usando cloud-init y perfiles.
- Migrar contenedores entre sitios sin tiempo de inactividad significativo.
- Monitorear el estado del cluster y sus contenedores desde Grafana.
- Recuperar servicios ante fallas de nodos individuales.

---

## Documentos relacionados

| Tema | Documento |
|---|---|
| Arquitectura completa | [02_Arquitectura.md](02_Arquitectura.md) |
| Instalación paso a paso | [04_Instalacion.md](04_Instalacion.md) |
| Decisiones técnicas | [10_Decisiones.md](10_Decisiones.md) |
| Riesgos identificados | [11_Riesgos.md](11_Riesgos.md) |
| Próximos pasos | [13_Linea_de_Tiempo.md](13_Linea_de_Tiempo.md) |
