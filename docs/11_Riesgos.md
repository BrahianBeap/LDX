# 11 — Riesgos identificados

> **Audiencia:** Ingenieros de infraestructura, SRE, gestores técnicos.
> **Propósito:** Catálogo de riesgos técnicos, operativos y de seguridad identificados durante la instalación inicial.

---

## RIE-001 — Red OVN no funcional entre sitios

| Campo | Detalle |
|---|---|
| **Descripción** | La red OVN que conecta contenedores entre sitios geográficos no está operativa |
| **Causa** | La interfaz de red VLAN 411 (dedicada para contenedores) no ha sido habilitada en las VMs |
| **Impacto** | Los contenedores de distintos nodos del cluster no pueden comunicarse entre sí |
| **Severidad** | Alta — bloquea la propuesta de valor principal del cluster |
| **Mitigación actual** | Dispositivos proxy LXD sobre la interfaz de gestión (workaround temporal) |
| **Acción requerida** | Solicitar a Cristian (VMware) la habilitación de VLAN 411 en PFR1, CAR1 y FDO1 |
| **Responsable** | Marcos Casco → Cristian |

---

## RIE-002 — Un solo nodo activo (sin alta disponibilidad real)

| Campo | Detalle |
|---|---|
| **Descripción** | Actualmente solo PFR1 está instalado. El cluster tiene un único miembro activo. |
| **Causa** | CAR1 y FDO1 están pendientes de instalación |
| **Impacto** | Si PFR1 falla, todos los contenedores quedan inaccesibles — no hay failover |
| **Severidad** | Alta — el cluster no tiene redundancia hasta agregar más nodos |
| **Mitigación actual** | Backup de VM en VMware (solicitar a SBA/AIT) |
| **Acción requerida** | Instalar LXD en CAR1 y FDO1 y agregarlos al cluster. Ver [04_Instalacion.md](04_Instalacion.md) |
| **Responsable** | Norberto Núñez + equipo técnico |

---

## RIE-003 — Proxy HTTP temporal con dependencia externa

| Campo | Detalle |
|---|---|
| **Descripción** | Los contenedores acceden a internet via proxy HTTP corporativo, habilitado temporalmente por el equipo de seguridad |
| **Causa** | La red OVN no está disponible; se usa dispositivo proxy LXD como workaround |
| **Impacto** | Si el equipo de seguridad deshabilita el proxy, los contenedores pierden acceso a internet (no pueden instalar paquetes). La duración del permiso no fue confirmada. |
| **Severidad** | Media |
| **Mitigación actual** | Nicolás (seguridad) habilitó el proxy. Marcos debe confirmar si es permanente. |
| **Acción requerida** | Confirmar con Nicolás la permanencia del acceso al proxy, o acelerar la configuración de OVN |
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

## Resumen de severidades

| Severidad | Riesgos |
|---|---|
| **Alta** | RIE-001 (OVN), RIE-002 (un nodo), RIE-004 (CentOS 7 EOL) |
| **Media-Alta** | RIE-006 (sin backup) |
| **Media** | RIE-003 (proxy temporal), RIE-005 (sin VPN) |
| **Baja** | RIE-007 (IP proxy), RIE-008 (IPs firewall) |

---

## Documentos relacionados

| Tema | Documento |
|---|---|
| Plan de acción (próximos pasos) | [13_Linea_de_Tiempo.md](13_Linea_de_Tiempo.md) |
| Decisiones que generaron estos riesgos | [10_Decisiones.md](10_Decisiones.md) |
| Procedimientos de backup | [06_Operacion.md](06_Operacion.md) |
