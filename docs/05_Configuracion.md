# 05 — Configuración del sistema

> **Audiencia:** Ingenieros de infraestructura y operadores del cluster.
> **Propósito:** Documentar todos los parámetros y configuraciones del sistema: proxy, cloud-init, perfiles, dispositivos y firewall. No incluye instalación (ver [04_Instalacion.md](04_Instalacion.md)).

---

## Proxy HTTP de LXD

### ¿Qué controla?
El proxy HTTP que LXD usa para comunicarse con internet: descargar imágenes de contenedores, actualizaciones, etc.

### Parámetros

| Parámetro | Archivo/Comando | Función | Ejemplo |
|---|---|---|---|
| `core.http_proxy` | `lxc config set` | Proxy para tráfico HTTP de LXD | `http://32.x.x.x:3128` |
| `core.https_proxy` | `lxc config set` | Proxy para tráfico HTTPS de LXD | `http://32.x.x.x:3128` |
| `core.proxy_ignore_hosts` | `lxc config set` | Hosts sin proxy (acceso directo) | `127.0.0.1,localhost` |

> **Nota:** La IP del proxy (🔴 Pendiente de validación) debe confirmarse con Nicolás (equipo de seguridad). En la reunión se mencionó `32.x.x.x:3128`.

### Ver la configuración actual
```bash
lxc config show
# Buscar las claves core.http_proxy, core.https_proxy, core.proxy_ignore_hosts
```

### Impacto de configuración incorrecta
Sin el proxy configurado correctamente, LXD no puede descargar imágenes de contenedores ni el cloud-init puede instalar paquetes via APT.

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
Un dispositivo proxy LXD crea un socket de red dentro del contenedor que traduce tráfico hacia el host. Se usa temporalmente para que los contenedores accedan al proxy HTTP mientras OVN no está disponible.

> **Importante:** Este es un workaround temporal. Una vez que OVN esté configurado con la VLAN 411, los contenedores tendrán acceso de red directo y estos dispositivos deben ser eliminados.

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

## Documentos relacionados

| Tema | Documento |
|---|---|
| Instalación previa | [04_Instalacion.md](04_Instalacion.md) |
| Operación con contenedores | [06_Operacion.md](06_Operacion.md) |
| Troubleshooting de configuración | [07_Troubleshooting.md](07_Troubleshooting.md) |
| Decisión sobre dispositivo proxy | [10_Decisiones.md](10_Decisiones.md) |
