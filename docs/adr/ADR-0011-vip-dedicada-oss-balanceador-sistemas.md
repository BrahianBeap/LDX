# ADR-0011 — VIP dedicada para `oss.personal.com.py` en el balanceador de Sistemas

| Campo | Valor |
|---|---|
| **Número** | ADR-0011 |
| **Fecha** | 2026-11-26 |
| **Estado** | Propuesto (acordado de palabra, sin implementar) |
| **Autores** | Elías Alfonzo |
| **Revisores** | Rocío Duarte; Maximiliano Romero (Seguridad), quien recomendó la VIP dedicada |
| **Reunión origen** | Chat de Teams del 2026-11-26 con Abel Díaz, Maximiliano Romero y Rocío Duarte (sin grabación) |

> **Relación con otros ADR:** cambia la parte de round-robin de [ADR-0009](ADR-0009-dns-fqdn-compartido-y-nombres-por-sitio.md). El nombre compartido se mantiene, pero cuando esto se implemente va a resolver a una sola IP (la VIP) y no a las 3 IP de los gateways. Los nombres propios por sitio de ADR-0009 no cambian.

---

## Contexto

- ✅ `oss.personal.com.py` resuelve hoy por DNS round-robin a las 3 IP de servicio: `10.143.11.8` (Franco), `192.168.91.117` (Carpinelli) y `10.11.11.12` (Fernando). Ver [02_Arquitectura.md](../02_Arquitectura.md#nombre-de-dominio-compartido-entre-sitios-fqdn--dns-round-robin).
- ✅ Los 3 gateways publican lo mismo desde la Etapa 2, re-verificado en vivo el 2026-11-26. Ver [RIE-020](../11_Riesgos.md#rie-020--gateways-de-car-y-fdo-no-homogéneos-con-pfr-bloquean-el-dns-compartido).
- ✅ Seguridad otorga los accesos por VPN/SDP por **ip:puerto**. Al 2026-11-26 el único servicio inventariado es `10.143.11.8:443` (Franco).
- ✅ Cada gateway pide certificado de cliente en `/ntf` (`SSLVerifyClient require`), que es la ruta que consume Tembiapó. En el resto de las rutas el certificado de cliente es `none` u `optional`.

## Problema

Con round-robin, el DNS le da al usuario cualquiera de las 3 IP. Si su permiso de VPN cubre solo una, las conexiones a las otras dos se cortan. El DNS además no sabe qué sitio está caído o sobrecargado: no sirve para repartir la carga ni para sacar del medio un sitio que falla.

¿Cómo logramos que el usuario pida **un solo acceso** y que el tráfico vaya a un sitio sano y poco cargado?

---

## Alternativas evaluadas

### Opción A — Mantener el round-robin y dar permiso a las 3 IP

**Ventajas:** no hay que montar nada nuevo.

**Desventajas:**
- Cada usuario necesita 3 permisos, y Seguridad tiene que inventariar 3 servicios para la misma aplicación.
- Si un sitio se cae, el DNS sigue mandando usuarios ahí.

### Opción B — IP flotante entre nuestros 3 gateways (keepalived/VRRP)

**Desventajas:** no es viable. Una IP flotante solo pasa de un equipo a otro dentro de la misma red de capa 2, y los 3 sitios están en redes distintas (`10.143.11.x`, `192.168.91.x`, `10.11.11.x`).

### Opción C — Balanceador propio, por ejemplo HAProxy con keepalived en un solo sitio

**Desventajas:**
- Si se cae el sitio donde está el balanceador, se cae el acceso a los 3.
- 🟡 Desde `pfr-oss` hoy no se llega a `10.11.11.12`, así que un balanceador en Franco no alcanzaría a Fernando sin abrir antes esa ruta.

### Opción D — VIP compartida en el balanceador de Sistemas (una IP para muchos servicios)

**Desventajas:**
- Un permiso a esa IP:443 abriría todos los servicios que cuelgan de ella, así que no separa los permisos.
- 🟡 Para enrutar por nombre, el balanceador suele terminar el SSL. Eso rompe el certificado de cliente de `/ntf`.

### Opción E — VIP dedicada para OSS en el balanceador de Sistemas *(elegida)*

**Ventajas:**
- Un solo permiso VPN/SDP (`VIP:443`) y un solo servicio inventariado.
- El health check saca solo al sitio que falla.
- Reparte por carga.
- Un permiso a la VIP abre solo OSS.

**Desventajas:**
- Depende de otro equipo (Sistemas) y de varios trámites.
- Hay que abrir firewall desde el balanceador hacia los 3 nodos.

---

## Decisión

Se elige la **Opción E**:

| Elemento | Definición |
|---|---|
| IP de la VIP | Una IP nueva, pedida a Da Silva y **dedicada solo a OSS** |
| Dónde vive | En el balanceador de Sistemas. Ahí flota entre los equipos del propio balanceador |
| Modo | **TCP/L4 pasante**, sin terminar SSL en el balanceador |
| Nodos | `10.143.11.8:443`, `192.168.91.117:443`, `10.11.11.12:443` |
| Health check | TCP al 443 de cada nodo |
| Algoritmo | Least connections |
| DNS | `oss.personal.com.py` pasa a apuntar a la VIP |
| Firewall | Pedido aparte: balanceador → 3 nodos al 443 |
| Acceso de usuarios | Permiso VPN/SDP solo a `VIP:443` |

## Justificación

- **TCP pasante es obligatorio.** Si el balanceador termina el SSL, el certificado de cliente que manda Tembiapó a `/ntf` no llega al gateway. Además, los certificados quedan en nuestros gateways y no hay que entregárselos a Sistemas.
- **VIP dedicada en vez de compartida.** Es lo que recomendó Maximiliano Romero porque separa los permisos, y también evita que el balanceador necesite abrir el SSL.

---

## Consecuencias

### Positivas
- Un solo permiso por usuario y un solo servicio inventariado.
- Si un sitio se cae, el health check lo saca solo, sin tocar el DNS.

### Negativas / Compromisos aceptados
- La disponibilidad del acceso depende del balanceador de Sistemas.
- 🟡 En modo L4 con SNAT, los gateways ven la IP del balanceador y no la del usuario. Hay que revisar si eso afecta logs o reglas por IP de origen (por ejemplo `/kanboard-prueba` o `--forwarded-allow-ips` de VulnApp NG).
- Hay que migrar los accesos ya otorgados a `10.143.11.8:443`.

### Riesgos
- 🔴 No está confirmado que el balanceador de Sistemas llegue a `10.11.11.12`, porque desde `pfr-oss` no se alcanza.
- Si Sistemas configura la VIP en modo L7, `/ntf` deja de funcionar para Tembiapó.

---

## Pendientes de seguimiento

- [ ] Confirmar con Sistemas cómo se pide (ticket o formulario) y cómo tienen implementado hoy el balanceador.
- [ ] Pedir la IP a Da Silva.
- [ ] Configurar la VIP en TCP pasante, con health check y least connections.
- [ ] Pedir el firewall del balanceador hacia los 3 nodos al 443 y verificar que llegue a Fernando.
- [ ] Cambiar el DNS `oss.personal.com.py` a la VIP (hoy tiene las 3 IP, ver [ADR-0009](ADR-0009-dns-fqdn-compartido-y-nombres-por-sitio.md)).
- [ ] Inventariar la VIP con Seguridad (Abel Díaz) y migrar los accesos dados a `10.143.11.8:443`.
- [ ] Probar `/ntf` con certificado de cliente a través de la VIP antes de cambiar el DNS.

---

## Referencias

- [02_Arquitectura.md — Nombre de dominio compartido entre sitios](../02_Arquitectura.md#nombre-de-dominio-compartido-entre-sitios-fqdn--dns-round-robin)
- [ADR-0009 — DNS compartido y nombres por sitio](ADR-0009-dns-fqdn-compartido-y-nombres-por-sitio.md)
- [RIE-025 — Permisos VPN/SDP por IP con DNS round-robin](../11_Riesgos.md#rie-025--permisos-vpnsdp-por-ip-con-dns-round-robin)
