# 06 — Operación del cluster LXD

> **Audiencia:** Operadores e ingenieros de infraestructura que trabajan día a día con el cluster.
> **Propósito:** Procedimientos operativos para gestionar contenedores, imágenes, perfiles y el cluster.

---

## Crear un contenedor desde una imagen oficial

### Objetivo
Desplegar un nuevo contenedor a partir de una imagen pública de Ubuntu.

### Comando

```bash
lxc launch ubuntu:24.04 NOMBRE_CONTENEDOR --profile NOMBRE_PERFIL
```

### Explicación

| Parámetro | Descripción |
|---|---|
| `ubuntu:24.04` | Fuente de imagen: imagen Ubuntu 24.04 LTS del servidor de imágenes de Canonical |
| `NOMBRE_CONTENEDOR` | Nombre del contenedor a crear |
| `--profile NOMBRE_PERFIL` | Perfil que define cloud-init y dispositivos del contenedor |

✅ La primera vez, LXD descarga la imagen desde internet (requiere proxy configurado). Las siguientes veces, usa la imagen cacheada localmente — el despliegue es instantáneo.

### Verificación después de crear

```bash
# Ver estado del contenedor:
lxc list

# Verificar que cloud-init terminó:
lxc exec NOMBRE_CONTENEDOR -- cloud-init status
# Resultado esperado: status: done

# Verificar servicios escuchando:
lxc exec NOMBRE_CONTENEDOR -- ss -ntlp
# Ejemplo: puerto 80 si se instaló apache2
```

---

## Crear un contenedor desde una imagen personalizada (clon)

### Objetivo
Desplegar un contenedor idéntico a uno ya configurado, sin esperar la ejecución de cloud-init.

### Flujo completo

#### 1. Detener el contenedor modelo

```bash
lxc stop CONTENEDOR_MODELO
```

#### 2. Crear imagen desde el contenedor

```bash
lxc publish CONTENEDOR_MODELO --alias NOMBRE_IMAGEN
```

#### 3. Crear nuevo contenedor desde la imagen

```bash
lxc launch NOMBRE_IMAGEN NOMBRE_NUEVO_CONTENEDOR --profile NOMBRE_PERFIL
```

### Explicación
Al publicar un contenedor como imagen, se captura su estado actual (paquetes instalados, archivos, configuración). Clonar desde esa imagen es instantáneo — no hay descarga ni cloud-init. Todos los contenedores creados desde esa imagen tendrán exactamente los mismos paquetes y configuración base.

### Verificación

```bash
lxc image list
# Debe aparecer la imagen con el alias dado

lxc list
# Debe aparecer el nuevo contenedor en estado Running
```

---

## Detener, iniciar y reiniciar contenedores

```bash
# Detener:
lxc stop NOMBRE_CONTENEDOR

# Iniciar:
lxc start NOMBRE_CONTENEDOR

# Reiniciar:
lxc restart NOMBRE_CONTENEDOR

# Forzar detención (si no responde):
lxc stop --force NOMBRE_CONTENEDOR
```

> **Nota:** Reiniciar un contenedor no re-ejecuta cloud-init. Para cambios de cloud-init, eliminar y recrear el contenedor.

---

## Acceder a la consola de un contenedor

```bash
# Ejecutar un comando:
lxc exec NOMBRE_CONTENEDOR -- COMANDO

# Abrir shell interactivo:
lxc exec NOMBRE_CONTENEDOR -- bash
```

---

## Eliminar un contenedor

```bash
# El contenedor debe estar detenido:
lxc stop NOMBRE_CONTENEDOR
lxc delete NOMBRE_CONTENEDOR

# O en un solo paso:
lxc delete --force NOMBRE_CONTENEDOR
```

> **Advertencia:** `lxc delete` es irreversible. Todos los datos del contenedor se pierden. Crear una imagen antes si se quieren preservar los datos.

---

## Migrar un contenedor entre nodos del cluster

### Objetivo
Mover un contenedor de un nodo a otro dentro del cluster.

### Desde la Web UI
1. Seleccionar el contenedor.
2. Ir a **Migrate**.
3. Seleccionar el nodo destino.
4. Confirmar.

### Desde CLI

```bash
lxc move NOMBRE_CONTENEDOR --target NOMBRE_NODO
```

> **Nota:** El contenedor debe estar detenido para migrar sin tiempo de inactividad extendido. La migración en caliente (live migration) 🔴 Pendiente de validación para este entorno.

### Verificación

```bash
lxc list
# El contenedor debe aparecer en el nodo destino

lxc cluster list
# Verificar que el nodo origen y destino siguen ONLINE
```

---

## Migrar un contenedor entre proyectos LXD

### Objetivo
Mover un contenedor del proyecto `default` a otro proyecto (o viceversa) — por ejemplo, para pasar un contenedor de prueba a su proyecto definitivo. Ver la restricción que motiva este procedimiento en [ADR-0007](adr/ADR-0007-proyectos-lxd-multitenancy.md) y [LL-016 en 12_Lecciones_Aprendidas.md](12_Lecciones_Aprendidas.md#ll-016--los-proxy-devices-de-lxd-no-son-migrables-fuera-del-proyecto-default).

### Por qué no alcanza con mover el contenedor directamente
Los dispositivos de tipo `proxy` solo están permitidos en el proyecto `default` — si el contenedor los tiene, la migración falla con `can not receive local origin for clone local container`. Lo mismo ocurre si se intenta migrar directamente desde un **snapshot**: los snapshots no son migrables entre proyectos.

### Procedimiento

```bash
# 1. Crear una copia normal del contenedor (no un snapshot) en el mismo proyecto
lxc copy CONTENEDOR_ORIGEN CONTENEDOR_COPIA --project PROYECTO_ORIGEN

# 2. Quitar los dispositivos proxy de la copia (repetir por cada dispositivo proxy que tenga)
lxc config device remove CONTENEDOR_COPIA NOMBRE_DISPOSITIVO_PROXY --project PROYECTO_ORIGEN

# 3. Migrar la copia limpia al proyecto de destino
lxc move CONTENEDOR_COPIA --project PROYECTO_ORIGEN --target-project PROYECTO_DESTINO
```

### Verificación

```bash
lxc list --project PROYECTO_DESTINO
# El contenedor debe aparecer en el proyecto de destino

lxc config device show CONTENEDOR_COPIA --project PROYECTO_DESTINO
# No debe listar ningún dispositivo de tipo proxy
```

---

## Tomar un snapshot de un contenedor (antes de cambios riesgosos)

### Objetivo
Poder revertir rápidamente un contenedor a su estado anterior si un cambio de configuración sale mal — distinto de publicar una imagen completa (ver [Crear un contenedor desde una imagen personalizada](#crear-un-contenedor-desde-una-imagen-personalizada-clon) arriba). Ver [LL-017 en 12_Lecciones_Aprendidas.md](12_Lecciones_Aprendidas.md#ll-017--snapshot-antes-de-cualquier-cambio-riesgoso-y-reglas-de-firewall-primero-en-runtime).

```bash
# Crear un snapshot antes de un cambio incierto:
lxc snapshot NOMBRE_CONTENEDOR NOMBRE_SNAPSHOT

# Listar snapshots existentes:
lxc info NOMBRE_CONTENEDOR

# Revertir el contenedor a un snapshot:
lxc restore NOMBRE_CONTENEDOR NOMBRE_SNAPSHOT

# Eliminar un snapshot que ya no se necesita:
lxc delete NOMBRE_CONTENEDOR/NOMBRE_SNAPSHOT
```

> **Nota:** El snapshot es **por contenedor** — si un servicio tiene el frontend y la base de datos en contenedores separados (ver [LL-006](12_Lecciones_Aprendidas.md#ll-006--separar-la-base-de-datos-del-frontend-en-contenedores-distintos)), cada uno necesita su propio snapshot independiente antes de un cambio que los afecte a ambos.

---

## Gestión de imágenes

```bash
# Listar imágenes disponibles:
lxc image list

# Ver detalles de una imagen:
lxc image info ALIAS_O_FINGERPRINT

# Eliminar una imagen:
lxc image delete ALIAS_O_FINGERPRINT

# Publicar contenedor como imagen:
lxc publish NOMBRE_CONTENEDOR --alias NOMBRE_IMAGEN
```

---

## Gestión de perfiles

```bash
# Listar perfiles:
lxc profile list

# Ver perfil completo:
lxc profile show NOMBRE_PERFIL

# Editar perfil:
lxc profile edit NOMBRE_PERFIL

# Crear nuevo perfil:
lxc profile create NOMBRE_PERFIL

# Asociar perfil a contenedor existente:
lxc profile add NOMBRE_CONTENEDOR NOMBRE_PERFIL
```

---

## Trabajar con proyectos (multi-tenancy)

### Objetivo
Operar contenedores dentro de un proyecto específico, en lugar del proyecto `default`. Ver la configuración de límites y grupos en [05_Configuracion.md](05_Configuracion.md) y la decisión en [ADR-0007](adr/ADR-0007-proyectos-lxd-multitenancy.md).

```bash
# Listar proyectos existentes:
lxc project list

# Cambiar el proyecto activo de la sesión de CLI:
lxc project switch NOMBRE_PROYECTO

# Listar contenedores de un proyecto específico sin cambiar de sesión:
lxc list --project NOMBRE_PROYECTO

# Crear un contenedor dentro de un proyecto específico:
lxc launch ubuntu:24.04 NOMBRE_CONTENEDOR --project NOMBRE_PROYECTO --profile NOMBRE_PERFIL
```

> **Nota:** Si no se especifica `--project` ni se hizo `lxc project switch`, todos los comandos `lxc` operan sobre el proyecto `default`. Verificar siempre en qué proyecto se está trabajando antes de crear o eliminar recursos.

---

## Cómo incorporar un nuevo sitio al cluster (checklist completo)

### Objetivo

Esta es la **hoja de ruta única** para agregar un sitio nuevo al cluster
(ej. Fernando/FDO1, IT, Ciudad del Este) — desde la instalación del
sistema operativo hasta tener sus contenedores gateway funcionando. Reúne
en un solo lugar, en el orden correcto, comandos que ya están documentados
por separado en [04_Instalacion.md](04_Instalacion.md),
[05_Configuracion.md](05_Configuracion.md), [ADR-0006](adr/ADR-0006-wireguard-underlay-ovn-multisitio.md)
y [ADR-0007](adr/ADR-0007-proyectos-lxd-multitenancy.md). Si un paso tiene
parámetros, tabla de errores frecuentes o rollback que no están repetidos
acá, ese detalle está en el documento enlazado — esta checklist es la
**secuencia**, no reemplaza la referencia completa de cada comando.

> Ejemplo usado en todos los comandos de abajo: se agrega **Fernando
> (FDO1)** como tercer miembro, junto a Franco (PFR1) y Carpinelli (CAR1)
> ya activos. Reemplazar `FDO`/`fdo-oss`/`fdo.1` por el sitio que
> corresponda.

---

### Fase 0 — Antes de tocar una terminal

- [ ] Confirmar con SBA/AIT que la VM del nuevo sitio existe, con **dos**
      interfaces de red (gestión y servicio) — ver
      [01_Contexto.md](01_Contexto.md).
- [ ] Confirmar el número de sitio en el esquema de direccionamiento ya
      reservado (no inventar uno nuevo). Para FDO ya está reservado en
      [02_Arquitectura.md](02_Arquitectura.md):

  | Dato | Valor reservado para FDO |
  |---|---|
  | IP interna WireGuard (`wg0`) | `169.254.0.2` |
  | IP del gateway de servicios en `OVN_1` (`FDO-OSS-GW-SRV`) | `192.168.0.4` |
  | IP del gateway de OAM en `OVN_1` (`FDO-GW-OAM`) | `192.168.0.9` |
  | IP de gestión (`nic_oam`) | `10.150.32.x/24`, VLAN 701 |
  | IP de servicio (`nic_srv1`) | `10.11.11.x/24`, VLAN 5 |

---

### Fase 1 — Sistema operativo, LXD y MicroOVN en el nuevo host

En **`fdo-oss`** (el nuevo host). Detalle completo, parámetros y errores
frecuentes de cada comando: [04_Instalacion.md — Pasos 0, 1, 1.5 y 3](04_Instalacion.md).

> ⚠️ **Antes de instalar cualquier snap, configurar el proxy — si no, el
> siguiente paso falla con `error: unable to contact snap store`.** `snap`
> **no** usa `/etc/apt/apt.conf.d/` ni las variables `http_proxy`/`https_proxy`
> del shell — tiene su propio mecanismo:
> ```bash
> snap set system proxy.http=http://10.150.32.100:3128
> snap set system proxy.https=http://10.150.32.100:3128
> ```
> Si después de configurar esto `snap install` sigue fallando con
> `connect: no route to host` (proxy bien configurado pero inalcanzable),
> el host probablemente **no está autorizado todavía** para salir por ese
> proxy — hace falta pedir el alta de servicio al equipo de seguridad/red
> (mismo trámite que se hizo para PFR1 y CAR1). Diagnóstico paso a paso
> (sin depender de `ping`/`iptables`, que pueden no estar instalados) en
> [`laboratorio/2026-07-25_incorporacion-sitio-fdo1/bitacora.md`](../laboratorio/2026-07-25_incorporacion-sitio-fdo1/bitacora.md).

```bash
# Paso 0 — Renombrar interfaces (mismo nombre lógico que los demás nodos)
# Editar /etc/netplan/*.yaml: nic_oam y nic_srv1, match por MAC + set-name

# Paso 1 — Instalar LXD
snap install lxd
snap refresh --hold          # Paso 1.5 — congelar actualizaciones automáticas

# Paso 3 — Instalar MicroOVN (todavía NO se hace bootstrap ni join acá)
snap install microovn
```

---

### Fase 2 — Conectar el nuevo sitio a la malla WireGuard

**El paso más importante de toda la checklist.** Debe completarse y
verificarse **antes** de unir el nuevo sitio a LXD o a OVN — si no, se
repite el problema original que motivó [ADR-0006](adr/ADR-0006-wireguard-underlay-ovn-multisitio.md)
(plano de control sincronizado, pero sin tráfico de datos entre
contenedores).

WireGuard no tiene base de datos distribuida — **hay que tocar todos los
nodos existentes, uno por uno**, no solo el nuevo. Matriz de qué hacer en
cada nodo para este ejemplo (agregar FDO):

| Nodo | Acción |
|---|---|
| `fdo-oss` (nuevo) | Generar su propio par de claves. Configurar `wg0` en su `netplan` con un `peer` por cada sitio ya existente (PFR1, CAR1). |
| `pfr-oss` (existente) | Agregar a FDO como **nuevo peer** en su `netplan` (nueva entrada en `peers` y en `routes`). |
| `car-oss` (existente) | Agregar a FDO como **nuevo peer** en su `netplan` (nueva entrada en `peers` y en `routes`). |

**1. En `fdo-oss` — generar el par de claves:**

```bash
apt install wireguard-tools
wg genkey | tee privatekey | wg pubkey > publickey
chown root:systemd-network privatekey
chmod 640 privatekey
```

**2. En `fdo-oss` — configurar `wg0` en netplan, con un peer hacia cada sitio existente:**

```yaml
network:
  tunnels:
    wg0:
      mode: wireguard
      addresses: [169.254.0.2/32]        # IP interna reservada para FDO
      key: /ruta/a/privatekey
      peers:
        - keys:
            public: "CLAVE_PUBLICA_DE_PFR1"
          endpoint: 10.143.11.228:51820
          allowed-ips: [169.254.0.0/32]
          keepalive: 25
        - keys:
            public: "CLAVE_PUBLICA_DE_CAR1"
          endpoint: 192.168.91.116:51820
          allowed-ips: [169.254.0.1/32]
          keepalive: 25
  routes:
    - to: 169.254.0.0/32
      via: 169.254.0.2
    - to: 169.254.0.1/32
      via: 169.254.0.2
```

**3. En `pfr-oss` y en `car-oss` — agregar a FDO como peer nuevo** (editar
el `netplan` existente, **no** reemplazarlo — solo sumar la entrada):

```yaml
      peers:
        # ... peers existentes se mantienen ...
        - keys:
            public: "CLAVE_PUBLICA_DE_FDO1"
          endpoint: 10.150.32.X:51820      # IP de gestión real de fdo-oss
          allowed-ips: [169.254.0.2/32]
          keepalive: 25
  routes:
    # ... rutas existentes se mantienen ...
    - to: 169.254.0.2/32
      via: 169.254.0.X                     # X = propia IP interna de ese nodo
```

**4. Aplicar y verificar en los tres nodos:**

```bash
netplan try     # o netplan apply, una vez confirmado
wg show
# Debe mostrar el peer nuevo con "latest handshake" reciente en los TRES nodos
```

📖 Tabla completa de parámetros, errores frecuentes (`wg show` sin
handshake, túnel que se pierde al reiniciar) y por qué la IP va siempre en
`netplan` y nunca solo con `ip addr add`: [04_Instalacion.md — Paso 4](04_Instalacion.md).

---

### Fase 3 — Unir el nuevo nodo al cluster LXD

Detalle completo del wizard y variante de storage con LVM:
[04_Instalacion.md — Paso 2](04_Instalacion.md).

```bash
# En un nodo YA miembro del cluster (ej. pfr-oss), generar el token:
lxc cluster add fdo.1

# En fdo-oss, ejecutar el wizard:
lxd init
# "Use LXD clustering?" -> yes
# "Are you joining an existing cluster?" -> yes
# Pegar el token generado en el paso anterior
# El resto de las respuestas: ver tabla completa en 04_Instalacion.md
```

```bash
# Verificar:
lxc cluster list
# fdo.1 debe aparecer ONLINE
```

---

### Fase 4 — Unir el nuevo nodo al cluster OVN

Requiere que la Fase 2 (WireGuard) ya esté verificada. Detalle completo:
[04_Instalacion.md — Paso 5](04_Instalacion.md).

```bash
# En un nodo ya miembro del cluster OVN:
microovn cluster add fdo-oss

# En fdo-oss, con el token generado:
microovn cluster join TOKEN_GENERADO
```

```bash
# Verificar:
microovn cluster list
snap services microovn
# Todos los servicios deben estar active/enabled
```

---

### Fase 5 — Firewall, proxy, NTP y usuarios del nuevo host

Igual que en cualquier nodo — detalle completo, parámetros y errores
frecuentes: [04_Instalacion.md — Pasos 6 a 10](04_Instalacion.md).

```bash
# Firewall: reglas por IP de cada operador (puertos 8443-8444)
firewall-cmd --add-rich-rule='rule family=ipv4 source address=IP_OPERADOR port port=8443-8444 protocol=tcp accept'
firewall-cmd --runtime-to-permanent

# Proxy HTTP corporativo
lxc config set core.http_proxy http://10.150.32.100:3128
lxc config set core.https_proxy http://10.150.32.100:3128

# Usuarios al grupo lxd
usermod -aG lxd NOMBRE_USUARIO

# NTP — ver 04_Instalacion.md Paso 10 para el contenido completo de timesyncd.conf
```

---

### Fase 6 — Crear los contenedores gateway del nuevo sitio

Las redes LXD (`OVN_1`, `lxdbr_OAM`, etc.) **no se vuelven a crear** — ya
existen a nivel de cluster desde que se crearon la primera vez (ver
[05_Configuracion.md — Creación de redes LXD](05_Configuracion.md)). Lo
que sí hay que crear por cada sitio nuevo son sus dos contenedores
gateway.

**6.1 — Gateway de operación y mantenimiento (`FDO-GW-OAM`, proyecto `default`):**

```bash
# Se copia desde un gateway OAM existente en vez de crear un perfil nuevo
lxc copy PFR-GW-OAM FDO-GW-OAM --profile PRF-GW-OAM --target fdo.1
lxc config set FDO-GW-OAM cloud-init.network-config='#cloud-config
version: 2
ethernets:
  eth0:
    dhcp4: true
    dhcp6: false
  eth1:
    dhcp4: false
    dhcp6: false
    addresses:
      - 192.168.0.9/24'   # IP reservada para el gateway OAM de FDO
```

Endurecimiento (deshabilitar SSH, firewall como router) — comandos
completos en [05_Configuracion.md — gateway de OAM](05_Configuracion.md).

**6.2 — Gateway de servicios por cada proyecto que use este sitio** (ej.
`FDO-OSS-GW-SRV` para el proyecto `PRJ-OSS`):

```bash
# Crear el perfil propio del sitio (mismo patrón que PFR/CAR, IPs distintas)
lxc profile create PRF-FDO-OSS-GW-SRV --project PRJ-OSS
lxc profile edit   PRF-FDO-OSS-GW-SRV --project PRJ-OSS
#   -> misma estructura que PRF-PFR-OSS-GW-SRV (ver 05_Configuracion.md),
#      con eth0 en 192.168.0.4/24 (IP reservada para el gateway de
#      servicios de FDO) y eth1 con la IP real de nic_srv1 en FDO

lxc copy PFR-OSS-GW-SRV FDO-OSS-GW-SRV --profile PRF-FDO-OSS-GW-SRV --target fdo.1 --project PRJ-OSS
```

📖 YAML completo del perfil (dispositivos, límites, cloud-init) y por qué
la ruta de salida pasa por el gateway de OAM:
[05_Configuracion.md — Ejemplo real completo: proyecto PRJ-OSS](05_Configuracion.md).

---

### Fase 7 — Verificación end-to-end

```bash
# 1. El nuevo miembro aparece online en ambos clusters (LXD y OVN)
lxc cluster list
microovn cluster list

# 2. Conectividad OVN cruzada: contenedor de prueba en el nuevo sitio
#    debe poder ver contenedores de los otros sitios (mismo método que
#    se usó para validar PFR1<->CAR1, ver ADR-0006)
lxc launch IMAGEN C-FDO-1 --project PRJ-OSS --target fdo.1
lxc exec C-FDO-1 -- ping -c 3 IP_DE_C-PFR-1

# 3. Los gateways del nuevo sitio están accesibles
lxc list --project default    # FDO-GW-OAM
lxc list --project PRJ-OSS    # FDO-OSS-GW-SRV
```

Si el ping cruzado no responde, volver a la Fase 2 — el 95% de las veces
el problema está en una clave pública, un endpoint o una ruta de
WireGuard mal copiada en alguno de los tres nodos.

---

## Actualizar LXD y MicroOVN de forma coordinada (snap)

### Objetivo
Actualizar la versión de LXD o MicroOVN sin romper la consistencia del cluster.

### Procedimiento

```bash
# En CADA nodo del cluster, de forma coordinada (todos el mismo día, uno después del otro):
snap refresh lxd
snap refresh microovn
```

> **Advertencia:** Todos los nodos deben tener `snap refresh --hold` aplicado (ver [04_Instalacion.md](04_Instalacion.md)) para que la actualización **no** ocurra automáticamente en un nodo mientras los demás quedan en una versión distinta. Si un nodo queda con una versión distinta de los demás, el cluster bloquea las operaciones de configuración hasta que todos coincidan. Ver [TRB-010 en 07_Troubleshooting.md](07_Troubleshooting.md#trb-010).

### Cómo verificar

```bash
snap list lxd
# La versión debe coincidir en todos los nodos

lxc cluster list
# Ningún nodo debe mostrarse bloqueado/con advertencia de versión
```

---

## Agregar usuarios al grupo lxd (acceso CLI)

### Objetivo
Permitir que un nuevo operador use `lxc` sin `sudo`.

```bash
usermod -aG lxd NOMBRE_USUARIO
```

> **Advertencia:** El grupo `lxd` otorga acceso completo al cluster. Solo para operadores autorizados.

---

## Backup de contenedores

### Opción 1: Exportar imagen localmente

```bash
lxc publish NOMBRE_CONTENEDOR --alias backup-NOMBRE-FECHA
lxc image export backup-NOMBRE-FECHA /ruta/local/
```

✅ Liviano. El contenedor base de Ubuntu sin datos adicionales pesa muy poco.

### Opción 2: Backup de la VM (solicitar a SBA/AIT)

Para backup completo del nodo incluyendo el pool ZFS, solicitar a SBA/AIT que configuren snapshots de la VM en VMware.

> **Nota:** Solicitar el backup desde el inicio del proyecto, no cuando se necesite urgentemente.

---

## Ver estado del cluster

```bash
lxc cluster list
# Muestra todos los nodos: nombre, estado (ONLINE/OFFLINE), arquitectura, URL

lxc info
# Información del nodo actual y el cluster

lxc list
# Lista todos los contenedores del cluster con su nodo de asignación
```

---

## Ver logs de un contenedor

```bash
# Logs de cloud-init:
lxc exec NOMBRE_CONTENEDOR -- cat /var/log/cloud-init.log
lxc exec NOMBRE_CONTENEDOR -- cat /var/log/cloud-init-output.log

# Logs del sistema:
lxc exec NOMBRE_CONTENEDOR -- journalctl -xe

# Log de LXD (en el host):
snap logs lxd
```

---

## Documentos relacionados

| Tema | Documento |
|---|---|
| Configuración de perfiles y dispositivos | [05_Configuracion.md](05_Configuracion.md) |
| Diagnóstico de problemas | [07_Troubleshooting.md](07_Troubleshooting.md) |
| Monitoreo y salud del cluster | [14_Manual_Operativo.md](14_Manual_Operativo.md) |
