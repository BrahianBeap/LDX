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

## LL-010 — Un problema de red intermitente puede tener causa raíz en el reloj del sistema, no en la red

**¿Qué pasó?**
Norberto Núñez relató una experiencia previa: durante una implementación anterior del cluster, la interfaz mostraba errores intermitentes al intentar migrar contenedores o hacer cambios — a veces funcionaba, a veces no, sin patrón aparente. Después de investigar, la causa fue una pequeña diferencia horaria (1-2 segundos) entre los relojes de los nodos del cluster.

**Lección:**
Cuando un cluster distribuido con base de datos consensuada (Dqlite, usada tanto por LXD como por MicroOVN) muestra comportamiento errático e intermitente, verificar la sincronización de reloj (NTP) **antes** de asumir que es un problema de red o de configuración. El síntoma (bloqueos aleatorios) puede ser engañoso.

Ver [TRB-009 en 07_Troubleshooting.md](07_Troubleshooting.md#trb-009) y la configuración recomendada en [04_Instalacion.md](04_Instalacion.md).

---

## LL-011 — `snap refresh --hold` es obligatorio en un cluster, no opcional

**¿Qué pasó?**
Norberto Núñez explicó que, sin este comando, `snapd` busca actualizaciones de LXD y MicroOVN una vez por día. Si un nodo tiene salida a internet (o a un repositorio distinto) y otro no, o simplemente se actualizan en momentos distintos, terminan con versiones diferentes — y el cluster bloquea todas las operaciones de configuración hasta que todos los nodos vuelvan a coincidir en versión.

**Lección:**
Aplicar `snap refresh --hold` inmediatamente después de instalar LXD y MicroOVN en cada nodo. Las actualizaciones deben hacerse siempre de forma manual y coordinada, el mismo día, en todos los nodos del cluster.

Ver [TRB-010 en 07_Troubleshooting.md](07_Troubleshooting.md#trb-010) y el procedimiento en [04_Instalacion.md](04_Instalacion.md).

---

## LL-012 — Los nombres de interfaz de red deben ser idénticos en todo el cluster

**¿Qué pasó?**
Cada VM llegó con nombres de interfaz distintos, asignados por el sistema operativo (ej. `NS35` en Carpinelli, `NS192` en Franco). Marcos Casco preguntó si esto era un problema. Norberto Núñez explicó que sí lo es: cuando un contenedor migra de un nodo a otro, se lleva consigo la configuración de red tal cual está, incluido el nombre de la interfaz a la que estaba asociado — si el nodo destino no tiene una interfaz con ese mismo nombre, la migración queda inconsistente.

**Lección:**
Renombrar todas las interfaces de red relevantes (gestión y servicio) a un nombre común (`nicsrv1`, etc.) usando `netplan` con `match` por MAC y `set-name`, **antes** de crear cualquier contenedor. Esto no depende de que la VLAN física sea la misma entre sitios — solo el nombre lógico de la interfaz debe coincidir.

Ver el procedimiento completo en [04_Instalacion.md — Paso 0](04_Instalacion.md).

---

## LL-013 — Deshabilitar SSH en los contenedores de infraestructura reduce el riesgo de movimiento lateral

**¿Qué pasó?**
Al configurar los contenedores gateway de servicios, Norberto Núñez deshabilitó SSH explícitamente en cada uno, dejando la administración exclusivamente vía `lxc exec`.

**Lección:**
Para contenedores que no necesitan ser accedidos desde afuera (routers internos, gateways), deshabilitar SSH reduce la superficie de ataque: si un contenedor del cluster llegara a estar comprometido, no hay un canal SSH adicional para saltar lateralmente hacia otros contenedores. La gestión vía `lxc exec` no depende de un servicio de red expuesto dentro del contenedor. SSH se reserva únicamente para los contenedores que deliberadamente necesitan ser accedidos como servidores desde el exterior.

Ver la configuración en [05_Configuracion.md](05_Configuracion.md).

---

## LL-014 — Limitar el tamaño de journald en contenedores de infraestructura

**¿Qué pasó?**
Al configurar el contenedor gateway de servicios, Norberto Núñez limitó `journald` a 100 MB explícitamente, señalando que por defecto puede acumular hasta 4 GB de logs.

**Lección:**
Un contenedor que actúa como router/gateway (sin aplicaciones propias) no necesita retener grandes volúmenes de logs. Limitar `journald` explícitamente evita que un contenedor de infraestructura consuma espacio de disco de forma desproporcionada a su función. El límite adecuado depende del rol del contenedor — no aplicar el mismo límite bajo a un contenedor que sí aloja una aplicación con logs relevantes.

Ver la configuración en [05_Configuracion.md](05_Configuracion.md).

---

## LL-015 — Ubuntu 26.04 LTS reemplaza `sudo` por `sudo-rs` y eso puede romper la instalación de SSSD/LDAP

**¿Qué pasó?**
Durante la reunión, Norberto Núñez mencionó al pasar que Ubuntu 26.04 LTS "tiene una pequeña diferencia con 24.04, que es que el sudo es distinto" y que había que "poner el uno" en un prompt con dos alternativas — sin más detalle audible en la grabación. La bitácora técnica (OneNote) confirma el contexto exacto: al instalar `sssd`/`sssd-ldap` en Ubuntu 26.04 LTS, el sistema pregunta con `update-alternatives --config sudo` cuál de las dos implementaciones de `sudo` usar — la clásica (`sudo`) o la reescritura en Rust (`sudo-rs`), que Canonical introdujo como opción en 26.04.

**Lección:**
En hosts con Ubuntu 26.04 LTS, ejecutar `update-alternatives --config sudo` explícitamente y elegir la opción clásica (`sudo`, no `sudo-rs`) antes o después de instalar SSSD, para evitar incompatibilidades con la integración LDAP/PAM que asume el comportamiento tradicional de `sudo`. Este paso no existe en Ubuntu 24.04 LTS.

Ver el procedimiento completo de SSSD/LDAP en [`onenote/Clúster-OSS/Clúster/SSSD.md`](../onenote/Clúster-OSS/Clúster/SSSD.md).

---

## LL-016 — Los "proxy devices" de LXD no son migrables fuera del proyecto `default`

**¿Qué pasó?**
Durante la reunión, al intentar migrar un contenedor de prueba desde el proyecto `default` hacia `PRJ-OSS` (o un proyecto equivalente), la operación falló con el error `can not receive local origin for clone local container`. Norberto Núñez explicó la causa: LXD restringe los dispositivos de tipo `proxy` (los mismos usados para exponer servicios o dar salida a internet antes de que OVN esté disponible, ver [05_Configuracion.md](05_Configuracion.md)) exclusivamente al proyecto `default`, por diseño de seguridad — se asume que los usuarios de proyectos no-`default` no deberían poder modificar reglas a nivel de sistema operativo del host. Además, intentar migrar directamente desde un **snapshot** entre proyectos tampoco funciona: los snapshots no son migrables entre proyectos.

**Lección:**
Antes de migrar un contenedor de un proyecto a otro, si tiene dispositivos `proxy` configurados, hay que quitarlos primero. El procedimiento que funcionó: hacer una **copia normal del contenedor** (no un snapshot), quitar los dispositivos `proxy` de esa copia, y recién entonces migrar la copia limpia al proyecto de destino. Ver el procedimiento completo en [06_Operacion.md — Migrar un contenedor entre proyectos LXD](06_Operacion.md) y la ampliación de este límite en [ADR-0007](adr/ADR-0007-proyectos-lxd-multitenancy.md).

---

## LL-017 — Snapshot antes de cualquier cambio riesgoso, y reglas de firewall primero en runtime

**¿Qué pasó?**
Norberto Núñez recomendó, antes de aplicar cambios de configuración de los que no se está completamente seguro, tomar un snapshot del contenedor para poder revertir rápidamente si algo sale mal. En la misma línea, contó una anécdota personal: hace aproximadamente 8 años perdió reglas de firewall completas al reiniciar un servicio, porque las había probado únicamente en runtime (`firewall-cmd` sin `--permanent`) y nunca las promovió a la configuración persistente.

**Lección:**
1. **Tomar un snapshot del contenedor** (`lxc snapshot`) antes de cualquier cambio de configuración incierto — es una operación rápida, distinta de publicar una imagen completa (`lxc publish`, ver [LL-004](12_Lecciones_Aprendidas.md#ll-004--las-imágenes-cacheadas-hacen-el-despliegue-instantáneo)). El snapshot es por contenedor: si un servicio tiene frontend y base de datos en contenedores separados, cada uno necesita su propio snapshot.
2. **Probar siempre las reglas de firewall primero en runtime, confirmarlas, y recién después persistirlas** con `--permanent` o `--runtime-to-permanent` (ver [05_Configuracion.md](05_Configuracion.md)). Aplicar una regla directamente como `--permanent` sin haberla probado antes es la forma más común de terminar con una regla incorrecta persistida — o, peor, de perder reglas al reiniciar si nunca se promovieron desde runtime.

Ver el comando de snapshot en [06_Operacion.md](06_Operacion.md).

---

## Documentos relacionados

| Tema | Documento |
|---|---|
| Operación con contenedores | [06_Operacion.md](06_Operacion.md) |
| Troubleshooting de los problemas que generaron estas lecciones | [07_Troubleshooting.md](07_Troubleshooting.md) |
| Configuración de cloud-init y proxy | [05_Configuracion.md](05_Configuracion.md) |
