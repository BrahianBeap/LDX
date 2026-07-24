# 11 — Riesgos identificados

> **Audiencia:** Ingenieros de infraestructura, SRE, gestores técnicos.
> **Propósito:** Catálogo de riesgos técnicos, operativos y de seguridad identificados durante la instalación inicial.

---

## RIE-001 — Red OVN no funcional entre sitios *(✅ Resuelto para PFR1↔CAR1, parcialmente vigente para FDO1)*

| Campo | Detalle |
|---|---|
| **Descripción** | La red OVN que conecta contenedores entre sitios geográficos no estaba operativa |
| **Causa raíz** | El túnel de datos nativo de OVN, viajando directamente sobre la red corporativa, es bloqueado por un elemento de red intermedio entre sitios en Capa 3 separada (confirmado en dos implementaciones independientes, con un año de diferencia) — **no** era, como se asumió originalmente, la falta de una interfaz VLAN 411 |
| **Impacto** | Los contenedores de distintos nodos del cluster no podían comunicarse entre sí |
| **Severidad** | Alta (mientras estuvo sin resolver) — bloqueaba la propuesta de valor principal del cluster |
| **Solución aplicada** | WireGuard como capa de transporte underlay cifrada entre sitios, con el túnel de OVN corriendo por encima. Ver [ADR-0006](adr/ADR-0006-wireguard-underlay-ovn-multisitio.md) |
| **Estado actual** | ✅ Resuelto y verificado entre PFR1 y CAR1 — confirmado de forma independiente por inspección directa del servidor real el 2026-07-24 (`lxc network list` muestra `OVN_1` `CREATED`, con contenedores de prueba `C-PFR-1`/`C-CAR-1` en ejecución en ambos sitios). 🔴 Pendiente repetir el procedimiento para FDO1 cuando se incorpore al cluster |
| **Responsable** | Norberto Núñez |

---

## RIE-001b — Configuración de WireGuard no persistida (riesgo de pérdida del enlace inter-sitio)

| Campo | Detalle |
|---|---|
| **Descripción** | La dirección IP de la interfaz WireGuard en PFR1 y CAR1 fue configurada manualmente durante la sesión, sin persistirla en `netplan` |
| **Causa** | Falta de tiempo para completar la configuración persistente durante la demostración |
| **Impacto** | Si el host se reinicia, la interfaz WireGuard pierde su IP y el enlace entre sitios (y por lo tanto la red OVN entre ellos) queda caído hasta que se reconfigure manualmente |
| **Severidad** | Alta — un reinicio de rutina (ej. mantenimiento, actualización del sistema operativo) puede interrumpir la conectividad entre sitios sin aviso |
| **Mitigación actual** | Ninguna — pendiente de aplicar |
| **Acción requerida** | Persistir la configuración de IP, claves y rutas de WireGuard en `netplan` en PFR1 y CAR1. Ver [04_Instalacion.md](04_Instalacion.md) |
| **Responsable** | Norberto Núñez |

---

## RIE-001c — Configuración manual de la malla WireGuard no escala automáticamente

| Campo | Detalle |
|---|---|
| **Descripción** | WireGuard no tiene plano de control ni base de datos distribuida — cada nuevo sitio que se agregue al cluster requiere generar claves nuevas y modificar manualmente la configuración de **todos** los nodos existentes |
| **Causa** | Es una limitación de diseño de WireGuard (por eso se eligió: simplicidad), aceptada como compromiso al tomar la decisión — ver [ADR-0006](adr/ADR-0006-wireguard-underlay-ovn-multisitio.md) |
| **Impacto** | A medida que se sumen más sitios (FDO1, y potencialmente IT y Ciudad del Este), el esfuerzo de configuración manual crece de forma cuadrática y aumenta la probabilidad de errores de configuración (claves, rutas) |
| **Severidad** | Media — manejable con pocos sitios, se vuelve relevante a partir de 4-5 sitios |
| **Mitigación actual** | Ninguna — proceso manual documentado en [04_Instalacion.md](04_Instalacion.md) |
| **Acción requerida** | Evaluar automatización (script o herramienta de gestión de configuración) antes de escalar a más de 3-4 sitios |
| **Responsable** | Norberto Núñez |

---

## RIE-002 — Dos de tres nodos activos (alta disponibilidad de base de datos incompleta)

| Campo | Detalle |
|---|---|
| **Descripción** | PFR1 y CAR1 están instalados y forman parte del cluster (roles `database-leader` y `database-standby`). Falta un tercer miembro para completar el quórum de alta disponibilidad de la base de datos distribuida (Dqlite) |
| **Causa** | FDO1 (Fernando) está pendiente de instalación |
| **Impacto** | Si PFR1 o CAR1 fallan, el cluster puede seguir operando con el nodo restante pero **sin margen de tolerancia a una segunda falla**. El quórum de escritura pleno recién se alcanza con 3 miembros |
| **Severidad** | Media-Alta — mejoró respecto del estado de un solo nodo, pero la HA real sigue incompleta |
| **Mitigación actual** | Backup de VM en VMware (solicitar a SBA/AIT); gestión posible desde cualquiera de los dos nodos activos gracias a la base de datos replicada |
| **Acción requerida** | Instalar LXD en FDO1 y agregarlo al cluster. Ver [04_Instalacion.md](04_Instalacion.md) |
| **Responsable** | Norberto Núñez + equipo técnico |

---

## RIE-003 — Proxy HTTP temporal con dependencia externa *(parcialmente vigente)*

| Campo | Detalle |
|---|---|
| **Descripción** | Los contenedores acceden a internet via proxy HTTP corporativo, habilitado temporalmente por el equipo de seguridad |
| **Causa** | En sitios sin OVN funcional se sigue usando el dispositivo proxy LXD por contenedor como workaround. En PFR1 y CAR1 (con OVN ya funcional) el workaround se reemplazó por un contenedor gateway dedicado de operación y mantenimiento — ver [05_Configuracion.md](05_Configuracion.md) — pero la dependencia del proxy corporativo en sí sigue existiendo |
| **Impacto** | Si el equipo de seguridad deshabilita el proxy, los contenedores pierden acceso a internet (no pueden instalar paquetes). La duración del permiso no fue confirmada |
| **Severidad** | Media |
| **Mitigación actual** | Nicolás (seguridad) habilitó el proxy. Marcos debe confirmar si es permanente |
| **Acción requerida** | Confirmar con Nicolás la permanencia del acceso al proxy. Repetir el patrón de gateway de operación y mantenimiento en FDO1 cuando se incorpore |
| **Responsable** | Marcos Casco → Nicolás |

---

## RIE-004 — InfraFileRoom en CentOS 7 (EOL)

| Campo | Detalle |
|---|---|
| **Descripción** | InfraFileRoom (~800 GB de datos) sigue corriendo en CentOS 7, que está en End of Life |
| **Causa** | La migración al cluster LXD no ha comenzado |
| **Impacto** | Sin parches de seguridad. Cualquier vulnerabilidad en CentOS 7 o sus paquetes queda expuesta indefinidamente. |
| **Severidad** | Alta — riesgo de seguridad y cumplimiento activo |
| **Mitigación actual** | Ninguna técnica. El proyecto LXD es la mitigación planificada. |
| **Acción requerida** | Definir plan y fecha de migración de InfraFileRoom al cluster LXD |
| **Responsable** | Marcos Casco + equipo técnico |

---

## RIE-005 — Acceso a Web UI solo desde red local

| Campo | Detalle |
|---|---|
| **Descripción** | La Web UI de LXD solo es accesible desde la red interna. No hay acceso remoto via VPN. |
| **Causa** | VPN no configurada para este servicio |
| **Impacto** | Los operadores que no estén en la red local no pueden administrar el cluster |
| **Severidad** | Media |
| **Mitigación actual** | Los operadores deben trabajar desde la red interna |
| **Acción requerida** | Evaluar y configurar acceso VPN para operadores remotos |
| **Responsable** | Pendiente de asignar |

---

## RIE-006 — Sin política de backup documentada

| Campo | Detalle |
|---|---|
| **Descripción** | No existe una política formal de backup para los contenedores ni para las VMs |
| **Causa** | El proyecto está en fase inicial de instalación |
| **Impacto** | En caso de pérdida de datos (falla de disco, error humano), puede no haber punto de restauración |
| **Severidad** | Media-Alta |
| **Mitigación actual** | Norberto sugirió: (1) exportar imágenes localmente, (2) pedir backup de VM a SBA/AIT |
| **Acción requerida** | Solicitar formalmente backup de VMs a SBA/AIT. Definir frecuencia y retención. Ver [06_Operacion.md](06_Operacion.md). |
| **Responsable** | Marcos Casco → SBA/AIT |

---

## RIE-007 — IP de proxy HTTP sin confirmar

| Campo | Detalle |
|---|---|
| **Descripción** | La dirección exacta del proxy HTTP (mencionada como `32.x.x.x:3128` en la reunión) no fue confirmada con certeza |
| **Causa** | Durante la reunión hubo confusión entre `31.100` y `32.x.x.x` en la discusión de la IP |
| **Impacto** | Si la IP configurada es incorrecta, los contenedores no pueden acceder a internet |
| **Severidad** | Baja (detectable fácilmente) |
| **Mitigación actual** | Verificar con `lxc config get core.http_proxy` y probar conectividad desde un contenedor |
| **Acción requerida** | Confirmar la IP correcta del proxy con Nicolás (equipo de seguridad) |
| **Responsable** | Equipo técnico → Nicolás |

---

## RIE-008 — IPs de operadores en firewall sin validar

| Campo | Detalle |
|---|---|
| **Descripción** | Las IPs de los operadores (Daniel, Rocío) agregadas al firewall fueron capturadas parcialmente durante la reunión |
| **Causa** | La transcripción VTT no capturó correctamente las IPs completas |
| **Impacto** | Si las IPs del firewall son incorrectas, los operadores no pueden acceder a la Web UI |
| **Severidad** | Baja |
| **Mitigación actual** | Verificar acceso con cada operador |
| **Acción requerida** | Que cada operador confirme su IP pública y verificar que está en las rich rules del firewall |
| **Responsable** | Equipo técnico |

---

## RIE-009 — Puerto de gestión de LXD en CAR1 sin alta de servicio formal

| Campo | Detalle |
|---|---|
| **Descripción** | El servidor CAR1 ya está inventariado y reconocido por la VPN corporativa, pero el puerto específico de gestión de LXD (8444) todavía no fue dado de alta como servicio ante el equipo de seguridad |
| **Causa** | El proceso de alta de servicio para CAR1 se inicia recién después de completar la instalación técnica (a diferencia de Franco, donde ya se completó) |
| **Impacto** | Mientras no se complete el alta, el acceso remoto (VPN) al puerto 8444 de CAR1 puede no estar habilitado para todos los operadores que lo necesiten |
| **Severidad** | Baja — mitigado porque el cluster se puede gestionar desde cualquier miembro con acceso habilitado (ver nota de mitigación abajo) |
| **Mitigación actual** | El cluster LXD se puede gestionar desde **cualquier nodo miembro** (CLI o Web UI), porque la base de datos se replica entre todos. No depender de un único nodo para la gestión reduce el impacto de que un nodo puntual no tenga su puerto declarado |
| **Acción requerida** | Marcos Casco debe gestionar el alta de servicio del puerto 8444 para CAR1 ante el equipo de seguridad |
| **Responsable** | Marcos Casco |

> **Nota — consulta de Marcos Casco sobre declarabilidad de IPs:** durante la reunión se preguntó si el rango IP de gestión de Carpinelli podía declararse sin problema ante seguridad. Norberto Núñez respondió que, siempre que la IP esté bien inventariada y declarada como servicio por las vías correspondientes, no debería haber problema — y que, en el peor caso de que un nodo puntual no pudiera inventariarse, el cluster sigue siendo gestionable desde los demás miembros gracias a la base de datos distribuida. Esta respuesta se documenta como mitigación de este riesgo, no como una garantía formal de seguridad — 🔴 pendiente de confirmación explícita por el equipo de seguridad.

---

## Resumen de severidades

| Severidad | Riesgos |
|---|---|
| **Alta** | RIE-001b (WireGuard no persistido), RIE-004 (CentOS 7 EOL) |
| **Media-Alta** | RIE-002 (2/3 nodos), RIE-006 (sin backup) |
| **Media** | RIE-001c (mesh WireGuard manual), RIE-003 (proxy temporal), RIE-005 (sin VPN) |
| **Baja** | RIE-007 (IP proxy), RIE-008 (IPs firewall), RIE-009 (alta de servicio CAR1) |
| **Resuelto** | RIE-001 (OVN entre PFR1 y CAR1) |

---

## Documentos relacionados

| Tema | Documento |
|---|---|
| Plan de acción (próximos pasos) | [13_Linea_de_Tiempo.md](13_Linea_de_Tiempo.md) |
| Decisiones que generaron estos riesgos | [10_Decisiones.md](10_Decisiones.md) |
| Procedimientos de backup | [06_Operacion.md](06_Operacion.md) |
