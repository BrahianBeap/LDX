# 05 — Configuración del sistema

> **Audiencia:** Ingenieros de infraestructura y operadores del cluster.
> **Propósito:** Documentar todos los parámetros y configuraciones del sistema: proxy, cloud-init, perfiles, dispositivos y firewall. No incluye instalación (ver [04_Instalacion.md](04_Instalacion.md)).

---

## Proxy HTTP de LXD

### ¿Qué controla?
El proxy HTTP que LXD usa para comunicarse con internet: descargar imágenes de contenedores, actualizaciones, etc.

### Parámetros

✅ Confirmado (fuente: [`onenote/Clúster-OSS/Clúster/Proxy.md`](../onenote/Clúster-OSS/Clúster/Proxy.md)) — el proxy corporativo (alias interno "SDI") es `10.150.32.100:3128`.

> **Corrección de nombre de parámetro** — ✅ confirmado visualmente en la grabación de la reunión (`reunion/Llamada con Daniel y 3 personas más-20260625_105957-Grabación de la reunión.mp4`, min ~01:23, output real de `lxc config show`) y contrastado con la documentación oficial de LXD (página "Server configuration" abierta en pantalla durante la reunión): el nombre correcto de la clave es `core.proxy_http` / `core.proxy_https` (proxy primero, protocolo después) — **no** `core.http_proxy`/`core.https_proxy` como figuraba antes en este documento. Con el nombre incorrecto, `lxc config set` crea una clave de configuración nueva e inerte en lugar de fallar con error, por lo que el proxy queda sin efecto de forma silenciosa.

| Parámetro | Archivo/Comando | Función | Valor |
|---|---|---|---|
| `core.proxy_http` | `lxc config set` | Proxy para tráfico HTTP de LXD | `http://10.150.32.100:3128` |
| `core.proxy_https` | `lxc config set` | Proxy para tráfico HTTPS de LXD | `http://10.150.32.100:3128` |
| `core.proxy_ignore_hosts` | `lxc config set` | Hosts/redes sin proxy (acceso directo) | `10.0.0.0/8,192.168.0.0/16,172.16.0.0/12,169.254.0.0/16` |

### Configuración completa en el host (APT, snap y LXD)

El mismo proxy debe configurarse en tres capas independientes del host — configurar solo `core.http_proxy` de LXD **no** alcanza para que `apt` o `snap` funcionen:

```bash
proxy_sdi=http://10.150.32.100:3128
no_proxy=10.0.0.0/8,192.168.0.0/16,172.16.0.0/12,169.254.0.0/16

# APT
cat > /etc/apt/apt.conf.d/99proxy.conf <<HERE
Acquire::http::Proxy "$proxy_sdi";
Acquire::https::Proxy "$proxy_sdi";
HERE

# SNAP
snap set system proxy.http=$proxy_sdi
snap set system proxy.https=$proxy_sdi

# LXD
lxc config set core.proxy_http  $proxy_sdi
lxc config set core.proxy_https $proxy_sdi
lxc config set core.proxy_ignore_hosts $no_proxy
```

> **Nota:** en el video de la reunión, el primer intento se hizo con `lxc config set core.proxy_http=http://...` (signo `=`) y no tuvo efecto — hubo que repetirlo con espacio en lugar de `=` (`lxc config set core.proxy_http http://...`) para que la clave se aplicara correctamente.

> **Nota:** `no_proxy`/`core.proxy_ignore_hosts` excluye todo el rango de redes privadas RFC1918 y el rango link-local (usado por WireGuard, ver [ADR-0006](adr/ADR-0006-wireguard-underlay-ovn-multisitio.md)) para que el tráfico interno del cluster no intente salir por el proxy corporativo.

### Ver la configuración actual
```bash
lxc config show
# Buscar las claves core.http_proxy, core.https_proxy, core.proxy_ignore_hosts
```

### Impacto de configuración incorrecta
Sin el proxy configurado correctamente en las tres capas, LXD no puede descargar imágenes de contenedores, `apt`/`snap` no pueden instalar o actualizar paquetes, y el cloud-init de los contenedores (que replica esta misma configuración vía `apt.http_proxy`/`apt.https_proxy` en su `user-data`) no puede completar su primer arranque.

---

## Endpoint de métricas Prometheus de LXD

### ¿Qué controla?
El puerto y la autenticación del endpoint HTTPS donde LXD expone sus métricas en formato Prometheus (uso de CPU, memoria, red y disco por instancia, entre otras).

✅ Confirmado visualmente en la grabación de la reunión (`reunion/Llamada con Daniel y 3 personas más-20260625_105957-Grabación de la reunión.mp4`, min ~00:07 y ~01:23 con `lxc config show`). No estaba documentado previamente.

### Parámetros

| Parámetro | Función | Valor confirmado |
|---|---|---|
| `core.metrics_address` | IP:puerto donde LXD expone las métricas (HTTPS) | `10.143.11.228:8555` |
| `core.metrics_authentication` | Si exige certificado cliente para leer el endpoint de métricas | `false` |

```bash
lxc config set core.metrics_address 10.143.11.228:8555
lxc config set core.metrics_authentication false
```

> **Advertencia:** con `core.metrics_authentication false`, cualquier cliente que alcance el puerto 8555 por red puede leer las métricas sin autenticarse. Este puerto debe estar protegido por firewall (ver [Configuración de firewall](#configuración-de-firewall-firewalld) más abajo) y accesible solo desde el servidor de observabilidad (SVATOOL, `10.150.31.68`, que también recibe los logs vía syslog — ver [Reenvío de logs del host a Loki](#reenvío-de-logs-del-host-a-loki-rsyslog)).

### Cómo verificar
```bash
curl -sk https://10.143.11.228:8555/1.0/metrics | head
# Debe devolver métricas en formato texto plano de Prometheus
```

---

## Perfiles (profiles)

Los perfiles agrupan configuración reutilizable: cloud-init, dispositivos y variables. Un contenedor puede asociarse a uno o múltiples perfiles.

### Ver perfiles existentes
```bash
lxc profile list
lxc profile show NOMBRE_PERFIL
```

### Editar un perfil
```bash
lxc profile edit NOMBRE_PERFIL
# Abre el perfil en el editor de texto configurado ($EDITOR)
```

### Estructura de un perfil con cloud-init y dispositivo proxy

```yaml
config:
  cloud-init.user-data: |
    #cloud-config
    package_update: true
    package_upgrade: true
    packages:
      - apache2
      - php8.5
devices:
  proxy1:
    bind: instance
    connect: tcp:IP_PROXY:3128
    listen: tcp:127.0.0.1:3128
    type: proxy
description: Perfil base con cloud-init y acceso a internet via proxy
name: nombre-perfil
```

> **Advertencia:** El bloque `user-data` **debe comenzar exactamente con `#cloud-config`** en la primera línea. Sin este header, cloud-init falla con error `unhandled not multipart text`. Ver [07_Troubleshooting.md](07_Troubleshooting.md).

---

## Configuración cloud-init (user-data)

### ¿Qué es?
La sección `user-data` del perfil define qué hace cloud-init en el primer arranque del contenedor.

### Campos principales

| Campo | Tipo | Descripción | Ejemplo |
|---|---|---|---|
| `package_update` | boolean | Actualizar la lista de paquetes APT antes de instalar | `true` |
| `package_upgrade` | boolean | Actualizar los paquetes instalados a sus últimas versiones | `true` |
| `packages` | lista | Lista de paquetes APT a instalar | `- apache2` |
| `write_files` | lista | Archivos a escribir en el filesystem | Ver documentación cloud-init |
| `runcmd` | lista | Comandos a ejecutar al finalizar la inicialización | `- systemctl restart apache2` |

### Ejemplo completo

```yaml
#cloud-config
package_update: true
package_upgrade: true
packages:
  - apache2
  - php8.5
```

### Verificar que cloud-init ejecutó correctamente
```bash
# Dentro del contenedor:
cloud-init status
# Resultado esperado: status: done

# Verificar servicios instalados:
ss -ntlp
# Debe mostrar puerto 80 escuchando (si apache2 está instalado)
```

### Limitación importante
✅ Cloud-init se ejecuta **solo en el primer arranque** del contenedor. Si se modifica el perfil y se reinicia el contenedor, los cambios en cloud-init **no se aplican**. Para re-ejecutar cloud-init, hay que **eliminar y recrear** el contenedor.

---

## Secciones de cloud-init en LXD

LXD expone tres secciones de cloud-init para los perfiles:

| Sección | Clave del perfil | Uso |
|---|---|---|
| User data | `cloud-init.user-data` | Paquetes, usuarios, archivos, comandos |
| Network config | `cloud-init.network-config` | Configuración de red estática (IPs fijas al contenedor) |
| Vendor data | `cloud-init.vendor-data` | Configuración del proveedor de infraestructura |

---

## Dispositivo proxy LXD (salida a internet)

### ¿Qué es?
Un dispositivo proxy LXD crea un socket de red dentro del contenedor que traduce tráfico hacia el host. Se usó como workaround temporal para que los contenedores accedan al proxy HTTP mientras OVN no estaba disponible.

> **Actualización (segunda reunión):** en PFR1 y CAR1, donde OVN ya está funcional (ver [ADR-0006](adr/ADR-0006-wireguard-underlay-ovn-multisitio.md)), este workaround fue reemplazado por un **contenedor gateway dedicado a operación y mantenimiento**: un segundo contenedor gateway (similar al gateway de servicios, ver [02_Arquitectura.md](02_Arquitectura.md)) conectado a la interfaz de gestión del host — la única que tiene permiso de salida hacia el proxy corporativo. Los demás contenedores del sitio enrutan su tráfico de salida (`apt`, descarga de imágenes, etc.) hacia este gateway a través de la red OVN interna, en lugar de tener cada uno su propio dispositivo proxy individual. Este patrón sigue siendo temporal en los sitios donde OVN todavía no está disponible (ej. FDO1), donde el dispositivo proxy por contenedor descrito abajo sigue siendo necesario.

### Configuración (en el perfil o en el contenedor)

```yaml
devices:
  proxy-salida:
    type: proxy
    bind: instance
    listen: tcp:127.0.0.1:3128
    connect: tcp:IP_PROXY:3128
```

| Parámetro | Descripción |
|---|---|
| `type: proxy` | Tipo de dispositivo: proxy de red |
| `bind: instance` | El socket `listen` está dentro del contenedor |
| `listen: tcp:127.0.0.1:3128` | El contenedor escucha en esta dirección |
| `connect: tcp:IP_PROXY:3128` | El host conecta esta dirección al exterior |

> **Confusión frecuente:** `bind: instance` significa que el lado `listen` (la dirección que escucha) es el **interior del contenedor**. `bind: host` significa que el lado `listen` es el **host**. Norberto lo invirtió durante la demostración y tuvo que corregirlo.

---

## Dispositivo proxy LXD (exposición de servicios sin OVN)

### ¿Cuándo usar?
Cuando se necesita exponer un servicio del contenedor hacia el exterior antes de que OVN esté disponible. Redirige tráfico de la interfaz de gestión del host hacia el contenedor.

> **Importante:** Workaround temporal. No es la solución de producción.

### Configuración

```yaml
devices:
  web-public:
    type: proxy
    bind: host
    listen: tcp:IP_GESTION_VM:80
    connect: tcp:127.0.0.1:80
```

| Parámetro | Descripción |
|---|---|
| `bind: host` | El socket `listen` está en el host (interfaz de gestión) |
| `listen: tcp:IP_GESTION_VM:80` | El host escucha en esta IP/puerto |
| `connect: tcp:127.0.0.1:80` | Conectar al servicio del contenedor en localhost:80 |

---

## Dirección de escucha de la API de LXD (`core.https_address`)

### ¿Qué controla?
La IP y el puerto en los que el daemon LXD escucha conexiones a su API HTTPS (Web UI, `lxc` remoto, comunicación entre miembros del cluster).

### Parámetros

| Parámetro | Función | Valor recomendado | Impacto de configuración incorrecta |
|---|---|---|---|
| `core.https_address` | IP:puerto donde escucha el socket HTTPS de LXD | La IP de gestión específica del nodo (ej. `10.150.32.101:8443`), **nunca** `0.0.0.0` | Con `0.0.0.0`, el socket escucha en **todas** las interfaces de red del host — incluida cualquier interfaz de servicio o futura, no solo la de gestión — ampliando innecesariamente la superficie expuesta a intentos de acceso no autorizado |

✅ Confirmado — recomendación explícita de la guía oficial de hardening de LXD (citada por Norberto Núñez durante la reunión): *"siempre que vayas a configurar un socket, nunca dejes en todo en cero. [...] Cuando volvés a poner todo cero, significa que va a escuchar ese socket en todas las interfaces. Y eso se presta a dejar puertas abiertas o exposiciones."*

### Comando

```bash
lxc config set core.https_address IP_DE_GESTION:8443
systemctl restart snap.lxd.daemon
```

### Cómo verificar

```bash
lxc config get core.https_address
# Debe mostrar la IP de gestión específica del nodo, no 0.0.0.0

ss -ntlp | grep 8443
# Debe mostrar el socket escuchando solo en la IP de gestión, no en 0.0.0.0
```

### Errores frecuentes

| Error | Causa | Solución |
|---|---|---|
| Tras el cambio, otros nodos del cluster o la Web UI dejan de responder | Se usó la IP incorrecta (ej. la de servicio en vez de la de gestión), o no se reinició el daemon | Confirmar la IP de gestión correcta con `ip -4 addr show` y reiniciar `snap.lxd.daemon` |

### Rollback

```bash
lxc config set core.https_address 0.0.0.0:8443
systemctl restart snap.lxd.daemon
```

> **Advertencia:** este rollback reabre el socket en todas las interfaces — usar solo como último recurso si el nodo queda inaccesible tras el cambio.

---

## Configuración de firewall (firewalld)

### Rich rules para acceso a Web UI

```bash
# Agregar IP de operador:
firewall-cmd --add-rich-rule='rule family=ipv4 source address=IP_OPERADOR port port=8443-8444 protocol=tcp accept'

# Hacer permanente:
firewall-cmd --runtime-to-permanent

# Ver reglas activas:
firewall-cmd --list-rich-rules

# Ver estado del firewall:
firewall-cmd --state
```

### Impacto de configuración incorrecta
Si falta la rich rule para la IP de un operador, ese operador no puede acceder a la Web UI aunque el servicio LXD esté funcionando.

---

## Reenvío de puertos del gateway hacia el balanceador (firewalld)

### ¿Qué controla?
Cómo el contenedor gateway de servicios reenvía el tráfico entrante hacia el contenedor balanceador (tráfico web) o directamente hacia un contenedor de destino (protocolos no-web). Ver el modelo completo en [02_Arquitectura.md](02_Arquitectura.md) y la decisión en [ADR-0008](adr/ADR-0008-gateway-balanceador-dos-etapas.md).

### Zonas de firewalld dentro del contenedor gateway

| Zona (nombre de uso interno del equipo) | Interfaz | Función |
|---|---|---|
| `external` | `eth1` (`ipvlan` sobre `nicsrv1`) | Tráfico hacia/desde la red del sitio (norte-sur) |
| `internal` | `eth0` (`OVN_1`) | Tráfico hacia/desde otros contenedores del cluster (este-oeste) |

### Reenviar un puerto a otro contenedor (`--add-forward-port`)

```bash
# Reenviar el puerto 80 del gateway al balanceador (mismo puerto de destino)
firewall-cmd --zone=external --add-forward-port=port=80:proto=tcp:toaddr=IP_BALANCEADOR --permanent

# Reenviar un puerto dedicado directamente a un contenedor no-web (ej. base de datos), sin pasar por el balanceador
firewall-cmd --zone=external --add-forward-port=port=5432:proto=tcp:toaddr=IP_CONTENEDOR_BD --permanent

firewall-cmd --reload
```

| Parámetro | Descripción |
|---|---|
| `port` | Puerto de entrada, tal como llega al gateway |
| `proto` | Protocolo (`tcp` o `udp`) |
| `toaddr` | IP interna (en `OVN_1`) del contenedor destino |
| `toport` | (Opcional) Puerto de destino, si es distinto al de entrada — por defecto usa el mismo |

> 🔴 **Pendiente de validación:** la sintaxis completa exacta usada en la demostración no quedó del todo clara en el audio de la reunión — confirmar el comando definitivo (incluyendo si hace falta `masquerade` en la zona) en la próxima sesión antes de replicarlo en otros sitios. Ver [ADR-0008 — Riesgos](adr/ADR-0008-gateway-balanceador-dos-etapas.md).

## Puente NAT temporal hacia el proxy SDI (para sitios sin autorización propia)

### Objetivo
Dar salida a internet a un host nuevo del cluster (ej. un sitio recién incorporado) que **todavía no tiene autorización propia** para salir por el proxy corporativo SDI (`10.150.32.100:3128`), reutilizando el permiso que ya tiene un host existente — sin esperar a que el equipo de seguridad complete el trámite de alta para el host nuevo. Ver el caso real aplicado a la incorporación de FDO1 en [`laboratorio/2026-07-25_incorporacion-sitio-fdo1/bitacora.md`](../laboratorio/2026-07-25_incorporacion-sitio-fdo1/bitacora.md).

> 🟡 **Inferencia razonable:** el mecanismo general (reutilizar el gateway de servicios existente como puente de dos saltos hacia el gateway de OAM, que sí tiene salida autorizada) está confirmado por la reunión. La sintaxis exacta y completa de los comandos `firewall-cmd` usados no se transcribió con suficiente claridad en el audio — la reconstrucción de abajo sigue el mismo patrón ya documentado en [Reenvío de puertos del gateway hacia el balanceador](#reenvío-de-puertos-del-gateway-hacia-el-balanceador-firewalld) de esta misma página. 🔴 **Pendiente de validación:** confirmar la sintaxis exacta (en particular si hace falta `masquerade`) en la próxima sesión con el equipo antes de reutilizar este procedimiento en otro sitio.

### Concepto — "vuelta en U" a través de dos contenedores gateway existentes

El puente no crea infraestructura nueva: reutiliza los dos contenedores gateway que ya existen en un sitio con acceso ya autorizado (ej. Franco/PFR1) — ver [Perfil del contenedor "gateway de servicios"](#perfil-del-contenedor-gateway-de-servicios) y [Perfil y contenedor "gateway de operación y mantenimiento"](#perfil-y-contenedor-gateway-de-operación-y-mantenimiento-prf-gw-oam) más arriba.

```
Host nuevo (sin permiso propio)
        │  petición al puerto 3128
        ▼
PFR-OSS-GW-SRV  (gateway de servicios de Franco — ya expuesto al exterior)
        │  forward-port 3128 → gateway de OAM
        ▼
PFR-GW-OAM      (gateway de OAM de Franco — sale por la IP de gestión
        │        del host Franco, que SÍ tiene permiso con SDI)
        ▼
Proxy SDI (10.150.32.100:3128)
```

### Comando (reconstrucción — ver advertencia de confianza arriba)

```bash
# En PFR-OSS-GW-SRV: aceptar tráfico al 3128 solo desde la IP del host nuevo
firewall-cmd --zone=external --add-rich-rule='rule family=ipv4 source address=IP_HOST_NUEVO port port=3128 protocol=tcp accept'

# Reenviar ese tráfico hacia PFR-GW-OAM
firewall-cmd --zone=external --add-forward-port=port=3128:proto=tcp:toaddr=IP_PFR-GW-OAM

# (sin --permanent / sin --runtime-to-permanent: la regla se pierde
#  intencionalmente al reiniciar el contenedor — ver "Rollback" abajo)
```

### Explicación
La regla `source address` limita qué host puede usar el puente — sin ella, cualquier host de la red podría usar `PFR-OSS-GW-SRV` como proxy abierto hacia SDI. El `forward-port` reenvía el tráfico hacia `PFR-GW-OAM`, que ya tiene, por su propia configuración de red (ver sección de arriba), una ruta de salida hacia el proxy real usando la IP de gestión de Franco.

### Parámetros

| Parámetro | Tipo | Descripción | Valor por defecto |
|---|---|---|---|
| `source address` | IP | Único host autorizado a usar el puente | — (obligatorio, sin default) |
| `port` | entero | Puerto del proxy SDI | `3128` |
| `toaddr` | IP | IP interna (en `OVN_1`) de `PFR-GW-OAM` | — |

### Resultado esperado
Desde el host nuevo, una petición HTTP/HTTPS a través de `http://IP_PFR-OSS-GW-SRV:3128` llega a internet como si el host nuevo tuviera su propio permiso con SDI.

### Cómo verificar

```bash
# Desde el host nuevo:
curl -x http://IP_PFR-OSS-GW-SRV:3128 https://archive.ubuntu.com -I
# Resultado esperado: HTTP/1.1 200 OK (o redirección), no "connection refused" ni "no route to host"
```

✅ Confirmado en la incorporación de FDO1: `curl` y `apt-get` desde `fdo-oss1` funcionaron correctamente a través de este puente.

### Errores frecuentes

| Error | Causa | Solución |
|---|---|---|
| `no route to host` | El host nuevo no está en la `source address` permitida | Verificar la IP exacta del host nuevo con `ip -4 addr show` y corregir la rich-rule |
| El puente deja de funcionar tras reiniciar el contenedor gateway | La regla no se persistió deliberadamente (ver diseño temporal) | Volver a aplicar el comando — es el comportamiento esperado, no un bug |

### Rollback
Al confirmarse el alta formal y definitiva del host nuevo con SDI, eliminar la rich-rule y el forward-port en `PFR-OSS-GW-SRV`:

```bash
firewall-cmd --zone=external --remove-rich-rule='rule family=ipv4 source address=IP_HOST_NUEVO port port=3128 protocol=tcp accept'
firewall-cmd --zone=external --remove-forward-port=port=3128:proto=tcp:toaddr=IP_PFR-GW-OAM
```

Como la regla nunca se persistió (`--permanent`), un simple reinicio del contenedor `PFR-OSS-GW-SRV` también la elimina — pero es preferible el rollback explícito para no depender de un reinicio no planificado.

---

### Por qué la zona `drop` para interfaces sin puertos abiertos

`firewalld` incluye una zona predefinida llamada `drop` con el comportamiento más restrictivo posible: no responde ping y, para cualquier puerto no explícitamente abierto, **descarta el paquete en silencio** (no hay respuesta de ningún tipo) — a diferencia de zonas como `external` o `work`, donde un puerto cerrado sí genera una respuesta de rechazo (ej. TCP reset) que confirma al que escanea que el host existe. Práctica del equipo: usar `drop` como zona por defecto en los contenedores gateway/balanceador para minimizar la información que un escaneo externo puede obtener sobre puertos no publicados deliberadamente.

```bash
firewall-cmd --permanent --set-default-zone drop
```

### Cómo verificar

```bash
firewall-cmd --zone=external --list-forward-ports
# Debe listar los reenvíos configurados (puerto, protocolo, IP destino)
```

---

## Contenedor balanceador (Apache como proxy reverso)

### ¿Qué controla?
El enrutamiento por URL/path de los servicios web publicados detrás del gateway de un sitio, y la centralización del certificado TLS. Ver la ficha completa del componente en [03_Componentes.md](03_Componentes.md) y la decisión en [ADR-0008](adr/ADR-0008-gateway-balanceador-dos-etapas.md).

### Instalación básica

```bash
apt-get update
apt-get install apache2
```

### Ejemplo de ruteo por URL/path

```apache
# /etc/apache2/sites-available/000-default.conf
ProxyPass /kanboard http://IP_CONTENEDOR_KANBOARD:80/
ProxyPassReverse /kanboard http://IP_CONTENEDOR_KANBOARD:80/
```

> **Nota:** Requiere habilitar el módulo `proxy_http` de Apache (`a2enmod proxy proxy_http`) para que las directivas `ProxyPass`/`ProxyPassReverse` funcionen.

### Requisito de ruta por defecto en cloud-init/netplan

El contenedor balanceador, igual que cualquier contenedor con IP fija en `OVN_1`, necesita una ruta por defecto explícita en su configuración de red — sin ella, el contenedor no responde a peticiones que lleguen desde fuera de su propia subred, aunque el firewall esté correctamente configurado (ver [TRB-011 en 07_Troubleshooting.md](07_Troubleshooting.md#trb-011)):

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

> **Advertencia:** El indentado de este bloque YAML es estrictamente significativo — un espacio de más o de menos hace que una línea se interprete como parte de otro grupo distinto, sin generar un error explícito. Revisar la alineación cuidadosamente antes de aplicar.

### Cómo verificar

```bash
lxc exec CONTENEDOR-LB -- ip route
# Debe mostrar una entrada "default via ..."

lxc exec CONTENEDOR-LB -- ss -ntlp
# Debe mostrar el puerto 80/443 escuchando (Apache)
```

---

## ACL por IP de origen en el balanceador

### ¿Qué controla?
Restringir el acceso a una ruta específica (ej. un servicio de mensajería) solo a un conjunto conocido de IPs de origen, en el escenario donde el balanceador está embebido en el mismo contenedor gateway (ver [ADR-0008 — Variante confirmada](adr/ADR-0008-gateway-balanceador-dos-etapas.md#variante-confirmada-balanceador-embebido-en-el-gateway) y [03_Componentes.md](03_Componentes.md#variante-balanceador-embebido-en-el-gateway-cuando-se-necesita-la-ip-real-de-origen)) y por lo tanto ve la IP real del cliente.

### Comando (configuración Apache — `mod_proxy_balancer`)

```apache
# /etc/apache2/sites-available/000-default.conf
<Location /ntf>
    Require ip 10.150.60.92
    Require ip 10.150.60.85
    ProxyPass "balancer://ntf-cluster/"
    ProxyPassReverse "balancer://ntf-cluster/"
</Location>

<Proxy "balancer://ntf-cluster">
    BalancerMember "http://IP_WS1_FERNANDO:8000"
    BalancerMember "http://IP_WS1_FRANCO:8000"
</Proxy>
```

### Explicación
`Require ip` limita el acceso a la ruta `/ntf` a las IPs listadas — cualquier otra IP recibe `403 Forbidden`. El bloque `<Proxy "balancer://...">` define los miembros del balanceo (uno por sitio, ambos corriendo el mismo servicio `WS1`/NTF en el puerto `8000`). Requiere los módulos `proxy`, `proxy_http`, `proxy_balancer` y `lbmethod_byrequests` habilitados (`a2enmod`).

### Parámetros

| Parámetro | Descripción |
|---|---|
| `Require ip` | Una entrada por IP (o rango) autorizada a acceder a la ruta |
| `ProxyPass "balancer://NOMBRE/"` | Redirige el tráfico que matchea el `<Location>` hacia el grupo de balanceo `NOMBRE` |
| `BalancerMember` | Un miembro del grupo de balanceo — un `BalancerMember` por contenedor de aplicación que sirve el mismo servicio |

### Resultado esperado
Una petición desde una IP no listada en `Require ip` recibe `403 Forbidden`. Una petición desde una IP autorizada se reparte entre los `BalancerMember` configurados.

### Cómo verificar

```bash
curl -I http://IP_GATEWAY/ntf   # desde una IP no autorizada -> 403
curl -I http://IP_GATEWAY/ntf   # desde una IP autorizada -> 200/502 según estado del backend
```

---

## Despliegue de configuración a varios contenedores sin SSH

### Objetivo
Aplicar el mismo archivo de configuración (ej. un `VirtualHost` de Apache, un archivo de `rsyslog`) a varios contenedores del cluster, sin necesidad de conectarse por SSH ni copiar archivos por FTP — usando exclusivamente la API de LXD.

### Comando

```bash
# 1. Enviar el archivo local al contenedor (modo 640 por defecto):
lxc file push ARCHIVO_LOCAL NOMBRE_CONTENEDOR/RUTA/DESTINO --project NOMBRE_PROYECTO

# 2. Ejecutar los comandos necesarios dentro del contenedor:
lxc exec NOMBRE_CONTENEDOR --project NOMBRE_PROYECTO -- a2enmod proxy proxy_http proxy_balancer lbmethod_byrequests
lxc exec NOMBRE_CONTENEDOR --project NOMBRE_PROYECTO -- a2dissite 000-default
lxc exec NOMBRE_CONTENEDOR --project NOMBRE_PROYECTO -- a2ensite NOMBRE_SITIO_NUEVO
lxc exec NOMBRE_CONTENEDOR --project NOMBRE_PROYECTO -- systemctl restart apache2
```

Para aplicar el mismo cambio a varios contenedores (ej. todos los gateways del mismo servicio), repetir los dos pasos en un loop, uno por contenedor destino.

### Explicación
`lxc file push` usa la API de LXD para escribir un archivo dentro del filesystem del contenedor, sin abrir ningún puerto de red adicional (SSH, FTP) en el contenedor de destino — coherente con la práctica de mantener SSH deshabilitado en los contenedores de infraestructura (ver [LL-013](12_Lecciones_Aprendidas.md#ll-013--deshabilitar-ssh-en-los-contenedores-de-infraestructura-reduce-el-riesgo-de-movimiento-lateral)). `lxc exec` ejecuta comandos dentro del contenedor de la misma forma.

### Parámetros

| Parámetro | Descripción |
|---|---|
| `--project` | Proyecto LXD al que pertenece el contenedor (omitir si es `default`) |
| Modo del archivo (`file push`) | 640 por defecto — ajustable con `--mode` si el archivo necesita otro permiso |

### Cómo verificar

```bash
lxc exec NOMBRE_CONTENEDOR --project NOMBRE_PROYECTO -- cat RUTA/DESTINO
# Debe mostrar el contenido del archivo enviado

lxc exec NOMBRE_CONTENEDOR --project NOMBRE_PROYECTO -- systemctl status apache2
# Debe mostrar "active (running)"
```

> **Buena práctica:** si el archivo local es temporal (solo para el push), eliminarlo después de enviarlo a todos los contenedores destino, para no dejar residuos de configuración en la máquina desde la que se ejecuta el despliegue.

---

## Interfaz de red del contenedor "gateway de servicios" (driver IPVLAN)

### ¿Qué es?
Dispositivo de red que conecta un contenedor directamente a una interfaz física del host, reutilizando su misma dirección MAC. Se usa exclusivamente en los contenedores que actúan como gateway de servicios de un sitio o proyecto (ver [02_Arquitectura.md](02_Arquitectura.md) y [03_Componentes.md](03_Componentes.md)).

### Configuración (en el perfil)

```yaml
devices:
  eth-ovn:
    type: nic
    network: ovn-red-interna     # Pata hacia la red virtualizada del cluster (este-oeste)
  eth-servicio:
    type: nic
    nictype: ipvlan
    parent: nicsrv1               # Interfaz física de servicio del host (norte-sur)
    mode: l2
```

| Parámetro | Descripción |
|---|---|
| `nictype: ipvlan` | Selecciona el driver IPVLAN en lugar del bridge por defecto |
| `parent: nicsrv1` | Interfaz física del host a la que se conecta (debe tener el mismo nombre en todos los nodos — ver [04_Instalacion.md — Paso 0](04_Instalacion.md)) |
| `mode: l2` | Modo de operación de IPVLAN a nivel de Capa 2 |

> **Por qué IPVLAN:** una política de seguridad de VMware bloquea tráfico saliente con una MAC distinta de la asignada a la VM. IPVLAN reutiliza la MAC del host para todo el tráfico de los contenedores, evitando ese bloqueo sin tener que solicitar una excepción a VMware. Ver el detalle completo en [03_Componentes.md](03_Componentes.md).

---

## Perfil del contenedor "gateway de servicios"

### ¿Qué controla?
La configuración estándar aplicada a cada contenedor que actúa como router/gateway de entrada y salida de servicios de un sitio o proyecto (ver [02_Arquitectura.md](02_Arquitectura.md)).

### Elementos del perfil

| Elemento | Configuración | Por qué |
|---|---|---|
| Interfaces | Una hacia la red OVN (`type: nic`), otra `ipvlan` hacia `nicsrv1` (ver sección anterior) | El contenedor enruta entre la red interna del cluster y la red de servicio del sitio |
| SSH | Deshabilitado (`systemctl disable --now ssh`, dentro del contenedor) | La administración se hace exclusivamente vía `lxc exec`. Reduce la superficie de movimiento lateral si algún contenedor del cluster estuviera comprometido |
| Firewall | Habilitado y configurado para actuar como router (reenvío de paquetes entre sus dos interfaces) | Es su única función — no aloja aplicaciones |
| `journald` | Límite de 100 MB (`SystemMaxUse=100M` en `/etc/systemd/journald.conf`, o `limits.kernel.journald.systemmaxuse` en el perfil) | Por defecto `journald` puede acumular hasta 4 GB de logs. Este contenedor no genera logs de aplicación — 100 MB es más que suficiente |
| NTP | `systemd-timesyncd` configurado igual que el host (ver [04_Instalacion.md — Paso 10](04_Instalacion.md)) | Evita desincronización de reloj entre el contenedor y el cluster |

### Ejemplo — límite de journald en el perfil

```yaml
config:
  limits.kernel.journald.systemmaxuse: "100MB"
```

### Cómo verificar
```bash
lxc exec CONTENEDOR -- systemctl status ssh
# Debe mostrar "inactive (dead)"

lxc exec CONTENEDOR -- journalctl --disk-usage
# Debe mostrar un uso cercano o menor a 100 MB
```

---

## Variable de entorno de proxy para APT y snap

### ¿Qué controla?
Que las herramientas de línea de comandos dentro de un contenedor o host (`apt`, `snap`) usen el proxy HTTP corporativo, además de la configuración nativa de LXD (`core.http_proxy`, ver arriba).

### Configuración

```bash
export http_proxy=http://IP_PROXY:3128
export https_proxy=http://IP_PROXY:3128
```

> **Nota:** Esta variable debe adaptarse al contexto donde se use: exportarla en la sesión de shell interactiva, agregarla a `/etc/environment` para que aplique a todos los procesos del sistema, o configurarla específicamente para `apt` (`/etc/apt/apt.conf.d/`) y para `snap` (variables de entorno del servicio `snapd`) según corresponda.

### Impacto de configuración incorrecta
Sin esta variable (o con una IP de proxy incorrecta), comandos como `apt update` o `snap install` fallan por falta de acceso a internet, incluso si `core.http_proxy` de LXD está bien configurado — son mecanismos independientes.

---

## Reenvío de logs del host a Loki (rsyslog)

### ¿Qué controla?
Que los logs del sistema operativo de cada host del cluster se envíen a un servidor Loki centralizado, ubicado en **otra infraestructura** (no en el propio cluster LXD).

### Configuración (rsyslog)

✅ Confirmado (fuente: [`onenote/Clúster-OSS/Clúster/Syslog.md`](../onenote/Clúster-OSS/Clúster/Syslog.md)):

```bash
echo 'action(type="omfwd" name="fw-To-Svatool-Loki" Target="10.150.31.68" Port="1514" Protocol="tcp" Template="RSYSLOG_SyslogProtocol23Format" queue.filename="fw-To-Svatool-Loki" queue.size="5000" queue.type="fixedarray" queue.maxFileSize="10M" queue.saveOnShutdown="on")' > /etc/rsyslog.d/To-Svatool-Loki.conf

systemctl restart rsyslog
```

| Parámetro | Valor | Función |
|---|---|---|
| `Target` | `10.150.31.68` (SVATOOL) | IP del servidor Loki externo al cluster |
| `Port` / `Protocol` | `1514` / `tcp` | Puerto y protocolo de recepción de syslog en el destino |
| `Template` | `RSYSLOG_SyslogProtocol23Format` | Formato estándar RFC 5424 |
| `queue.type=fixedarray`, `queue.size=5000` | — | Cola en memoria para no bloquear el envío si el destino está momentáneamente inaccesible |
| `queue.saveOnShutdown=on` | — | Persiste la cola a disco si el servicio se detiene, evitando pérdida de logs en tránsito |

El mismo servidor SVATOOL (`10.150.31.68`) recibe además las métricas de `prometheus-node-exporter` (puerto 9100) y del exportador de LXD (puerto 8555) — ver reglas de firewall en [`onenote/Clúster-OSS/Clúster/Firewall.md`](../onenote/Clúster-OSS/Clúster/Firewall.md).

### Por qué un Loki externo al cluster
Si los hosts del cluster LXD apuntaran a un Loki alojado dentro del mismo cluster, una falla del cluster dejaría al equipo sin logs justo en el momento en que más se necesitan para diagnosticar. Ver [12_Lecciones_Aprendidas.md](12_Lecciones_Aprendidas.md).

### Cómo verificar
🔴 Pendiente de validación — confirmar recepción de logs en el Loki destino.

---

## Creación de redes LXD (OVN_1 y bridges de gestión)

### ¿Qué controla?
Las redes lógicas de LXD que existen **antes** de poder asignarlas a un proyecto o perfil. Se crean una sola vez en el proyecto `default` (ver [ADR-0007](adr/ADR-0007-proyectos-lxd-multitenancy.md) sobre por qué los proyectos comparten estas redes en lugar de tener redes propias).

### Comandos

✅ Confirmado (fuente: [`onenote/Clúster-OSS/Proyectos/Proyecto-default.md`](../onenote/Clúster-OSS/Proyectos/Proyecto-default.md)):

```bash
# Red OVN para conectividad este-oeste entre contenedores
lxc network create UplinkOvn1 --type=bridge ipv4.address=none ipv6.address=none ipv4.routes=192.168.0.0/24
lxc network create OVN_1      --type=ovn    network=UplinkOvn1  ipv4.address=none

# Bridge para salida por la interfaz de gestión del host (usado por los gateway de OAM)
lxc network create lxdbr_OAM --type=bridge

# Bridge para conectividad este-oeste sobre la malla WireGuard (uno por miembro, con el mismo nombre)
lxc network create lxdbr_wg0 --type bridge bridge.external_interfaces=wg0 --target pfr.1
lxc network create lxdbr_wg0 --type bridge bridge.external_interfaces=wg0 --target car.1
lxc network create lxdbr_wg0 --type=bridge ipv4.address=none ipv6.address=none
```

| Red | Tipo | Función |
|---|---|---|
| `UplinkOvn1` | bridge | Red física/uplink que sostiene a `OVN_1` — sin IP propia, solo enruta hacia `192.168.0.0/24` |
| `OVN_1` | ovn | Red virtualizada este-oeste entre contenedores (ver el esquema de IPAM en [02_Arquitectura.md](02_Arquitectura.md)) |
| `lxdbr_OAM` | bridge | Salida de los contenedores gateway de operación y mantenimiento hacia la interfaz de gestión del host |
| `lxdbr_wg0` | bridge | Vincula la interfaz física `wg0` (WireGuard, ver [ADR-0006](adr/ADR-0006-wireguard-underlay-ovn-multisitio.md)) como bridge — se crea una vez por miembro del cluster con `--target`, más una definición general sin target |

> **Nota:** `lxc network create` con `--target` configura la red **solo en ese miembro** del cluster (necesario porque cada miembro tiene su propia interfaz física `wg0`); sin `--target`, la configuración se aplica a nivel de cluster.

### Cómo verificar
```bash
lxc network list
# Deben aparecer OVN_1, UplinkOvn1, lxdbr_OAM y lxdbr_wg0 en estado CREATED
```

---

## Perfil y contenedor "gateway de operación y mantenimiento" (`PRF-GW-OAM`)

### ¿Qué controla?
El contenedor por sitio que da salida a internet (vía el proxy corporativo) a las tareas de gestión del propio cluster — actualización de paquetes, descarga de imágenes — separado del contenedor "gateway de servicios" de cada proyecto (ver [02_Arquitectura.md](02_Arquitectura.md)).

### Comandos

✅ Confirmado (ejemplo real para Franco/PFR1; fuente: [`onenote/Clúster-OSS/Proyectos/Proyecto-default.md`](../onenote/Clúster-OSS/Proyectos/Proyecto-default.md)):

```bash
lxc profile create PRF-GW-OAM
lxc profile edit   PRF-GW-OAM <<HERE
name: PRF-Proxy
description: Salida por la interface de gestión del host
devices:
  eth0:
    network: lxdbr_OAM
    type: nic
  eth1:
    network: OVN_1
    type: nic
  root:
    path: /
    pool: local
    size: 5GiB
    type: disk
config:
  limits.cpu: '1'
  limits.memory: 1GiB
  limits.processes: '500'
  cloud-init.user-data: |
    #cloud-config
    apt:
      http_proxy: "http://10.150.32.100:3128"
      https_proxy: "http://10.150.32.100:3128"
    package_update: true
    package_upgrade: true
    packages:
      - firewalld
HERE

lxc launch ubuntu-minimal:resolute PFR-GW-OAM --profile PRF-GW-OAM
```

Para replicar el mismo contenedor en otro miembro (ej. Carpinelli), se copia la instancia existente en lugar de relanzarla desde cero, y se le ajusta la IP de su interfaz de servicio:

```bash
lxc copy PFR-GW-OAM CAR-GW-OAM --profile PRF-GW-OAM --target car.1
lxc config set CAR-GW-OAM cloud-init.network-config='#cloud-config
version: 2
ethernets:
  eth0:
    dhcp4: true
    dhcp6: false
  eth1:
    dhcp4: false
    dhcp6: false
    addresses:
      - 192.168.0.8/24'
```

Dentro de cada instancia, se deshabilita SSH y se configura el firewall como router (mismo criterio que el gateway de servicios, ver [LL-013 en 12_Lecciones_Aprendidas.md](12_Lecciones_Aprendidas.md)):

```bash
lxc shell PFR-GW-OAM
systemctl stop ssh ssh.socket
systemctl disable ssh ssh.socket
systemctl mask ssh

firewall-cmd --permanent --set-default-zone drop
firewall-cmd --permanent --zone external --change-interface eth0
firewall-cmd --permanent --zone external --remove-service ssh
firewall-cmd --permanent --zone internal --change-interface eth1
firewall-cmd --permanent --zone internal --remove-service ssh
firewall-cmd --permanent --zone internal --remove-service samba-client
firewall-cmd --permanent --zone internal --remove-service mdns
firewall-cmd --permanent --zone internal --remove-service dhcpv6-client
firewall-cmd --permanent --zone external --set-target=ACCEPT
firewall-cmd --permanent --zone internal --set-target=ACCEPT
firewall-cmd --reload
```

### Cómo verificar
```bash
lxc list --project default
# PFR-GW-OAM / CAR-GW-OAM deben aparecer (RUNNING una vez activados para producción)
```

> **Nota:** al 2026-07-24, estos contenedores existen creados en ambos sitios pero **detenidos** — ver [13_Linea_de_Tiempo.md](13_Linea_de_Tiempo.md).

---

## Proyectos LXD (multi-tenancy)

### ¿Qué controla?
El aislamiento de recursos y de acceso entre distintos equipos/áreas que comparten el cluster. Ver la decisión completa en [ADR-0007](adr/ADR-0007-proyectos-lxd-multitenancy.md).

### Crear un proyecto nuevo

```bash
lxc project create PRJ-CODIGO_AREA
lxc project switch PRJ-CODIGO_AREA
```

### Definir límites del proyecto

```bash
lxc project set PRJ-CODIGO_AREA limits.networks 2
lxc project set PRJ-CODIGO_AREA limits.cpu 5
lxc project set PRJ-CODIGO_AREA limits.memory 16GB
lxc project set PRJ-CODIGO_AREA limits.instances 5
lxc project set PRJ-CODIGO_AREA limits.containers 4
lxc project set PRJ-CODIGO_AREA limits.virtual-machines 1
```

| Parámetro | Función | Valor por defecto | Impacto de cambiar el valor |
|---|---|---|---|
| `limits.networks` | Cantidad máxima de redes que el proyecto puede referenciar | Sin límite | Limita cuántas redes (ej. OVN + servicio) puede usar el proyecto |
| `limits.cpu` | Cantidad máxima de vCPUs que puede consumir la suma de instancias del proyecto | Sin límite | Evita que el proyecto agote la CPU disponible del cluster |
| `limits.memory` | Memoria RAM máxima total del proyecto | Sin límite | Evita que el proyecto agote la RAM disponible del cluster |
| `limits.instances` | Cantidad máxima de instancias (contenedores + VMs) | Sin límite | Limita el crecimiento descontrolado de instancias |
| `limits.containers` | Cantidad máxima de contenedores | Sin límite | Subconjunto de `limits.instances`, específico para contenedores |
| `limits.virtual-machines` | Cantidad máxima de VMs | Sin límite | Subconjunto de `limits.instances`, específico para VMs |

> **Riesgo de configuración incorrecta:** si un proyecto se crea **sin** definir estos límites explícitamente, hereda un comportamiento sin restricciones — el mismo riesgo que compartir el proyecto `default`. Definir límites es un paso obligatorio, no opcional, al dar de alta un proyecto nuevo.

### Crear un grupo de acceso restringido al proyecto

```bash
lxc auth group create NOMBRE_GRUPO
lxc auth group permission add NOMBRE_GRUPO project PRJ-CODIGO_AREA operator
lxc auth identity group add NOMBRE_USUARIO NOMBRE_GRUPO
```

Los usuarios del grupo solo ven y pueden operar los recursos del proyecto al que el grupo tiene permiso — no ven el proyecto `default` ni los de otros equipos.

### Cómo verificar

```bash
lxc project list
# Debe mostrar el proyecto nuevo con sus límites

lxc project show PRJ-CODIGO_AREA
# Muestra la configuración completa, incluidos los límites definidos

lxc auth group list
# Debe mostrar el grupo y su permiso restringido al proyecto
```

### Recomendación del equipo

✅ A partir de esta reunión, **todo trabajo nuevo de un equipo/área se hace en un proyecto dedicado**, no en `default`. Ver [ADR-0007](adr/ADR-0007-proyectos-lxd-multitenancy.md).

### Ejemplo real completo: proyecto `PRJ-OSS`

✅ Confirmado (fuente: [`onenote/Clúster-OSS/Proyectos/Proyecto-PRJ-OSS.md`](../onenote/Clúster-OSS/Proyectos/Proyecto-PRJ-OSS.md)) — este es el procedimiento real aplicado, como referencia concreta de la plantilla genérica de arriba:

```bash
# 1. Crear el proyecto
lxc project create PRJ-OSS

# 2. Definir límites y restricciones
lxc project set PRJ-OSS \
  limits.networks=2 \
  restricted.networks.access=nic_srv1,OVN_1 \
  restricted.devices.nic=allow \
  features.networks=false features.networks.zones=true \
  restricted=true
```

`restricted.networks.access` es la forma concreta de limitar a qué redes puede llegar un proyecto sin darle una red OVN propia (ver [ADR-0007 — pendiente resuelto](adr/ADR-0007-proyectos-lxd-multitenancy.md)): `PRJ-OSS` solo puede usar `OVN_1` (este-oeste) y `nic_srv1` (servicio local del sitio), no cualquier otra red del cluster.

```bash
# 3. Crear el perfil del gateway de servicios (uno por sitio)
lxc profile create PRF-PFR-OSS-GW-SRV --project PRJ-OSS
lxc profile edit   PRF-PFR-OSS-GW-SRV --project PRJ-OSS <<HERE
name: PRF-PFR-OSS-GW-SRV
description: Perfil para Gateway de networking para servicios entre los contenedores y la red corporativa
devices:
  eth0:
    network: OVN_1
    type: nic
  eth1:
    mode: l2
    nictype: ipvlan
    parent: nic_srv1
    type: nic
  root:
    path: /
    pool: local
    size: 5GiB
    type: disk
config:
  limits.cpu: '1'
  limits.memory: 1GiB
  limits.processes: '500'
  cloud-init.user-data: |
    #cloud-config
    apt:
      http_proxy: "http://10.150.32.100:3128"
      https_proxy: "http://10.150.32.100:3128"
    package_update: true
    package_upgrade: true
    packages:
      - firewalld
  cloud-init.network-config: |
    #cloud-config
    version: 2
    ethernets:
      eth0:
        dhcp4: false
        dhcp6: false
        addresses:
          - 192.168.0.1/24
        routes:
          - to: 10.150.32.100
            via: 192.168.0.6
      eth1:
        dhcp4: false
        dhcp6: false
        addresses:
          - 10.143.11.8/26
        nameservers:
          addresses:
            - 10.129.4.176
            - 10.129.4.177
        routes:
          - to: default
            via: 10.143.11.1
HERE

# 4. Lanzar la instancia y endurecerla (SSH deshabilitado, firewall como router)
lxc launch ubuntu-minimal:resolute PFR-OSS-GW-SRV --profile PRF-PFR-OSS-GW-SRV --project PRJ-OSS
```

Para Carpinelli, se repite el mismo patrón con un perfil propio (`PRF-CAR-OSS-GW-SRV`, misma estructura con IPs distintas) y se copia la instancia al nuevo miembro:

```bash
lxc copy PFR-OSS-GW-SRV CAR-OSS-GW-SRV --profile PRF-CAR-OSS-GW-SRV --target car.1 --project PRJ-OSS
```

> **Nota:** la ruta `via: 192.168.0.6` en `eth0` apunta al contenedor `PFR-GW-OAM`/`CAR-GW-OAM` (gateway de operación y mantenimiento) — es cómo el gateway de servicios sale a internet a través del proxy corporativo sin tener él mismo una salida directa. Ver la sección anterior.

---

## Buckets de almacenamiento S3 (backend de Loki/Mimir)

### ¿Qué controla?
LXD puede exponer un *storage pool* como servidor de objetos compatible con S3. El equipo lo usa para dar almacenamiento de objetos a las herramientas de observabilidad (Loki para logs, Mimir para métricas de largo plazo) sin depender de un servicio S3 externo al cluster.

✅ Confirmado visualmente en la grabación de la reunión (`reunion/Llamada con Daniel y 3 personas más-20260625_105957-Grabación de la reunión.mp4`, min ~00:28). No estaba documentado previamente.

### Comandos

```bash
# Crear un bucket en un storage pool existente
lxc storage bucket create POOL NOMBRE_BUCKET [size=TAMAÑO]

# Ejemplos reales observados:
lxc storage bucket create local:svatool-lxc-storage-1 mimir-vol1 --project default
lxc storage bucket create pool_lvm loki-svatool
lxc storage bucket set pool_lvm loki-svatool size=1TiB
```

| Parámetro | Descripción |
|---|---|
| `POOL` | Storage pool de LXD donde vive el bucket (ej. `local`, `pool_lvm`) |
| `NOMBRE_BUCKET` | Nombre del bucket S3 (ej. `loki-svatool`, `mimir-vol1`) |
| `size` | Cuota del bucket (se puede fijar en la creación o después con `lxc storage bucket set`) |

Al crear el bucket, LXD genera automáticamente una clave de acceso (`access key`) y una clave secreta (`secret key`) de administrador para ese bucket.

> **Advertencia de seguridad:** las claves de acceso S3 son credenciales — **no** deben copiarse a este repositorio ni a ningún documento en texto plano. Se muestran una sola vez en la salida del comando (`lxc storage bucket create` no las reimprime después); guardarlas en el gestor de credenciales del equipo (ver [`recursos/`](../recursos/) o el proceso interno de gestión de secretos). Si una clave quedó expuesta en una grabación de pantalla, rotarla (`lxc storage bucket key delete` / recrear la key) apenas sea posible.

### Cómo verificar
```bash
lxc storage bucket list POOL
lxc storage bucket show POOL NOMBRE_BUCKET
```

---

## MTU de dispositivos de red por contenedor

### ¿Qué controla?
El tamaño máximo de paquete (MTU) de una interfaz de red específica de un contenedor, que sobrescribe el valor heredado del perfil o de la red.

✅ Confirmado visualmente en la grabación de la reunión (`reunion/Llamada con Daniel y 3 personas más-20260625_105957-Grabación de la reunión.mp4`, min ~00:28). No estaba documentado previamente.

### Comando

```bash
lxc config device set NOMBRE_CONTENEDOR eth0 mtu 9216 --project NOMBRE_PROYECTO

# Ejemplo real observado:
lxc config device set C-SyslogDist-h1 eth0 mtu 9216 --project IAAS-Logs
```

### Explicación
Se usó para el contenedor distribuidor de syslog (`C-SyslogDist-h1`, proyecto `IAAS-Logs`), donde un MTU de jumbo frame (9216) reduce la fragmentación de paquetes al reenviar grandes volúmenes de líneas de log hacia el destino centralizado.

> 🔴 **Pendiente de validación:** no quedó claro en la reunión si el MTU de 9216 requiere que la red/switch físico subyacente también tenga jumbo frames habilitados extremo a extremo — confirmar antes de replicar este ajuste en otro sitio, ya que un MTU mayor al soportado por la red causa fragmentación silenciosa o pérdida de paquetes grandes.

### Cómo verificar
```bash
lxc exec NOMBRE_CONTENEDOR -- ip link show eth0
# El campo "mtu" debe mostrar el valor configurado
```

---

## Documentos relacionados

| Tema | Documento |
|---|---|
| Instalación previa | [04_Instalacion.md](04_Instalacion.md) |
| Operación con contenedores y proyectos | [06_Operacion.md](06_Operacion.md) |
| Troubleshooting de configuración | [07_Troubleshooting.md](07_Troubleshooting.md) |
| Decisión sobre dispositivo proxy | [10_Decisiones.md](10_Decisiones.md) |
| Decisión sobre WireGuard como underlay | [ADR-0006](adr/ADR-0006-wireguard-underlay-ovn-multisitio.md) |
| Decisión sobre proyectos LXD | [ADR-0007](adr/ADR-0007-proyectos-lxd-multitenancy.md) |
