# 04 — Instalación del cluster LXD

> **Audiencia:** Ingenieros de infraestructura que instalarán nuevos nodos.
> **Propósito:** Procedimiento completo y reproducible para instalar y configurar un nodo LXD. Seguir este documento en orden estricto.

---

## Prerrequisitos

Antes de comenzar, verificar que se cumplen todos estos requisitos:

| Prerrequisito | Verificación | Responsable |
|---|---|---|
| VM con Ubuntu LTS disponible | `lsb_release -a` | SBA/AIT (Cristian) |
| Disco dedicado para ZFS (mínimo 100 GB, recomendado 300+ GB) | `lsblk` | SBA/AIT |
| Acceso SSH a la VM | `ssh usuario@IP` | SBA/AIT |
| Acceso a internet (proxy HTTP o directo) | `curl -I https://cloud-images.ubuntu.com` | Nicolás (seguridad) |
| IP de la VM en red de gestión (/29) | `ip addr` | SBA/AIT |
| 🔴 Interfaz VLAN 411 disponible (para OVN — futuro) | `ip addr` | Cristian |

---

## Paso 1: Instalar LXD

### Objetivo
Instalar el daemon LXD en la VM. LXD se distribuye como snap, lo que garantiza versiones reproducibles y actualizaciones automáticas.

### Comando

```bash
snap install lxd
```

### Explicación
`snap install lxd` descarga e instala LXD desde el Snap Store de Canonical. La versión snap es la versión oficial y recomendada. No usar el paquete `lxd` de los repositorios deb del sistema operativo (es la versión antigua y discontinuada).

### Parámetros
Sin parámetros. El snap toma automáticamente la versión estable más reciente (5.21 al momento de la reunión).

### Resultado esperado
```
lxd 5.21 from Canonical✓ installed
```

### Cómo verificar
```bash
snap list lxd
# Debe mostrar: lxd  5.21  ...  stable  canonical✓
```

### Rollback
```bash
snap remove lxd
# No afecta datos hasta que se haya corrido lxd init
```

---

## Paso 2: Inicializar LXD (lxd init)

### Objetivo
Configurar el daemon LXD: storage pool, networking, clustering y métricas. Este es el paso más importante y no se puede deshacer fácilmente sin reinstalar.

### Comando

```bash
lxd init
```

### Explicación
`lxd init` es un wizard interactivo que hace preguntas sobre la configuración del nodo. Las respuestas determinan cómo LXD almacena datos, se comunica y se une al cluster.

> **Advertencia:** Ejecutar **una sola vez** por nodo. Si se necesita reconfigurar, hay que hacer reset completo.

### Respuestas recomendadas para el wizard

| Pregunta | Respuesta | Justificación |
|---|---|---|
| Clustering? | Yes | Este nodo formará parte del cluster distribuido |
| Create a new cluster? | Yes (solo en el primero, PFR1) | PFR1 es el nodo fundador |
| Join existing cluster? | Yes (para CAR1, FDO1, etc.) | Nodos adicionales se unen con token |
| Storage driver | ZFS | Ver [10_Decisiones.md](10_Decisiones.md) |
| Disk for ZFS pool | `/dev/sda6` (o el disco dedicado disponible) | Disco exclusivo para LXD |
| MAAS server? | No | No aplica a este entorno |
| Bridge for networking? | No | La red de contenedores es OVN (MicroOVN) |
| Prometheus metrics? | Yes | Habilitar métricas para observabilidad |
| Admin port | 8444 | Puerto de administración local |
| Cluster port | 8443 | Puerto de comunicación entre nodos y acceso a Web UI |

### Para nodos adicionales (CAR1, FDO1)

Al seleccionar "Join existing cluster", el wizard pedirá un **join token**. Este token se genera desde PFR1:

```bash
# En PFR1:
lxc cluster add CAR1
# LXD muestra un token. Copiarlo y usarlo en el wizard de CAR1.
```

### Resultado esperado
```
LXD has been successfully configured.
```

### Cómo verificar
```bash
lxc cluster list
# Debe mostrar el nodo actual con estado ONLINE
```

### Errores frecuentes

| Error | Causa | Solución |
|---|---|---|
| `ZFS pool already exists` | El disco ya fue usado por ZFS antes | `zpool destroy NOMBRE_POOL` y volver a intentar |
| `Cannot connect to cluster` | Firewall bloqueando puerto 8443 | Ver Paso 5 (configuración de firewall) |

---

## Paso 3: Instalar MicroOVN

### Objetivo
Instalar el componente de red SDN que conectará los contenedores entre nodos y sitios.

### Comando

```bash
snap install microovn
```

### Explicación
MicroOVN es la distribución de OVN de Canonical, instalada como snap. Simplifica la configuración de OVN, que de otro modo requeriría instalar y configurar múltiples componentes manualmente.

### Resultado esperado
```
microovn X.Y.Z from Canonical✓ installed
```

### Cómo verificar
```bash
snap list microovn
```

---

## Paso 4: Bootstrap del cluster OVN (solo en PFR1)

### Objetivo
Inicializar el cluster OVN. Este comando solo se ejecuta en el primer nodo (PFR1). Los nodos siguientes se unirán al cluster OVN en su propio proceso de instalación.

### Comando

```bash
microovn cluster bootstrap
```

### Explicación
`microovn cluster bootstrap` configura este nodo como el nodo inicial del cluster OVN. Establece los servicios internos de OVN (ovsdb-server, ovn-northd, ovn-controller). Solo se ejecuta una vez en el clúster.

> **Advertencia:** No ejecutar en CAR1 ni FDO1. Esos nodos se unen al cluster OVN durante su proceso de lxd init.

### Resultado esperado
El comando no produce output visible en caso de éxito.

### Cómo verificar
```bash
snap services microovn
# Todos los servicios deben estar en estado active/enabled
```

---

## Paso 5: Configurar firewall (firewalld)

### Objetivo
Permitir que los operadores del equipo accedan a la Web UI de LXD desde sus IPs.

### Comando

```bash
# Agregar regla para cada IP de operador:
firewall-cmd --add-rich-rule='rule family=ipv4 source address=IP_OPERADOR port port=8443-8444 protocol=tcp accept'

# Una vez agregadas todas las IPs, hacer las reglas permanentes:
firewall-cmd --runtime-to-permanent
```

### Explicación
firewalld gestiona el firewall del host. Las rich rules permiten especificar el origen (IP del operador), el protocolo y los puertos permitidos.

`--runtime-to-permanent` promueve todas las reglas activas en memoria a reglas persistentes que sobreviven reinicios del servicio. Sin este paso, las reglas se pierden al reiniciar firewalld o el sistema.

### Parámetros de la rich rule

| Parámetro | Descripción |
|---|---|
| `family=ipv4` | Aplica solo a tráfico IPv4 |
| `source address=IP` | IP de origen permitida |
| `port port=8443-8444` | Rango de puertos permitidos |
| `protocol=tcp` | Solo TCP |
| `accept` | Acción: permitir el tráfico |

### IPs a agregar

| Operador | IP | Estado |
|---|---|---|
| Daniel Medina | 🔴 Pendiente de validación (IP parcialmente capturada en reunión) | Pendiente |
| Rocío Duarte | 🔴 Pendiente de validación | Pendiente |
| Otros operadores | 🔴 Pendiente de validación | Pendiente |

### Cómo verificar
```bash
firewall-cmd --list-rich-rules
# Deben aparecer las reglas agregadas
```

### Rollback
```bash
# Remover una regla específica:
firewall-cmd --remove-rich-rule='rule family=ipv4 source address=IP_OPERADOR port port=8443-8444 protocol=tcp accept'
firewall-cmd --runtime-to-permanent
```

---

## Paso 6: Configurar proxy HTTP en LXD

### Objetivo
Permitir que LXD (y los contenedores) descarguen imágenes y paquetes a través del proxy HTTP corporativo.

### Comandos

```bash
lxc config set core.http_proxy http://PROXY_IP:3128
lxc config set core.https_proxy http://PROXY_IP:3128
lxc config set core.proxy_ignore_hosts 127.0.0.1,localhost
```

> **Nota:** La IP exacta del proxy (🔴 Pendiente de validación — se mencionó `32.x.x.x:3128` en la reunión) debe ser confirmada con Nicolás (equipo de seguridad).

### Explicación

| Parámetro | Descripción |
|---|---|
| `core.http_proxy` | Proxy para tráfico HTTP saliente de LXD |
| `core.https_proxy` | Proxy para tráfico HTTPS saliente de LXD |
| `core.proxy_ignore_hosts` | Hosts que LXD debe acceder directamente sin proxy |

### Cómo verificar
```bash
lxc config get core.http_proxy
# Debe mostrar la URL del proxy
```

---

## Paso 7: Agregar usuarios al grupo lxd

### Objetivo
Permitir que los operadores usen `lxc` desde la línea de comandos sin necesidad de `sudo`.

### Comando

```bash
usermod -aG lxd NOMBRE_USUARIO
```

### Explicación
LXD usa un socket Unix (`/var/snap/lxd/common/lxd/unix.socket`) que solo puede ser accedido por `root` o miembros del grupo `lxd`. Agregar un usuario al grupo `lxd` le otorga acceso completo al cluster desde esa VM.

> **Advertencia:** El grupo `lxd` es equivalente a acceso root al host. Solo agregar usuarios de confianza.

### Cómo verificar
```bash
groups NOMBRE_USUARIO
# Debe incluir "lxd" en la lista
```

---

## Paso 8: Acceso a la Web UI

### Objetivo
Que cada operador pueda acceder a la Web UI de LXD desde su navegador.

### Procedimiento por operador

1. Abrir el navegador en modo incógnito.
2. Navegar a `https://IP_DEL_NODO:8443`.
3. El navegador advertirá sobre el certificado. Continuar.
4. En la UI: **Generate certificate** → descargar el archivo de certificado.
5. Instalar el certificado en el almacén del navegador (siguiente, siguiente, finalizar).
6. Cerrar la pestaña y abrir una nueva (en modo incógnito si el certificado fue rechazado antes).
7. Ingresar el **token** proporcionado por el administrador.

> **Nota:** Si el navegador rechazó el certificado anteriormente, usar modo incógnito para el primer acceso con el certificado nuevo.

### Cómo generar un token para un nuevo usuario

Desde la Web UI o CLI:

```bash
lxc config trust add NOMBRE_USUARIO
# LXD muestra el token. Compartirlo de forma segura con el usuario.
```

### Verificación
El usuario debe poder ver el dashboard del cluster al ingresar el token.

---

## Paso 9: Verificar estado del cluster

### Objetivo
Confirmar que el nodo está activo y es miembro del cluster.

### Comandos

```bash
lxc cluster list
# Muestra todos los nodos del cluster con su estado

lxc info
# Muestra información del nodo actual y el cluster al que pertenece

snap services lxd
# Verifica que el servicio LXD está activo
```

---

## Resumen del procedimiento

```
Paso 1: snap install lxd
Paso 2: lxd init (wizard — responder según tabla)
Paso 3: snap install microovn
Paso 4: microovn cluster bootstrap (solo en PFR1)
Paso 5: Configurar firewall (rich rules por IP de operador)
Paso 6: Configurar proxy HTTP (core.http_proxy, etc.)
Paso 7: Agregar operadores al grupo lxd
Paso 8: Guiar a cada operador en el acceso a Web UI
Paso 9: Verificar estado del cluster
```

---

## Documentos relacionados

| Tema | Documento |
|---|---|
| Configuración posterior a la instalación | [05_Configuracion.md](05_Configuracion.md) |
| Operación diaria | [06_Operacion.md](06_Operacion.md) |
| Troubleshooting de instalación | [07_Troubleshooting.md](07_Troubleshooting.md) |
| Componentes instalados | [03_Componentes.md](03_Componentes.md) |
