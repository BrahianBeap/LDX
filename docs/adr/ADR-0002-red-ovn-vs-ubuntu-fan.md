# ADR-0002 — Elección de red SDN para contenedores: OVN vs Ubuntu Fan

| Campo | Valor |
|---|---|
| **Número** | ADR-0002 |
| **Fecha** | 2026-06-25 |
| **Estado** | Aceptado |
| **Autores** | Norberto Núñez |
| **Revisores** | Marcos Casco, equipo técnico |
| **Reunión origen** | `reunion/Llamada con Daniel y 3 personas más.vtt` |

---

## Contexto

El cluster LXD está distribuido en 3 sitios geográficos (Franco, Carpinelli, Fernando) en redes Layer 3 separadas. Los contenedores de distintos sitios necesitan una red virtual que los conecte como si estuvieran en la misma red, independientemente de su ubicación física.

La red de gestión de las VMs usa una subred **/29** (solo 6 IPs utilizables). Esta restricción es una constante del entorno — no es modificable sin coordinación con el equipo de red corporativo.

---

## Problema

¿Qué tecnología de red SDN usar para interconectar los contenedores LXD entre nodos en distintos sitios geográficos, dado que la red de gestión es /29?

---

## Alternativas evaluadas

### Opción A — OVN (Open Virtual Network) via MicroOVN

**Descripción:**
OVN es una capa de virtualización de red de código abierto que corre sobre Open vSwitch. MicroOVN es la distribución de Canonical que simplifica su instalación y gestión via snap.

OVN crea redes virtuales overlay que pueden cruzar cualquier topología de red subyacente (Layer 3), permitiendo que contenedores en distintos sitios se comuniquen como si estuvieran en la misma red local.

**Ventajas:**
- Funciona sobre redes Layer 3 (no requiere Layer 2 compartido entre sitios).
- No depende del tamaño de la subred de gestión.
- Integración nativa con LXD.
- Soporte oficial de Canonical.
- Escalable a múltiples sitios.

**Desventajas:**
- Más complejo de configurar que Ubuntu Fan.
- Requiere una interfaz de red adicional dedicada (VLAN 411) en cada VM.
- La configuración inter-sitio requiere planificación de red.

---

### Opción B — Ubuntu Fan

**Descripción:**
Ubuntu Fan es una tecnología de overlay de red desarrollada por Canonical para conectar contenedores. Crea una red overlay usando el mapeo de direcciones IP entre la subred de host y la subred de contenedores.

**Ventajas:**
- Más simple de configurar.
- Integrado directamente en Ubuntu.

**Desventajas:**
- **Requiere que la red de hosts use subred /24 o mayor.**
- La red de gestión del entorno es /29 — incompatible con Ubuntu Fan.
- No puede usarse en este entorno sin cambios fundamentales en la infraestructura de red.

---

## Decisión

**Se elige: Opción A — OVN via MicroOVN.**

---

## Justificación

Ubuntu Fan fue descartado directamente por incompatibilidad técnica: requiere /24 y la red disponible es /29. No existe workaround para esta restricción sin modificar la infraestructura de red corporativa.

OVN es la única opción viable que:
- Funciona sobre la red Layer 3 existente.
- No depende del tamaño de la subred de gestión.
- Tiene soporte oficial de Canonical (MicroOVN).
- Se integra nativamente con LXD.

---

## Consecuencias

### Positivas
- Red de contenedores que funciona entre sitios geográficos.
- Separación limpia entre red de gestión (VMs) y red de contenedores (OVN).
- Escalable al agregar nuevos sitios.

### Negativas / Compromisos aceptados
- Requiere una interfaz de red adicional (VLAN 411) en cada VM — dependencia del administrador VMware (Cristian).
- Configuración más compleja que Ubuntu Fan.
- Mayor superficie de componentes (MicroOVN + OVN) para mantener.

### Riesgos
- Hasta que VLAN 411 esté disponible, la red de contenedores no está operativa. Se usa un workaround temporal (dispositivo proxy LXD) que no escala a producción.
- La configuración OVN inter-sitio puede revelar problemas de routing corporativo no anticipados.

---

## Pendientes de seguimiento

- [x] Solicitar interfaz de red dedicada a Cristian para PFR1 y CAR1 — completado (ver actualización debajo).
- [x] Configurar OVN con la nueva interfaz — completado en PFR1 y CAR1.
- [x] Verificar conectividad OVN entre PFR1 y CAR1 (primer test inter-sitio) — completado.
- [ ] Solicitar/configurar interfaz de red dedicada en FDO1 (Fernando) al incorporarlo como tercer miembro.
- [ ] Documentar la configuración OVN resultante en [05_Configuracion.md](../05_Configuracion.md).

---

## Actualización (2026-07-24 — segunda reunión)

La conectividad OVN entre sitios en Capa 3 separada **no funcionó** usando el túnel nativo de OVN directamente sobre la red corporativa (bloqueado por un elemento de red intermedio no identificado). Se resolvió agregando WireGuard como capa de transporte underlay, con el túnel de OVN corriendo por encima. Ver el análisis completo, las alternativas evaluadas y la decisión en **[ADR-0006](ADR-0006-wireguard-underlay-ovn-multisitio.md)**.

También se aclaró que la interfaz de red dedicada para contenedores (referida originalmente como "VLAN 411") **no necesita ser la misma VLAN ni pertenecer a la misma Capa 2 en los tres sitios** — cada sitio puede tener su propia VLAN local. Lo único que LXD exige es que el **nombre de la interfaz** sea idéntico en todos los miembros del cluster. Ver detalle en [ADR-0006](ADR-0006-wireguard-underlay-ovn-multisitio.md#aclaración-importante-sobre-vlan-411-actualiza-adr-0002).

---

## Referencias

- [02_Arquitectura.md — Sección de redes](../02_Arquitectura.md)
- [11_Riesgos.md — RIE-001](../11_Riesgos.md)
- [13_Linea_de_Tiempo.md](../13_Linea_de_Tiempo.md)
- [ADR-0006 — WireGuard como transporte underlay para OVN entre sitios](ADR-0006-wireguard-underlay-ovn-multisitio.md)
