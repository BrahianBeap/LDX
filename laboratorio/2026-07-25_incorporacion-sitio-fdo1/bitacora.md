# Bitácora — Incorporación de FDO1

Registro fase por fase, en el mismo orden que
[`docs/06_Operacion.md` — checklist de incorporación de sitios](../../docs/06_Operacion.md).
Cada fase se completa con lo que realmente se ejecutó (no solo lo que
"debería" hacerse) — incluyendo desvíos o problemas encontrados.

---

## Fase 0 — Antes de tocar una terminal

**Estado: ✅ Completada** (verificado 2026-07-25, por SSH de solo lectura)

- [x] VM de `fdo-oss1` existe, con dos interfaces de red (gestión y servicio).
- [x] Número de sitio confirmado: **FDO**, con los valores ya reservados en [`02_Arquitectura.md`](../../docs/02_Arquitectura.md):

  | Dato | Valor reservado |
  |---|---|
  | IP interna WireGuard (`wg0`) | `169.254.0.2` |
  | IP del gateway de servicios en `OVN_1` (`FDO-OSS-GW-SRV`) | `192.168.0.4` |
  | IP del gateway de OAM en `OVN_1` (`FDO-GW-OAM`) | `192.168.0.9` |
  | IP de gestión (`nic_oam`) | `10.150.32.101/24`, VLAN 701 |
  | IP de servicio (`nic_srv1`) | `10.11.11.x/24`, VLAN 5 (a confirmar el host exacto en Fase 6) |

---

## Fase 1 — Sistema operativo, LXD y MicroOVN

### Paso 0 — Renombrar interfaces con netplan

**Estado: ✅ Completada** (verificado 2026-07-25)

Archivo aplicado en `fdo-oss1` (`/etc/netplan/00-installer-config.yaml`):

```yaml
network:
 version: 2
 ethernets:
  nic_srv1:
   match:
     macaddress: 00:50:56:a3:c4:e3
   set-name: nic_srv1
   dhcp4: false
   dhcp6: false
  nic_oam:
   match:
     macaddress: 00:50:56:a3:d6:5e
   set-name: nic_oam
   dhcp4: false
   addresses:
    - 10.150.32.101/24
   routes:
    - to: default
      via: 10.150.32.1
   nameservers:
    addresses:
      - 10.129.4.176
      - 10.129.4.177
# tunnels: ...  (bloque de WireGuard, todavía comentado — ver Fase 2)
```

**Verificación real (2026-07-25):**

```
$ ip -4 addr show
nic_oam: inet 10.150.32.101/24 brd 10.150.32.255 scope global nic_oam   ✅
nic_srv1: (sin dirección IPv4 — esperado, ver nota abajo)

$ ip link show nic_srv1
3: nic_srv1: <BROADCAST,MULTICAST,UP,LOWER_UP> ... state UP
    link/ether 00:50:56:a3:c4:e3   ✅ (MAC coincide, interfaz activa)
```

> **Nota:** que `nic_srv1` no tenga IPv4 a nivel de sistema operativo es
> **correcto y esperado** — esa IP la va a llevar el contenedor gateway de
> servicios (`FDO-OSS-GW-SRV`) vía el driver IPVLAN, no el host. Mismo
> patrón que PFR1 y CAR1.

**Contexto de por qué quedó a medias:** esta configuración se hizo durante
una reunión con Norberto Núñez que se cortó antes de continuar con el
resto de la Fase 1 y la Fase 2 (WireGuard).

### Resto de la Fase 1 (`snap install lxd`, `snap refresh --hold`, `snap install microovn`, proxy)

**Estado: 🟡 En progreso — bloqueado por un tema de red (ver abajo)**

Este tramo se ejecutó **deliberadamente en el orden "ingenuo"** (seguir la
checklist literal, sin configurar el proxy de antemano) para documentar
qué le pasa a alguien que hace exactamente eso — no el camino optimizado.

#### Intento 1 — `snap install lxd` sin proxy configurado

```
root@fdo-oss1:~# snap install lxd
error: unable to contact snap store
```

**Diagnóstico:** `snap` no tenía ningún proxy configurado. A diferencia de
`apt`, `snap` **no** lee `/etc/apt/apt.conf.d/` ni las variables de
entorno `http_proxy`/`https_proxy` — tiene su propio mecanismo, separado.

**⚠️ Hallazgo sobre la checklist de [`06_Operacion.md`](../../docs/06_Operacion.md):**
la configuración de proxy está descrita recién en la Fase 5, pero en la
práctica **hace falta antes de la Fase 1** para que `snap install`
funcione. Se agregó una nota de excepción en el documento (ver más abajo).

#### Intento 2 — Configurar el proxy de `snap` y de `apt`

```bash
sudo snap set system proxy.http=http://10.150.32.100:3128
sudo snap set system proxy.https=http://10.150.32.100:3128
```

Para `apt`, el primer intento fue con un heredoc pegado en la sesión SSH:

```bash
sudo bash -c 'cat > /etc/apt/apt.conf.d/99proxy.conf <<HERE
Acquire::http::Proxy "http://10.150.32.100:3128";
Acquire::https::Proxy "http://10.150.32.100:3128";
HERE'
```

**⚠️ Hallazgo — heredocs pegados por SSH pueden corromperse:** el cliente
SSH indentó las líneas pegadas, y bash no reconoció el `HERE` (con
espacios adelante) como cierre del bloque:

```
bash: line 4: warning: here-document at line 1 delimited by end-of-file (wanted `HERE')
```

El archivo quedó con una línea `HERE` literal al final, lo cual rompe el
archivo de configuración. **Se corrigió evitando el heredoc por completo**,
con `echo` línea por línea (no depende de que el pegado sea exacto):

```bash
sudo sh -c 'echo "Acquire::http::Proxy \"http://10.150.32.100:3128\";" > /etc/apt/apt.conf.d/99proxy.conf'
sudo sh -c 'echo "Acquire::https::Proxy \"http://10.150.32.100:3128\";" >> /etc/apt/apt.conf.d/99proxy.conf'
```

Verificado con `cat` — el archivo quedó con exactamente las dos líneas
esperadas.

**Lección general:** al pasar comandos multilínea (heredocs) por copiar y
pegar en una sesión SSH interactiva, preferir `echo`/`printf` línea por
línea, o subir el archivo ya armado (`scp`/`pscp`) en vez de pegarlo a
mano — el heredoc es frágil ante cualquier indentado que agregue el
cliente SSH al pegar.

#### Intento 3 — `snap install lxd` con el proxy ya configurado

```
root@fdo-oss1:~# snap install lxd
error: cannot install "lxd": Post "https://api.snapcraft.io/v2/snaps/refresh": proxyconnect tcp:
       dial tcp 10.150.32.100:3128: connect: no route to host
```

El proxy está bien configurado, pero el host **no puede llegar** a
`10.150.32.100:3128`. Se diagnosticó sin instalar herramientas nuevas
(el sistema no tenía `ping`, `iptables` ni `ufw`):

```bash
# Probar el puerto real del proxy con un builtin de bash (no requiere instalar nada):
timeout 3 bash -c "echo > /dev/tcp/10.150.32.100/3128" && echo "CONECTA" || echo "NO conecta"
# -> NO conecta ("No route to host")

# Probar que al menos el gateway de la VLAN responde:
timeout 3 bash -c "echo > /dev/tcp/10.150.32.1/22" && echo "CONECTA" || echo "NO conecta"
# -> CONECTA (el gateway sí responde)

# Ver si se resolvió la MAC del proxy por ARP:
ip neigh
# -> 10.150.32.100 dev nic_oam lladdr 00:50:56:a3:75:4c REACHABLE
```

**Diagnóstico final:**

| Evidencia | Qué descarta / confirma |
|---|---|
| `ip neigh` muestra al proxy como `REACHABLE` | Descarta un problema de VLAN/capa 2 — el host sí ve al proxy en la red |
| El gateway de la VLAN responde en otro puerto | Descarta que la VLAN 701 esté mal armada de punta a punta |
| No hay `iptables` ni `ufw` instalados en el host | Descarta un firewall local en `fdo-oss1` |
| La conexión da "No route to host" (no timeout, no "connection refused") | Consistente con un **firewall/ACL de red explícito** rechazando el tráfico de este host puntualmente |

**Conclusión: `fdo-oss1` (10.150.32.101) todavía no está autorizado/dado de
alta para salir hacia el proxy corporativo.** Es el mismo trámite de red
que se hizo para PFR1 y CAR1 al incorporarlos — se resuelve pidiendo al
equipo de seguridad/red que habilite el acceso desde esta IP al proxy
`10.150.32.100:3128`, no desde la terminal del host.

**🔴 Bloqueante activo — 2026-07-25.** Responsable: equipo de seguridad/red
(mismo circuito que habilitó el proxy para PFR1/CAR1). El resto de la
Fase 1 (`snap install lxd`, `snap install microovn`) queda en pausa hasta
que se resuelva esto.

---

## Fase 2 — Conectar a la malla WireGuard

**Estado: 🔴 Pendiente**

Verificado 2026-07-25: no está instalado `wireguard-tools`, no existe
`/etc/wireguard/`. El bloque `tunnels: wg0` del netplan está comentado tal
cual quedó en la reunión cortada.

⚠️ Esta fase también requiere editar el `netplan` de **PFR1 y CAR1**
(agregar a FDO como peer nuevo) — se acordó explícitamente hacer esto como
un paso aparte, después de terminar el resto de la Fase 1 en `fdo-oss1`.

_(Completar esta sección cuando se ejecuten los comandos.)_

---

## Fase 3 — Unir el nuevo nodo al cluster LXD

**Estado: 🔴 Pendiente** — no se puede empezar hasta cerrar la Fase 2.

---

## Fase 4 — Unir el nuevo nodo al cluster OVN

**Estado: 🔴 Pendiente** — no se puede empezar hasta cerrar la Fase 2.

---

## Fase 5 — Firewall, proxy, NTP y usuarios

**Estado: 🔴 Pendiente**

---

## Fase 6 — Crear los contenedores gateway del nuevo sitio

**Estado: 🔴 Pendiente**

---

## Fase 7 — Verificación end-to-end

**Estado: 🔴 Pendiente**
