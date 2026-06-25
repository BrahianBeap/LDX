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
| Nodo CAR1 (Carpinelli) instalado | 🔴 Pendiente |
| Nodo FDO1 (Fernando) instalado | 🔴 Pendiente |
| VLAN 411 habilitada para red de contenedores | 🔴 Pendiente (requiere Cristian) |
| OVN funcional entre sitios | 🔴 Pendiente (depende de VLAN 411) |
| Servicios en producción | 🔴 Pendiente |

---

## Estado actual del proyecto

🟡 El cluster está en **fase de instalación inicial**. El primer nodo (PFR1) es funcional y sirve como referencia para replicar la instalación en los nodos restantes.

La red de contenedores (OVN) **aún no está operativa** por falta de la interfaz de red dedicada (VLAN 411) en las VMs. Como solución temporal, los servicios se exponen mediante un dispositivo de proxy reverso sobre la interfaz de gestión.

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
