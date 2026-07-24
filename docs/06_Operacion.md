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
