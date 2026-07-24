# ADR-0006 — WireGuard como transporte underlay para OVN entre sitios en Capa 3

| Campo | Valor |
|---|---|
| **Número** | ADR-0006 |
| **Fecha** | 2026-07-24 |
| **Estado** | Aceptado |
| **Autores** | Norberto Núñez |
| **Revisores** | Marcos Casco, equipo técnico |
| **Reunión origen** | `reunion/segunda_reunion LXD _ Implementacion.vtt` |

---

## Contexto

[ADR-0002](ADR-0002-red-ovn-vs-ubuntu-fan.md) eligió OVN (via MicroOVN) como red SDN para interconectar contenedores entre los sitios geográficos del cluster (Franco/PFR1, Carpinelli/CAR1, Fernando/FDO1), asumiendo que bastaba con habilitar una interfaz de red dedicada (VLAN 411) en cada VM.

OVN funciona sin problemas cuando todos los miembros del cluster están **bajo un mismo switch o una misma Capa 2**. En ese escenario, el túnel de datos de OVN (que interconecta los routers y switches virtualizados de cada chassis) se establece directamente sobre esa red compartida.

El entorno real de este proyecto es distinto: Franco, Carpinelli y Fernando están en **redes de Capa 3 separadas**, sin una Capa 2 común entre sitios. Este mismo escenario ya había sido intentado el año anterior en una implementación del equipo de "ingeniería de servicios" y no se logró hacer funcionar — se identificó el problema en ese momento pero no se pudo completar el troubleshooting por falta de tiempo.

Norberto Núñez replicó la misma metodología en este proyecto y volvió a reproducirse el mismo problema:

- El plano de control de OVN se establecía correctamente (la base de datos distribuida de OVN — activo/standby — sincronizaba sin problemas entre sitios).
- El tráfico de datos entre contenedores de distintos sitios **no llegaba**: un contenedor en Franco no podía ver a un contenedor en Carpinelli, y viceversa.
- El comportamiento era asimétrico: de Franco hacia Carpinelli llegaban **algunos** paquetes (no todos); de Carpinelli hacia Franco **no llegaba ninguno**.

**Diagnóstico:** en algún punto de la red corporativa entre Carpinelli y Franco hay un elemento (firewall, ACL de switch/router, o equivalente) que bloquea o filtra el tráfico del túnel de transporte de OVN (el que interconecta los chassis/hosts entre datacenters). El plano de control de OVN no se ve afectado porque usa un canal distinto al del túnel de datos entre chassis.

Adicionalmente, el túnel de datos nativo de OVN, en su estado del arte actual, **no cifra el tráfico** que viaja entre datacenters. Esto implica que, aunque el túnel funcionara, cualquier atacante en una posición de *man-in-the-middle* en el tránsito entre sitios podría capturar ese tráfico en texto plano (riesgo de *sniffing*).

---

## Problema

¿Cómo lograr que la red overlay de OVN interconecte contenedores entre sitios geográficos que están en Capa 3 separada, dado que el túnel de datos nativo de OVN es bloqueado por elementos de red intermedios y, adicionalmente, no cifra el tráfico en tránsito?

---

## Alternativas evaluadas

### Opción A — Túnel nativo de OVN directamente sobre la red corporativa (backbone IP)

**Descripción:**
Enfoque original de [ADR-0002](ADR-0002-red-ovn-vs-ubuntu-fan.md): el túnel de datos de OVN viaja directamente sobre la red IP corporativa que conecta los sitios, usando la interfaz de red dedicada a contenedores (VLAN 411) en cada VM.

**Ventajas:**
- No agrega ninguna capa adicional de software.
- Es la configuración estándar recomendada por la documentación de OVN/MicroOVN.

**Desventajas:**
- **No funciona en este entorno.** Confirmado dos veces (implementación del año anterior e implementación actual): el tráfico del túnel es bloqueado o filtrado entre sitios en Capa 3 separada.
- No cifra el tráfico en tránsito entre datacenters.
- El troubleshooting de la causa exacta del bloqueo (qué elemento de red específico filtra el tráfico) requeriría coordinación con el equipo de red corporativo, sin garantía de resolución ni plazo.

---

### Opción B — VXLAN

**Descripción:**
Tecnología de red overlay que encapsula tráfico Capa 2 sobre UDP, evaluada como alternativa de transporte.

**Ventajas:**
- Tecnología overlay madura y ampliamente soportada.

**Desventajas:**
- **Es una tecnología de Capa 2 pura**, que depende de ARP para resolución de direcciones. No resuelve el problema de fondo (interconectar sitios en Capa 3 separada sin Capa 2 común) de una forma estructuralmente distinta al túnel nativo de OVN.
- No aporta cifrado del tráfico en tránsito.
- Descartada sin implementación de prueba — el análisis conceptual fue suficiente para priorizar la Opción C.

---

### Opción C — WireGuard como transporte underlay, con OVN corriendo por encima

**Descripción:**
WireGuard es una red overlay punto a punto (mesh), mucho más simple que OVN: no tiene plano de control propio, no usa una base de datos distribuida — la configuración de cada túnel (claves, endpoints, rutas) es enteramente manual y debe replicarse en cada par de nodos ("peers") que deben verse entre sí.

La propuesta es usar WireGuard como una capa de transporte ("underlay") entre los sitios, y hacer que el túnel de datos de OVN viaje **encima** de esa malla WireGuard en lugar de viajar directamente sobre la red corporativa.

**Ventajas:**
- **Probado y funcional:** se estableció la malla WireGuard entre Franco y Carpinelli y, sobre ella, el túnel de datos de OVN — la comunicación entre contenedores de ambos sitios quedó operativa.
- WireGuard **cifra todo el tráfico** que atraviesa el túnel. Esto resuelve, de paso, el problema de falta de cifrado del túnel nativo de OVN: aunque OVN no cifre su propio túnel, ese túnel ahora viaja dentro de un túnel WireGuard ya cifrado.
- No depende de que el equipo de red corporativo abra o modifique reglas — el túnel WireGuard atraviesa la red igual que cualquier tráfico UDP normal, sin quedar bloqueado como el túnel nativo de OVN.
- Configuración simple por par de nodos (clave pública/privada + endpoint + rutas).

**Desventajas:**
- Al no tener plano de control ni base de datos distribuida, **toda la configuración es manual**: agregar un nuevo sitio al cluster implica generar un nuevo par de claves y actualizar la configuración de **todos** los nodos existentes para agregarlo como nuevo *peer* (no escala automáticamente como sí lo hace la base de datos distribuida de OVN o de LXD).
- Agrega una capa adicional de infraestructura a operar y a diagnosticar en caso de falla (ver diagrama de capas más abajo).
- La configuración de IP de la interfaz WireGuard debe persistirse explícitamente (por ejemplo, en `netplan`); si se configura solo en caliente (`ip addr add`, etc.) se pierde al reiniciar el host. **Pendiente de resolver de forma definitiva** — ver sección de Pendientes.

---

## Decisión

**Se elige: Opción C — WireGuard como transporte underlay, con OVN (overlay) corriendo por encima de la malla WireGuard.**

Modelo de capas resultante para la interconexión de sitios:

```
  ┌─────────────────────────────────────────┐
  │  Capa 3 — Red virtualizada del cluster   │   ← Contenedores LXD (red horizontal
  │  (OVN — routers/switches virtualizados)  │      entre contenedores, este-oeste)
  ├─────────────────────────────────────────┤
  │  Capa 2 — Overlay cifrado (WireGuard)    │   ← Malla punto a punto (mesh) entre
  │                                           │      los hosts de cada sitio
  ├─────────────────────────────────────────┤
  │  Capa 1 — Red de transporte (backbone IP)│   ← Red corporativa existente entre
  │                                           │      Franco, Carpinelli y Fernando
  └─────────────────────────────────────────┘
```

Esto significa que **OVN sigue siendo la tecnología SDN elegida en [ADR-0002](ADR-0002-red-ovn-vs-ubuntu-fan.md)** — esta decisión no la reemplaza, sino que resuelve el problema de transporte entre sitios que ADR-0002 no había anticipado.

---

## Justificación

WireGuard fue la única alternativa, de las evaluadas, que se probó exitosamente en el entorno real: el mismo tráfico que era bloqueado al viajar directamente sobre la red corporativa (Opción A) sí atraviesa la red cuando va encapsulado dentro de un túnel WireGuard.

Adicionalmente, WireGuard resuelve un problema de seguridad que Opción A no resolvía (falta de cifrado en tránsito), sin necesidad de escalar el troubleshooting con el equipo de red corporativo ni depender de cambios de infraestructura fuera del control del equipo de plataforma.

VXLAN (Opción B) fue descartada por ser conceptualmente Capa 2, lo que no resuelve el problema de fondo de interconectar sitios sin Capa 2 común.

---

## Aclaración importante sobre VLAN 411 (actualiza [ADR-0002](ADR-0002-red-ovn-vs-ubuntu-fan.md))

Durante la reunión se aclaró una confusión relevante: **cada sitio sigue necesitando una segunda interfaz de red dedicada** (la que en Franco se llama `nicsrv1` y hospeda la VLAN de servicio local de ese sitio) para el tráfico de contenedores — esto no cambia respecto de ADR-0002.

Lo que **no es necesario** es que esa VLAN tenga el mismo identificador ni pertenezca a la misma Capa 2 en los tres sitios. Marcos Casco preguntó explícitamente si había que crear la misma VLAN (ej. VLAN 5, usada en Fernando) en Franco y Carpinelli — Norberto Núñez respondió que **no**: a nivel de networking, cada sitio puede usar su propia VLAN local, distinta de las demás.

✅ Lo único que **LXD exige** es que **el nombre de la interfaz de red** usada para la red virtualizada del cluster sea **idéntico en todos los miembros del cluster** (ej. `nicsrv1` en Franco y en Carpinelli, aunque la interfaz física original tuviera nombres distintos como `NS35` o `NS37`). Esto se logra renombrando la interfaz con `netplan`, haciendo *match* por dirección MAC. Ver [05_Configuracion.md](../05_Configuracion.md).

Esta aclaración es importante porque desacopla la conectividad entre sitios (resuelta por WireGuard, Capa 3) de la topología de VLAN local de cada sitio (que puede ser distinta en cada uno).

---

## Consecuencias

### Positivas
- Conectividad de contenedores entre sitios geográficos en Capa 3 separada, validada en producción entre Franco y Carpinelli.
- Cifrado del tráfico inter-sitio, mitigando el riesgo de *sniffing* que tenía el túnel nativo de OVN.
- No depende de cambios en la red corporativa ni de una Capa 2 compartida entre sitios — reduce la dependencia de equipos externos al proyecto.
- Confirma que **no es necesario** que la VLAN de servicio sea idéntica entre sitios, simplificando la coordinación con el administrador de VMware para futuros sitios.

### Negativas / Compromisos aceptados
- Una capa adicional de infraestructura (WireGuard) que operar, monitorear y diagnosticar.
- Configuración de la malla WireGuard **completamente manual**: agregar un nuevo sitio requiere generar claves nuevas y modificar la configuración de `netplan` en **todos** los nodos existentes del cluster para agregar el nuevo *peer*. No escala automáticamente.
- Documentación operativa (`clave pública`, IP interna, rutas) debe mantenerse actualizada y sincronizada manualmente entre todos los sitios.

### Riesgos
- 🔴 **Pendiente de validación:** la configuración de la dirección IP de la interfaz WireGuard se realizó manualmente en la sesión y **no fue persistida** en `netplan`. Se perderá si el host se reinicia, dejando el enlace WireGuard (y por lo tanto OVN entre sitios) caído hasta que se reconfigure manualmente. Ver [11_Riesgos.md](../11_Riesgos.md).
- A medida que se agreguen más sitios (Fernando/FDO1, y potencialmente IT y Ciudad del Este), la configuración manual de la malla WireGuard crece de forma cuadrática (cada nuevo nodo debe agregarse como *peer* en todos los nodos existentes). Sin automatización, esto es propenso a errores de configuración a mediano plazo.
- Un error en la clave pública, el endpoint o las rutas de un peer WireGuard produce fallas de conectividad silenciosas (el túnel no reporta error explícito; simplemente no hay tráfico), similar a como se manifestó originalmente el problema que motivó este ADR.

---

## Pendientes de seguimiento

- [ ] Persistir la configuración de IP de la interfaz WireGuard en `netplan` en Franco y Carpinelli, para que sobreviva reinicios.
- [ ] Repetir el procedimiento de configuración de WireGuard + OVN al incorporar Fernando (FDO1) como tercer miembro del cluster.
- [ ] Evaluar automatización (script o herramienta de gestión de configuración) para la generación y distribución de claves/peers de WireGuard antes de escalar a más de 3-4 sitios.
- [ ] Documentar el esquema de direccionamiento interno de la malla WireGuard (rango no enrutable usado, asignación numérica por sitio) de forma centralizada.

---

## Referencias

- [ADR-0002 — Red SDN: OVN vs Ubuntu Fan](ADR-0002-red-ovn-vs-ubuntu-fan.md)
- [02_Arquitectura.md — Redes del sistema](../02_Arquitectura.md)
- [05_Configuracion.md — Configuración de WireGuard](../05_Configuracion.md)
- [11_Riesgos.md](../11_Riesgos.md)
- [13_Linea_de_Tiempo.md](../13_Linea_de_Tiempo.md)
- Reunión origen: `reunion/segunda_reunion LXD _ Implementacion.vtt`
