# 14 — Manual Operativo

> **Audiencia:** Operadores e ingenieros SRE que monitorean y mantienen el cluster día a día.
> **Propósito:** Checklist de salud, procedimientos de verificación, monitoreo y escalamiento de incidentes.

---

## Checklist de salud del cluster

Ejecutar periódicamente (o ante cualquier síntoma de problema):

```bash
# 1. Estado del cluster:
lxc cluster list
# Todos los nodos deben estar ONLINE

# 2. Estado de los contenedores:
lxc list
# Los contenedores de producción deben estar en estado Running

# 3. Estado del daemon LXD (en cada nodo):
snap services lxd
# Debe mostrar active/enabled

# 4. Estado del pool ZFS (en cada nodo):
zpool status
# Debe mostrar ONLINE

# 5. Estado del firewall (en cada nodo):
firewall-cmd --state
# Debe mostrar: running

# 6. Estado de MicroOVN (en cada nodo):
snap services microovn
# Todos los servicios deben estar active
```

---

## Verificar que cloud-init terminó en un contenedor

```bash
lxc exec NOMBRE_CONTENEDOR -- cloud-init status
# Resultado esperado: status: done

# Si muestra "running", cloud-init sigue ejecutándose. Esperar y volver a verificar.
# Si muestra "error", revisar logs:
lxc exec NOMBRE_CONTENEDOR -- cat /var/log/cloud-init-output.log
```

---

## Verificar servicios activos en un contenedor

```bash
# Ver puertos escuchando:
lxc exec NOMBRE_CONTENEDOR -- ss -ntlp

# Ver servicios systemd:
lxc exec NOMBRE_CONTENEDOR -- systemctl list-units --type=service --state=running

# Ejemplo para verificar Apache:
lxc exec NOMBRE_CONTENEDOR -- systemctl status apache2
```

---

## Monitoreo con Prometheus

> **Estado:** 🔴 Pendiente de validación — la configuración del servidor Prometheus externo y los dashboards de Grafana no fueron documentados en detalle en la reunión inicial.

LXD expone métricas en formato Prometheus. Cuando el servidor Prometheus externo esté configurado, monitoreará:

- Estado de nodos del cluster.
- Número de contenedores y su estado.
- Uso de CPU, RAM y almacenamiento por contenedor y por nodo.
- Operaciones de storage.

Para ver dashboards: Grafana Labs provee dashboards de LXD importables por ID (🔴 IDs específicos: Pendiente de validación).

---

## Qué hacer si un nodo está OFFLINE

### Paso 1: Verificar conectividad

```bash
ping IP_NODO_CAIDO
# ¿Responde?
```

### Paso 2: Intentar SSH al nodo

```bash
ssh USUARIO@IP_NODO
```

Si responde:

```bash
# Verificar LXD:
snap services lxd

# Si no está activo, reiniciar:
snap restart lxd

# Volver a verificar:
lxc cluster list
```

Si el nodo no responde SSH:

→ Escalar a SBA/AIT para verificar estado de la VM en VMware.
→ Si la VM está caída, solicitar inicio de VM.
→ Si hay corrupción de datos, solicitar restauración de backup de VM.

---

## Qué hacer si un contenedor no inicia

```bash
# Ver error al iniciar:
lxc start NOMBRE_CONTENEDOR
# LXD muestra el error

# Ver logs del contenedor:
lxc console NOMBRE_CONTENEDOR
# (Ctrl+a q para salir)

# Verificar logs de LXD:
snap logs lxd | grep NOMBRE_CONTENEDOR
```

Causas comunes:
- Pool ZFS lleno → verificar con `zpool status` y espacio disponible.
- Imagen corrupte → recrear el contenedor desde una imagen conocida.
- Problema de red → verificar configuración OVN o dispositivos proxy.

---

## Qué hacer si no se puede acceder a la Web UI

1. Verificar que LXD está activo: `snap services lxd`.
2. Verificar que la IP del operador tiene regla en el firewall: `firewall-cmd --list-rich-rules`.
3. Verificar acceso desde la red correcta (actualmente solo red local, sin VPN).
4. Si hay certificado rechazado: usar modo incógnito. Ver [TRB-004 en 07_Troubleshooting.md](07_Troubleshooting.md#trb-004).

---

## Cómo agregar un nuevo operador

### Acceso a Web UI

1. El nuevo operador accede a `https://IP_NODO:8443` en modo incógnito.
2. Genera su certificado en la UI.
3. Un administrador genera un token:
   ```bash
   lxc config trust add NOMBRE_OPERADOR
   ```
4. Compartir el token de forma segura con el operador.
5. El operador ingresa el token en la UI.

### Acceso CLI (opcional)

```bash
# Agregar al grupo lxd (solo si necesita acceso desde terminal):
usermod -aG lxd NOMBRE_OPERADOR
```

### Acceso al firewall (si se conecta desde una IP fija)

```bash
firewall-cmd --add-rich-rule='rule family=ipv4 source address=IP_OPERADOR port port=8443-8444 protocol=tcp accept'
firewall-cmd --runtime-to-permanent
```

---

## Escalamiento de incidentes

| Situación | Acción | Contacto |
|---|---|---|
| VM caída o inaccesible | Solicitar verificación/inicio de VM | SBA o AIT |
| Pool ZFS degradado o faulted | Solicitar restauración de backup de VM | SBA o AIT |
| Acceso al proxy HTTP cortado | Solicitar restauración del permiso | Nicolás (seguridad) |
| Necesidad de nueva interfaz de red | Solicitar VLAN 411 en la VM | Cristian (VMware) |
| Problema con reglas de firewall | Verificar y agregar rich rules | Equipo técnico |
| Problema con OVN | 🔴 Procedimiento pendiente de documentar | Norberto Núñez |

---

## Mantenimiento programado

### Antes de realizar mantenimiento en un nodo

1. Migrar contenedores críticos a otro nodo:
   ```bash
   lxc move CONTENEDOR --target OTRO_NODO
   ```
2. Verificar que el contenedor esté corriendo en el nodo destino.
3. Realizar el mantenimiento.
4. Volver a verificar el estado del cluster después.

### Actualizar LXD (snap)

```bash
# Ver versión actual:
snap list lxd

# Actualizar:
snap refresh lxd
```

> **Nota:** Snap puede actualizar automáticamente. Verificar la política de actualización automática del entorno.

---

## Comandos de referencia rápida

```bash
# Ver todo el cluster:
lxc cluster list && lxc list

# Estado completo de un contenedor:
lxc info CONTENEDOR

# Entrar al shell de un contenedor:
lxc exec CONTENEDOR -- bash

# Logs en tiempo real de LXD:
snap logs -f lxd

# Ver perfil de un contenedor:
lxc config show CONTENEDOR

# Ver dispositivos de un contenedor:
lxc config device show CONTENEDOR
```

---

## Documentos relacionados

| Tema | Documento |
|---|---|
| Operación habitual | [06_Operacion.md](06_Operacion.md) |
| Diagnóstico de problemas | [07_Troubleshooting.md](07_Troubleshooting.md) |
| Riesgos actuales | [11_Riesgos.md](11_Riesgos.md) |
