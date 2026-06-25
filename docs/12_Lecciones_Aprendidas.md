# 12 — Lecciones aprendidas

> **Audiencia:** Todo el equipo técnico.
> **Propósito:** Conocimiento tácito extraído de la instalación inicial. Se documenta el *porqué* sucedió cada problema, no solo la solución — que vive en [07_Troubleshooting.md](07_Troubleshooting.md). Especialmente valioso para nuevos integrantes del equipo.

---

## LL-001 — Cloud-init requiere el header #cloud-config

**¿Qué pasó?**
Durante la demostración, Norberto configuró cloud-init en el perfil sin el header `#cloud-config`. El resultado fue un error silencioso: `unhandled not multipart text x no multipart user data`. Los paquetes no se instalaron.

**Lección:**
El bloque `user-data` en el perfil LXD **debe comenzar exactamente con `#cloud-config`** en la primera línea. Sin este header, cloud-init interpreta el contenido como texto plano y lo ignora.

Ver ejemplo correcto y ficha de diagnóstico completa en [TRB-001 — 07_Troubleshooting.md](07_Troubleshooting.md#trb-001).

---

## LL-002 — El dispositivo proxy LXD: bind define dónde está el socket listen

**¿Qué pasó?**
Norberto configuró el dispositivo proxy con `bind: host` y `listen: tcp:127.0.0.1:3128` apuntando a dar salida al contenedor. El resultado fue que el proxy estaba configurado al revés — escuchaba en el host pero no en el contenedor.

**Lección:**
El parámetro `bind` define en qué lado está el socket `listen`. Ver la tabla de referencia y casos de uso en [05_Configuracion.md — Dispositivo proxy LXD](05_Configuracion.md). Si el proxy está configurado al revés, ver [TRB-003 — 07_Troubleshooting.md](07_Troubleshooting.md#trb-003).

---

## LL-003 — Cloud-init se ejecuta solo al primer arranque

**¿Qué pasó?**
El equipo intentó aplicar cambios en la configuración de cloud-init simplemente reiniciando el contenedor. Los cambios no se aplicaron.

**Lección:**
Cloud-init es un mecanismo de inicialización de primer arranque, no de gestión continua. Una vez ejecutado, no vuelve a correr aunque se modifique el perfil o se reinicie el contenedor. Para aplicar cambios, el contenedor debe ser eliminado y recreado.

Ver la explicación completa y el procedimiento en [TRB-002 — 07_Troubleshooting.md](07_Troubleshooting.md#trb-002) y [05_Configuracion.md](05_Configuracion.md).

---

## LL-004 — Las imágenes cacheadas hacen el despliegue instantáneo

**¿Qué pasó?**
Al crear el segundo contenedor desde la imagen base de Ubuntu, LXD no descargó la imagen nuevamente. La usó desde la caché local. El contenedor estuvo listo en segundos.

**Lección:**
LXD cachea las imágenes descargadas. La primera vez que se lanza un contenedor desde `ubuntu:24.04`, descarga la imagen (~500 MB). Todas las veces siguientes, usa la imagen cacheada.

**Extensión:** Si se publica un contenedor configurado como imagen personalizada (`lxc publish CONTENEDOR --alias NOMBRE`), clonar desde esa imagen es también prácticamente instantáneo — sin descarga, sin cloud-init.

**Estrategia recomendada:**
1. Configurar un contenedor modelo (con todos los paquetes necesarios).
2. Publicarlo como imagen: `lxc publish MODELO --alias imagen-apache-php`.
3. Clonar desde esa imagen para todos los contenedores de producción.

---

## LL-005 — Modo incógnito para el primer acceso con certificado TLS

**¿Qué pasó?**
Daniel intentó acceder a la Web UI con su navegador habitual. El navegador había rechazado el certificado TLS en un intento anterior y guardó ese rechazo en caché. Aunque generó el certificado correctamente, el navegador seguía bloqueando el acceso.

**Lección:**
Si el navegador rechazó el certificado TLS de LXD, usar modo incógnito para el primer acceso con el certificado nuevo. El modo incógnito no tiene caché de rechazos de certificados.

Ver procedimiento completo de diagnóstico y solución en [TRB-004 — 07_Troubleshooting.md](07_Troubleshooting.md#trb-004).

---

## LL-006 — Separar la base de datos del frontend en contenedores distintos

**¿Qué pasó?**
El equipo preguntó si debían hospedar Apache/PHP y la base de datos en el mismo contenedor. Norberto fue explícito al respecto.

**Lección:**
> "Vamos a tratar de mantener esta metodología: tener contenedores separados para las bases de datos y contenedores separados para los frontends. [...] Eso te da maniobrabilidad: si vos tenés que hacer algo con tu frontend, cambiar algo acá, cambiar la versión de PHP, no tenés que reinstalar todo — tu base de datos se mantiene ahí separadita sola."

**Regla:** Un servicio por contenedor. Nunca mezclar base de datos con aplicación web en el mismo contenedor.

---

## LL-007 — Solicitar backup de VM a SBA/AIT desde el inicio

**¿Qué pasó?**
Norberto mencionó que al crear las VMs en VMware, el equipo debe pedir formalmente a SBA o AIT que configuren backup para esas VMs.

**Lección:**
> "Cuando se crean estas VMs a nivel de VMware, tienen que pedirle a SBA o AIT que la VM que se le está creando tenga backup."

El backup de la VM es la red de seguridad para situaciones catastróficas: falla de disco ZFS, error humano grave, corrupción de datos. No pedirlo al inicio significa que si ocurre un desastre antes de que se pida, no hay punto de restauración.

**Regla:** Solicitar backup de VM a SBA/AIT **antes** de crear contenedores de producción en ese nodo.

---

## LL-008 — Verificar siempre el estado de cloud-init antes de asumir que funciona

**¿Qué pasó?**
Después de crear el primer contenedor con cloud-init, Norberto no asumió que funcionó — verificó explícitamente con `cloud-init status` y luego con `ss -ntlp` para confirmar que Apache estaba escuchando en el puerto 80.

**Lección:**
Nunca asumir que cloud-init ejecutó correctamente. Siempre ejecutar `cloud-init status` y `ss -ntlp` antes de declarar el contenedor listo. Ver los comandos completos en [06_Operacion.md — Verificación después de crear](06_Operacion.md).

---

## LL-009 — El dispositivo proxy es temporal; OVN es la solución permanente

**Lección implícita de la reunión:**
Norberto fue claro en que el dispositivo proxy LXD (tanto el de salida a internet como el de exposición de servicios) es una **solución temporal** mientras OVN no está disponible.

> "Esto idealmente no tiene que estar acá. Vamos a hacer por esta vez porque no tenemos todavía interfaces para los contenedores."

**Implicación:**
No escalar la arquitectura basándose en dispositivos proxy LXD. Cuando OVN esté activo, eliminarlos de todos los perfiles y contenedores. Ver la configuración completa del dispositivo proxy en [05_Configuracion.md — Dispositivo proxy LXD](05_Configuracion.md).

---

## Documentos relacionados

| Tema | Documento |
|---|---|
| Operación con contenedores | [06_Operacion.md](06_Operacion.md) |
| Troubleshooting de los problemas que generaron estas lecciones | [07_Troubleshooting.md](07_Troubleshooting.md) |
| Configuración de cloud-init y proxy | [05_Configuracion.md](05_Configuracion.md) |
