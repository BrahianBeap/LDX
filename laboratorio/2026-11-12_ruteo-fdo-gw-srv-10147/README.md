# Ruteo de FDO-GW-SRV hacia la red 10.147.x (incidente y plan de remediación, 2026-11-12)

> Estado: **Paso 1 y Paso 2 aplicados y verificados (2026-11-12).**
> Las 9 rutas por `10.11.11.253` (y la de `eth0`) están declaradas en `/etc/netplan/90-oss-rutas.yaml` (copia en esta carpeta) y figuran en la tabla con `proto static`. Pendiente: prueba de reboot controlado y la consulta a Seguridad sobre prefijos.

## Contexto

Se pidió por Jerure un **permiso de firewall** para que `FDO-GW-SRV` alcanzara `10.147.8.2:22` (SSH).
Seguridad (Maximiliano Romero) probó en el contenedor por `lxc`, concluyó que **no es un problema de firewall sino de ruteo**, y **cerró** el ticket dejando la configuración permanente a cargo del dueño del servidor (nosotros, OSS, que operamos el contenedor por `lxc`).

- Informe de Seguridad: `FDO-GW-SRV_Routing_Incident_Report.pdf` (adjunto al ticket de Jerure).
- `FDO-GW-SRV` = gateway de servicios de Fernando, proyecto `PRJ-OSS`. Su interfaz de servicio `eth1` es `10.11.11.12/24` (ipvlan L2 en la LAN de servicio de Fernando). Ver [02_Arquitectura.md](../../docs/02_Arquitectura.md).

## Diagnóstico de Seguridad (resumen del informe)

| Dato | Valor |
|---|---|
| Origen | `FDO-GW-SRV`, `10.11.11.12/24` en `eth1` |
| Destino | `10.147.8.2` / TCP 22 (SSH) |
| Gateway elegido (falla) | `10.11.11.1` → responde *Destination Net Unreachable* |
| Gateway alternativo (funciona) | `10.11.11.253` → ICMP OK y banner `SSH-2.0-OpenSSH_8.8` |
| Prueba de Seguridad | Agregaron `10.147.8.2/32 via 10.11.11.253` **temporal**, verificaron, y la **quitaron** |
| Veredicto | No hay bloqueo de firewall local; la ruta por `.1` no alcanza `10.147.x`. Falta ruta persistente por `.253` |

✅ Coincide con nuestra arquitectura: `10.147.0.0/x` es una red corporativa que **no** cae bajo la ruta de salida `10.150.0.0/16` (que sale por el OAM `192.168.0.6` con doble NAT). Es otra LAN, alcanzable por el segundo router de la red de servicio, `10.11.11.253`.

## Verificación en vivo (2026-11-12, solo lectura)

Confirmado desde `pfr-oss` con `lxc exec FDO-GW-SRV --project PRJ-OSS`:

```
# ip -4 route get 10.147.8.2
10.147.8.2 via 10.11.11.1 dev eth1 src 10.11.11.12      <- sale por el gateway que NO llega
```

Tabla de rutas relevante (`eth1`, red de servicio):

```
default via 10.11.11.1   dev eth1 proto static          <- default (gana; sin metric)
default via 192.168.0.254 dev eth0 proto dhcp metric 100
10.11.11.0/24 dev eth1 proto kernel scope link src 10.11.11.12
10.12.151.30  via 10.11.11.253 dev eth1   \
10.12.151.202 via 10.11.11.253 dev eth1    |
10.12.151.220 via 10.11.11.253 dev eth1    |
10.12.151.222 via 10.11.11.253 dev eth1    |  7 destinos de monitoreo SNMP
10.12.151.238 via 10.11.11.253 dev eth1    |  (snmpwalk / snmptrapd / 162)
10.12.151.249 via 10.11.11.253 dev eth1    |
10.12.151.250 via 10.11.11.253 dev eth1   /
10.147.5.119  via 10.11.11.253 dev eth1       <- la "preexistente" que cita el informe
```

Camino del tráfico:

```
          10.11.11.12 (FDO-GW-SRV eth1)
                 │
      ┌──────────┴───────────┐
      ▼                      ▼
  10.11.11.1              10.11.11.253
  (default)              (ruta a 10.147.x / 10.12.151.x)
      │                      │
   ✗ Net Unreachable      ✓ ICMP + SSH:22
      ▼                      ▼
                  10.147.8.2
```

## Dos hallazgos que el informe NO contempla

### 🔴 Hallazgo 1 — Las rutas por `.253` son de *runtime*, no persistentes

Las siete `10.12.151.x`, la `10.147.5.119` (y una `10.150.58.126 via 192.168.0.1` en `eth0`, 🟡 propósito desconocido) **se agregaron a mano** con `ip route add` — están en `/root/.bash_history` del contenedor, no tienen `proto` en la tabla y **no figuran en `netplan`** (`/etc/netplan/50-cloud-init.yaml` solo define el default por `.1` en `eth1` y `10.150.32.100 via 192.168.0.6` en `eth0`).

- El contenedor lleva **12 semanas sin reiniciar** (arranque 2026-08-18). Esas rutas sobreviven solo porque nadie reinició ni reconfiguró la red.
- **En el próximo reboot se pierden todas**, incluida la `10.147.5.119` que el informe llama "preexistente". Es una **fragilidad latente** del gateway, independiente de este pedido.

### 🔴 Hallazgo 2 — `ManageForeignRoutes=yes` + cloud-init: un `netplan apply` descuidado rompe el monitoreo

- `systemd-networkd` está con el **default `ManageForeignRoutes=yes`** (sin override). Al reconfigurar `eth1` (lo que hace `netplan apply`), **borra las rutas "ajenas"** (las agregadas a mano) → se caería el **monitoreo SNMP** a `10.12.151.x` y el camino a `10.147.5.119`.
- `cloud-init` sigue activo (`cloud-init-network.service` enabled) y **no** hay `99-disable-network-config`. Editar `50-cloud-init.yaml` directo es riesgoso: un boot podría regenerarlo.

> **Conclusión:** agregar la ruta es fácil; **persistirla bien requiere cuidado**, porque el gateway hoy se sostiene sobre rutas no persistentes y el mecanismo de netplan puede barrerlas.

## Plan de remediación — en 2 pasos

### Paso 1 — Desbloqueo inmediato (reversible, igual que las otras 8 rutas)

#### Objetivo
Que `FDO-GW-SRV` alcance `10.147.8.2:22` hoy, sin tocar firewall, default ni netplan.

#### Comando
```bash
lxc exec FDO-GW-SRV --project PRJ-OSS -n -- ip route add 10.147.8.2/32 via 10.11.11.253 dev eth1
```

#### Explicación
Redirige **solo** ese destino `/32` al router que sí lo alcanza (`.253`), replicando el patrón ya existente. No es persistente (se pierde en reboot), igual que las otras 8 rutas actuales.

#### Resultado esperado / Cómo verificar
```bash
lxc exec FDO-GW-SRV --project PRJ-OSS -n -- ip -4 route get 10.147.8.2
# Esperado: 10.147.8.2 via 10.11.11.253 dev eth1 src 10.11.11.12
lxc exec FDO-GW-SRV --project PRJ-OSS -n -- ping -c 3 10.147.8.2
lxc exec FDO-GW-SRV --project PRJ-OSS -n -- curl -v --connect-timeout 5 telnet://10.147.8.2:22   # banner SSH-2.0-...
```

#### Rollback
```bash
lxc exec FDO-GW-SRV --project PRJ-OSS -n -- ip route del 10.147.8.2/32 via 10.11.11.253 dev eth1
```

#### ✅ Ejecución (2026-11-12, `alfonzel_opr@pfr-oss`)

El `ip route add` devolvió sin salida (éxito). Verificación posterior:

| Prueba | Resultado |
|---|---|
| `ip -4 route get 10.147.8.2` | `10.147.8.2 via 10.11.11.253 dev eth1 src 10.11.11.12` (antes: `via 10.11.11.1`) |
| `ping -c 3 10.147.8.2` | 3/3 recibidos, 0% pérdida, ~0,3 ms, `ttl=63` (un salto: el router `.253`) |
| `curl telnet://10.147.8.2:22` | Conexión establecida desde `10.11.11.12`, banner `SSH-2.0-OpenSSH_8.8` |

Coincide exactamente con lo que Seguridad obtuvo en su prueba temporal. El acceso SSH a `10.147.8.2` queda **operativo en runtime**.

### Paso 2 — Persistencia correcta (programado, con ventana)

No hacer un `netplan apply` "a secas". El procedimiento seguro:

1. **Confirmar con Seguridad/red el alcance (🟡 pendiente):** ¿un `/32` por destino, o aprueban un **prefijo** (`10.147.0.0/16` y `10.12.151.0/24` vía `.253`)? El propio informe pide no usar un rango sin validación de la red. Un prefijo elimina la necesidad de sumar un `/32` cada vez.
2. **Rescatar las 8 rutas frágiles a la vez:** persistir en netplan el default por `.1` **más** todas las rutas por `.253` que se usan hoy (monitoreo incluido) + la nueva `10.147.8.2`. Así el cambio es un *superset* y no se cae nada.
3. **Evitar que cloud-init lo pise:** usar un archivo propio `/etc/netplan/90-oss-rutas.yaml` (o además `/etc/cloud/cloud.cfg.d/99-disable-network-config.cfg` con `network: {config: disabled}`).
4. **Aplicar con red de seguridad:** `netplan generate` + **`netplan try`** (auto-revierte a los 120 s), en ventana, con acceso de recuperación por `lxc exec` (consola fuera de la red de servicio). Verificar que sobreviven el monitoreo **y** el enlace nuevo.
5. **Prueba de reboot** controlada para confirmar persistencia.

Archivo propio, **sin tocar `50-cloud-init.yaml`** (que conserva el default por `.1` y la ruta de `eth0`). Netplan combina los archivos en orden alfabético y este solo *agrega* rutas; se valida con `netplan generate` que el default sigue presente antes de aplicar:

```yaml
# /etc/netplan/90-oss-rutas.yaml  (modo 0600)
network:
  version: 2
  ethernets:
    eth0:
      routes:
        - {to: "10.150.58.126/32", via: "192.168.0.1"}   # 🟡 preexistente a mano, propósito desconocido
    eth1:
      routes:
        - {to: "10.147.8.2/32",    via: "10.11.11.253"}   # nuevo (este pedido, Paso 1)
        - {to: "10.147.5.119/32",  via: "10.11.11.253"}
        - {to: "10.12.151.30/32",  via: "10.11.11.253"}
        - {to: "10.12.151.202/32", via: "10.11.11.253"}
        - {to: "10.12.151.220/32", via: "10.11.11.253"}
        - {to: "10.12.151.222/32", via: "10.11.11.253"}
        - {to: "10.12.151.238/32", via: "10.11.11.253"}
        - {to: "10.12.151.249/32", via: "10.11.11.253"}
        - {to: "10.12.151.250/32", via: "10.11.11.253"}
```

> **Advertencia:** si Seguridad aprueba un prefijo, esta lista se reemplaza por `10.147.0.0/16` y `10.12.151.0/24` vía `.253` (más el default), que es más mantenible.

#### ✅ Ejecución (2026-11-12 18:43–19:00, `alfonzel_opr@pfr-oss`)

| Paso | Resultado |
|---|---|
| Snapshot `lxc snapshot` | ❌ `Project "PRJ-OSS" doesn't allow for snapshot creation` (restricción del proyecto). Reemplazado por respaldo en texto: `/root/rutas-antes-20261112.txt` (17 líneas) y `/root/netplan.bak-20261112/` |
| Escritura del archivo | Primer intento con heredoc por `lxc exec -n` **dejó el archivo vacío** (no reenvía stdin). Resuelto con `lxc file push --uid 0 --gid 0 --mode 0600` desde `pfr-oss`. Ver [90-oss-rutas.yaml](90-oss-rutas.yaml) |
| `netplan generate` | OK. `10-netplan-eth1.network` con **10 `[Route]`**: default `0.0.0.0/0 via 10.11.11.1` + 9 × `via 10.11.11.253`. ✅ Confirma que netplan **suma** las rutas de varios archivos (no reemplaza) |
| `netplan try` | Sin errores; aceptado con Enter |
| Tabla posterior | 9 rutas por `.253` con `proto static`; default por `.1` intacto; `eth0` con `10.150.32.100` y `10.150.58.126` (`proto static onlink`) |
| Pings | `10.147.8.2` ✅ (0,3 ms) · `10.147.5.119` ✅ (0,4 ms) · `10.12.151.30` ❌ *Destination Net Unreachable* **devuelto por `10.11.11.253`** |

Sobre `10.12.151.30`: la ruta funciona (el paquete llega al router `.253`); es el **router** el que no alcanza ese destino. Mismo next-hop que antes del cambio → no es consecuencia de la persistencia. ✅ Verificado con `10.12.151.202` (`ttl=253`, 0,5 ms) y `10.12.151.250` (`ttl=250`, 4,6 ms): ambos responden por `.253`, así que la red de monitoreo está sana y **`.30` es un caso aislado** (host o segmento no alcanzable desde `.253`). Derivar a quien administra el monitoreo; no bloquea nada de este cambio.

Lecciones de método:
- `lxc exec -n -- sh -c 'cat > archivo' <<EOF` **no sirve** para escribir archivos (stdin no llega). Usar `lxc file push`.
- `PRJ-OSS` no permite snapshots: el rollback de cambios de configuración debe planificarse con respaldos de archivos.

## Alcance al NCE desde Franco y Carpinelli (verificado 2026-11-12, solo lectura)

El ticket **#1089314** (Alta de Permisos - Firewall-17, Rocío Duarte, 06/11) listaba como orígenes también `fr-oss 10.143.11.8` y `car 192.168.91.112`. Seguridad probó **solo desde FDO** antes de cerrarlo. Se verificó el cuadro completo:

| Gateway | LAN de servicio | Gateway(s) en la LAN | `eth1` sana (TCP/53 a `10.129.4.176/177`) | TCP/22 a `10.147.8.2` | TCP/22 a `10.147.5.119` |
|---|---|---|---|---|---|
| `FDO-GW-SRV` | `10.11.11.0/24` | `.1` (default, MAC `d4:6d:50:…`) y `.253`/`.254` (MAC `08:ec:f5:…`, 🟡 pareja Cisco) | ❌ timeout por `.1` | ✅ (vía `.253`) | ✅ (vía `.253`) |
| `PFR-GW-SRV` | `10.143.11.0/26` | solo `.1` (VRRP `00:00:5e:00:01:4d`; físicos `.2`/`.3`) | ✅ | ❌ **timeout** | ❌ **timeout** |
| `CAR-GW-SRV` | `192.168.91.96/27` | solo `.97` (VRRP `00:00:5e:00:01:45`; físicos `.98`/`.99`, MAC `08:ec:f5:…`) | ✅ | ❌ **timeout** | ❌ **timeout** |

Lectura:

- En Fernando el default `.1` es un equipo **distinto** de la pareja `.253`/`.254`, y es ese default el que no conoce `10.147.x` (ni `10.129.4.x`). Por eso allí la solución fue de ruteo en el contenedor: existía un next-hop alternativo.
- En Franco y Carpinelli **no existe un router alternativo**: el único gateway es el VRRP de la red, `eth1` funciona (los DNS corporativos conectan) y **toda `10.147.x`** da timeout silencioso (no *Net Unreachable*). ✅ No es un problema resoluble en el contenedor; es falta de ruta o bloqueo de firewall **aguas arriba**: exactamente el pedido original del ticket, que quedó cerrado sin probar estos orígenes.
- 🟡 Solo aplica si la colecta hacia el NCE va a correr también desde Franco/Carpinelli. Si es solo desde FDO, está resuelto.

Hallazgos secundarios:

- 🟡 `PFR-GW-SRV` y `CAR-GW-SRV` no tienen `ping` ni `traceroute` (sí `nc` y `curl`); `FDO-GW-SRV` sí tiene `ping`. Diagnóstico de red limitado a TCP.
- 🟡 Desde `FDO-GW-SRV`, los resolvers de `eth1` (`10.129.4.176/177`) no responden por TCP/53 (vía `.1`). La resolución **funciona** igual (`resolvectl query` resuelve en ~11 ms), presumiblemente por el resolver de `eth0` (`192.168.0.254`/`169.254.1.1`, OVN). No bloquea nada; conviene revisarlo si algún día falla DNS en FDO.
- 🟡 La ruta `10.12.151.30` no aparece ni en el historial de root del contenedor (0 líneas, contra 23 de `.202`) ni en el de `alfonzel_opr@pfr-oss`. Se agregó por otra vía (otro usuario/host con `lxc exec`, que no deja historial en el contenedor). Origen desconocido; destino inalcanzable desde `.253`. Si nadie del equipo la reclama, candidata a retirarse del YAML.

## Nota de seguridad (aparte del ruteo)

Al revisar cómo se agregaron las rutas, se encontró en `/root/.bash_history` de `FDO-GW-SRV` un **secreto en claro** (una *community* SNMP). No se reproduce aquí. **Recomendación:** rotar esa credencial y limpiar el history. 🔴 Pendiente.

## Responsabilidades y pendientes

| Responsable | Entregable |
|---|---|
| OSS (dueño del contenedor) | Aplicar el Paso 1 (si se autoriza) y el Paso 2 en ventana; documentar rollback |
| Seguridad / red | Confirmar que `10.11.11.253` es el next-hop soportado y aprobar el alcance (`/32` vs prefijo) |
| Verificación | Registrar `ip route get`, `ping` y TCP/22 después de aplicar y tras un reboot |

- ✅ Paso 1 aplicado y verificado el 2026-11-12 (runtime).
- ✅ Paso 2 aplicado y verificado el 2026-11-12 (`90-oss-rutas.yaml`, `netplan try` aceptado, 9 rutas `proto static`).
- 🟡 Prueba definitiva: reboot controlado de `FDO-GW-SRV` en horario tranquilo y repetir la verificación de rutas y pings.
- 🟡 `10.12.151.30` no alcanzable desde `.253` (caso aislado, preexistente; `.202` y `.250` sí responden): derivar a monitoreo.
- 🟡 `10.150.58.126 via 192.168.0.1` (`eth0`): persistida tal cual, propósito desconocido; confirmar si sigue en uso.
- 🟡 Consultar a Seguridad el prefijo antes de persistir.
- 🔴 Rotar el secreto SNMP del `bash_history`.
- 🟡 Proponer **TRB-024** (gateway no alcanza una red corporativa por falta de ruta específica) y **RIE-024** (gateways dependen de rutas no persistentes agregadas a mano) para los docs oficiales — ver abajo.

## El ticket y la IP de origen (aclaración para el equipo)

Ticket **#1089314** — "Alta de Permisos - Firewall-17", cargado por Rocío Duarte el 2026-11-06, aplicación 608 PLATAFORMA-LXD-OSS. Motivo: colecta por SSH del estado de los RE gestionados desde el **NCE** (`10.147.8.2:22`). Cerrado por Maximiliano Romero (Seguridad) el 2026-11-11 con el informe adjunto, habiendo probado solo desde `FDO-GW-SRV`.

Una confusión frecuente: "¿no salgo siempre por la IP del host?" (`fr-oss 10.143.11.228`, `car-oss 192.168.91.116`, `FDO-OSS 10.150.32.101`). **No.** Esas son las IPs de administración de los hosts, por donde entra el operador. El tráfico hacia el NCE lo genera el **contenedor gateway**, que tiene IP propia en la LAN de servicio (IPVLAN) y sale directo por el router de esa LAN con **su** IP: `10.143.11.8`, `192.168.91.117`, `10.11.11.12`. La prueba: el `curl` desde FDO conectó `from 10.11.11.12`. La IP del host solo aparece cuando una *aplicación* sale hacia `10.150.x` por el doble NAT del OAM. Tabla completa en [02_Arquitectura.md](../../docs/02_Arquitectura.md#ip-que-ve-el-firewall-corporativo-entrada-y-salida).

Consecuencias para el ticket:
- Los orígenes `10.11.11.12` y `10.143.11.8` están bien. 🟡 `192.168.91.112` ("car-dns-lxd") no corresponde a ningún contenedor de `PRJ-OSS`; el gateway de Carpinelli es **`.117`**.
- 🟡 Falta saber **desde qué contenedor** va a correr la colecta. Si es un contenedor de aplicación (OVN), su camino hacia `10.147.x` no existe todavía (solo tienen `10.150.0.0/16` vía OAM) y habría que sumar ruta + NAT por el gateway + ACL.

## Documentación oficial derivada

- [TRB-024](../../docs/07_Troubleshooting.md#trb-024--un-gateway-de-servicios-no-alcanza-una-red-corporativa-timeout-o-net-unreachable-y-seguridad-responde-que-no-es-firewall) — ficha de diagnóstico con los dos casos (ruteo en el contenedor vs. red corporativa).
- [RIE-024](../../docs/11_Riesgos.md#rie-024--rutas-agregadas-a-mano-en-los-gateways-no-persistentes) — rutas a mano no persistentes.
- [05_Configuracion.md — Rutas estáticas persistentes](../../docs/05_Configuracion.md#rutas-estáticas-persistentes-del-gateway-de-servicios-netplan) — el archivo `90-oss-rutas.yaml`, procedimiento y rollback.
- [02_Arquitectura.md — IP que ve el firewall](../../docs/02_Arquitectura.md#ip-que-ve-el-firewall-corporativo-entrada-y-salida) — fila nueva "Salida desde el propio gateway".
- [LL-021](../../docs/12_Lecciones_Aprendidas.md#ll-021--una-ruta-agregada-con-ip-route-add-no-existe-hasta-que-está-en-netplan) — lección aprendida.
- [13_Linea_de_Tiempo.md](../../docs/13_Linea_de_Tiempo.md#corto-plazo--consolidación-de-lo-implementado) — pendientes (PFR/CAR, reboot, SNMP).
