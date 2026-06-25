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
```

---

## Documentos relacionados

| Tema | Documento |
|---|---|
| Configuración de cloud-init y proxy | [05_Configuracion.md](05_Configuracion.md) |
| Operación normal | [06_Operacion.md](06_Operacion.md) |
| Manual operativo con checklist de salud | [14_Manual_Operativo.md](14_Manual_Operativo.md) |
