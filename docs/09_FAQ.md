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

La red OVN aún no está activa: requiere VLAN 411 en cada VM, pendiente de habilitación por Cristian (administrador VMware). Ver: [11_Riesgos.md](11_Riesgos.md).

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

## Sobre seguridad

### ¿Es seguro agregar a alguien al grupo lxd?

No, o más precisamente: debe hacerse con precaución. El grupo `lxd` otorga acceso completo al cluster LXD, lo que es equivalente a acceso root al host. Solo agregar usuarios de confianza que necesiten administrar el cluster.

### ¿El acceso a la Web UI es seguro?

Sí. La comunicación es HTTPS con TLS. Cada usuario se autentica con su propio certificado TLS generado en su navegador. El token inicial tiene tiempo de expiración.

---

## Documentos relacionados

| Tema | Documento |
|---|---|
| Decisiones técnicas con justificación completa | [ADR](adr/) · [10_Decisiones.md](10_Decisiones.md) |
| Diagnóstico de problemas | [07_Troubleshooting.md](07_Troubleshooting.md) |
| Riesgos actuales | [11_Riesgos.md](11_Riesgos.md) |
| Glosario de términos | [08_Glosario.md](08_Glosario.md) |
