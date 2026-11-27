# Alcance del cluster a los nodos Huawei del módulo Oxígeno (2026-11-27)

> Estado: **camino encontrado y probado con cambios temporales, ya retirados.** Todavía no existe el contenedor de Oxígeno. Cuando se cree, hay que aplicar la regla de ACL y las rutas de la sección [Esquema para el contenedor de Oxígeno](#esquema-para-el-contenedor-de-oxígeno).

## Contexto

✅ Oxígeno es un módulo de Néstor Cardozo. Su backend en Python se conecta por Telnet a nodos Huawei. El plan es crear un contenedor propio en el cluster, con un stack actualizado. Antes de crearlo había que confirmar que la red interna del cluster (`OVN_1`) llega a esos nodos.

| Plataforma | Rol | Host | Puerto |
|---|---|---|---|
| UDM | Master · CAR | `10.148.48.88` | 7776 (Telnet) |
| UPCF | Master · CAR | `10.148.50.89` | 7776 (Telnet) |
| UDM | Redundancia · FRA | `10.148.37.88` | 7776 (Telnet) |
| UPCF | Redundancia · FRA | `10.148.39.89` | 7776 (Telnet) |
| MAE | — | `10.147.10.7` | 31114 |

✅ La web actual de Oxígeno es `http://oxigeno.personal.com.py:2020`, que resuelve a `10.150.31.80`. Se publica por HTTP, así que las credenciales de TPPY viajan sin cifrar.

## Método

Todas las pruebas fueron de **alcance TCP**. Se abrió el puerto y se cerró, sin iniciar sesión Telnet en los nodos:

```bash
timeout 5 bash -c 'echo > /dev/tcp/<ip>/<puerto>' && echo ABIERTO || echo CERRADO
```

Se complementó con `ip route get <ip>` para ver por qué gateway sale el tráfico, y con `traceroute -n` donde está instalado (solo en `FDO-GW-SRV`).

## Resultados

| Origen | 4 nodos :7776 | MAE :31114 | Detalle |
|---|---|---|---|
| Host `pfr-oss` | ✗ | ✗ | Sale por `10.143.11.225`; no vuelve respuesta |
| `PFR-GW-SRV` | ✗ | ✗ | Sale por `10.143.11.1` |
| `CAR-GW-SRV` | ✗ | ✗ | Sale por `192.168.91.97` |
| `FDO-GW-SRV` por `10.11.11.1` | ✗ | ✗ | El router responde *Destination Net Unreachable* (`!N`): no tiene ruta a `10.148.x` |
| `FDO-GW-SRV` por `10.11.11.253` (ruta temporal) | ✗ | ✗ | Hacia el MAE pasa el primer salto y después se pierde. Hacia `10.148.x` ni `.253` responde |
| `PFR-GW-OAM` / `CAR-GW-OAM` | ✗ | ✗ | Sus redes de gestión no llegan. Sí llegan a `10.150.31.80:2020` |
| Host `fdo-oss1` | ✅ | ✅ | Sale por `nic_oam`, vía `10.150.32.1` (red de gestión `10.150.32.x`) |
| **`FDO-GW-OAM`** (`192.168.0.9`, proyecto `default`) | ✅ | ✅ | Sale por `lxdbr_OAM` y la gestión de `fdo-oss1` |
| Contenedor de `OVN_1` (`DEV-ADMTECH-APP`) con ruta vía `192.168.0.9` | ✗ | ✗ | Lo descarta `ACL-OVN-1`, que no tiene regla para esos destinos. Tampoco responde el ping a `.9`: no hay regla ICMP |
| **Mismo contenedor, con ruta y regla temporal en `ACL-OVN-1`** | ✅ | ✅ | **Es el esquema para Oxígeno** |

✅ Conclusión: el único camino del cluster hacia estos nodos es la **red de gestión de Fernando**, a través de `FDO-GW-OAM`. No hace falta pedir firewall a otro equipo. Alcanza con una regla en `ACL-OVN-1` y rutas en el contenedor. Es el mismo patrón que Kanboard usa con `PFR-GW-OAM` para el OAuth de SDI (ver [03_Componentes.md](../../docs/03_Componentes.md)).

### Cómo se hizo la prueba con la ACL (y cómo se revirtió)

1. Se guardó la ACL completa: `lxc network acl show ACL-OVN-1 --project default > /tmp/acl_antes.yaml`.
2. Se agregaron 2 reglas temporales para `source=192.168.0.19`, con `description=TEMP-prueba-Oxigeno*`.
3. En `DEV-ADMTECH-APP` se agregaron 5 rutas `/32` vía `192.168.0.9`, se probaron los puertos y se borraron.
4. Se quitaron las 2 reglas con `lxc network acl rule remove` y se comparó contra la copia: **la ACL quedó idéntica** (sin diferencias en `diff`).

## Esquema para el contenedor de Oxígeno

> 🔴 Pendiente de aplicar: el contenedor todavía no existe.

1. **Crearlo en `fdo.1`.** El camino depende de Fernando: si se cae ese sitio, Oxígeno pierde los nodos aunque el contenedor corra en otro lado.
2. **Regla en `ACL-OVN-1`**, con el origen puntual (ver las buenas prácticas en [05_Configuracion.md](../../docs/05_Configuracion.md#buenas-prácticas)):

   ```bash
   lxc network acl rule add ACL-OVN-1 ingress action=allow \
     source=<IP-oxigeno> protocol=tcp destination_port=7776 \
     destination=10.148.48.88,10.148.50.89,10.148.37.88,10.148.39.89 \
     description="Oxígeno hacia UDM/UPCF Huawei" --project default
   lxc network acl rule add ACL-OVN-1 ingress action=allow \
     source=<IP-oxigeno> protocol=tcp destination_port=31114 \
     destination=10.147.10.7 description="Oxígeno hacia MAE" --project default
   ```

   **Rollback:** el mismo comando con `rule remove`, con los mismos campos exactos.

3. **Rutas persistentes en netplan** dentro del contenedor, nunca con `ip route add` suelto (ver [LL-021](../../docs/12_Lecciones_Aprendidas.md#ll-021--una-ruta-agregada-con-ip-route-add-no-existe-hasta-que-está-en-netplan)). La interfaz y el formato de abajo son una propuesta: verificar el nombre de la interfaz en el contenedor nuevo.

   ```yaml
   network:
     version: 2
     ethernets:
       eth0:
         routes:
           - { to: 10.148.48.88/32, via: 192.168.0.9 }
           - { to: 10.148.50.89/32, via: 192.168.0.9 }
           - { to: 10.148.37.88/32, via: 192.168.0.9 }
           - { to: 10.148.39.89/32, via: 192.168.0.9 }
           - { to: 10.147.10.7/32,  via: 192.168.0.9 }
   ```

4. **Verificar** con la prueba de puertos del [Método](#método): los 5 tienen que dar `ABIERTO`.
5. 🟡 **Avisar a Seguridad** que una aplicación va a usar el camino de gestión (OAM). Se pensó para operación. Para el OAuth de SDI ya hay un precedente.

## Hallazgo lateral

✅ `FDO-GW-SRV` tiene **10 rutas nuevas agregadas a mano**, sin `proto static`, así que no están en netplan:
- `10.12.151.226`, `.230`, `.242` y `.246`.
- `10.12.159.10`, `.38`, `.54`, `.58`, `.74` y `.86`.

Todas menos `10.12.159.54` tienen una regla nueva en `ACL-OVN-1` para sitios **Comap**. 🟡 Alguien sumó sitios Comap con su regla y su ruta, pero no persistió las rutas. Se pierden en el próximo reinicio del contenedor. Ver [RIE-024](../../docs/11_Riesgos.md#rie-024--rutas-agregadas-a-mano-en-los-gateways-no-persistentes).
