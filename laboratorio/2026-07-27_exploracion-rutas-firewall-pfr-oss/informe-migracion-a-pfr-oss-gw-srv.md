# Informe — Qué falta para publicar Kanboard vía PFR-OSS-GW-SRV

> **Fecha:** 2026-07-27
> **Método:** revisión exclusiva de documentación ya existente en este
> repositorio (`docs/`, `laboratorio/`, `onenote/`, `proyectos/`,
> `CHANGELOG.md`). **No se ejecutó ningún comando nuevo, no se hizo
> ninguna consulta en vivo al cluster para este informe** — todo lo que
> sigue está citado con su fuente exacta. Donde el dato no existe, se
> indica explícitamente como tal, sin completarlo con supuestos.

---

## 1. Arquitectura actual

Hoy Kanboard se alcanza por **dos caminos**, ninguno de los dos es la vía
oficial del gateway de servicios:

**Camino 1 — Túnel SSH personal (el original):**

```
PC del usuario --SSH (-L 8080:127.0.0.1:8080)--> pfr-oss (10.143.11.228)
                                                      │
                                          dispositivo proxy LXD "web-public"
                                          listen: 127.0.0.1:8080 (solo local)
                                          connect: 127.0.0.1:80
                                                      │
                                          PFR-KANBOARD-TEST (proyecto "default", OVN_1)
```
Fuente: [`laboratorio/2026-07-27_exploracion-rutas-firewall-pfr-oss/SOP-acceso-temporal-demo-kanboard.md`](SOP-acceso-temporal-demo-kanboard.md), sección "Arquitectura antes del cambio".

**Camino 2 — Acceso temporal por firewall (agregado para la demo del 2026-07-28):**

```
6 IPs autorizadas (VPN corporativa)
        │  HTTP directo a 10.143.11.228:8080
        ▼
firewalld, zona "work" (interfaz ens192) — 6 reglas /32, puerto 8080
        │
        ▼
dispositivo proxy LXD nuevo "web-lan" — listen: 10.143.11.228:8080
        │
        ▼
PFR-KANBOARD-TEST (192.168.0.106:80)
```
Fuente: mismo SOP, sección "Arquitectura después del cambio", y
[`comandos-agregar-ip.md`](comandos-agregar-ip.md).

**Detalle común a ambos caminos:** `PFR-KANBOARD-TEST` vive en el
proyecto LXD **`default`**, no en `PRJ-OSS` — se movió ahí durante la
prueba original porque `PRJ-OSS` tiene `restricted.devices.proxy`
bloqueado por diseño (ver
[`ADR-0007`](../../docs/adr/ADR-0007-proyectos-lxd-multitenancy.md)).
Fuente: [`laboratorio/2026-07-24_kanboard-contenedor-prueba/conclusiones.md`](../2026-07-24_kanboard-contenedor-prueba/conclusiones.md), punto 5.

Ninguno de los dos caminos pasa por `PFR-OSS-GW-SRV`.

---

## 2. Arquitectura objetivo

Según el patrón ya documentado ("gateway de servicios"), la vía oficial
sería:

```
Usuario (red corporativa / VPN)
        │
        ▼
PFR-OSS-GW-SRV — eth1 (IPVLAN sobre nic_srv1) — IP de servicio 10.143.11.8
        │
        │  [MECANISMO DE REENVÍO — NO CONFIGURADO TODAVÍA, ver sección 4]
        │
        ▼
PFR-OSS-GW-SRV — eth0 (OVN_1) — IP interna 192.168.0.1
        │
        ▼
Contenedor de Kanboard en OVN_1 (192.168.0.0/24)
```

Fuente de la arquitectura del gateway:
[`docs/02_Arquitectura.md`](../../docs/02_Arquitectura.md) ("Patrón de
contenedor 'gateway de servicios'") y
[`docs/03_Componentes.md`](../../docs/03_Componentes.md) (ficha completa
del componente).

**Dato relevante encontrado:** el contenedor gateway está diseñado
explícitamente para **no alojar aplicaciones** — es un router, no un
servidor de aplicaciones (`docs/03_Componentes.md`, "Buenas prácticas...
este contenedor actúa como router y no aloja aplicaciones"). El
`cloud-init` real de su creación solo instala el paquete `firewalld`
— ningún servidor web ni proxy de aplicación
([`onenote/Clúster-OSS/Proyectos/Proyecto-PRJ-OSS.md`](../../onenote/Clúster-OSS/Proyectos/Proyecto-PRJ-OSS.md),
[`docs/05_Configuracion.md`](../../docs/05_Configuracion.md) líneas
560-620). Esto sugiere que el mecanismo esperado sería un reenvío a
nivel de red (NAT/DNAT), no un reverse-proxy HTTP con `VirtualHost`/
`ProxyPass` — pero **no hay ninguna confirmación explícita de esto en
ningún documento** (ver sección 4).

**Sobre el proyecto LXD de Kanboard:** la red `OVN_1` es compartida entre
proyectos (`default` y `PRJ-OSS` ya conviven en la misma red, confirmado
en `laboratorio/2026-07-27_exploracion-rutas-firewall-pfr-oss/bitacora.md`,
sección 3) — técnicamente no sería obligatorio mover
`PFR-KANBOARD-TEST` a `PRJ-OSS` para que el reenvío funcione, aunque por
consistencia de modelo (`ADR-0007`) tendría sentido que un servicio de
`PRJ-OSS` viva dentro de ese proyecto.

---

## 3. Evidencias encontradas

| Documento | Qué aporta |
|---|---|
| [`docs/02_Arquitectura.md`](../../docs/02_Arquitectura.md) | Direccionamiento IP de `OVN_1`, patrón "gateway de servicios", diagrama de capas de red |
| [`docs/03_Componentes.md`](../../docs/03_Componentes.md) | Ficha completa del componente "Contenedor gateway de servicios" (función, dependencias, impacto si falla, buenas prácticas) |
| [`docs/05_Configuracion.md`](../../docs/05_Configuracion.md) | Comandos reales de creación del perfil `PRF-PFR-OSS-GW-SRV`/`PRF-CAR-OSS-GW-SRV` y la instancia `PFR-OSS-GW-SRV` |
| [`docs/adr/ADR-0007-proyectos-lxd-multitenancy.md`](../../docs/adr/ADR-0007-proyectos-lxd-multitenancy.md) | Por qué `PRJ-OSS` bloquea dispositivos `proxy` (justamente para forzar el uso del gateway) |
| [`docs/11_Riesgos.md`](../../docs/11_Riesgos.md) | Riesgo del proxy corporativo y el patrón de gateway de OAM (relacionado, no específico de GW-SRV) |
| [`onenote/Clúster-OSS/Proyectos/Proyecto-PRJ-OSS.md`](../../onenote/Clúster-OSS/Proyectos/Proyecto-PRJ-OSS.md) | Notas originales de Norberto: creación real de `PFR-OSS-GW-SRV`/`CAR-OSS-GW-SRV`, configuración interna de firewalld del gateway (zonas `internal`/`external`, ambas en `target=ACCEPT`) |
| [`onenote/Clúster-OSS/Planning/Planning-IP-OVN_1.md`](../../onenote/Clúster-OSS/Planning/Planning-IP-OVN_1.md) | Tabla de asignación de IPs en `OVN_1`, confirma `.1`-`.5` reservadas para gateways de servicio por sitio |
| [`onenote/Clúster-OSS/Planning/Planning-IP-Hosts.md`](../../onenote/Clúster-OSS/Planning/Planning-IP-Hosts.md) | IP de servicio real de cada sitio (`10.143.11.8/26` para Franco) |
| [`laboratorio/2026-07-24_kanboard-contenedor-prueba/conclusiones.md`](../2026-07-24_kanboard-contenedor-prueba/conclusiones.md) | **Confirmación explícita** de que el NAT/reverse-proxy hacia contenedores individuales no está configurado en los gateways de servicio |
| [`laboratorio/2026-07-24_kanboard-contenedor-prueba/README.md`](../2026-07-24_kanboard-contenedor-prueba/README.md) y [`comandos.md`](../2026-07-24_kanboard-contenedor-prueba/comandos.md) | Por qué se terminó usando `default` + túnel SSH en lugar de `PRJ-OSS` + gateway |
| [`laboratorio/2026-07-27_exploracion-rutas-firewall-pfr-oss/bitacora.md`](bitacora.md) | Confirma la IP real de servicio de `PFR-OSS-GW-SRV` (`10.143.11.8`), que `OVN_1` es compartida entre proyectos, y recomienda esta vía como la consistente con `ADR-0007` |
| [`laboratorio/2026-07-27_exploracion-rutas-firewall-pfr-oss/SOP-acceso-temporal-demo-kanboard.md`](SOP-acceso-temporal-demo-kanboard.md) | Arquitectura actual (temporal) completamente documentada, con su propio rollback |
| [`docs/13_Linea_de_Tiempo.md`](../../docs/13_Linea_de_Tiempo.md) | Menciona el patrón de gateway en la cronología general del cluster |

🔴 **No se encontró ningún diagrama de red** — la carpeta `diagramas/`
del repositorio existe solo como mención en la navegación de
`README.md`/`CLAUDE.md`, pero está vacía (sin archivos).

---

## 4. Información faltante

Esto es lo que **no existe** en la documentación actual, no una opinión:

1. **No hay ninguna regla de NAT/DNAT/reenvío de puertos configurada en
   `PFR-OSS-GW-SRV` hacia ningún contenedor individual.** Confirmado
   explícitamente en `laboratorio/2026-07-24_kanboard-contenedor-prueba/conclusiones.md`:
   *"ni siquiera con los gateways de servicio (`PFR-OSS-GW-SRV`)
   encendidos, porque esos todavía no tienen configurado el
   NAT/reverse-proxy hacia contenedores individuales"* y *"Solución
   'real' pendiente: wireear el gateway de servicios con reglas de
   reenvío explícitas — trabajo separado, más grande."*
2. **No está definido el mecanismo exacto de reenvío** — nada en la
   documentación confirma si será NAT/DNAT a nivel de firewall (lo que
   sugiere el diseño "el gateway no aloja aplicaciones") o algún tipo de
   reverse-proxy de aplicación. No se encontró ninguna mención de
   `ProxyPass`, `VirtualHost` con proxy, `nginx`, ni ninguna
   configuración de reenvío HTTP en ningún documento relacionado con
   `PFR-OSS-GW-SRV`.
3. **No está confirmado si el reenvío de IP (`net.ipv4.ip_forward`) está
   habilitado** dentro del contenedor gateway — la documentación lo
   describe como "router" pero no muestra el comando que habilita el
   forwarding a nivel de kernel.
4. **No existe ningún caso real ya publicado** a través de este patrón
   de gateway — Kanboard sería el primer caso de uso real documentado,
   no hay un ejemplo previo del que copiar el procedimiento exacto.
5. **No está decidido si Kanboard debe migrar al proyecto `PRJ-OSS`**
   o puede seguir en `default` (técnicamente ambas comparten `OVN_1`,
   pero no hay una decisión documentada sobre qué es preferible).
6. **No hay ningún diagrama de red** que muestre visualmente este flujo
   (carpeta `diagramas/` vacía).
7. **No hay evidencia de que el trámite formal de "alta de servicio"**
   se haya iniciado específicamente para el puerto/IP de Kanboard — se
   conoce el procedimiento general (usado para PFR1, CAR1 y FDO1, ver
   `docs/11_Riesgos.md` RIE-009), pero no hay una solicitud registrada
   para este caso.
8. **No está aclarado qué significa la nota "Cambio conflictivo."**
   que aparece al final de las notas originales de configuración del
   firewall del host y de la creación de los gateways de servicio
   (`onenote/Clúster-OSS/Clúster/Firewall.md` y
   `onenote/Clúster-OSS/Proyectos/Proyecto-PRJ-OSS.md`) — podría indicar
   un problema real no documentado en el momento de esa configuración.

---

## 5. Checklist de implementación

Basado únicamente en lo confirmado y en los vacíos de la sección 4:

- [ ] **Definir con Norberto el mecanismo de reenvío** (NAT/DNAT a nivel
      de firewall vs. reverse-proxy de aplicación) — es la decisión de
      la que depende todo lo demás, y hoy no está tomada en ningún lado.
- [ ] **Decidir el proyecto LXD definitivo de Kanboard** (`default` vs.
      `PRJ-OSS`).
- [ ] **Confirmar/habilitar IP forwarding** en `PFR-OSS-GW-SRV` si el
      mecanismo elegido lo requiere.
- [ ] **Configurar la regla de reenvío real** en `PFR-OSS-GW-SRV`
      (puerto elegido en `10.143.11.8` → IP interna de Kanboard en
      `OVN_1`) — sería la primera vez que se hace esto en el cluster.
- [ ] **Definir el puerto/protocolo definitivo** (¿seguir con 8080, o
      pasar a 80/443 ahora que hay una IP dedicada?) y si se agrega
      HTTPS en este punto (riesgo ya señalado en el SOP del acceso
      temporal).
- [ ] **Iniciar el trámite formal de alta de servicio** ante
      Norberto/Seguridad para ese puerto/IP — mismo circuito ya usado
      para PFR1, CAR1 y FDO1.
- [ ] **Probar el acceso real de punta a punta** a través del gateway,
      documentando con el mismo nivel de detalle que el SOP del acceso
      temporal (comando, resultado esperado, validación, rollback).
- [ ] **Retirar el acceso temporal** (las 6 reglas de firewall en
      `pfr-oss` y el dispositivo `web-lan`) una vez confirmado que la
      vía oficial funciona — procedimiento ya documentado en
      [`SOP-acceso-temporal-demo-kanboard.md`](SOP-acceso-temporal-demo-kanboard.md).
- [ ] **Documentar el resultado en `docs/`** (no solo en `laboratorio/`)
      una vez validado, ya que hoy el patrón de gateway está documentado
      de forma genérica pero sin ningún caso de uso real aplicado.

---

## 6. Investigación exhaustiva del mecanismo de reenvío (2026-07-27, segunda pasada)

Búsqueda sistemática de 15 términos técnicos en **todo** el repositorio
(`docs/`, `laboratorio/`, `onenote/`, `CHANGELOG.md`) — únicamente
revisión de documentación, sin ninguna consulta en vivo al cluster.

| Término buscado | Resultado | Detalle |
|---|---|---|
| `firewalld` | ✅ Documentado | Presente en los **cuatro** contenedores gateway construidos hasta ahora (`PFR-GW-OAM`, `CAR-GW-OAM` — `onenote/Clúster-OSS/Proyectos/Proyecto-default.md` —, y `PFR-OSS-GW-SRV`, `CAR-OSS-GW-SRV` — `onenote/Clúster-OSS/Proyectos/Proyecto-PRJ-OSS.md`). Patrón **idéntico en los cuatro**: `set-default-zone drop`, zona `external` sobre la interfaz de servicio, zona `internal` sobre OVN, y **ambas puestas en `set-target=ACCEPT`** |
| `forward-port` | ❌ Sin evidencia | Cero coincidencias en cualquier fuente original del repositorio |
| `DNAT` | ❌ Sin evidencia | Cero coincidencias |
| `masquerade` | ❌ Sin evidencia | Cero coincidencias |
| `iptables` | ❌ Sin evidencia | Cero coincidencias |
| `nftables` | ❌ Sin evidencia | Cero coincidencias |
| `sysctl` / `ip_forward` | ❌ Sin evidencia | Cero coincidencias — no hay ningún comando de habilitación de reenvío de IP a nivel de kernel documentado para ningún contenedor gateway |
| `routing` / `enrutamiento` | 🟡 Solo genérico | Aparece en `docs/08_Glosario.md` y `ADR-0002` como término general, sin relación con la publicación de servicios del gateway |
| `reverse proxy` / `proxy inverso` | ❌ Sin evidencia | Cero coincidencias en todo el repositorio, en ningún idioma |
| `apache` | 🟡 Otro contexto | Aparece solo como paquete de ejemplo para **contenedores de aplicación** (plantilla genérica de Norberto en `onenote/Clúster-OSS/Varios/Cloud-init-user-data.md`, y el propio Kanboard de prueba) — nunca en el contenedor gateway |
| `nginx` | ❌ Sin evidencia | Cero coincidencias, en ningún documento |
| `haproxy` | ❌ Sin evidencia | Cero coincidencias |
| `proxy` (genérico) | 🟡 Otro significado | Todas las coincidencias en `Proyecto-PRJ-OSS.md`/`Proyecto-default.md` son el **proxy HTTP corporativo** (`http_proxy`/`https_proxy` de `apt`, puerto 3128) — nada relacionado con publicar servicios |
| `VirtualHost` | 🟡 Otro contexto | Una sola aparición real: el vhost de Kanboard mismo (`DocumentRoot`, sirve la app directamente, sin proxy) |
| `ProxyPass` | ❌ Sin evidencia | Cero coincidencias en todo el repositorio |

### Conclusión de la búsqueda

**No existe evidencia de que se haya decidido ni implementado ningún
mecanismo específico de publicación de servicios** en ningún contenedor
gateway del cluster — ni en `PFR-OSS-GW-SRV` ni en ningún otro. Lo único
real y repetido en los cuatro gateways es la asignación de zonas de
firewalld con ambas en `ACCEPT`, sin ninguna regla de reenvío puerto a
puerto ni de traducción de direcciones. Esto no es una laguna de
documentación — el propio equipo ya lo dejó escrito explícitamente en
`laboratorio/2026-07-24_kanboard-contenedor-prueba/conclusiones.md`
(sección 3 de este informe).

**Dado que ningún gateway del cluster tiene todavía ningún servicio real
publicado a través de él, Kanboard sería el primer caso — no hay ningún
precedente del que copiar el procedimiento exacto.**

---

## 7. Propuesta técnica del procedimiento

```
Usuario (red corporativa / VPN)
        │
        ▼
PFR-OSS-GW-SRV — eth1 (10.143.11.8, IPVLAN L2 sobre nic_srv1)
        │
        │  ← acá está el vacío de la sección 6
        ▼
PFR-OSS-GW-SRV — eth0 (192.168.0.1, OVN_1)
        │
        ▼
Kanboard (contenedor en OVN_1)
```

### ✅ Lo documentado (no cambia, ya existe y está confirmado)

- `PFR-OSS-GW-SRV` ya existe, corriendo, con sus dos interfaces
  configuradas exactamente como se planeó (`docs/05_Configuracion.md`,
  `onenote/Clúster-OSS/Proyectos/Proyecto-PRJ-OSS.md`).
- `eth1` usa **IPVLAN en modo L2** sobre `nic_srv1` — el contenedor
  recibe tráfico dirigido a `10.143.11.8` directamente en el mismo
  segmento L2 del host, sin necesidad de una ruta adicional para que el
  paquete *llegue* al contenedor (`docs/03_Componentes.md`, sección
  "Driver de red IPVLAN").
- Ambas zonas de firewalld (`external`=eth1, `internal`=eth0) están en
  `target=ACCEPT` — hoy no hay ningún filtro adicional bloqueando salida
  ni entrada dentro del propio contenedor gateway.
- `OVN_1` es una red compartida entre proyectos LXD (`default` y
  `PRJ-OSS` conviven en ella) — confirmado en
  `laboratorio/2026-07-27_exploracion-rutas-firewall-pfr-oss/bitacora.md`.

### 🟡 Inferencia técnica (no documentada, pero necesaria dado lo anterior)

Estos pasos **no están escritos en ningún documento** — se derivan de
cómo funciona Linux/firewalld en general, aplicado a lo que sí está
confirmado arriba. No deberían ejecutarse sin que Norberto los revise.

1. **Habilitar reenvío de IP dentro de `PFR-OSS-GW-SRV`.** Para que un
   contenedor actúe como router entre dos interfaces (recibir en `eth1`,
   reenviar por `eth0`), el kernel de ese contenedor necesita
   `net.ipv4.ip_forward=1`. No hay ningún comando de este tipo en las
   notas de creación del gateway — sin él, el contenedor no reenviaría
   tráfico entre sus dos interfaces aunque el firewall lo permita.
   ```bash
   sysctl -w net.ipv4.ip_forward=1
   # persistir en /etc/sysctl.d/99-forwarding.conf
   ```
2. **Agregar una regla de reenvío de puerto (DNAT) en la zona `external`
   de firewalld**, apuntando del puerto público al contenedor interno de
   Kanboard:
   ```bash
   firewall-cmd --zone=external --add-forward-port=port=<PUERTO>:proto=tcp:toaddr=<IP_KANBOARD_OVN1>:toport=80 --permanent
   firewall-cmd --reload
   ```
   Es el mecanismo nativo de firewalld para justamente este caso
   (publicar un puerto externo hacia una IP interna) — coherente con que
   `firewalld` es la única herramienta de red/filtrado ya instalada en
   este contenedor, sin necesidad de agregar nada nuevo (nginx, HAProxy,
   Apache como proxy) que contradiga el principio ya documentado de "el
   gateway no aloja aplicaciones".
3. **Posiblemente haga falta `masquerade`** en la zona correspondiente
   para que el tráfico de retorno de Kanboard vuelva correctamente a
   través del gateway (comportamiento estándar de NAT cuando origen y
   destino están en redes distintas) — a confirmar con una prueba real,
   no se puede asegurar sin probarlo.
4. **El firewall del host `pfr-oss` (fuera del contenedor) probablemente
   no interviene en este camino.** Ya se confirmó en una sesión anterior
   de esta misma investigación (`bitacora.md`, sección 2) que la
   interfaz física `nic_srv1` no tiene ninguna zona de firewalld asignada
   en el host — el filtrado de este camino ocurriría enteramente dentro
   del contenedor gateway, no en `pfr-oss` mismo.

### 🔴 A confirmar explícitamente con Norberto (no se puede decidir sin él)

1. **¿El mecanismo pensado era realmente `forward-port`/DNAT de
   firewalld, o tenía en mente otra cosa?** No hay evidencia de ningún
   mecanismo decidido — la inferencia de la sección anterior es la más
   consistente con lo ya construido, pero es una inferencia, no una
   confirmación.
2. **¿Kanboard debe migrar al proyecto `PRJ-OSS`**, o puede seguir en
   `default` aprovechando que `OVN_1` es compartida?
3. **¿Qué puerto/IP definitivos usar** — ¿el mismo 8080, o pasar a
   80/443 ahora que hay una IP de servicio dedicada?
4. **Qué significa la nota "Cambio conflictivo."** que aparece al final
   de sus notas originales de creación de los cuatro contenedores
   gateway (`Proyecto-default.md`, `Proyecto-PRJ-OSS.md`,
   `Clúster/Firewall.md`) — podría revelar un problema real ya conocido
   por él que no llegó a documentarse en detalle.
5. **Si corresponde iniciar ya el trámite formal de alta de servicio**
   para este puerto/IP, en paralelo a la implementación técnica (mismo
   circuito ya usado para PFR1, CAR1 y FDO1 — `docs/11_Riesgos.md`
   RIE-009).

---

## 8. Addendum (2026-07-30) — Norberto respondió el punto 1 en la reunión del 2026-07-28

La reunión `reunion/LXD - Configuración FDO.vtt` (2026-07-28), procesada
el 2026-07-30, responde directamente el punto 1 de la lista anterior
("¿el mecanismo pensado era realmente `forward-port`/DNAT de firewalld?").
Respuesta de Norberto: sí, pero **no es un DNAT directo del gateway hacia
Kanboard** como asumía la inferencia de la sección 7 — es un modelo de
**dos etapas**: el gateway reenvía (`firewall-cmd --add-forward-port`)
hacia un contenedor **balanceador** dedicado (Apache como proxy reverso),
y es ese balanceador quien enruta por URL/path hacia el contenedor de
Kanboard. El balanceador también centraliza el certificado TLS.

Queda documentado como decisión oficial en
[`docs/adr/ADR-0008-gateway-balanceador-dos-etapas.md`](../../docs/adr/ADR-0008-gateway-balanceador-dos-etapas.md),
con el diagrama en
[`docs/02_Arquitectura.md`](../../docs/02_Arquitectura.md) y los comandos
de referencia en
[`docs/05_Configuracion.md`](../../docs/05_Configuracion.md).

🔴 La sintaxis exacta del `--add-forward-port` usada en la demostración no
quedó del todo clara en el audio — sigue pendiente confirmarla antes de
aplicar el mecanismo real a `PFR-OSS-GW-SRV` para publicar Kanboard (ver
el pendiente en el propio ADR-0008). Los puntos 2 a 5 de la lista
anterior **siguen sin respuesta** — no se tocaron en esa reunión.
