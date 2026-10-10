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

## RIE-001b — Configuración de WireGuard no persistida (riesgo de pérdida del enlace inter-sitio) *(✅ Resuelto)*

| Campo | Detalle |
|---|---|
| **Descripción** | Durante la reunión, la dirección IP de la interfaz WireGuard en PFR1 y CAR1 se había configurado manualmente (`ip addr add`), sin persistirla en `netplan` |
| **Causa** | Falta de tiempo para completar la configuración persistente durante la demostración |
| **Impacto (mientras estuvo vigente)** | Si el host se reiniciaba, la interfaz WireGuard perdía su IP y el enlace entre sitios (y por lo tanto la red OVN entre ellos) quedaba caído hasta reconfigurar manualmente |
| **Severidad** | Alta (mientras estuvo sin resolver) |
| **Estado actual** | ✅ Resuelto — confirmado en [`onenote/Clúster-OSS/Clúster/Netplan.md`](../onenote/Clúster-OSS/Clúster/Netplan.md): tanto PFR1 como CAR1 tienen el túnel `wg0` (dirección IP, clave privada, puerto, peer y rutas) definido dentro de `/etc/netplan/00-installer-config.yaml` como bloque `tunnels:`, y aplicado con `netplan try`. Esto sí sobrevive un reinicio |
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

## RIE-002 — Dos de tres nodos activos (alta disponibilidad de base de datos incompleta) *(🟡 posiblemente resuelto)*

| Campo | Detalle |
|---|---|
| **Descripción** | PFR1 y CAR1 están instalados y forman parte del cluster (roles `database-leader` y `database-standby`). Falta un tercer miembro para completar el quórum de alta disponibilidad de la base de datos distribuida (Dqlite) |
| **Causa** | FDO1 (Fernando) está pendiente de instalación |
| **Impacto** | Si PFR1 o CAR1 fallan, el cluster puede seguir operando con el nodo restante pero **sin margen de tolerancia a una segunda falla**. El quórum de escritura pleno recién se alcanza con 3 miembros |
| **Severidad** | Media-Alta — mejoró respecto del estado de un solo nodo, pero la HA real sigue incompleta |
| **Mitigación actual** | Backup de VM en VMware (solicitar a SBA/AIT); gestión posible desde cualquiera de los dos nodos activos gracias a la base de datos replicada |
| **Acción requerida** | Instalar LXD en FDO1 y agregarlo al cluster. Ver [04_Instalacion.md](04_Instalacion.md) |
| **Responsable** | Norberto Núñez + equipo técnico |

> **Actualización 2026-10-06 (verificación en vivo, solo lectura, por SSH a los 3 hosts):** ✅ `lxc cluster list` muestra los 3 miembros (`pfr.1` database-leader, `car.1` y `fdo.1` database) en estado `ONLINE` — el tercer miembro del quórum ya está incorporado. 🟡 Esto sugiere que este riesgo está resuelto, pero no fue confirmado formalmente con el equipo/Norberto Núñez (quién lo completó, cuándo). Ver el detalle de la verificación en [`laboratorio/2026-10-06_verificacion-viva-cluster/`](../laboratorio/2026-10-06_verificacion-viva-cluster/).

---

## RIE-003 — Proxy HTTP temporal con dependencia externa *(parcialmente vigente)*

| Campo | Detalle |
|---|---|
| **Descripción** | Los contenedores acceden a internet via proxy HTTP corporativo, habilitado temporalmente por el equipo de seguridad |
| **Causa** | En sitios sin OVN funcional se sigue usando el dispositivo proxy LXD por contenedor como workaround. En PFR1 y CAR1 (con OVN ya funcional) el workaround se reemplazó por un contenedor gateway dedicado de operación y mantenimiento — ver [05_Configuracion.md](05_Configuracion.md) — pero la dependencia del proxy corporativo en sí sigue existiendo |
| **Impacto** | Si el equipo de seguridad deshabilita el proxy, los contenedores pierden acceso a internet (no pueden instalar paquetes). La duración del permiso no fue confirmada |
| **Severidad** | Media |
| **Mitigación actual** | Nicolás (seguridad) habilitó el proxy en PFR1/CAR1. Marcos debe confirmar si es permanente. Para FDO1, mientras no tiene autorización propia, se implementó un puente NAT temporal que reutiliza el permiso de Franco — ver [05_Configuracion.md — Puente NAT temporal hacia el proxy SDI](05_Configuracion.md#puente-nat-temporal-hacia-el-proxy-sdi-para-sitios-sin-autorización-propia) |
| **Acción requerida** | Confirmar con Nicolás la permanencia del acceso al proxy para PFR1/CAR1, y tramitar el alta propia de FDO1 para poder desmontar el puente NAT temporal (ver rollback en 05_Configuracion.md). Repetir el patrón de gateway de operación y mantenimiento en FDO1 cuando se incorpore |
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

> **Actualización 2026-10-08:** ✅ Primer caso concreto resuelto — Kanboard tiene ahora snapshot automático (LXD nativo, cada 6h, expiración 7 días) + copia cruzada a otro sitio (`car.1`), probado de punta a punta incluyendo arranque de la copia y verificación de que sirve la aplicación correctamente. Ver [`laboratorio/2026-10-08_backup-dr-kanboard/`](../laboratorio/2026-10-08_backup-dr-kanboard/). 🔴 **Sigue pendiente:** este riesgo es a nivel de todo el cluster (VMs, otros contenedores) — Kanboard es solo el primer servicio cubierto, no una solución general. Además, la automatización de la copia cruzada para Kanboard específicamente quedó bloqueada por falta de `cron`/`Linger` en el host `pfr-oss` — requiere una acción puntual de alguien con acceso root (`apt-get install cron` o `loginctl enable-linger`).
| **Responsable** | Marcos Casco → SBA/AIT |

---

## RIE-007 — IP de proxy HTTP sin confirmar *(✅ Resuelto)*

| Campo | Detalle |
|---|---|
| **Descripción** | Durante la reunión hubo confusión entre `31.100` y `32.x.x.x` al mencionar de memoria la IP del proxy HTTP corporativo |
| **Impacto (mientras estuvo vigente)** | Si la IP configurada era incorrecta, los contenedores no podían acceder a internet |
| **Severidad** | Baja (detectable fácilmente) |
| **Estado actual** | ✅ Confirmado: `10.150.32.100:3128` (alias interno "proxy SDI"). Ver [`onenote/Clúster-OSS/Clúster/Proxy.md`](../onenote/Clúster-OSS/Clúster/Proxy.md) y [05_Configuracion.md](05_Configuracion.md) |
| **Responsable** | Equipo técnico → Nicolás |

---

## RIE-008 — IPs de operadores en firewall sin validar *(✅ Resuelto)*

| Campo | Detalle |
|---|---|
| **Descripción** | Las IPs de los operadores (Daniel, Rocío) agregadas al firewall habían sido capturadas parcialmente durante la reunión (la transcripción VTT no capturó las IPs completas) |
| **Impacto (mientras estuvo vigente)** | Si las IPs del firewall eran incorrectas, los operadores no podían acceder a la Web UI |
| **Severidad** | Baja |
| **Estado actual** | ✅ Confirmadas las 4 IPs (Norberto, Rocío, Daniel, Elías) — ver [04_Instalacion.md — Paso 6](04_Instalacion.md) y [`onenote/Clúster-OSS/Clúster/Firewall.md`](../onenote/Clúster-OSS/Clúster/Firewall.md). El riesgo estructural de fondo (reglas por IP individual en lugar de por identidad/VPN) sigue siendo una limitación de diseño — ver recomendación A-08 en [15_Revision_Arquitectonica.md](15_Revision_Arquitectonica.md) |
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

## RIE-010 — Arranque más lento en Ubuntu 26.04 LTS por causa no identificada

| Campo | Detalle |
|---|---|
| **Descripción** | Durante la reunión, Norberto Núñez notó que un contenedor con Ubuntu 26.04 LTS tardaba más en completar su arranque/`cloud-init` que uno equivalente en Ubuntu 24.04 LTS |
| **Causa** | 🔴 **No identificada con precisión.** Norberto mencionó al pasar un servicio nuevo relacionado con "console" como posible responsable, pero explícitamente no supo confirmar cuál era exactamente ("no sé cuál es exactamente") |
| **Impacto** | Contenedores creados desde imágenes de Ubuntu 26.04 LTS pueden tardar más de lo esperado en estar listos — riesgo de falsos negativos si se verifica `cloud-init status` demasiado pronto |
| **Severidad** | Baja — no bloquea el trabajo, pero puede generar confusión operativa si no se conoce de antemano |
| **Mitigación actual** | Usar `cloud-init status --wait` en lugar de una sola verificación puntual, para no asumir una falla antes de que el arranque termine |
| **Acción requerida** | Investigar la causa raíz exacta (posible candidato: un servicio systemd nuevo en 26.04 relacionado con la consola) la próxima vez que se cree un contenedor con esta versión |
| **Responsable** | Norberto Núñez |

---

## RIE-011 — Sesiones del balanceador sin replicar (failover puede desloguear usuarios)

| Campo | Detalle |
|---|---|
| **Descripción** | El estado de sesión de los servicios web publicados detrás del contenedor balanceador (Apache, ver [ADR-0008](adr/ADR-0008-gateway-balanceador-dos-etapas.md)) se guarda en archivos temporales locales del contenedor, no en un almacén compartido |
| **Causa** | Todavía no se implementó un mecanismo de sesiones compartidas/replicadas entre las instancias balanceadas |
| **Impacto** | Si ocurre un failover (el balanceador redirige tráfico a otra instancia, o el contenedor se reinicia), los usuarios con sesión activa quedan deslogueados |
| **Severidad** | Media — no bloquea la operación normal, pero degrada la experiencia en cada evento de failover |
| **Mitigación actual** | Ninguna |
| **Acción requerida** | Evaluar un mecanismo de sesiones compartidas (ej. almacén de sesiones centralizado) para los servicios detrás del balanceador. Identificado explícitamente por el equipo como "desafiante" — 🔴 sin propuesta técnica concreta todavía |
| **Responsable** | Pendiente de asignar |

---

## RIE-012 — Sin estrategia definida de réplica/centralización de base de datos entre los 3 sitios

| Campo | Detalle |
|---|---|
| **Descripción** | No hay una decisión tomada sobre cómo replicar o centralizar las bases de datos de aplicación (no la base de datos interna del cluster LXD/Dqlite, que ya se replica — ver RIE-002) entre los servicios de los 3 sitios |
| **Causa** | Tema identificado como pendiente de investigación durante una reunión de trabajo, sin desarrollo posterior. La responsabilidad de la replicación es de quien diseña cada servicio, no de LXD — ver [09_FAQ.md](09_FAQ.md#sobre-exposición-de-servicios-y-bases-de-datos) — pero falta la definición concreta para los servicios que sí requieran alta disponibilidad multi-sitio |
| **Impacto** | Sin definición, cada servicio nuevo puede terminar con una estrategia de datos distinta e inconsistente entre sitios, dificultando la alta disponibilidad real a nivel de aplicación |
| **Severidad** | Media — no bloquea el trabajo actual, pero condiciona el diseño de cualquier servicio con estado que se despliegue en más de un sitio |
| **Mitigación actual** | Ninguna |
| **Acción requerida** | Investigar y definir una estrategia (ej. réplica maestro-réplica, centralización en un único sitio) antes de desplegar el primer servicio con datos que requiera alta disponibilidad multi-sitio |
| **Responsable** | Pendiente de asignar |

---

## RIE-013 — Interfaz OVN bloqueada en Fernando, causa raíz no identificada *(🟡 posiblemente resuelto)*

| Campo | Detalle |
|---|---|
| **Descripción** | Tras unir Fernando (FDO1) al cluster OVN, la interfaz `OVN_1` no levanta en ese nodo, aunque todos los servicios de MicroOVN aparecen `running`. Ver diagnóstico completo en [TRB-012 en 07_Troubleshooting.md](07_Troubleshooting.md#trb-012) |
| **Causa** | 🔴 No identificada. Hipótesis sin confirmar: estado inconsistente en la base de datos de OVN, posiblemente de un primer intento de join fallido |
| **Impacto** | Fernando no puede alojar contenedores conectados a la red OVN del cluster — bloquea completar la incorporación del tercer sitio y, con ella, el quórum pleno de alta disponibilidad (ver [RIE-002](#rie-002--dos-de-tres-nodos-activos-alta-disponibilidad-de-base-de-datos-incompleta)) |
| **Severidad** | Alta — bloqueante activo para completar la incorporación de FDO1 |
| **Mitigación actual** | Ninguna. Franco y Carpinelli siguen operando con OVN funcional entre ambos |
| **Acción requerida** | Continuar el diagnóstico (sesión siguiente): confirmar o descartar la hipótesis de estado inconsistente; si se confirma, remover a Fernando del cluster OVN y volver a unirlo desde cero |
| **Responsable** | Norberto Núñez |

> 🟡 **Actualización (reunión OSS, agosto):** se encontró y corrigió un error de configuración de WireGuard en Fernando (claves de peer invertidas, `allowed-ips` demasiado amplio — ver [TRB-013](07_Troubleshooting.md#trb-013--peer-de-wireguard-mal-configurado-claves-invertidas-o-allowed-ips-demasiado-amplio-bloquea-rutas-entre-sitios)) que produce exactamente el síntoma de este riesgo. Es una hipótesis razonable, no confirmada, que sea la misma causa raíz — falta re-verificar si la interfaz OVN de Fernando levanta correctamente ahora que ese error de WireGuard está corregido.

> **Actualización 2026-10-06 (verificación en vivo, solo lectura, por SSH a los 3 hosts):** ✅ Se observó el contenedor de aplicación `FDO-WS-1` **corriendo en `fdo.1`** con IP `192.168.0.110` en la red `OVN_1` (proyecto `PRJ-OSS`) — evidencia directa de que Fernando sí puede alojar contenedores conectados a OVN. 🟡 Esto es consistente con la hipótesis de la nota anterior: lo más probable es que la corrección del bug de WireGuard (TRB-013) haya resuelto también este bloqueo de OVN, ya que ambos dependen del mismo transporte underlay entre sitios. 🔴 Pero esto sigue sin confirmarse explícitamente — no se pudo revisar el estado interno de MicroOVN (`microovn status` requirió una contraseña de `sudo` que la cuenta de la verificación no tiene), y nadie del equipo lo validó formalmente. Pendiente de confirmar con Norberto Núñez antes de cerrar este riesgo y [TRB-012](07_Troubleshooting.md#trb-012) como resueltos. Ver el detalle completo en [`laboratorio/2026-10-06_verificacion-viva-cluster/`](../laboratorio/2026-10-06_verificacion-viva-cluster/).

---

## RIE-014 — Overcommit de memoria sin alerta entre perfiles LXD

| Campo | Detalle |
|---|---|
| **Descripción** | LXD permite que la suma de `limits.memory` de todos los perfiles/instancias de un nodo supere la memoria RAM física del host, sin advertencia — ej. un servidor con 16 GB físicos con 20 instancias a 2 GB cada una (40 GB asignados) |
| **Causa** | Comportamiento por diseño de LXD: los límites de un perfil son un techo por instancia, no una reserva garantizada ni una validación contra la capacidad total del host |
| **Impacto** | Mientras el uso real de memoria de las instancias esté por debajo de la capacidad física, no hay problema. Si el uso real se acerca o supera la RAM física del host, puede degradar el rendimiento del nodo o forzar al kernel a matar procesos (OOM) de forma impredecible |
| **Severidad** | Media — no es un problema activo, pero crece con cada instancia nueva sin que LXD avise |
| **Mitigación actual** | Ninguna automática. Revisión manual de la suma de `limits.memory` de los perfiles activos en cada nodo |
| **Acción requerida** | Antes de asignar un perfil nuevo, verificar manualmente que la suma de memoria de todos los perfiles activos en ese nodo no supere la RAM física disponible. Evaluar a futuro alguna forma de alerta o límite agregado por nodo |
| **Responsable** | Equipo técnico |

---

## RIE-015 — Conectividad de VulnApp NG hacia la API de SDI bloqueada

| Campo | Detalle |
|---|---|
| **Descripción** | El contenedor `PFR-VULNAPP-APP` (`192.168.0.14`) no puede alcanzar `10.150.58.116:443` (API de SDI, de donde la aplicación debe traer datos todos los días) |
| **Causa** | 🔴 No identificada con certeza. Se descartó que sea un problema de este cluster: la ruta existe (`ip route get 10.150.58.116` devuelve una ruta válida vía `192.168.0.6`) y la regla de `ACL-OVN-1` que permite ese tráfico está `enabled` (ver [05_Configuracion.md — Firewall de la red OVN_1](05_Configuracion.md#firewall-de-la-red-ovn_1-lxc-network-acl)). El fallo (`No route to host`) ocurre después de `192.168.0.6`, fuera de lo administrado por este cluster — hipótesis más probable: la IP con la que el cluster sale hacia esa red todavía no está habilitada del lado de Seguridad/Redes para ese destino puntual, mientras que sí lo está para la pasarela de SMS (`10.150.31.68:80`, que conecta sin problema desde el mismo contenedor) |
| **Impacto** | VulnApp NG no puede ejecutar su carga diaria de datos desde SDI — queda instalada y accesible, pero sin la función que la hace útil día a día |
| **Severidad** | Media-Alta — bloquea una función ya planificada y pendiente de activar, no una falla de algo que ya funcionaba |
| **Mitigación actual** | Ninguna. El servicio de carga (`vulnapp-sdi.service`/`.timer`) no se instaló ni se activó a propósito, para no insistir contra un destino que todavía rechaza la conexión |
| **Acción requerida** | Pedir a Seguridad/Redes que confirme qué IP ven en el destino `10.150.58.116:443` cuando el tráfico sale de este cluster, y que habiliten esa IP si todavía no lo está. Una vez confirmado, repetir la prueba de conectividad desde `PFR-VULNAPP-APP` antes de instalar el servicio de carga |
| **Responsable** | Pendiente de asignar (Seguridad/Redes) |

Ver el detalle de la prueba realizada en [`laboratorio/2026-10-09_alta-vulnapp-ng/bitacora.md`](../laboratorio/2026-10-09_alta-vulnapp-ng/bitacora.md#7-alcance-hacia-sdi-y-hacia-la-pasarela-de-sms-sin-ejecutar-03_instalar_cargash).

---

## Resumen de severidades

| Severidad | Riesgos |
|---|---|
| **Alta** | RIE-004 (CentOS 7 EOL) |
| **Media-Alta** | RIE-006 (sin backup), RIE-015 (conectividad SDI de VulnApp NG bloqueada) |
| **Media** | RIE-001c (mesh WireGuard manual), RIE-003 (proxy temporal), RIE-005 (sin VPN), RIE-011 (sesiones balanceador), RIE-012 (réplica BD entre sitios), RIE-014 (overcommit de memoria) |
| **Baja** | RIE-009 (alta de servicio CAR1), RIE-010 (arranque lento Ubuntu 26.04) |
| **Resuelto** | RIE-001 (OVN entre PFR1 y CAR1), RIE-001b (WireGuard persistido en netplan), RIE-007 (IP de proxy confirmada), RIE-008 (IPs de operadores confirmadas) |
| **🟡 Posiblemente resuelto (pendiente confirmación formal)** | RIE-002 (3/3 nodos `ONLINE`, verificado en vivo 2026-10-06), RIE-013 (contenedor corriendo sobre `OVN_1` en Fernando, verificado en vivo 2026-10-06 — causa raíz original aún sin confirmar) |

---

## Documentos relacionados

| Tema | Documento |
|---|---|
| Plan de acción (próximos pasos) | [13_Linea_de_Tiempo.md](13_Linea_de_Tiempo.md) |
| Decisiones que generaron estos riesgos | [10_Decisiones.md](10_Decisiones.md) |
| Procedimientos de backup | [06_Operacion.md](06_Operacion.md) |
