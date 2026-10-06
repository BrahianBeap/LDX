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
| `rsyslog` instalado para reenvío de logs a Loki externo | ✅ Completado y directiva confirmada — ver [05_Configuracion.md](05_Configuracion.md) |
| Documentación técnica migrada a OneNote compartido con el equipo | ✅ Completado |
| Diagrama de arquitectura de networking (dibujo detallado) | 🔴 Pendiente — Norberto Núñez se comprometió a completarlo y convocar una nueva reunión |

> **✅ Verificación en servidor real (`pfr-oss` / PFR1, 2026-07-24):** se confirmó por inspección directa (`lxc cluster list`, `lxc list`, `lxc project list`, `lxc network list`) que `pfr.1` (database-leader) y `car.1` (database-standby) están ambos `ONLINE`; la red `OVN_1` existe y está `CREATED`, con dos contenedores de prueba (`C-PFR-1` 192.168.0.100, `C-CAR-1` 192.168.0.101) **en ejecución** y con conectividad cruzada confirmada entre sitios; el proyecto `PRJ-OSS` existe con sus perfiles y contenedores gateway. Esto eleva de 🟡 inferencia a ✅ hecho confirmado varios de los hitos de esta tabla que hasta ahora dependían solo del relato de la reunión.

---

### Tercera reunión — Arquitectura de exposición de servicios (gateway + balanceador)
**Fecha:** 2026-07-28
**Referencia:** [`reunion/LXD - Configuración FDO.vtt`](../reunion/LXD%20-%20Configuración%20FDO.vtt)

| Hito | Estado |
|---|---|
| Decisión: modelo de gateway + balanceador en dos etapas para exponer servicios (reemplaza la redirección directa a nivel de host) | ✅ Completado — ver [ADR-0008](adr/ADR-0008-gateway-balanceador-dos-etapas.md) |
| Primer contenedor balanceador creado (`PFR-LB`, Apache, IP fija `192.168.0.11`) | ✅ Completado (demostración) |
| Aclaración sobre responsabilidad de replicación de bases de datos (no la gestiona LXD) | ✅ Completado — ver [09_FAQ.md](09_FAQ.md) |
| Exploración de CockroachDB como alternativa a Postgres distribuido | 🟡 Solo exploratorio — sin decisión ni responsable asignado |
| Procedimiento de migración de contenedores entre proyectos LXD (workaround de proxy devices/snapshots) | ✅ Documentado — ver [06_Operacion.md](06_Operacion.md) y [ADR-0007](adr/ADR-0007-proyectos-lxd-multitenancy.md) |
| Diagnóstico de contenedor sin ruta por defecto (balanceador) | ✅ Resuelto en vivo — ver [TRB-011](07_Troubleshooting.md#trb-011) |

> **Nota:** la sintaxis exacta de la regla de firewalld para el reenvío de puertos del gateway hacia el balanceador no quedó completamente confirmada en el audio — ver el pendiente en [ADR-0008](adr/ADR-0008-gateway-balanceador-dos-etapas.md).

---

### Cuarta ronda — Incorporación de Fernando (FDO1) y observabilidad de aplicación (agosto)
**Fecha:** 🔴 Pendiente de validación (archivos VTT sin fecha exacta en el nombre; procesados 2026-08-20). Orden reconstruido por contenido: puente proxy → join WireGuard/LXD/OVN → demostración OSS.
**Referencias:** [`reunion/Llamada con Daniel y 3 personas más_agosto_v1.vtt`](../reunion/Llamada%20con%20Daniel%20y%203%20personas%20más_agosto_v1.vtt), [`_agosto_v2.vtt`](../reunion/Llamada%20con%20Daniel%20y%203%20personas%20más_agosto_v2.vtt), [`Reunión en OSS_agosto_v3.vtt`](../reunion/Reunión%20en%20OSS_agosto_v3.vtt)

| Hito | Estado |
|---|---|
| Puente NAT temporal hacia el proxy SDI para Fernando (mientras se tramita su alta propia) | ✅ Completado — ver [05_Configuracion.md](05_Configuracion.md#puente-nat-temporal-hacia-el-proxy-sdi-para-sitios-sin-autorización-propia) |
| Instalación de LXD/MicroOVN en Fernando (`fdo-oss1`) | ✅ Completado |
| Malla WireGuard extendida a los 3 sitios (Franco, Carpinelli, Fernando) | ✅ Completado — con error de configuración encontrado y corregido en el proceso, ver [TRB-013](07_Troubleshooting.md#trb-013--peer-de-wireguard-mal-configurado-claves-invertidas-o-allowed-ips-demasiado-amplio-bloquea-rutas-entre-sitios) |
| Fernando unido al cluster LXD (tercer miembro) | ✅ Completado |
| Fernando unido al cluster OVN | 🔴 Bloqueado — interfaz OVN no levanta, ver [RIE-013](11_Riesgos.md#rie-013--interfaz-ovn-bloqueada-en-fernando-causa-raíz-no-identificada-activo) |
| Hardening de `core.https_address` (IP de gestión específica, no `0.0.0.0`) en los 3 nodos | ✅ Completado — ver [05_Configuracion.md](05_Configuracion.md#dirección-de-escucha-de-la-api-de-lxd-corehttps_address) |
| Servicio NTF (mensajería SMS/email) desplegado en Fernando y Franco, con balanceador embebido en el gateway | ✅ Completado — ver [ADR-0008 — Variante confirmada](adr/ADR-0008-gateway-balanceador-dos-etapas.md#variante-confirmada-balanceador-embebido-en-el-gateway) |
| Bug de migración entre sitios por WireGuard mal configurado (claves invertidas, `allowed-ips` amplio) | 🟡 Corregido en Fernando, pendiente aplicar en Franco |
| Esquema de inventario de servicios acordado con el equipo | ✅ Completado — ver [06_Operacion.md](06_Operacion.md#inventario-de-servicios-alta-de-un-servicio-nuevo) |
| Loki + MinIO propio del proyecto para logs de aplicación | 🟡 Planificado, no desplegado — ver [14_Manual_Operativo.md](14_Manual_Operativo.md#logs-de-aplicación-loki--minio-propio-del-proyecto) |

---

## Hitos pendientes (próximos pasos)

### Corto plazo — Tercer miembro del cluster (Fernando / FDO1)

> Referencia: [04_Instalacion.md](04_Instalacion.md) y bitácora real de ejecución en [`laboratorio/2026-07-25_incorporacion-sitio-fdo1/bitacora.md`](../laboratorio/2026-07-25_incorporacion-sitio-fdo1/bitacora.md).

| Acción | Nodo | Estado |
|---|---|---|
| Solicitar/confirmar interfaz de red dedicada a servicio en FDO1 | FDO1 | ✅ Completado |
| Configurar malla WireGuard entre FDO1 y los sitios existentes | FDO1 | ✅ Completado (con corrección de configuración en el camino, ver [TRB-013](07_Troubleshooting.md#trb-013--peer-de-wireguard-mal-configurado-claves-invertidas-o-allowed-ips-demasiado-amplio-bloquea-rutas-entre-sitios)) |
| Instalar LXD y MicroOVN en Fernando | FDO1 | ✅ Completado |
| Unir FDO1 al cluster LXD (join token) | FDO1 | ✅ Completado |
| Unir FDO1 al cluster OVN — completaría el quórum de HA de la base de datos | FDO1 | 🔴 Bloqueado — ver [RIE-013](11_Riesgos.md#rie-013--interfaz-ovn-bloqueada-en-fernando-causa-raíz-no-identificada-activo) |
| Aplicar en Franco la misma corrección de WireGuard ya aplicada en Fernando | Franco | 🔴 Pendiente |
| Crear contenedor gateway de servicios en FDO1 | FDO1 | 🔴 Pendiente — depende de resolver el join a OVN |

---

### Corto plazo — Consolidación de lo implementado

| Acción | Responsable | Estado |
|---|---|---|
| Persistir configuración de IP de WireGuard en `netplan` (PFR1 y CAR1) | Norberto Núñez | ✅ Completado — ver [RIE-001b en 11_Riesgos.md](11_Riesgos.md) |
| Completar y compartir diagrama de arquitectura de networking | Norberto Núñez | 🔴 Pendiente |
| Gestionar alta de servicio del puerto 8444 (gestión LXD) para CAR1 | Marcos Casco | 🔴 Pendiente — ver [RIE-009 en 11_Riesgos.md](11_Riesgos.md) |
| Enviar diagrama de red a Roberto de Paula / equipo SVA para apoyo de diseño | Marcos Casco | 🔴 Pendiente |
| Definir política estándar de límites de recursos por proyecto LXD | Equipo técnico | 🔴 Pendiente — ver [ADR-0007](adr/ADR-0007-proyectos-lxd-multitenancy.md) |
| Continuar la sesión de arquitectura de exposición de servicios (esbozar versión práctica) | Norberto Núñez | 🔴 Pendiente — acordado para el día siguiente de la reunión, ver [ADR-0008](adr/ADR-0008-gateway-balanceador-dos-etapas.md) |
| Completar el inventario de IP + puerto + servicio para cada servicio nuevo expuesto (esquema ya acordado, ver [06_Operacion.md](06_Operacion.md#inventario-de-servicios-alta-de-un-servicio-nuevo)) | Elías Alfonzo / equipo | 🔴 Pendiente — carga de datos en curso |
| Retirar la redirección directa a nivel de host (esquema inicial de Kanboard) una vez migrado al modelo gateway + balanceador | Elías Alfonzo | 🔴 Pendiente — ver [ADR-0008](adr/ADR-0008-gateway-balanceador-dos-etapas.md) |
| Investigar opciones de base de datos con alta disponibilidad/replicación nativa (incluye CockroachDB) | Sin asignar | 🟡 Solo sugerido, sin dueño ni fecha |

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
| Decisión sobre gateway + balanceador | [ADR-0008](adr/ADR-0008-gateway-balanceador-dos-etapas.md) |
