# Exploración — rutas, firewall e IP de servicio en `pfr-oss`

> **Fecha:** 2026-07-27
> **Motivo:** el usuario obtuvo acceso root real en `pfr-oss`
> (`10.143.11.228`) y quería evaluar si era viable abrir un rango de IP
> para que el equipo pueda acceder a Kanboard, en reemplazo del túnel SSH
> actual (ver
> [`../2026-07-24_kanboard-contenedor-prueba/README.md`](../2026-07-24_kanboard-contenedor-prueba/README.md)).
> **Alcance:** exploración de **solo lectura** — no se modificó ningún
> archivo de configuración, ninguna regla de firewall, ninguna ruta ni la
> base de datos. El objetivo era juntar información real para una
> conversación con Norberto, no tomar la decisión unilateralmente.
> **Credenciales:** las contraseñas reales usadas para esta sesión no se
> incluyen en este documento — se compartieron por chat y se usaron solo
> para las consultas puntuales de esta exploración.

---

## 1. Cómo se obtuvo acceso root

`sudo` seguía bloqueado para `alfonzel_opr` (`is not allowed to run sudo
on pfr-oss` — el mismo mensaje ya visto antes en la incorporación de
FDO1). El acceso root funcionó con `su -` y la contraseña de root
provista, no con `sudo`. 🟡 Esto sugiere que la cuenta `alfonzel_opr`
sigue sin estar habilitada en `sudoers`, y que "tener root" hoy significa
conocer la contraseña de la cuenta `root` directamente, no un permiso
elevado sobre la cuenta de trabajo — vale la pena confirmar con Norberto
si esa es la intención o un paso intermedio.

## 2. Firewall — estado real

**Zonas activas:**
- `work` → interfaz `ens192` (la de gestión, `10.143.11.228/29`). Es la
  única interfaz con reglas reales.
- `trusted` (zona por defecto, `target: ACCEPT`) → todas las demás
  interfaces (LXD, OVN, WireGuard) caen acá — el host no las filtra.

**Zona `work` — estilo de las reglas:** whitelist por IP puntual. Cada
regla es `source address=X.X.X.X/32` para un puerto específico (SSH,
puertos de clustering OVN/LXD — `6641-6644`, `6081`, `6686`, `8443`,
`8444` —, WireGuard `51820`, monitoreo `9100`/`8555`). La única excepción
a "una IP por regla" es un rango `/26` (`10.150.100.0/26`) habilitado
solo para SSH. **No existe ninguna regla para Kanboard** (ni puerto 80 ni
8080) — coincide con que hoy el único acceso es el túnel SSH.

**Interfaz de servicio (`nic_srv1`):** no tiene zona de firewall asignada
en el host (`firewall-cmd --get-zone-of-interface=nic_srv1` → `no zone`)
y tampoco tiene IP propia en el host — es un passthrough IPVLAN hacia los
contenedores gateway. El filtrado de qué entra por ahí se define **dentro
del contenedor gateway**, no en `pfr-oss`.

## 3. Rutas e IP — estado real

```
default via 10.143.11.225 dev ens192              (salida a internet/corporativa)
10.143.11.224/29 dev ens192                        (red de gestión, este host)
10.231.193.0/24 dev lxdbr_OAM                      (bridge OAM local del host)
169.254.0.1-4 dev wg0                              (peers de la malla WireGuard)
169.254.1.0/24 dev UplinkOvn1                       (uplink de OVN, link-local)
192.168.0.0/24 dev UplinkOvn1 (ruta estática)        (red OVN_1, hacia los contenedores)
```

**Red `OVN_1`** (`lxc network show OVN_1`): `192.168.0.0/24`, gateway
`192.168.0.254`, DHCP `192.168.0.100-199`, NAT activado. Es una red
**compartida entre proyectos** — la usan contenedores tanto de `PRJ-OSS`
(`C-PFR-1`, `C-CAR-1`, `PFR-OSS-GW-SRV`, `CAR-OSS-GW-SRV`) como de
`default` (`PFR-GW-OAM`, `CAR-GW-OAM`, y **`PFR-KANBOARD-TEST`**) — y
también entre sitios (`pfr.1` y `car.1`, vía el underlay WireGuard de
ADR-0006). Esto confirma que `PFR-KANBOARD-TEST` (en `default`) y
`PFR-OSS-GW-SRV` (en `PRJ-OSS`) **ya se pueden alcanzar directamente**
por esta red interna, sin importar a qué proyecto de LXD pertenece cada
uno — la separación por proyecto es de permisos/límites, no de
segmentación de red en este caso.

## 4. El patrón ya documentado: gateway de servicios

`docs/02_Arquitectura.md` (sección "Patrón de contenedor 'gateway de
servicios'") ya describe esto: cada proyecto tiene un contenedor
dedicado con dos interfaces — una hacia `OVN_1` (este-oeste, interna) y
otra vía IPVLAN atada a `nic_srv1`, con la IP de servicio de cara a la
red corporativa.

Confirmado en vivo:

```
PFR-OSS-GW-SRV
  eth0: 192.168.0.1        (interna, OVN_1)
  eth1: 10.143.11.8        (de servicio, vía nic_srv1)
```

## 5. Conclusión de esta exploración

🟡 **No conviene abrir un rango de IP en el firewall de `pfr-oss`
directamente.** Sería inconsistente con el estilo de firewall ya
establecido (whitelist puntual, sin rangos salvo una excepción de SSH) y
con el propio motivo de `ADR-0007`: los dispositivos `proxy` se
restringieron dentro de `PRJ-OSS` justamente para forzar que todo el
tráfico entrante pase por el gateway de servicios del proyecto, no por
proxies sueltos en cada contenedor.

**La vía consistente con la arquitectura actual es exponer Kanboard a
través de `PFR-OSS-GW-SRV`**, con una regla de reenvío (DNAT) desde su IP
de servicio (`10.143.11.8`) hacia la IP interna de Kanboard en `OVN_1`
(`192.168.0.106` en la prueba actual). Técnicamente no requiere mover el
contenedor de proyecto (ambos ya comparten `OVN_1`), aunque si Kanboard
pasa de ser una prueba a ser la herramienta real del equipo, tiene
sentido evaluar aparte que termine viviendo dentro de `PRJ-OSS` como
cualquier otro contenedor del proyecto.

## 6. Lo que queda para decidir con Norberto (no resuelto acá)

1. Confirmar si el acceso root de hoy es el modelo definitivo o un paso
   intermedio hasta habilitar `sudo` para `alfonzel_opr`.
2. **Quién puede llegar a `10.143.11.8`** una vez configurado el reenvío
   — ¿toda la red de oficina, un rango puntual, algo detrás de VPN? Esta
   es una decisión de política de acceso, no de arquitectura de red — la
   arquitectura de red (pasar por el gateway) ya está clara.
3. Si corresponde pedir esto también vía el mismo circuito de seguridad
   (ticket a Jira) que se usó para la autorización de red de FDO1, o si
   al ser tráfico *interno* del propio proyecto no aplica el mismo
   procedimiento.
4. Si conviene migrar `PFR-KANBOARD-TEST` a `PRJ-OSS` de una vez (con un
   nombre definitivo, no "-TEST") en lugar de dejarlo en `default`
   apuntado desde el gateway de otro proyecto.

## 7. No se hizo en esta sesión

- No se agregó ninguna regla de firewall.
- No se configuró ningún reenvío (DNAT) en `PFR-OSS-GW-SRV`.
- No se movió ningún contenedor.
- No se tocó la base de datos de Kanboard ni la de LXD/OVN.

---

## 8. Actualización — implementación temporal para la demo (2026-07-27, más tarde el mismo día)

🟢 A diferencia de lo registrado en la sección 7 (que describía el
estado en el momento de esta exploración de solo lectura), **más tarde
el mismo día sí se aplicó un cambio real**, con aprobación explícita del
usuario y ejecutado fase por fase con validación en cada paso: se
habilitó el acceso a Kanboard desde 6 IPs puntuales (4 ya inventariadas
para administración del cluster — Norberto, Rocío, Daniel, Elías — y 2
nuevas, exclusivas para esta demo — Fernando Fleitas, Andrés Semidei),
hacia el puerto 8080, explícitamente como medida **temporal** para la
demo interna del 2026-07-28.

No se implementó la vía definitiva (`PFR-OSS-GW-SRV`) descrita en las
secciones 4-6 de este documento — ese trámite formal con
Norberto/Seguridad sigue pendiente.

Procedimiento completo, con cada comando real ejecutado, su salida real,
validación y rollback específico:
[`SOP-acceso-temporal-demo-kanboard.md`](SOP-acceso-temporal-demo-kanboard.md).
