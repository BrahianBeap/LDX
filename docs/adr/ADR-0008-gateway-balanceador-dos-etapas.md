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

## Pendientes de seguimiento

- [ ] Confirmar y documentar la sintaxis exacta de la regla de firewalld de reenvío de puerto (gateway → balanceador) — pendiente de la siguiente sesión con Norberto.
- [ ] Migrar la exposición real de Kanboard desde el acceso temporal por firewall (ver [`laboratorio/2026-07-27_exploracion-rutas-firewall-pfr-oss/SOP-acceso-temporal-demo-kanboard.md`](../../laboratorio/2026-07-27_exploracion-rutas-firewall-pfr-oss/SOP-acceso-temporal-demo-kanboard.md)) hacia este modelo definitivo, y retirar el acceso temporal.
- [ ] Completar el inventario de IP + puerto + servicio para cada servicio nuevo expuesto por este mecanismo (pedido explícito de Marcos Casco).
- [ ] Evaluar si corresponde balanceo activo entre réplicas del mismo servicio, o si el balanceador solo hace ruteo 1:1 por URL.

---

## Referencias

- [02_Arquitectura.md — Patrón de contenedor "gateway de servicios"](../02_Arquitectura.md)
- [03_Componentes.md — Contenedor balanceador](../03_Componentes.md)
- [05_Configuracion.md — Reenvío de puertos y balanceador](../05_Configuracion.md)
- [`laboratorio/2026-07-27_exploracion-rutas-firewall-pfr-oss/informe-migracion-a-pfr-oss-gw-srv.md`](../../laboratorio/2026-07-27_exploracion-rutas-firewall-pfr-oss/informe-migracion-a-pfr-oss-gw-srv.md)
- Reunión origen: `reunion/LXD - Configuración FDO.vtt`
