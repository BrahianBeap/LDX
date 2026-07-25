# Conclusiones

## Qué funcionó

- Crear un contenedor de aplicación nuevo en un proyecto LXD existente,
  reutilizando la imagen ya cacheada ahí.
- Copiar una aplicación PHP completa (3163 archivos) directo desde Windows
  al contenedor, sin pasar por git ni por internet, en dos saltos
  (`pscp` → host → `lxc file push` → contenedor).
- Instalar Apache + PHP 8.5 + SQLite y dejar corriendo Kanboard v1.2.46 sin
  incompatibilidades.
- Acceder a un servicio en una red interna del cluster (`OVN_1`, no
  ruteada) desde una PC externa, sin tocar el firewall del host, usando un
  túnel SSH sobre un dispositivo proxy de LXD bindeado a loopback.

## Qué no funcionó como se esperaba (y por qué)

### 1. Las imágenes son por-proyecto
**Supuesto:** cualquier imagen del servidor está disponible para lanzar un
contenedor en cualquier proyecto.
**Realidad:** con `features.images: true` (el default), cada proyecto tiene
su propio catálogo de imágenes. Hubo que usar la imagen que ya estaba en
`PRJ-OSS`, no la de `default`.

### 2. `--network` duplica la interfaz si el perfil ya trae una
**Supuesto:** hay que declarar explícitamente la red al lanzar el
contenedor.
**Realidad:** el perfil `default` de `PRJ-OSS` ya define una interfaz en
`OVN_1`. Pasar `--network` de nuevo genera un conflicto de nombre DNS entre
dos interfaces apuntando a la misma red.

### 3. `OVN_1` no es alcanzable desde fuera del cluster
**Supuesto (el más importante, y el que originó la pregunta del usuario):**
"¿puedo crear un contenedor y apuntar directo a su IP para verlo?"
**Realidad:** no. `192.168.0.0/24` es una red privada virtualizada interna
de OVN — no está ruteada hacia la red corporativa. Ni siquiera con los
gateways de servicio (`PFR-OSS-GW-SRV`) encendidos, porque esos todavía no
tienen configurado el NAT/reverse-proxy hacia contenedores individuales.
**Solución de esta prueba:** dispositivo proxy de LXD + túnel SSH.
**Solución "real" pendiente:** wireear el gateway de servicios con
reglas de reenvío explícitas — trabajo separado, más grande.

### 4. Un contenedor nuevo no tiene salida a internet por sí solo
**Supuesto:** configurar `Acquire::http::Proxy` alcanza para que `apt`
funcione.
**Realidad:** también hace falta una **ruta** hacia la IP del proxy
(`10.150.32.100`), porque esa IP está fuera de `OVN_1`. Se resuelve
agregando una ruta vía el contenedor gateway de OAM del sitio
(`PFR-GW-OAM`, `192.168.0.6`) — el mismo mecanismo que ya usa el perfil
oficial de gateway de servicios.
**Pendiente:** esa ruta no es persistente (`ip route add` se pierde en
cada reinicio). Para algo permanente habría que agregarla al
`cloud-init.network-config` o a un netplan, no se hizo acá por ser solo
una prueba.

### 5. Los proyectos restringidos bloquean dispositivos `proxy`
**Supuesto:** se podía exponer el contenedor de prueba sin salir de
`PRJ-OSS`.
**Realidad:** `PRJ-OSS` tiene `restricted: true` (ver
[ADR-0007](../../docs/adr/ADR-0007-proyectos-lxd-multitenancy.md)), lo que
bloquea dispositivos `proxy` por defecto. Se evaluó habilitarlo
(`restricted.devices.proxy=allow`) pero se descartó — eso afectaría a
**todo el proyecto**, aflojando una restricción de seguridad puesta a
propósito, solo para una prueba puntual. Se optó por mover el contenedor
de prueba a `default` (proyecto sin restricciones) en su lugar.

### 6. Los perfiles (y sus dispositivos) no viajan entre proyectos
**Supuesto:** mover un contenedor de proyecto (`lxc move ... --target-project`)
conserva su configuración de red.
**Realidad:** el contenedor quedó sin ninguna interfaz de red después de
moverse, porque el dispositivo de red venía heredado del perfil `default`
de `PRJ-OSS`, que no existe (con esa configuración) en `default`. Hubo que
agregar la interfaz a mano después de mover.

### 7. La cuenta usada no tiene `sudo` en este host
**Hallazgo, no un supuesto roto:** `alfonzel_opr` puede usar `lxc`
libremente (está en el grupo `lxd`), pero no tiene `sudo` en `pfr-oss` —
`firewall-cmd` y cualquier comando que necesite root no están disponibles
con esta cuenta en este host. Esto **determinó** la solución final (proxy a
loopback + túnel SSH) en vez del enfoque original (proxy a la IP pública +
regla de firewall nueva).

## Para la próxima vez

- Antes de crear un contenedor de prueba, revisar en qué proyecto conviene
  hacerlo según si necesita exposición externa (`default`) o aislamiento
  de equipo (`PRJ-OSS`, pero sin poder usar dispositivos `proxy`).
- Si el contenedor necesita internet, agregar la ruta al proxy corporativo
  como parte del cloud-init/perfil desde el principio, no como parche
  manual después.
- Confirmar de antemano si la cuenta que se va a usar tiene `sudo` en el
  host de destino, para no descubrirlo a mitad de la tarea.
