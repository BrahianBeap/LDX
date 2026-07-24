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

### Segunda reunión — Implementación (WireGuard, CAR1, proyectos)
**Fecha:** 2026-07-24 (fecha de procesamiento de la reunión; fecha real de la reunión 🔴 pendiente de validación — el archivo VTT no trae fecha en el nombre)
**Referencia:** [`reunion/segunda_reunion LXD _ Implementacion.vtt`](../reunion/segunda_reunion%20LXD%20_%20Implementacion.vtt)

| Hito | Estado |
|---|---|
| Diagnóstico de causa raíz del bloqueo de red OVN entre sitios en Capa 3 | ✅ Completado |
| Decisión: WireGuard como transporte underlay para OVN entre sitios | ✅ Completado — ver [ADR-0006](adr/ADR-0006-wireguard-underlay-ovn-multisitio.md) |
| Malla WireGuard configurada y probada entre PFR1 y CAR1 | ✅ Completado |
| Red OVN funcional entre PFR1 y CAR1 (sobre WireGuard) | ✅ Completado |
| Instalación de LXD y MicroOVN en Carpinelli (CAR1) | ✅ Completado |
| CAR1 unido al cluster LXD (segundo miembro, `database-standby`) | ✅ Completado |
| Renombrado de interfaces de red por MAC (`netplan`) para consistencia entre nodos | ✅ Completado en PFR1 y CAR1 |
| Contenedores gateway de servicios creados (perfil, IPVLAN) en PFR1 y CAR1 | ✅ Creados (`PFR-OSS-GW-SRV`, `CAR-OSS-GW-SRV`) — 🔴 aún **detenidos**, pendientes de activación para producción (verificado en servidor real, ver nota abajo) |
| Contenedor gateway de operación y mantenimiento (salida a proxy) en PFR1 y CAR1 | ✅ Creados (`PFR-GW-OAM`, `CAR-GW-OAM`, proyecto `default`) — 🔴 aún **detenidos**, pendientes de activación |
| Decisión y adopción de proyectos LXD para multi-tenancy | ✅ Completado — ver [ADR-0007](adr/ADR-0007-proyectos-lxd-multitenancy.md) |
| Primer proyecto LXD con límites de recursos creado (ejemplo/demostración) | ✅ Completado |
| `snap refresh --hold` aplicado en PFR1 y CAR1 | ✅ Completado |
| NTP (`systemd-timesyncd`) configurado en hosts y contenedores gateway | ✅ Completado |
| `rsyslog` instalado para reenvío de logs a Loki externo | 🟡 Instalado; directiva de reenvío no confirmada — Pendiente de validación |
| Documentación técnica migrada a OneNote compartido con el equipo | ✅ Completado |
| Diagrama de arquitectura de networking (dibujo detallado) | 🔴 Pendiente — Norberto Núñez se comprometió a completarlo y convocar una nueva reunión |

> **✅ Verificación en servidor real (`pfr-oss` / PFR1, 2026-07-24):** se confirmó por inspección directa (`lxc cluster list`, `lxc list`, `lxc project list`, `lxc network list`) que `pfr.1` (database-leader) y `car.1` (database-standby) están ambos `ONLINE`; la red `OVN_1` existe y está `CREATED`, con dos contenedores de prueba (`C-PFR-1` 192.168.0.100, `C-CAR-1` 192.168.0.101) **en ejecución** y con conectividad cruzada confirmada entre sitios; el proyecto `PRJ-OSS` existe con sus perfiles y contenedores gateway. Esto eleva de 🟡 inferencia a ✅ hecho confirmado varios de los hitos de esta tabla que hasta ahora dependían solo del relato de la reunión.

---

## Hitos pendientes (próximos pasos)

### Corto plazo — Tercer miembro del cluster (Fernando / FDO1)

> Referencia: [04_Instalacion.md](04_Instalacion.md) — seguir el mismo procedimiento que PFR1/CAR1, incluyendo la configuración de WireGuard hacia los sitios existentes.

| Acción | Nodo | Estado |
|---|---|---|
| Solicitar/confirmar interfaz de red dedicada a servicio en FDO1 | FDO1 | 🔴 Pendiente |
| Configurar malla WireGuard entre FDO1 y los sitios existentes | FDO1 | 🔴 Pendiente |
| Instalar LXD y MicroOVN en Fernando | FDO1 | 🔴 Pendiente |
| Unir FDO1 al cluster (join token) — completaría el quórum de HA de la base de datos | FDO1 | 🔴 Pendiente |
| Crear contenedor gateway de servicios en FDO1 (interfaz de servicio `FDO-SS-gateway-servicio`) | FDO1 | 🔴 Pendiente |

---

### Corto plazo — Consolidación de lo implementado

| Acción | Responsable | Estado |
|---|---|---|
| Persistir configuración de IP de WireGuard en `netplan` (PFR1 y CAR1) | Norberto Núñez | 🔴 Pendiente — ver [RIE-001b en 11_Riesgos.md](11_Riesgos.md) |
| Completar y compartir diagrama de arquitectura de networking | Norberto Núñez | 🔴 Pendiente |
| Gestionar alta de servicio del puerto 8444 (gestión LXD) para CAR1 | Marcos Casco | 🔴 Pendiente — ver [RIE-009 en 11_Riesgos.md](11_Riesgos.md) |
| Confirmar directiva de reenvío de logs `rsyslog` → Loki | Equipo técnico | 🔴 Pendiente |
| Enviar diagrama de red a Roberto de Paula / equipo SVA para apoyo de diseño | Marcos Casco | 🔴 Pendiente |
| Definir política estándar de límites de recursos por proyecto LXD | Equipo técnico | 🔴 Pendiente — ver [ADR-0007](adr/ADR-0007-proyectos-lxd-multitenancy.md) |

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
| Onboarding de equipos adicionales (CCR, OMC, AIT/transporte) usando proyectos LXD dedicados | Media | 🔴 Pendiente — ver [ADR-0007](adr/ADR-0007-proyectos-lxd-multitenancy.md) |

---

### Largo plazo

| Acción | Estado |
|---|---|
| Solicitar nuevo servidor para un sitio adicional (a través de Roberto de Paula) | 🔴 Pendiente |
| Evaluar sitios adicionales fuera de los 3 iniciales (candidatos mencionados: IT, Ciudad del Este) | 🟡 Planificación abierta, sin compromiso de fecha |
| Automatizar la configuración de la malla WireGuard antes de escalar a más sitios | 🔴 Pendiente — ver [RIE-001c en 11_Riesgos.md](11_Riesgos.md) |
| Configurar VPN para acceso remoto a la Web UI | 🔴 Pendiente |
| Documentar todos los servicios migrados | 🔴 Pendiente |
| Establecer procedimientos de DR (Disaster Recovery) | 🔴 Pendiente |

---

## Dependencias entre hitos

```
FDO1: interfaz de servicio dedicada ──► Malla WireGuard PFR1↔CAR1↔FDO1 ──► microovn cluster join
                                                                                    │
                                                                                    ▼
                                                              Tercer miembro del cluster
                                                              (quórum de HA de base de datos)
                                                                                    │
                                                                                    ▼
                                                    Contenedor gateway de servicios en FDO1

Persistir config. WireGuard en netplan (PFR1, CAR1) ──► Enlace inter-sitio resiliente a reinicios

Proyecto LXD con límites definidos ──► Onboarding de equipos adicionales (CCR, OMC, AIT)
```

> **Nota:** A diferencia de la primera reunión (donde se asumía que la red OVN dependía de habilitar una VLAN 411 compartida entre sitios), el modelo actual desacopla la conectividad inter-sitio (resuelta con WireGuard) de la VLAN local de cada sitio. Ver [ADR-0006](adr/ADR-0006-wireguard-underlay-ovn-multisitio.md).

---

## Documentos relacionados

| Tema | Documento |
|---|---|
| Estado actual del cluster | [00_Resumen_Ejecutivo.md](00_Resumen_Ejecutivo.md) |
| Procedimiento de instalación para nuevos nodos | [04_Instalacion.md](04_Instalacion.md) |
| Riesgos actuales | [11_Riesgos.md](11_Riesgos.md) |
| Decisión sobre OVN vs alternativas | [10_Decisiones.md](10_Decisiones.md) |
| Decisión sobre WireGuard como underlay | [ADR-0006](adr/ADR-0006-wireguard-underlay-ovn-multisitio.md) |
| Decisión sobre proyectos LXD | [ADR-0007](adr/ADR-0007-proyectos-lxd-multitenancy.md) |
