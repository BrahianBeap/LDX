# Línea de tiempo — De Microsoft Planner a Kanboard

> **Propósito:** material de referencia para preparar una presentación al
> director. Reconstruye, en orden cronológico y con las fechas reales de
> cada commit, cómo era la gestión de tareas del equipo antes, qué se probó,
> qué decisiones se tomaron por el camino (y por qué) y en qué estado queda
> todo al día de hoy.
> **Alcance:** este documento **no reemplaza** la documentación técnica ya
> existente — es un resumen ejecutivo que enlaza a cada fuente original.
> Para el detalle completo de cualquier punto, seguir los enlaces.
> **Ver también:** [`docs/17_Avance_Presentacion.md`](../../docs/17_Avance_Presentacion.md)
> — resumen de avance de **todo** el proyecto LDX (no solo Kanboard),
> pensado para el mismo tipo de presentación a dirección. Este documento
> se enfoca únicamente en el detalle de Kanboard.
> **Última actualización:** 2026-07-30.

---

## 1. Resumen para el director (1 párrafo)

El equipo usaba **Microsoft Planner** (una sola pizarra, "Proyectos OSS",
con etiquetas de color para distinguir sistemas) para organizar el
trabajo. En 5 días (2026-07-24 a 2026-07-28) se evaluó, probó y migró
manualmente ese contenido a **Kanboard** (herramienta open-source,
autoalojada en el propio cluster LXD), con un estándar de organización
propio (un proyecto por sistema, no una sola pizarra con etiquetas) y una
funcionalidad nueva que Planner no tenía: una vista de carga de trabajo
por persona a través de todos los proyectos (plugin **TeamWorkload**,
desarrollo propio). Se hizo una demo interna el 2026-07-28 con acceso
temporal habilitado para 6 personas. **Quedan pendientes:** migrar el
resto de los sistemas de Planner, definir la vía de acceso definitiva
(hoy es un acceso temporal, no la solución final) y algunos ajustes
menores del plugin — ver sección 6.

---

## 2. Antes vs. ahora

| Dimensión | Antes (Microsoft Planner) | Ahora (Kanboard) |
|---|---|---|
| Herramienta | Microsoft Planner, embebido en Teams (equipo OSS, pestaña "Proyectos OSS") | Kanboard (PHP, open-source), autoalojado en un contenedor del propio cluster LXD |
| Organización | **Un solo plan** para todos los sistemas, con una etiqueta de color por sistema (`adm-tech`, `SOC`, `INFRAWORK`, etc.) | **Un proyecto independiente por sistema/producto** (INFRAWORK, ADM-TECH, ...) — nunca se mezclan sistemas en un mismo tablero. Ver [decisión completa](#31-decisión-un-proyecto-por-sistema-no-un-solo-tablero-con-etiquetas) |
| Columnas del tablero | Bucket de Planner, sin flujo estandarizado entre planes | Flujo fijo por *tipo* de proyecto — los de tipo Desarrollo usan siempre: Pendiente de Análisis → Listo para Desarrollo → En Curso → En Revisión → Realizados |
| Asignación de tareas | Varios asignados por tarea | Un asignado principal por tarea (limitación propia de Kanboard, resuelta caso por caso en la migración) |
| Etiquetas | Identificaban el *sistema* (redundante con el plan) | Identifican categoría *funcional/técnica* (`Backend`, `Frontend`, `Reportes`, etc.) — nunca un sistema ni una persona |
| Nombres de tarea | Libres, sin convención | Convención fija `<Módulo> - <Funcionalidad>`, sin prefijos de tipo (`BUG`, `MEJORA`, etc.) |
| Vista de carga de trabajo por persona | No existía nativamente | **Nueva:** plugin propio **TeamWorkload** — ver [sección 5](#5-desarrollo-propio-plugin-teamworkload) |
| Acceso | Vía Microsoft Teams / cuenta corporativa | Túnel SSH personal → temporalmente ampliado a 6 IPs para la demo → **pendiente** la vía definitiva (gateway de servicios) |
| Alojamiento | SaaS de Microsoft | Contenedor propio (`PFR-KANBOARD-TEST`) en `pfr-oss`, base de datos SQLite (de prueba, no definitiva) |

---

## 3. Cronología

### 2026-07-24 — Exploración técnica: ¿se puede correr Kanboard en el cluster?

**Commit:** [`5dc960b`](https://github.com/BrahianBeap/LDX/commit/5dc960b) (registrado 2026-07-25 09:00)
**Documento:** [`laboratorio/2026-07-24_kanboard-contenedor-prueba/`](../2026-07-24_kanboard-contenedor-prueba/)

Se levantó la instalación local de Kanboard como contenedor LXD real en
`pfr-oss`, para probarlo por navegador antes de decidir nada. Resultado:
✅ éxito, pero con ajustes no previstos:

- La red interna `OVN_1` no es alcanzable desde una PC externa al
  cluster → se resolvió con un **túnel SSH** hacia un proxy LXD en
  loopback (`127.0.0.1:8080`).
- El proyecto `PRJ-OSS` (el del equipo) bloquea dispositivos `proxy` por
  diseño ([ADR-0007](../../docs/adr/ADR-0007-proyectos-lxd-multitenancy.md))
  → el contenedor de prueba se creó en el proyecto `default` en su lugar.

📌 Detalle completo de qué funcionó y qué no: [`conclusiones.md`](../2026-07-24_kanboard-contenedor-prueba/conclusiones.md).

---

### 2026-07-25 — Arranca la migración real de contenido (Planner → Kanboard)

**Commit:** [`98144e7`](https://github.com/BrahianBeap/LDX/commit/98144e7) (16:45)
**Documentos:** [`laboratorio/2026-07-25_migracion-planner-a-kanboard/`](../2026-07-25_migracion-planner-a-kanboard/)

- Se extrajo el contenido real de Planner (`planner-data.json`): 4 buckets,
  31 tareas, 9 personas.
- **Decisión — carga manual, no por script/API.** Se evaluaron 3 opciones
  (manual / API scripteada / híbrida). Se eligió carga manual por la
  interfaz web: menor riesgo antes de la demo, y para que el usuario se
  familiarice con el flujo real de Kanboard mientras carga.
- Se ejecutó el proyecto piloto **INFRAWORK** con el plan original (un
  solo proyecto "Proyectos OSS" con tags). **Al cargar datos reales el
  enfoque no funcionó** — ver decisión siguiente.

#### 3.1 Decisión: un proyecto por sistema, no un solo tablero con etiquetas

> ✅ **Confirmada por el equipo, 2026-07-25.**

El plan original usaba las etiquetas de Planner como tags dentro de un
único proyecto "Proyectos OSS". Se abandonó por dos motivos:

1. Mezclar sistemas distintos (INFRAWORK, SOC, ADM-TECH...) en un mismo
   tablero no refleja cómo trabaja cada área — un tablero debe representar
   un producto, no una mezcla de aplicaciones.
2. Las etiquetas de Planner ya identificaban el *sistema* de la tarea,
   dejando sin uso real el concepto de tag de Kanboard para clasificación
   funcional — que es donde más valor aporta.

Se formalizó un **estándar de organización** completo (proyecto = sistema,
flujo por tipo de proyecto, convención de nombres, uso de tags,
estructura del contenido de cada tarea). INFRAWORK quedó como plantilla de
referencia para todos los proyectos de tipo Desarrollo.

📌 Estándar completo: [`estandar-organizacion-kanboard.md`](../2026-07-25_migracion-planner-a-kanboard/estandar-organizacion-kanboard.md).

---

### 2026-07-26 — Segundo proyecto migrado + nace el plugin TeamWorkload

**Commits:** [`4371cfd`](https://github.com/BrahianBeap/LDX/commit/4371cfd) (12:10), [`751bb76`](https://github.com/BrahianBeap/LDX/commit/751bb76) (14:05), [`2f97567`](https://github.com/BrahianBeap/LDX/commit/2f97567) (14:41)

- **ADM-TECH** migrado y operativo, con el mismo flujo de 5 columnas que
  INFRAWORK. Se agregaron al estándar las reglas de uso de comentarios
  (registro cronológico de reuniones/decisiones/avances) y de subtareas
  (solo acciones concretas de trabajo).
- Se confirmó explícitamente que **toda la carga en Kanboard es manual**,
  no vía API/CLI/base de datos.
- **Nace la necesidad de una vista de carga de trabajo por persona:** al
  pasar de "un plan" (Planner) a "un proyecto por sistema" (Kanboard), se
  perdió la vista única de "qué tiene pendiente cada persona en todos los
  sistemas". Antes de escribir código, se investigó si algún plugin
  existente resolvía esto — ninguno lo hacía completo, pero se encontró
  que el propio Core de Kanboard ya tenía una página oculta y sin
  documentar (`ProjectUserOverviewController`) que resolvía gran parte del
  problema.
- **Fase 1 del plugin TeamWorkload** implementada y probada en
  `PFR-KANBOARD-TEST`: 9/10 pruebas pasaron (la restante quedó pendiente
  por falta de una cuenta de rol Standard en el entorno de prueba, no
  bloquea el cierre de la fase).
- **v1.1** el mismo día: modo "👥 Todos" (ver tareas de todo el equipo a
  la vez, incluidas las sin asignar) + resumen numérico. 8/8 pruebas
  pasaron.

📌 Ver [sección 5](#5-desarrollo-propio-plugin-teamworkload) para el detalle del plugin.

---

### 2026-07-27 — Reorganización de la documentación + exploración de acceso por red

**Commits:** [`277adba`](https://github.com/BrahianBeap/LDX/commit/277adba) (09:16), [`d371897`](https://github.com/BrahianBeap/LDX/commit/d371897) (11:08), [`cba54d9`](https://github.com/BrahianBeap/LDX/commit/cba54d9) (17:52), [`a8669bc`](https://github.com/BrahianBeap/LDX/commit/a8669bc) (18:01)

- **El plugin deja de ser un experimento de laboratorio.** Se promovió a
  su propia carpeta [`proyectos/kanboard-team-workload/`](../../proyectos/kanboard-team-workload/),
  con README, CHANGELOG propio y registro histórico de decisiones —
  mismo criterio que ya usa el repo para separar "estado actual" de
  "registro histórico" (ver [sección 5](#5-desarrollo-propio-plugin-teamworkload)).
- El usuario obtuvo **acceso root real** en `pfr-oss` y se evaluó si
  convenía abrir un rango de IP en el firewall del host para reemplazar el
  túnel SSH individual. **Exploración de solo lectura**, sin cambios —
  conclusión: 🟡 no conviene abrir un rango; la vía consistente con la
  arquitectura ya documentada (patrón "gateway de servicios") es exponer
  Kanboard a través de `PFR-OSS-GW-SRV`, pero ese mecanismo **todavía no
  está implementado en ningún gateway del cluster** (sería el primer caso
  real). Ver [informe completo](../2026-07-27_exploracion-rutas-firewall-pfr-oss/informe-migracion-a-pfr-oss-gw-srv.md).
- **Con la demo interna del día siguiente (2026-07-28) ya agendada**, se
  implementó — con aprobación explícita del usuario — un **acceso
  temporal**: 6 IPs puntuales autorizadas por firewall hacia el puerto
  8080, sin tocar el túnel SSH original ni la vía definitiva (que sigue
  pendiente del trámite formal con Norberto/Seguridad). Ejecutado y
  validado paso a paso, con rollback documentado.

📌 Procedimiento completo con cada comando real: [`SOP-acceso-temporal-demo-kanboard.md`](../2026-07-27_exploracion-rutas-firewall-pfr-oss/SOP-acceso-temporal-demo-kanboard.md).

#### 3.2 Decisión: acceso temporal por firewall en vez de esperar la vía definitiva

> 🟢 Implementado y validado, 2026-07-27 — vigencia explícitamente
> temporal, solo para la demo del 2026-07-28.

La vía "correcta" según la arquitectura (gateway de servicios
`PFR-OSS-GW-SRV`) requiere un trámite formal de alta de servicio con
seguridad — el mismo circuito usado para PFR1, CAR1 y FDO1 — que no
alcanzaba a completarse antes de la demo. Se optó por una excepción
puntual, acotada (6 IPs, un puerto, con fecha de retiro), en vez de
demorar la demo o forzar la vía definitiva sin el trámite correspondiente.

---

### 2026-07-28 — Demo interna e investigación de la vía definitiva

**Commit:** [`65cf194`](https://github.com/BrahianBeap/LDX/commit/65cf194) (06:13)

- Investigación exhaustiva (15 términos técnicos buscados en todo el
  repositorio) para determinar qué falta exactamente para publicar
  Kanboard vía `PFR-OSS-GW-SRV` de forma definitiva. **Conclusión:**
  ningún gateway del cluster tiene hoy ningún mecanismo de reenvío de
  puertos (NAT/DNAT) configurado — Kanboard sería el primer caso real de
  uso de ese patrón, no hay precedente del que copiar el procedimiento.
- Quedó un checklist explícito de lo que falta decidir con Norberto antes
  de implementar la vía definitiva (mecanismo de reenvío, proyecto LXD
  final de Kanboard, puerto/HTTPS, trámite formal de alta de servicio).

📌 Informe completo: [`informe-migracion-a-pfr-oss-gw-srv.md`](../2026-07-27_exploracion-rutas-firewall-pfr-oss/informe-migracion-a-pfr-oss-gw-srv.md).

---

### 2026-07-28 (más tarde) — Se resuelve el mecanismo de exposición definitivo

**Reunión:** `reunion/LXD - Configuración FDO.vtt` — **Decisión:** [ADR-0008](../../docs/adr/ADR-0008-gateway-balanceador-dos-etapas.md)

La pregunta que quedó explícitamente abierta esa misma mañana (sección
anterior) se resolvió con Norberto Núñez en esta reunión: el reenvío
directo a nivel de host (lo implementado para la demo de Kanboard) **es
válido pero no escala** a múltiples réplicas ni a varios servicios detrás
de un mismo certificado TLS. Se decidió un modelo de **dos etapas**:

```
Petición externa
   → contenedor GATEWAY (reglas de firewall, ya existente por sitio)
   → contenedor BALANCEADOR nuevo (Apache, TLS centralizado, ruteo por URL/path)
   → contenedor de la aplicación (Kanboard, en este caso)
```

Se decidió explícitamente **migrar Kanboard a este modelo y retirar el
acceso temporal por firewall** una vez aplicado — queda como pendiente de
seguimiento del propio ADR-0008, no como algo ya hecho.

📌 Detalle completo, alternativas evaluadas y pendientes de seguimiento:
[ADR-0008](../../docs/adr/ADR-0008-gateway-balanceador-dos-etapas.md).

---

## 4. Decisiones clave — resumen para referencia rápida

| # | Decisión | Fecha | Por qué |
|---|---|---|---|
| 1 | Carga de contenido manual, no scripteada por API | 2026-07-25 | Menor riesgo antes de la demo; el usuario se familiariza con el flujo real de Kanboard |
| 2 | Un proyecto de Kanboard por sistema/producto, no un solo tablero con etiquetas | 2026-07-25 | El plan original mezclaba sistemas distintos en un mismo tablero y dejaba sin uso real el concepto de tag |
| 3 | Flujo de 5 columnas estándar para proyectos tipo Desarrollo (INFRAWORK como plantilla) | 2026-07-26 | Evitar que cada proyecto invente su propio flujo sin criterio común |
| 4 | Plugin propio (TeamWorkload) en vez de adoptar un plugin de terceros | 2026-07-26 | Ninguna solución existente resolvía la necesidad completa; se encontró una base reutilizable en el propio Core de Kanboard |
| 5 | Contenedor de Kanboard en el proyecto `default`, no en `PRJ-OSS` | 2026-07-24 | `PRJ-OSS` bloquea dispositivos `proxy` por diseño ([ADR-0007](../../docs/adr/ADR-0007-proyectos-lxd-multitenancy.md)) |
| 6 | Acceso temporal por firewall (6 IPs) para la demo, en vez de esperar la vía definitiva | 2026-07-27 | El trámite formal de alta de servicio no alcanzaba a completarse antes de la demo agendada |
| 7 | Promover el plugin de `laboratorio/` a `proyectos/` con ciclo de versiones propio | 2026-07-27 | Dejó de ser un experimento puntual — pasó a ser software mantenido, con su propio historial |
| 8 | Modelo definitivo de exposición: gateway + balanceador en dos etapas ([ADR-0008](../../docs/adr/ADR-0008-gateway-balanceador-dos-etapas.md)) | 2026-07-28 | El reenvío directo a nivel de host (usado para la demo) no escala a varios servicios/réplicas ni centraliza el certificado TLS |

---

## 5. Desarrollo propio: plugin TeamWorkload

Kanboard, al organizarse por proyecto/sistema (ver decisión #2), perdió la
vista única que sí tenía Planner ("todo lo mío en un solo lugar"). Se
desarrolló un plugin propio para resolver exactamente eso.

| Versión | Fecha | Qué agrega |
|---|---|---|
| Investigación previa | 2026-07-26 | Se determinó que ningún plugin existente resolvía la necesidad; se decidió una arquitectura liviana apoyada en modelos ya existentes del Core |
| Fase 1 (v1.0) | 2026-07-26 | Vista de solo lectura: tareas abiertas de una persona en todos sus proyectos, agrupadas por proyecto, restringida a administradores. 9/10 pruebas pasaron |
| v1.1 | 2026-07-26 | Modo "👥 Todos" (todo el equipo a la vez, incluidas tareas sin asignar) + resumen numérico. 8/8 pruebas pasaron |

**Filosofía de desarrollo acordada:** reutilizar siempre el Core antes de
escribir código nuevo, no duplicar lógica, no modificar el Core, mantener
el plugin lo más pequeño posible.

📌 Documentación viva del plugin (arquitectura actual, investigación,
CHANGELOG, decisiones de diseño por versión): [`proyectos/kanboard-team-workload/`](../../proyectos/kanboard-team-workload/).

---

## 6. Qué queda pendiente (para la conversación con el director)

| Pendiente | Bloquea | Estado |
|---|---|---|
| Migrar el resto de los proyectos de Planner (VulnApp, Portal OSS, SOC, NCE, ODCIMLISY, Video Wall, etc.) | Cierre completo de la migración | 🔴 No iniciado — explícitamente aplazado por el usuario |
| ~~Definir la vía de acceso definitiva~~ → **Aplicar** el modelo ya decidido (gateway + balanceador, [ADR-0008](../../docs/adr/ADR-0008-gateway-balanceador-dos-etapas.md)) | Reemplazar el acceso temporal de la demo | 🟡 Modelo **decidido** (2026-07-28) — falta crear el contenedor balanceador y migrar Kanboard a este esquema |
| Confirmar la sintaxis exacta de la regla de firewalld del gateway hacia el balanceador | Aplicar ADR-0008 en cualquier sitio | 🔴 Pendiente de una siguiente sesión con Norberto (no quedó del todo confirmada en la reunión) |
| Retirar el acceso temporal (6 IPs por firewall) una vez migrado al modelo definitivo | Higiene de seguridad | 🔴 Pendiente, procedimiento de rollback ya documentado |
| Trámite formal de alta de servicio para el puerto/IP de Kanboard | Vía definitiva | 🔴 No iniciado (mismo circuito ya usado para PFR1, CAR1, FDO1) |
| Decidir si Kanboard migra al proyecto `PRJ-OSS` o sigue en `default` | Vía definitiva / consistencia con ADR-0007 | 🔴 No decidido |
| Migrar de SQLite a una base de datos definitiva | Estabilidad — ya se observó `database is locked` con uso concurrente | 🔴 Pendiente |
| Traducciones al español del plugin TeamWorkload | Experiencia de usuario | 🔴 Pendiente |
| Prueba del plugin con una cuenta de rol Standard (no admin) | Validación completa de permisos | 🔴 Pendiente — no existe todavía esa cuenta en el entorno |
| Corregir roles `app-admin` de los usuarios migrados | Modelo de permisos correcto | 🔴 Pendiente |
| Próxima versión del plugin (filtros, agrupar por prioridad/fecha/tags) | Mejora incremental, no bloquea nada ya entregado | 🔴 No iniciada, camino ya documentado |

---

## 7. Fuentes (para profundizar en cualquier punto)

| Tema | Documento |
|---|---|
| Experimento del contenedor de Kanboard | [`laboratorio/2026-07-24_kanboard-contenedor-prueba/`](../2026-07-24_kanboard-contenedor-prueba/) |
| Migración de contenido Planner → Kanboard | [`laboratorio/2026-07-25_migracion-planner-a-kanboard/`](../2026-07-25_migracion-planner-a-kanboard/) |
| Estándar de organización vigente | [`estandar-organizacion-kanboard.md`](../2026-07-25_migracion-planner-a-kanboard/estandar-organizacion-kanboard.md) |
| Plugin TeamWorkload (arquitectura, investigación, CHANGELOG, decisiones) | [`proyectos/kanboard-team-workload/`](../../proyectos/kanboard-team-workload/) |
| Exploración de red/firewall + acceso temporal para la demo | [`laboratorio/2026-07-27_exploracion-rutas-firewall-pfr-oss/`](../2026-07-27_exploracion-rutas-firewall-pfr-oss/) |
| Por qué el proyecto LXD de Kanboard no es `PRJ-OSS` | [ADR-0007](../../docs/adr/ADR-0007-proyectos-lxd-multitenancy.md) |
| Patrón de arquitectura "gateway de servicios" | [`docs/02_Arquitectura.md`](../../docs/02_Arquitectura.md), [`docs/03_Componentes.md`](../../docs/03_Componentes.md) |
| Modelo definitivo de exposición (gateway + balanceador) que reemplazará el acceso temporal de Kanboard | [ADR-0008](../../docs/adr/ADR-0008-gateway-balanceador-dos-etapas.md) |
| Avance de **todo** el proyecto LDX para presentación a dirección (no solo Kanboard) | [`docs/17_Avance_Presentacion.md`](../../docs/17_Avance_Presentacion.md) |
