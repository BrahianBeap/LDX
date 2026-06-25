# 13 — Línea de tiempo del proyecto

> **Audiencia:** Todo el equipo.
> **Propósito:** Cronología de hitos del proyecto. No es una transcripción de reuniones — es una reconstrucción de los hechos técnicos relevantes en orden temporal.

---

## Hitos completados

### Reunión inicial de instalación
**Fecha:** 🔴 Pendiente de validación (archivo VTT sin fecha en el nombre)
**Referencia:** [`reunion/Llamada con Daniel y 3 personas más.vtt`](../reunion/Llamada%20con%20Daniel%20y%203%20personas%20más.vtt)

| Hito | Estado |
|---|---|
| Instalación de LXD 5.21 en PFR1 (Franco) | ✅ Completado |
| Configuración de storage pool ZFS en /dev/sda6 (315 GB) | ✅ Completado |
| LXD clustering inicializado (PFR1 como primer miembro) | ✅ Completado |
| Instalación de MicroOVN en PFR1 | ✅ Completado |
| Bootstrap del cluster OVN en PFR1 | ✅ Completado |
| Configuración de proxy HTTP en LXD | ✅ Completado |
| Reglas de firewall para acceso de operadores | ✅ Completado |
| Acceso a Web UI verificado por Daniel y Rocío | ✅ Completado |
| Primer contenedor Ubuntu 24.04 creado | ✅ Completado |
| Perfil con cloud-init funcional (apache2 + PHP) | ✅ Completado |
| Primera imagen personalizada creada desde contenedor | ✅ Completado |
| Repositorio LDX inicializado como base de conocimiento | ✅ Completado (2026-06-25) |

---

## Hitos pendientes (próximos pasos)

### Corto plazo — Prerequisito: VLAN 411

> Responsable coordinación: Marcos Casco → Cristian (administrador VMware)

| Acción | Responsable | Estado |
|---|---|---|
| Solicitar interfaz de red VLAN 411 en PFR1 | Marcos Casco → Cristian | 🔴 Pendiente |
| Solicitar interfaz de red VLAN 411 en CAR1 | Marcos Casco → Cristian | 🔴 Pendiente |
| Solicitar interfaz de red VLAN 411 en FDO1 | Marcos Casco → Cristian | 🔴 Pendiente |

---

### Corto plazo — Instalación de nodos adicionales

> Referencia: [04_Instalacion.md](04_Instalacion.md) — seguir el mismo procedimiento que PFR1.

| Acción | Nodo | Estado |
|---|---|---|
| Instalar LXD y MicroOVN en Carpinelli | CAR1 | 🔴 Pendiente |
| Unir CAR1 al cluster (join token desde PFR1) | CAR1 | 🔴 Pendiente |
| Instalar LXD y MicroOVN en Fernando | FDO1 | 🔴 Pendiente |
| Unir FDO1 al cluster (join token desde PFR1) | FDO1 | 🔴 Pendiente |

---

### Mediano plazo — OVN funcional

> Requiere VLAN 411 en todos los nodos.

| Acción | Estado |
|---|---|
| Configurar OVN con interfaz VLAN 411 en PFR1 | 🔴 Pendiente |
| Extender OVN a CAR1 y FDO1 | 🔴 Pendiente |
| Verificar conectividad cross-site entre contenedores | 🔴 Pendiente |
| Eliminar dispositivos proxy temporales de los contenedores | 🔴 Pendiente |

---

### Mediano plazo — Infraestructura física

> Trabajo de herrería/cableado en azotea.

| Acción | Ventana | Contacto | Estado |
|---|---|---|---|
| Instalación física en azotea | Lunes-martes, 08:00–18:00 | Ramiro (director), José Enciso (CDE) | 🔴 Pendiente |

---

### Mediano plazo — Migración de servicios

| Acción | Prioridad | Estado |
|---|---|---|
| Migrar InfraFileRoom (~800 GB) de CentOS 7 a LXD | Alta | 🔴 Pendiente |
| Definir plan de migración de otros servicios CentOS 7 | Media | 🔴 Pendiente |

---

### Largo plazo

| Acción | Estado |
|---|---|
| Configurar VPN para acceso remoto a la Web UI | 🔴 Pendiente |
| Documentar todos los servicios migrados | 🔴 Pendiente |
| Establecer procedimientos de DR (Disaster Recovery) | 🔴 Pendiente |

---

## Dependencias entre hitos

```
Instalar CAR1 y FDO1 ──► Unir al cluster
(independiente de VLAN 411)

VLAN 411 habilitada
       │
       └──► Configurar OVN ──► Red cross-site funcional
                                       │
                                       ├──► Eliminar proxies temporales
                                       └──► Despliegue en producción
```

> **Nota:** La instalación de nodos (CAR1, FDO1) y la habilitación de VLAN 411 son acciones **paralelas e independientes**. No es necesario esperar a VLAN 411 para instalar los nodos. Ambas deben completarse antes de configurar OVN.

---

## Documentos relacionados

| Tema | Documento |
|---|---|
| Estado actual del cluster | [00_Resumen_Ejecutivo.md](00_Resumen_Ejecutivo.md) |
| Procedimiento de instalación para nuevos nodos | [04_Instalacion.md](04_Instalacion.md) |
| Riesgos mientras OVN no esté activo | [11_Riesgos.md](11_Riesgos.md) |
| Decisión sobre OVN vs alternativas | [10_Decisiones.md](10_Decisiones.md) |
