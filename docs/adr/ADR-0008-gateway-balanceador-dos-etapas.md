# ADR-0008 — Exposición de servicios en dos etapas: gateway + balanceador

| Campo | Valor |
|---|---|
| **Número** | ADR-0008 |
| **Fecha** | 2026-07-28 |
| **Estado** | Aceptado |
| **Autores** | Norberto Núñez |
| **Revisores** | Elías Alfonzo, Marcos Casco |
| **Reunión origen** | `reunion/LXD - Configuración FDO.vtt` |

---

## Contexto

Antes de esta reunión, Elías Alfonzo había implementado y documentado un esquema de prueba en el sitio Franco (PFR): las peticiones externas llegaban directamente a la VM del host, y un dispositivo proxy LXD (o una regla de firewall a nivel de sistema operativo) redirigía ese tráfico directamente al contenedor de destino — el mismo patrón usado para exponer `PFR-KANBOARD-TEST` (ver [`laboratorio/2026-07-27_exploracion-rutas-firewall-pfr-oss/`](../../laboratorio/2026-07-27_exploracion-rutas-firewall-pfr-oss/)).

Ese esquema es válido, pero tiene una limitación estructural: **redirige tráfico directamente desde el host hacia un único contenedor**. Funciona bien si solo hay un servidor sin alta disponibilidad, pero no está pensado para un escenario con **múltiples contenedores del mismo servicio, distribuidos por el cluster**, ni para centralizar el certificado TLS de varios servicios detrás de un mismo punto de entrada.

El equipo ya cuenta con el patrón de "contenedor gateway de servicios" (ver [02_Arquitectura.md](../02_Arquitectura.md)), que resuelve el tráfico este-oeste/norte-sur a nivel de sitio o proyecto, pero hasta esta reunión no existía una definición documentada de **qué pasa después de que el tráfico entra al gateway** — es decir, cómo llegar desde el gateway hasta el contenedor de aplicación correcto. Esta pregunta estaba explícitamente abierta en [`laboratorio/2026-07-27_exploracion-rutas-firewall-pfr-oss/informe-migracion-a-pfr-oss-gw-srv.md`](../../laboratorio/2026-07-27_exploracion-rutas-firewall-pfr-oss/informe-migracion-a-pfr-oss-gw-srv.md), sección 7, como "🔴 A confirmar explícitamente con Norberto".

---

## Problema

¿Cómo enrutar el tráfico entrante desde el contenedor gateway de un sitio/proyecto hasta el contenedor de aplicación correcto, de forma que:

- Funcione igual cuando hay un solo contenedor de servicio que cuando hay varios contenedores del mismo servicio distribuidos por el cluster (alta disponibilidad).
- Permita alojar múltiples servicios web detrás de un mismo punto de entrada, sin abrir un puerto distinto por cada uno.
- Centralice el certificado TLS en un solo lugar, en vez de instalarlo en cada contenedor de aplicación.
- Permita también exponer servicios no-web (ej. una base de datos) de forma directa, sin forzarlos a pasar por un balanceador HTTP.

---

## Alternativas evaluadas

### Opción A — Redirección directa a nivel de host/VM (esquema ya implementado por Elías)

**Descripción:**
El firewall del sistema operativo de la VM (o un dispositivo proxy LXD) redirige el puerto externo directamente al contenedor de aplicación.

**Ventajas:**
- Ya estaba implementado y funcionando para el caso de prueba (Kanboard en Franco).
- Más simple y más rápido de configurar para un caso puntual.
- Suficiente cuando hay un solo servidor y no se necesita alta disponibilidad ni distribución por el cluster.

**Desventajas:**
- No escala a múltiples contenedores del mismo servicio: el firewall del host redirige a una única IP:puerto fija.
- Cada servicio expuesto necesita su propia gestión de certificado TLS si usa HTTPS.
- Mezcla la responsabilidad de "networking de entrada del sitio" (a nivel de host/VM) con el enrutamiento específico de cada aplicación.
- No aprovecha el contenedor gateway de servicios ya adoptado como patrón estándar (ver [02_Arquitectura.md](../02_Arquitectura.md)).

---

### Opción B — Gateway + balanceador en dos etapas

**Descripción:**
El contenedor **gateway** (ya existente como patrón, ver [02_Arquitectura.md](../02_Arquitectura.md)) recibe el tráfico externo y lo reenvía —replicando dentro de sí las mismas reglas de firewall que antes vivían en el host— hacia un segundo contenedor dedicado, el **balanceador** (Apache u otro servidor web como proxy reverso). El balanceador centraliza el certificado TLS y enruta por URL/path hacia el contenedor de aplicación que corresponda. Para protocolos no-web (ej. una base de datos), el gateway puede redirigir un puerto dedicado directamente al contenedor de destino, sin pasar por el balanceador.

```
Petición externa (LAN corporativa)
         │
┌────────────────────┐
│  Contenedor GATEWAY │  reglas de firewall (forwarder entrante + NAT saliente)
└────────────────────┘
         │
         ├── puerto 80/443 ──► Contenedor BALANCEADOR (Apache, TLS centralizado)
         │                            │
         │                            └── ruteo por URL/path ──► Contenedor de SERVICIO
         │
         └── puerto dedicado (ej. 5432) ──► Contenedor de BASE DE DATOS (directo, sin balanceador)
```

**Ventajas:**
- El mismo punto de entrada (balanceador) puede alojar múltiples servicios web, enrutando por URL/path.
- El certificado TLS se instala una sola vez, en el balanceador — no en cada contenedor de aplicación.
- Es la evolución natural del patrón de gateway de servicios ya adoptado: separa "cómo entra el tráfico al sitio" (gateway) de "a qué aplicación va" (balanceador).
- Escala mejor a futuro hacia múltiples contenedores del mismo servicio (el balanceador puede repartir tráfico entre ellos), aunque el balanceo activo entre réplicas no se configuró todavía en esta reunión.
- Los servicios no-web (ej. bases de datos) pueden seguir usando redirección directa del gateway, sin forzar todo el tráfico a pasar por un proxy HTTP.

**Desventajas:**
- Un contenedor adicional por sitio/proyecto (el balanceador) a mantener, con su propio perfil, IP fija y ciclo de vida.
- Más pasos de configuración que la redirección directa: reglas de firewall en el gateway **y** configuración de virtual hosts/rutas en el balanceador.
- Introduce un nuevo punto único de falla por sitio (el balanceador) si no se configuran varias réplicas — mitigado por ser más simple de replicar que reconfigurar el firewall del host cada vez.

---

## Decisión

**Se elige: Opción B — Gateway + balanceador en dos etapas.**

A partir de esta reunión:

1. El contenedor **gateway de servicios** de cada sitio/proyecto (ya definido en [02_Arquitectura.md](../02_Arquitectura.md)) es responsable de reenviar el tráfico entrante hacia el contenedor correspondiente — balanceador para tráfico web, o directamente al contenedor de destino para protocolos no-web — replicando dentro de sí mismo las reglas de firewall que antes se aplicaban a nivel de host/VM.
2. Se crea un contenedor **balanceador** por sitio (primer ejemplo: `PFR-LB`, IP fija `192.168.0.11` en `OVN_1`, con Apache como proxy reverso), responsable de centralizar el certificado TLS y enrutar por URL/path hacia el contenedor de aplicación correspondiente.
3. El esquema de redirección directa a nivel de host que Elías había configurado para el caso de prueba de Kanboard se retira una vez migrado el servicio a este nuevo modelo (ver pendiente en [13_Linea_de_Tiempo.md](../13_Linea_de_Tiempo.md)).
4. Servicios no-web que necesiten exposición directa (ej. una base de datos accedida por su propio protocolo) pueden seguir recibiendo un puerto dedicado directamente desde el gateway, sin pasar por el balanceador.

---

## Justificación

El modelo de dos etapas es la opción que resuelve simultáneamente los cuatro requisitos del problema (múltiples réplicas, múltiples servicios detrás de un mismo punto de entrada, TLS centralizado, y exposición directa para protocolos no-web) sin depender de reconfigurar el firewall del host cada vez que se agrega o cambia un servicio. Norberto Núñez señaló explícitamente que el esquema de Elías (Opción A) es "totalmente válido" y que él mismo lo implementó varias veces, pero que es más apropiado "cuando tenés un solo servidor" y no se busca alta disponibilidad ni distribución por el cluster — que es precisamente el escenario que este cluster está construido para soportar.

---

## Consecuencias

### Positivas
- El modelo de exposición de servicios queda desacoplado del firewall del host/VM — cualquier cambio de enrutamiento se hace dentro de los contenedores gateway/balanceador, sin tocar la VM.
- Un mismo balanceador puede crecer para alojar nuevos servicios web sin abrir puertos nuevos en el host.
- El certificado TLS se gestiona en un único lugar por sitio.
- Responde y cierra la pregunta abierta documentada en [`laboratorio/2026-07-27_exploracion-rutas-firewall-pfr-oss/informe-migracion-a-pfr-oss-gw-srv.md`](../../laboratorio/2026-07-27_exploracion-rutas-firewall-pfr-oss/informe-migracion-a-pfr-oss-gw-srv.md) sobre el mecanismo de reenvío.

### Negativas / Compromisos aceptados
- Un contenedor más por sitio (el balanceador) para crear, endurecer y mantener con el mismo criterio que el gateway (ver [12_Lecciones_Aprendidas.md — LL-013](../12_Lecciones_Aprendidas.md#ll-013--deshabilitar-ssh-en-los-contenedores-de-infraestructura-reduce-el-riesgo-de-movimiento-lateral)).
- Más pasos de configuración por servicio nuevo expuesto (regla de firewall en el gateway + virtual host/ruta en el balanceador) que con la redirección directa.

### Riesgos
- 🔴 **Pendiente de validación:** la sintaxis exacta de la regla de firewalld para reenviar el puerto del gateway al balanceador no quedó completamente confirmada en el audio de la reunión (se mencionaron fragmentos de `rule family="ipv4"` para un forward de puerto). Confirmar y documentar el comando exacto en la próxima sesión antes de replicarlo en otros sitios.
- 🟡 El balanceo activo de tráfico entre múltiples réplicas del mismo servicio (más allá de reenviar a un único contenedor de destino por ruta) no se configuró ni se probó en esta reunión — queda como trabajo futuro si un servicio necesita más de una réplica simultánea.
- Un balanceador único por sitio es, en sí mismo, un punto único de falla para todos los servicios web de ese sitio si no se le da alta disponibilidad propia — no evaluado en esta reunión.

---

## Variante confirmada: balanceador embebido en el gateway

**Fecha:** Reunión OSS (agosto) — `reunion/Reunión en OSS_agosto_v3.vtt`

Al implementar el servicio **NTF** (mensajería SMS/email vía SMPP), surgió un caso que el modelo de dos etapas descrito arriba no resuelve directamente: el servicio necesita aplicar reglas de control de acceso (ACL) según la **IP real del cliente externo** que hace la petición (ej. restringir el endpoint `/ntf` a un conjunto conocido de IPs).

Con el balanceador en un contenedor separado (modelo estándar de este ADR), el balanceador solo ve la IP del contenedor gateway como origen — la IP real del cliente se pierde en el primer salto. Por eso, para este servicio, Norberto Núñez embebió la funcionalidad de balanceador (Apache + `mod_proxy_balancer`) **dentro del mismo contenedor gateway**, en lugar de crear un contenedor balanceador aparte. Así el balanceador ve la IP real de origen y puede aplicar la regla ACL antes de reenviar el tráfico a los contenedores de aplicación (`WS1` en Fernando y Franco).

**Esto no reemplaza la decisión de este ADR.** El modelo de dos etapas (gateway y balanceador en contenedores separados) sigue siendo el default. La variante embebida es una excepción deliberada, a usar únicamente cuando el servicio necesita ACLs por IP de origen real — ver el detalle de configuración en [05_Configuracion.md — ACL por IP de origen en el balanceador](../05_Configuracion.md#acl-por-ip-de-origen-en-el-balanceador) y la ficha del componente en [03_Componentes.md](../03_Componentes.md#variante-balanceador-embebido-en-el-gateway-cuando-se-necesita-la-ip-real-de-origen).

---

## Actualización — migración de Kanboard (2026-10-08)

**Fecha:** 2026-10-08. **Referencia:** [`laboratorio/2026-10-08_migracion-kanboard-gateway-balanceador/`](../../laboratorio/2026-10-08_migracion-kanboard-gateway-balanceador/).

Al retirar el acceso temporal de Kanboard (pendiente abajo), se encontró que `PFR-GW-SRV` **ya tenía Apache embebido corriendo** desde el **2026-09-18**, sirviendo Loki y NTF — trabajo hecho entre reuniones, nunca documentado en este repositorio. El mismo archivo tenía además una línea sin terminar para Kanboard, apuntando a un hostname inexistente (`CAR-kanboard-1`).

✅ **Autoría confirmada (actualización posterior):** Norberto Núñez explica él mismo, en `reunion/2026-10_llamada-abel-balanceadores-ntf-loki.vtt` (min. ~24:36), el mecanismo que usa para mantener `LB.conf` igual en los 3 gateways: *"Es un archivo de apache que yo repliqué en los tres apaches [...] cada vez que yo modifico esto [...] copio el lb.conf [...] a los 3 [...] por el protocolo del LXD"* — con el detalle completo del procedimiento (copiar el archivo, `a2enmod`, habilitar el sitio, habilitar SSL, reiniciar Apache). En el mismo tramo de la reunión (min. ~27:25) señala dentro de ese archivo el bloque de Kanboard ya presente. Con esto se confirma formalmente lo que antes era un supuesto. 🔴 Sigue sin confirmar si tenía algo más planeado para Kanboard que no llegó a aplicar — la reunión no entra en ese detalle puntual.

🟡 **Observación que ameritaría revisar el "modelo estándar" de este ADR:** en la práctica, **los 3 servicios reales del cluster (Loki, NTF y ahora Kanboard) usan la variante embebida**, no un balanceador separado — el contenedor `PFR-LB` mencionado como "primer ejemplo" en la Decisión de este ADR nunca llegó a crearse de forma persistente (fue una demostración en vivo durante la reunión de julio). Esto no invalida la decisión original, pero sugiere que, en la práctica, el equipo prefirió reutilizar el gateway ya existente antes que mantener un contenedor adicional por sitio. Queda pendiente confirmar con el equipo si esto debería formalizarse como el nuevo default, o si sigue siendo deuda técnica a resolver (crear los balanceadores separados).

Kanboard se migró usando esta misma variante embebida, con una particularidad: no necesitaba ACL por IP (a diferencia de NTF), se usó por pragmatismo, reutilizando la infraestructura ya existente. Además, Kanboard no soporta ejecutarse bajo un subpath (no tiene opción de "base URL" configurable) — el `ProxyPass /kanboard` con el prefijo pelado rompía la navegación interna. La solución aplicada fue servir Kanboard en la **raíz** del `VirtualHost` del gateway, con `/kanboard` y `/kamboard` como alias de redirección (no de proxy) hacia la raíz. Ver el diagnóstico completo en la bitácora del laboratorio referenciado arriba, y el patrón general documentado en [05_Configuracion.md — Apps sin soporte de subpath detrás del balanceador](../05_Configuracion.md#apps-sin-soporte-de-subpath-detrás-del-balanceador).

---

## Actualización — HTTPS para Kanboard con el certificado compartido, sin pedir uno nuevo (2026-10-09)

**Fecha:** 2026-10-09. **Referencia:** [`laboratorio/2026-10-09_https-kanboard-certificado-compartido/`](../../laboratorio/2026-10-09_https-kanboard-certificado-compartido/).

Antes de pedir certificados nuevos para los 3 gateways del cluster, se investigó el estado actual: **no hay DNS configurado para ninguna de las 3 IPs de servicio** (`10.143.11.8`, `192.168.91.117`, `10.11.11.12`), ni siquiera para el nombre que ya tiene el certificado existente (`oss.personal.com.py`, todo `NXDOMAIN`). Pero **el certificado ya existe** — es el mismo archivo, con el mismo hash, desplegado idéntico en los 3 gateways (junto con el `LB.conf` del 18-09 mencionado arriba), para `CN=oss.personal.com.py`, sin SAN, emitido por la CA interna `AutoridadOSS`.

**Hallazgo clave:** `SSLVerifyClient require` (la exigencia de certificado de cliente que protege a NTF) es una directiva de Apache independiente del certificado de servidor — no hace falta un certificado nuevo para que Kanboard tenga HTTPS, solo una configuración de Apache que permita que ambos servicios convivan en el mismo `VirtualHost *:443` con requisitos distintos.

🔴 **Error descartado, documentado para no repetirlo:** intentar "relajar" `SSLVerifyClient` de `require` (a nivel de vhost) a `none` (en un `<Location>` específico) tiene sintaxis válida pero **no funciona en tiempo real** — el servidor sigue pidiendo certificado. La dirección que sí funciona es la inversa: vhost en `SSLVerifyClient optional`, con `require` explícito solo en el `<Location '/ntf'>`. Ver el patrón completo, con los dos intentos (el que falló y el que funcionó), en [05_Configuracion.md — mTLS opcional por defecto, obligatorio solo en rutas específicas](../05_Configuracion.md#mtls-opcional-por-defecto-obligatorio-solo-en-rutas-específicas).

**Resultado:** Kanboard accesible por `https://10.143.11.8/` sin certificado de cliente; `http://10.143.11.8/` redirige automáticamente a HTTPS; Loki (que solo vive en el puerto 80) sin cambios; NTF verificado sin cambios, sigue exigiendo certificado de cliente. Validado con los 4 casos probados explícitamente (Loki HTTP, Kanboard HTTP→redirect, Kanboard HTTPS, NTF HTTPS sin cert).

Pendiente: DNS para el nombre del certificado (o uno nuevo por sitio, lo que requeriría un certificado con SAN), confirmar que las PCs del equipo confían en `AutoridadOSS`, y replicar el mismo cambio en `CAR-GW-SRV`/`FDO-GW-SRV` si se decide exponer algo por HTTPS ahí también. 🟡 El diseño acordado para ese DNS (un mismo nombre resolviendo, por round-robin, a las 3 IPs de servicio) ya está explicado en [02_Arquitectura.md — Nombre de dominio compartido entre sitios](../02_Arquitectura.md#nombre-de-dominio-compartido-entre-sitios-fqdn--dns-round-robin) — falta pedirlo, no falta diseñarlo.

✅ **Justificación explícita del usuario (Elías Alfonzo) para no crear un balanceador separado en este caso puntual:** Kanboard es un servicio chico, usado por ~5-6 personas del equipo — no justifica el costo de mantener un contenedor adicional solo por alta disponibilidad del balanceador. Es una decisión consciente de costo/beneficio para este servicio en particular, no una limitación técnica ni un descuido. 🟡 Esto no resuelve la pregunta más amplia de si el modelo embebido debería ser el default general del ADR para *todo* servicio nuevo — esa decisión sigue pendiente de conversar con el equipo, especialmente para servicios con más usuarios o mayor criticidad que sí podrían justificar un balanceador separado con alta disponibilidad propia.

---

## Actualización — alta de VulnApp NG, cuarto caso de la variante embebida (2026-10-09)

**Fecha:** 2026-10-09. **Referencia:** [`laboratorio/2026-10-09_alta-vulnapp-ng/`](../../laboratorio/2026-10-09_alta-vulnapp-ng/).

Se alojó **VulnApp NG** (reemplazo de una aplicación legacy, decisión tomada en el repositorio de la propia aplicación — DEC-042, fuera de este repositorio) en `pfr.1`, sin alta disponibilidad, publicada por `PFR-GW-SRV` bajo `/vulnapp`. Es el **cuarto** servicio en usar la variante embebida de este mismo gateway (después de Loki, NTF y Kanboard) — a diferencia de Kanboard, VulnApp NG sí soporta ejecutarse bajo un prefijo de path (`SCRIPT_NAME`), así que el bloque de Apache es el más simple de los cuatro: un `ProxyPass /vulnapp` directo, sin los alias de redirección que necesitó Kanboard.

Dos hallazgos nuevos durante esta alta:

- **`mod_headers` no estaba habilitado** en `PFR-GW-SRV` — necesario para `RequestHeader set X-Forwarded-Proto`, que esta aplicación sí usa (a diferencia de Loki, NTF y Kanboard). El primer intento de despliegue abortó solo (`apache2ctl configtest` lo rechazó) sin llegar a afectar los otros tres servicios; se habilitó el módulo y se reintentó con éxito. Ver [TRB-015](../07_Troubleshooting.md#trb-015--requestheader-falla-con-invalid-command-porque-mod_headers-no-está-habilitado).
- Se usó por primera vez `lxc network acl` de forma documentada — la ACL (`ACL-OVN-1`) ya existía, aplicada a `OVN_1`, sin ningún registro en este repositorio. Se documentó completa (reglas preexistentes y las 4 nuevas de este alta) en [05_Configuracion.md — Firewall de la red OVN_1](../05_Configuracion.md#firewall-de-la-red-ovn_1-lxc-network-acl).

**Pendiente, fuera del alcance de este cluster:** la conectividad hacia la API de SDI (`10.150.58.116:443`) está bloqueada después del primer salto del contenedor — ver [RIE-015](../11_Riesgos.md#rie-015--conectividad-de-vulnapp-ng-hacia-la-api-de-sdi-bloqueada). Mientras no se resuelva, la carga diaria de datos de la aplicación no se instaló ni se activó.

---

## Pendientes de seguimiento

- [ ] Confirmar y documentar la sintaxis exacta de la regla de firewalld de reenvío de puerto (gateway → balanceador) — pendiente de la siguiente sesión con Norberto. 🟡 Parcialmente confirmado: el `forward-port` funciona correctamente a nivel de firewalld/kernel (probado con Kanboard, ver actualización arriba), pero el tráfico externo real fue bloqueado por un firewall corporativo intermedio — sigue sin resolverse el trámite de alta de servicio para puertos no estándar.
- [x] Migrar la exposición real de Kanboard desde el acceso temporal por firewall hacia este modelo definitivo, y retirar el acceso temporal — ✅ Completado 2026-10-08, ver actualización arriba.
- [ ] Completar el inventario de IP + puerto + servicio para cada servicio nuevo expuesto por este mecanismo (pedido explícito de Marcos Casco).
- [ ] Evaluar si corresponde balanceo activo entre réplicas del mismo servicio, o si el balanceador solo hace ruteo 1:1 por URL.
- [x] Confirmar con Norberto Núñez el trabajo del 2026-09-18 en `LB.conf` — ✅ Confirmado por él mismo en `reunion/2026-10_llamada-abel-balanceadores-ntf-loki.vtt`, ver la actualización arriba. Qué es `CAR-kanboard-1`/`CAR-KANBOARD` ya se había aclarado por separado (el usuario, no Norberto) — ver [13_Linea_de_Tiempo.md](../13_Linea_de_Tiempo.md). 🔴 Sigue sin confirmar si Norberto tenía algo más planeado para Kanboard que no llegó a aplicar.
- [ ] Decidir si el "modelo estándar" de este ADR debería actualizarse para reflejar que, en la práctica, se usa la variante embebida en los 4 casos reales existentes (Loki, NTF, Kanboard, VulnApp NG).
- [ ] Pedir a Seguridad/Redes que habilite la conectividad de `PFR-VULNAPP-APP` hacia `10.150.58.116:443` (API de SDI) — ver [RIE-015 en 11_Riesgos.md](../11_Riesgos.md#rie-015--conectividad-de-vulnapp-ng-hacia-la-api-de-sdi-bloqueada).

---

## Referencias

- [02_Arquitectura.md — Patrón de contenedor "gateway de servicios"](../02_Arquitectura.md)
- [03_Componentes.md — Contenedor balanceador](../03_Componentes.md)
- [05_Configuracion.md — Reenvío de puertos y balanceador](../05_Configuracion.md)
- [`laboratorio/2026-07-27_exploracion-rutas-firewall-pfr-oss/informe-migracion-a-pfr-oss-gw-srv.md`](../../laboratorio/2026-07-27_exploracion-rutas-firewall-pfr-oss/informe-migracion-a-pfr-oss-gw-srv.md)
- Reunión origen: `reunion/LXD - Configuración FDO.vtt`
