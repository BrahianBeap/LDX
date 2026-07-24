# 09 — Preguntas frecuentes (FAQ)

> **Audiencia:** Todo el equipo.
> **Propósito:** Respuestas directas a las preguntas más comunes, con enlace al documento dueño para la información completa. Para problemas técnicos, ver [07_Troubleshooting.md](07_Troubleshooting.md).

---

## Sobre LXD

### ¿Por qué LXD y no Docker?

Docker está diseñado para contenedores de aplicación: un proceso por contenedor, inmutable, efímero. LXD está diseñado para contenedores de sistema: emula un sistema operativo completo con init, múltiples servicios, red y filesystem propio.

El equipo necesita hospedar servicios completos (Apache, base de datos, PHP) con acceso SSH, gestión como un servidor y posibilidad de migrar entre nodos. LXD es la herramienta correcta para este modelo.

### ¿Puedo tener múltiples servicios en un contenedor LXD?

Técnicamente sí — LXD es un contenedor de sistema y puede correr múltiples servicios. Sin embargo, el equipo adoptó el principio de **un servicio por contenedor** por razones arquitecturales: aislamiento de fallas, actualización independiente de componentes, y maniobrabilidad operativa. Ver [10_Decisiones.md](10_Decisiones.md) y [12_Lecciones_Aprendidas.md](12_Lecciones_Aprendidas.md).

### ¿Cuál es la diferencia entre el puerto 8443 y 8444?

- **Puerto 8443:** Puerto del cluster LXD. Usado para comunicación entre nodos y para acceso de usuarios a la Web UI.
- **Puerto 8444:** Puerto de administración local del daemon LXD. Usado para gestión del nodo individual.

---

## Sobre el cluster

### ¿Qué pasa si un nodo del cluster se cae?

Los contenedores que corren en ese nodo quedan inaccesibles mientras el nodo esté caído. Los contenedores de otros nodos siguen funcionando normalmente. El cluster no se cae completamente — solo los contenedores del nodo afectado.

Para restaurar: encender la VM del nodo y LXD se reconecta automáticamente al cluster. Si la VM tiene problemas, solicitar restauración del backup a SBA/AIT.

### ¿Los contenedores migran automáticamente si cae un nodo?

No. La migración automática no fue configurada. Por ahora, la migración es manual y debe hacerse con el nodo en funcionamiento. Ver: [11_Riesgos.md](11_Riesgos.md) y [13_Linea_de_Tiempo.md](13_Linea_de_Tiempo.md).

### ¿Cómo sé en qué nodo está corriendo un contenedor?

```bash
lxc list
# La columna LOCATION muestra el nodo donde corre cada contenedor
```

---

## Sobre cloud-init

### ¿Cloud-init se ejecuta en cada reinicio del contenedor?

No. Cloud-init es un mecanismo de inicialización de primer arranque, no de gestión continua. Para cambios post-despliegue, hay que eliminar y recrear el contenedor, o usar otras herramientas. Ver: [TRB-002 en 07_Troubleshooting.md](07_Troubleshooting.md#trb-002) y [05_Configuracion.md](05_Configuracion.md).

### Modifiqué el perfil, ¿se aplican los cambios al contenedor existente?

Los cambios de cloud-init no se aplican retroactivamente: hay que eliminar el contenedor y recrearlo. Los cambios de dispositivos en el perfil sí se aplican a contenedores existentes de inmediato. Ver: [TRB-002 en 07_Troubleshooting.md](07_Troubleshooting.md#trb-002).

### ¿Cómo verifico que cloud-init terminó correctamente?

```bash
lxc exec NOMBRE_CONTENEDOR -- cloud-init status
# Resultado esperado: status: done
```

Si muestra `error`, revisar logs en `/var/log/cloud-init-output.log` dentro del contenedor. Ver [07_Troubleshooting.md](07_Troubleshooting.md).

---

## Sobre la red

### ¿Por qué no funciona la red entre contenedores de distintos nodos?

✅ Entre Franco (PFR1) y Carpinelli (CAR1) ya funciona: la red OVN corre sobre una malla WireGuard cifrada que actúa como transporte entre sitios. Ver [ADR-0006](adr/ADR-0006-wireguard-underlay-ovn-multisitio.md). Fernando (FDO1) todavía no fue incorporado al cluster — ver [11_Riesgos.md](11_Riesgos.md) y [13_Linea_de_Tiempo.md](13_Linea_de_Tiempo.md).

### ¿Por qué se necesitó agregar WireGuard si ya se había elegido OVN?

El túnel de datos nativo de OVN, viajando directamente sobre la red corporativa, resultó bloqueado entre sitios en Capa 3 separada (confirmado dos veces, en dos implementaciones independientes). WireGuard se agregó como transporte underlay cifrado sobre el cual corre el túnel de OVN — no reemplaza la decisión de usar OVN, la complementa. Ver el análisis completo en [ADR-0006](adr/ADR-0006-wireguard-underlay-ovn-multisitio.md).

### ¿Todas las VLAN de los sitios tienen que ser la misma?

No. Cada sitio puede tener su propia VLAN local para la interfaz de servicio de contenedores. Lo único que exige LXD es que el **nombre de la interfaz** sea idéntico en todos los nodos del cluster (se logra renombrando por MAC en `netplan`). Ver [04_Instalacion.md](04_Instalacion.md) y [ADR-0006](adr/ADR-0006-wireguard-underlay-ovn-multisitio.md).

### ¿Puedo acceder a la Web UI desde fuera de la red local?

No en este momento. El acceso es solo desde la red local; la VPN está pendiente de configurar. Ver: [11_Riesgos.md](11_Riesgos.md) y [13_Linea_de_Tiempo.md](13_Linea_de_Tiempo.md).

### ¿Por qué se usa un proxy HTTP en el contenedor?

Workaround temporal mientras OVN no está activo: los contenedores no tienen ruta directa a internet. El dispositivo proxy LXD redirige el tráfico del contenedor hacia el proxy corporativo. Se eliminará cuando OVN esté configurado. Ver: [05_Configuracion.md — Dispositivo proxy LXD](05_Configuracion.md) y [LL-009 en 12_Lecciones_Aprendidas.md](12_Lecciones_Aprendidas.md).

### ¿Por qué se descartó Ubuntu Fan?

Ubuntu Fan requiere subred /24; la red de gestión de las VMs es /29 (solo 6 IPs) — son incompatibles. Ver la decisión completa en [ADR-0002](adr/ADR-0002-red-ovn-vs-ubuntu-fan.md).

---

## Sobre almacenamiento

### ¿Por qué ZFS?

Por sus snapshots integrados (copy-on-write instantáneo), checksums de integridad de datos y mejor integración con LXD. Ver la decisión completa en [ADR-0003](adr/ADR-0003-storage-zfs.md).

### ¿Las imágenes de contenedores pesan mucho?

Las imágenes base de Ubuntu (sin datos de usuario) pesan muy poco. LXD las cachea localmente, por lo que el segundo contenedor creado desde la misma imagen es prácticamente instantáneo — no hay descarga.

---

## Sobre proyectos y multi-tenancy

### ¿Por qué no simplemente crear todos los contenedores en el proyecto `default`?

Porque no da aislamiento: cualquier usuario con acceso ve y puede modificar los recursos de todos los equipos, y no hay forma de limitar cuánto consume cada equipo del cluster compartido. Desde la segunda reunión, el equipo adopta **proyectos LXD** dedicados por área, con límites de recursos y grupos de acceso restringidos. Ver [ADR-0007](adr/ADR-0007-proyectos-lxd-multitenancy.md) y [05_Configuracion.md](05_Configuracion.md).

### ¿Qué pasa si creo un proyecto nuevo y no le defino límites?

Hereda un comportamiento sin restricciones — el mismo riesgo que el proyecto `default`. Definir límites (`limits.cpu`, `limits.memory`, `limits.instances`, etc.) es un paso obligatorio al dar de alta un proyecto nuevo. Ver [05_Configuracion.md](05_Configuracion.md).

---

## Sobre seguridad

### ¿Es seguro agregar a alguien al grupo lxd?

No, o más precisamente: debe hacerse con precaución. El grupo `lxd` otorga acceso completo al cluster LXD, lo que es equivalente a acceso root al host. Solo agregar usuarios de confianza que necesiten administrar el cluster.

### ¿El acceso a la Web UI es seguro?

Sí. La comunicación es HTTPS con TLS. Cada usuario se autentica con su propio certificado TLS generado en su navegador. El token inicial tiene tiempo de expiración.

### ¿Por qué se deshabilita SSH dentro de los contenedores del cluster?

Para reducir la superficie de movimiento lateral: si un contenedor llegara a estar comprometido, no debería poder usarse SSH para saltar a otros contenedores. La administración del cluster se hace exclusivamente vía `lxc exec` (shell del propio LXD). SSH solo se habilita de forma excepcional en contenedores que necesitan ser accedidos explícitamente desde afuera. Ver [05_Configuracion.md](05_Configuracion.md) y [12_Lecciones_Aprendidas.md](12_Lecciones_Aprendidas.md).

### ¿Es un problema que la IP de gestión de un nodo no se pueda inventariar o declarar ante seguridad?

Es un riesgo menor gracias a la naturaleza distribuida del cluster: como la base de datos se replica entre todos los miembros, el cluster se puede gestionar desde **cualquier** nodo — no es necesario tener acceso específicamente al nodo cuya IP no pudiera declararse. Alcanza con que al menos un miembro del cluster esté correctamente inventariado y accesible. Ver [11_Riesgos.md](11_Riesgos.md).

---

## Documentos relacionados

| Tema | Documento |
|---|---|
| Decisiones técnicas con justificación completa | [ADR](adr/) · [10_Decisiones.md](10_Decisiones.md) |
| Diagnóstico de problemas | [07_Troubleshooting.md](07_Troubleshooting.md) |
| Riesgos actuales | [11_Riesgos.md](11_Riesgos.md) |
| Glosario de términos | [08_Glosario.md](08_Glosario.md) |
