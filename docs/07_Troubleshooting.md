# 07 — Troubleshooting

> **Audiencia:** Operadores e ingenieros de infraestructura.
> **Propósito:** Fichas de diagnóstico y resolución de problemas conocidos.

---

## TRB-001 — Cloud-init no instaló los paquetes

| Campo | Contenido |
|---|---|
| **Problema** | Los paquetes definidos en `user-data` no se instalaron en el contenedor |
| **Síntomas** | `cloud-init status` muestra `error` o el servicio esperado (ej: apache2) no está instalado. En logs aparece: `unhandled not multipart text x no multipart user data` |
| **Causa** | El bloque `user-data` en el perfil no tiene el header `#cloud-config` en la primera línea, o tiene formato YAML incorrecto |
| **Diagnóstico** | `lxc exec CONTENEDOR -- cat /var/log/cloud-init.log \| grep -i error` |
| **Solución** | 1. Corregir el perfil: asegurar que `user-data` empiece exactamente con `#cloud-config`. 2. Detener y eliminar el contenedor. 3. Recrearlo. |
| **Prevención** | Siempre incluir `#cloud-config` como primera línea del bloque `user-data`. Validar el YAML antes de crear el contenedor. |

### Configuración correcta

```yaml
config:
  cloud-init.user-data: |
    #cloud-config
    package_update: true
    package_upgrade: true
    packages:
      - apache2
```

---

## TRB-002 — Cloud-init no re-ejecuta cambios tras modificar el perfil

| Campo | Contenido |
|---|---|
| **Problema** | Se modifica la configuración de cloud-init en el perfil, se reinicia el contenedor, pero los cambios no se aplican |
| **Síntomas** | El paquete nuevo no está instalado, el archivo esperado no existe |
| **Causa** | Cloud-init se ejecuta **solo en el primer arranque**. Reiniciar el contenedor no lo re-ejecuta. |
| **Diagnóstico** | `lxc exec CONTENEDOR -- cloud-init status` — si muestra `done`, cloud-init ya terminó y no volverá a ejecutarse |
| **Solución** | 1. Modificar el perfil con la configuración correcta. 2. Detener el contenedor. 3. Eliminarlo. 4. Recrearlo. |
| **Prevención** | Probar la configuración de cloud-init antes de crear el contenedor en producción. Usar `laboratorio/` para experimentos. |

---

## TRB-003 — Dispositivo proxy con dirección invertida

| Campo | Contenido |
|---|---|
| **Problema** | El contenedor no accede a internet a través del proxy, o el proxy device no funciona |
| **Síntomas** | `curl http://google.com` dentro del contenedor falla. El dispositivo está configurado con `bind: host` cuando debería ser `bind: instance` |
| **Causa** | `bind` define en qué lado (host vs contenedor) está el socket `listen`. Es fácil invertirlos. |
| **Diagnóstico** | `lxc config device show CONTENEDOR` — verificar los valores de `bind`, `listen` y `connect` |
| **Solución** | Corregir el dispositivo: `bind: instance` cuando el socket que escucha está DENTRO del contenedor, `bind: host` cuando está en el HOST. |
| **Prevención** | Recordar la regla: **`bind` = dónde está el socket `listen`**. |

### Referencia rápida

| Caso de uso | bind | listen | connect |
|---|---|---|---|
| Contenedor → proxy internet | `instance` | `tcp:127.0.0.1:3128` | `tcp:IP_PROXY:3128` |
| Exterior → servicio del contenedor | `host` | `tcp:IP_VM:80` | `tcp:127.0.0.1:80` |

---

## TRB-004 — Certificado de navegador rechazado (acceso a Web UI)

| Campo | Contenido |
|---|---|
| **Problema** | El navegador bloquea el acceso a la Web UI porque rechazó el certificado TLS en un intento anterior |
| **Síntomas** | El navegador muestra "certificado no confiable" y no permite continuar, incluso después de generar el certificado correcto |
| **Causa** | El navegador guardó en caché el rechazo del certificado anterior |
| **Diagnóstico** | Intentar acceder en modo incógnito — si funciona, el problema es el caché del certificado |
| **Solución** | Acceder a la Web UI en **modo incógnito**. Desde ahí, generar el certificado, instalarlo y luego acceder normalmente. |
| **Prevención** | La primera vez que se accede a la Web UI, hacerlo siempre en modo incógnito. |

---

## TRB-005 — Contenedor sin acceso a internet (APT falla)

| Campo | Contenido |
|---|---|
| **Problema** | APT no puede descargar paquetes dentro del contenedor |
| **Síntomas** | `apt update` falla con error de conexión. Cloud-init no instala paquetes. |
| **Causa** | El contenedor no tiene ruta a internet. Puede ser: proxy no configurado, dispositivo proxy no agregado al perfil, o proxy HTTP con IP incorrecta |
| **Diagnóstico** | `lxc exec CONTENEDOR -- curl -x http://127.0.0.1:3128 https://archive.ubuntu.com` |
| **Solución** | 1. Verificar que el dispositivo proxy está en el perfil. 2. Verificar IP del proxy (`lxc config get core.http_proxy`). 3. Si OVN está disponible, verificar configuración de red OVN. |
| **Prevención** | Configurar el proxy HTTP antes de crear contenedores. Verificar acceso a internet inmediatamente después de crear el primer contenedor. |

---

## TRB-006 — Nodo del cluster en estado OFFLINE

| Campo | Contenido |
|---|---|
| **Problema** | `lxc cluster list` muestra un nodo como `OFFLINE` |
| **Síntomas** | El nodo no responde. Los contenedores asignados a ese nodo no están accesibles. |
| **Causa** | Puede ser: VM apagada, LXD daemon detenido, problema de red, o partición del cluster |
| **Diagnóstico** | 1. SSH al nodo: ¿responde? 2. `snap services lxd` en el nodo: ¿está `active`? 3. Verificar conectividad: `ping IP_NODO` desde otro nodo |
| **Solución** | 1. Si la VM está apagada: encenderla. 2. Si LXD está detenido: `snap restart lxd`. 3. Si no hay conectividad: problema de red — escalar a SBA/AIT |
| **Prevención** | Monitorear el estado del cluster con Prometheus/Grafana. Solicitar backup de VMs. |

---

## TRB-007 — Falla de ZFS pool

| Campo | Contenido |
|---|---|
| **Problema** | El pool ZFS del nodo tiene errores o está DEGRADED/FAULTED |
| **Síntomas** | `zpool status` muestra estado diferente a `ONLINE`. Los contenedores del nodo pueden no iniciar. |
| **Causa** | Falla de disco, corrupción de datos, o error de configuración |
| **Diagnóstico** | `zpool status` — ver estado del pool y discos |
| **Solución** | Si hay backup de VM: solicitar restauración a SBA/AIT. Si no: escalar a SBA/AIT con `zpool status` output. |
| **Prevención** | Solicitar backup de VM a SBA/AIT antes de comenzar a crear contenedores en producción. |

---

## TRB-008 — No se puede acceder a la Web UI (error de conexión)

| Campo | Contenido |
|---|---|
| **Problema** | El navegador no puede conectar a `https://IP:8443` |
| **Síntomas** | Timeout de conexión o "Conexión rechazada" |
| **Causa** | Puede ser: LXD no está corriendo, firewall bloqueando la IP del operador, o acceso desde fuera de la red local (sin VPN) |
| **Diagnóstico** | 1. `snap services lxd` en el nodo: verificar que está activo. 2. `firewall-cmd --list-rich-rules`: verificar que la IP del operador tiene acceso a 8443-8444. |
| **Solución** | Si LXD no corre: `snap restart lxd`. Si falta la regla de firewall: agregar rich rule con la IP del operador. Si está fuera de la red local: 🔴 VPN no disponible aún. |
| **Prevención** | Documentar las IPs de todos los operadores y verificarlas al configurar el firewall. |

---

## TRB-009 — Cluster con bloqueos intermitentes (desincronización de reloj)

| Campo | Contenido |
|---|---|
| **Problema** | Operaciones de configuración del cluster (crear contenedor, editar perfil, migrar, etc.) fallan o se bloquean de forma intermitente y sin un patrón claro |
| **Síntomas** | En la Web UI aparecen indicadores en rojo/error sin razón evidente. A veces la operación se permite, a veces no, para la misma acción repetida |
| **Causa** | Diferencia de reloj entre nodos del cluster (aunque sea de 1-2 segundos). LXD y MicroOVN usan Dqlite, que depende de la hora de cada nodo para coordinar la sincronización de la base de datos distribuida. Norberto Núñez reportó haber vivido este problema en una implementación previa |
| **Diagnóstico** | `timedatectl` en cada nodo — comparar la hora entre todos los miembros del cluster |
| **Solución** | Configurar NTP (`systemd-timesyncd`) apuntando a los mismos servidores NTP en todos los nodos. Ver [04_Instalacion.md — Paso 10](04_Instalacion.md) |
| **Prevención** | Configurar NTP como parte obligatoria de la instalación de cada nodo, **antes** de unirlo al cluster. Aplicar la misma configuración a los contenedores gateway de servicios |

---

## TRB-010 — Cluster bloqueado por versiones de snap distintas entre nodos

| Campo | Contenido |
|---|---|
| **Problema** | No se pueden hacer cambios de configuración en el cluster (crear contenedores, editar perfiles, etc.) |
| **Síntomas** | En `lxc cluster list` o en la Web UI, uno o más nodos aparecen marcados (ej. en rojo) con una versión de LXD distinta a la de los demás. Los contenedores en ejecución siguen funcionando con normalidad — el bloqueo es solo sobre operaciones de configuración |
| **Causa** | `snapd` actualizó automáticamente LXD o MicroOVN en un nodo (comportamiento por defecto: revisa actualizaciones una vez por día) mientras los demás nodos quedaron en una versión anterior. LXD bloquea deliberadamente las operaciones de configuración para evitar incompatibilidades entre versiones distintas dentro del mismo cluster |
| **Diagnóstico** | `snap list lxd` en cada nodo — comparar versiones |
| **Solución** | Actualizar manualmente (`snap refresh lxd`) los nodos que quedaron atrás, hasta que todos tengan la misma versión |
| **Prevención** | Aplicar `snap refresh --hold` en todos los nodos inmediatamente después de la instalación (ver [04_Instalacion.md](04_Instalacion.md)). Actualizar siempre de forma manual y coordinada en todos los nodos el mismo día |

---

## TRB-011 — Contenedor sin ruta por defecto (conectividad entrante rota)

| Campo | Contenido |
|---|---|
| **Problema** | Un contenedor con IP fija (ej. el balanceador, ver [ADR-0008](adr/ADR-0008-gateway-balanceador-dos-etapas.md)) no responde a peticiones externas, aunque el firewall esté correctamente configurado |
| **Síntomas** | `curl`/petición desde otro contenedor o desde el gateway no obtiene respuesta ni error explícito — simplemente no hay conectividad. El servicio (ej. Apache) está corriendo y escuchando en el puerto esperado |
| **Causa** | Falta la ruta por defecto (`default gateway`) en la configuración de red del contenedor (`cloud-init.network-config` / Netplan). Puede deberse a haberla omitido al escribir la configuración, o a un error de indentación en el YAML de Netplan — Ubuntu exige alineación estricta de bloques; una línea mal alineada se interpreta silenciosamente como parte de otro grupo, sin generar un error visible |
| **Diagnóstico** | `lxc exec CONTENEDOR -- ip route` — si no aparece ninguna línea `default via ...`, esta es la causa |
| **Solución** | Temporal (no persiste un reinicio): `lxc exec CONTENEDOR -- ip route add default via IP_GATEWAY`. Definitiva: agregar el bloque `routes: - to: default via: IP_GATEWAY` dentro de `cloud-init.network-config` en el perfil, y recrear el contenedor (cloud-init solo corre en el primer arranque, ver [LL-003](12_Lecciones_Aprendidas.md#ll-003--cloud-init-se-ejecuta-solo-al-primer-arranque)) |
| **Prevención** | Incluir siempre la ruta por defecto al definir `cloud-init.network-config` de un contenedor con IP fija. Validar la indentación del YAML con cuidado antes de aplicar — un editor con resaltado de sintaxis YAML ayuda a detectar desalineaciones |

### Configuración correcta

```yaml
cloud-init.network-config: |
  #cloud-config
  version: 2
  ethernets:
    eth0:
      dhcp4: false
      addresses:
        - 192.168.0.11/24
      routes:
        - to: default
          via: 192.168.0.254
```

---

## TRB-012 — La interfaz OVN no levanta en un nodo nuevo aunque los servicios de MicroOVN estén "running" *(🟡 posiblemente resuelto)*

| Campo | Contenido |
|---|---|
| **Problema** | Después de unir un nuevo nodo al cluster OVN (`microovn cluster join`), el Open vSwitch se crea correctamente, pero la interfaz de red de OVN (`OVN_1`) no llega a levantarse en ese nodo |
| **Síntomas** | `ip -4 addr show` no muestra la interfaz OVN activa en el nodo nuevo. `microovn.chassis` y `snap services microovn` muestran todos los servicios como `running`/`active` — no hay ningún servicio caído que explique el fallo. Migrar o crear un contenedor con destino a ese nodo falla |
| **Causa** | 🔴 **No identificada.** Se descartó que fuera un servicio detenido (todo aparece corriendo). Se revisó el puerto 6081 (Geneve, tráfico de datos entre chassis OVN — ver [Paso 6 en 04_Instalacion.md](04_Instalacion.md#paso-6-configurar-firewall-firewalld)) sin encontrar la causa raíz antes de que se cortara la sesión |
| **Diagnóstico realizado hasta el momento** | `journalctl -xe` en el nodo nuevo; `microovn.chassis` (estado del chasis OVN); `ip -4 addr show` (confirma que el Open vSwitch existe pero la interfaz OVN no aparece); revisión de la rich-rule de firewall para el puerto 6081 UDP entre los miembros del cluster |
| **Hipótesis sin confirmar** | Estado inconsistente en la base de datos de OVN, posiblemente arrastrado de un primer intento de `microovn cluster join` fallido en el mismo nodo (join, error, y reintento sin limpiar el estado anterior) |
| **Solución** | 🔴 Pendiente. Próximo paso propuesto por Norberto Núñez: si se confirma la hipótesis de estado inconsistente, remover las referencias de ese miembro en la base de datos de OVN y volver a unirlo al cluster desde cero (`microovn cluster remove` + `microovn cluster add`/`join` nuevamente) |
| **Prevención** | Sin definir todavía — depende de identificar la causa raíz |

Ver el seguimiento de este bloqueo en el caso real (incorporación de FDO1/Fernando): [`laboratorio/2026-07-25_incorporacion-sitio-fdo1/bitacora.md`](../laboratorio/2026-07-25_incorporacion-sitio-fdo1/bitacora.md).

> 🟡 **Actualización (reunión OSS, agosto):** en una sesión posterior se encontró y corrigió un error de configuración de WireGuard (ver [TRB-013](#trb-013--peer-de-wireguard-mal-configurado-claves-invertidas-o-allowed-ips-demasiado-amplio-bloquea-rutas-entre-sitios) abajo) que produce exactamente este síntoma: rutas OVN entre sitios que no funcionan pese a que los servicios muestran `running`. Es una **hipótesis razonable, no confirmada**, de que sea la misma causa raíz de este TRB-012 en Fernando — hace falta revisar la configuración de WireGuard de `fdo-oss1` con el mismo criterio (claves de cada peer, `allowed-ips` específico) antes de reintentar el join.

> **Actualización 2026-10-06 (verificación en vivo, solo lectura):** ✅ Se observó el contenedor `FDO-WS-1` corriendo en `fdo.1` con IP en la red `OVN_1` — la interfaz OVN de Fernando parece estar operativa, consistente con la hipótesis de la nota anterior (la corrección de TRB-013 también habría resuelto este bloqueo). 🔴 Pero sigue sin confirmarse explícitamente: no se pudo correr `microovn status` sin contraseña de `sudo`, y nadie del equipo lo validó formalmente. Ver [RIE-013 en 11_Riesgos.md](11_Riesgos.md#rie-013--interfaz-ovn-bloqueada-en-fernando-causa-raíz-no-identificada-posiblemente-resuelto) y [`laboratorio/2026-10-06_verificacion-viva-cluster/`](../laboratorio/2026-10-06_verificacion-viva-cluster/).

---

## TRB-013 — Peer de WireGuard mal configurado (claves invertidas o `AllowedIPs` demasiado amplio) bloquea rutas entre sitios

| Campo | Contenido |
|---|---|
| **Problema** | Un contenedor no puede migrarse ni comunicarse a nivel de OVN con contenedores de otro sitio del cluster, aunque la malla WireGuard aparente estar activa |
| **Síntomas** | `wg show` puede mostrar el túnel activo, pero el tráfico OVN entre sitios específicos falla o se "tranca" de forma silenciosa (sin error explícito) al intentar una operación entre esos dos sitios en particular |
| **Causa** | Dos errores de configuración encontrados juntos en el mismo `netplan`: (1) las claves públicas de los peers estaban **invertidas** — la clave configurada para un peer en realidad correspondía a otro; (2) el campo `allowed-ips` de un peer tenía un rango demasiado amplio (`/0` en vez de la IP puntual `/32` de ese peer), lo que mete **todas** las rutas hacia esa IP dentro de la misma interfaz del túnel, en vez de solo la ruta específica hacia ese peer — confundiendo el enrutamiento cuando hay más de dos sitios en la malla |
| **Diagnóstico** | Revisar con `cat /etc/netplan/*.yaml` que: (a) cada `peers.keys.public` corresponda efectivamente a la clave pública del peer remoto correcto (no a otro peer de la lista); (b) cada `peers.allowed-ips` sea la IP interna puntual de ESE peer (`/32`), nunca un rango amplio como `/0` |
| **Solución** | Corregir el `netplan`: asignar cada clave pública al peer correcto, y dejar `allowed-ips` como la IP `/32` puntual de cada peer. Aplicar con `netplan try`/`netplan apply` y verificar con `wg show` que el *handshake* siga vigente tras el cambio |
| **Prevención** | Al agregar un nuevo peer (ver [04_Instalacion.md — Paso 4](04_Instalacion.md#paso-4-configurar-wireguard-como-transporte-underlay-entre-sitios)), revisar explícitamente que la clave pública y el `allowed-ips` copiados correspondan al peer correcto — con 3+ sitios es fácil copiar/pegar la entrada equivocada. Ver [LL-020 en 12_Lecciones_Aprendidas.md](12_Lecciones_Aprendidas.md#ll-020--en-wireguard-allowed-ips-va-la-ip-puntual-del-peer-nunca-un-rango-amplio) |

**Estado al cierre de la reunión:** ✅ Corregido en el `netplan` de Fernando (en vivo, durante la demostración). 🔴 **Pendiente aplicar la misma corrección en Franco** — quedó como tarea explícita para el equipo. También quedaron entradas de rutas locales obsoletas por limpiar en los tres nodos (`allowed-ips` residual con `/0`).

---

## Comandos de diagnóstico rápido

```bash
# Estado del cluster:
lxc cluster list

# Estado del daemon LXD:
snap services lxd

# Logs de LXD:
snap logs lxd

# Estado del pool ZFS:
zpool status

# Estado del firewall:
firewall-cmd --state
firewall-cmd --list-rich-rules

# Verificar cloud-init en contenedor:
lxc exec CONTENEDOR -- cloud-init status
lxc exec CONTENEDOR -- cat /var/log/cloud-init-output.log

# Verificar servicios en contenedor:
lxc exec CONTENEDOR -- ss -ntlp

# Verificar estado de MicroOVN:
snap services microovn
microovn cluster list

# Verificar estado del túnel WireGuard (transporte entre sitios):
wg show

# Verificar sincronización de reloj (NTP):
timedatectl

# Verificar si hay actualizaciones automáticas pendientes de snap:
snap refresh --list
```

---

## Documentos relacionados

| Tema | Documento |
|---|---|
| Configuración de cloud-init y proxy | [05_Configuracion.md](05_Configuracion.md) |
| Operación normal | [06_Operacion.md](06_Operacion.md) |
| Manual operativo con checklist de salud | [14_Manual_Operativo.md](14_Manual_Operativo.md) |
