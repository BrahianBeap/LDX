# 17 — Avance del proyecto: línea de tiempo para presentación

> **Audiencia:** Dirección / stakeholders no técnicos.
> **Propósito:** Insumo para armar la presentación (.ppt) de avance del proyecto. Resume qué había antes, qué se hizo, qué decisiones se tomaron y cuánto tiempo llevó. No reemplaza la documentación técnica detallada — cada sección enlaza al documento fuente si se necesita profundizar.
> **Corte de esta versión:** 2026-07-30.
> **Clasificación:** ✅ hecho confirmado · 🟡 inferencia razonable · 🔴 pendiente de validación (mismo criterio que el resto del repositorio, ver [`CLAUDE.md`](../CLAUDE.md)).

---

## 1. Resumen en una línea

En 5 semanas (2026-06-25 → 2026-07-30), el equipo pasó de **cero infraestructura de contenedores** a un **cluster LXD de 2 sitios geográficos funcionando en red**, con un **modelo de arquitectura estándar para publicar servicios** ya decidido, y **Kanboard operativo** como herramienta de gestión de tareas del equipo (reemplazo de Microsoft Planner).

---

## 2. Punto de partida (antes del proyecto)

| Situación | Problema |
|---|---|
| Servidores en **CentOS 7** | Sistema operativo en *End of Life* — sin parches de seguridad desde hace tiempo |
| Modelo **monolítico**: un servidor = un stack completo de servicios | Si cae el servidor, caen todos sus servicios. Actualizar un componente (ej. PHP) obliga a tocar todo el stack |
| **InfraFileRoom** (~800 GB de datos) corriendo en CentOS 7 | Servicio productivo expuesto, sin plan de migración |
| Gestión de tareas del equipo en **Microsoft Planner**, dispersa | Sin estándar de organización entre proyectos |
| Sin arquitectura definida para exponer servicios con alta disponibilidad | Cada caso se resolvía ad-hoc |

Ver el detalle completo en [01_Contexto.md](01_Contexto.md).

---

## 3. Línea de tiempo de avance

| Fecha | Hito | Detalle |
|---|---|---|
| 🔴 sin confirmar (procesada 2026-06-25) | **Reunión 1 — Instalación inicial** | Se instala LXD en el primer sitio (Franco/PFR1): storage ZFS, MicroOVN, Web UI, primer contenedor de prueba con Apache/PHP vía cloud-init |
| 2026-06-25 | **Repositorio LDX creado** | Base de conocimiento técnica del proyecto inicializada; primera reunión documentada por completo (17 documentos técnicos) |
| 2026-06-25 | **Auditorías de calidad** | Revisión arquitectónica externa + auditoría interna de la documentación, para asegurar que la base de conocimiento sea confiable desde el arranque |
| 🔴 sin confirmar (procesada 2026-07-24) | **Reunión 2 — Segundo sitio e implementación** | Se une **Carpinelli (CAR1)** como segundo sitio del cluster. Se resuelve el bloqueo de red entre sitios con WireGuard. Se adopta el modelo de **proyectos LXD** (aislamiento entre equipos) |
| 2026-07-25 | **Kanboard: primer contenedor de prueba** | Se levanta Kanboard como aplicación de prueba del cluster (`PFR-KANBOARD-TEST`). Se define el estándar de organización para migrar todos los proyectos desde Planner |
| 2026-07-25 – 07-26 | **Migración de Planner a Kanboard** | Se migran los primeros dos proyectos del equipo (**INFRAWORK** como piloto, **ADM-TECH** en segundo lugar), validando el estándar de organización |
| 2026-07-26 | **Plugin propio para Kanboard** | Se desarrolla **TeamWorkload**, plugin propio para ver la carga de trabajo del equipo por usuario |
| 2026-07-27 | **Investigación de exposición de Kanboard** | Se investiga cómo publicar Kanboard de forma definitiva a través del gateway del cluster — queda una pregunta técnica abierta para resolver con el consultor |
| 2026-07-27 | **Acceso temporal a Kanboard habilitado** | Se habilita acceso directo (6 personas autorizadas) para una demo interna, como solución puente mientras se define la vía definitiva |
| **2026-07-28** | **Reunión 3 — Arquitectura de exposición de servicios** | Se define y se prueba en vivo el modelo definitivo para publicar servicios: **gateway + balanceador en dos etapas**, con certificado TLS centralizado. Resuelve la pregunta abierta del 2026-07-27 |
| 2026-07-30 | **Documentación consolidada** | Se documenta formalmente la decisión de arquitectura (ADR-0008) y se actualiza toda la base de conocimiento técnica en consecuencia |

📁 Fuente completa y detallada de cada hito: [13_Linea_de_Tiempo.md](13_Linea_de_Tiempo.md).

---

## 4. Decisiones clave tomadas

| # | Decisión | Fecha | Por qué |
|---|---|---|---|
| ADR-0002 | Red de contenedores: **OVN**, no Ubuntu Fan | 2026-06-25 | La red de gestión disponible es demasiado chica (`/29`) para lo que exige Ubuntu Fan |
| ADR-0003 | Almacenamiento: **ZFS** | 2026-06-25 | Snapshots instantáneos y verificación de integridad de datos incluidos |
| ADR-0004 | Acceso a la Web UI: **certificado + token** | 2026-06-25 | Estándar de LXD, sin depender de usuarios y contraseñas |
| ADR-0005 | **Un servicio por contenedor** | 2026-06-25 | Aísla fallas y permite actualizar cada componente sin tocar los demás |
| ADR-0006 | **WireGuard** como enlace cifrado entre sitios | 2026-07-24 | La red corporativa bloqueaba el tráfico nativo entre sitios geográficos distintos |
| ADR-0007 | **Proyectos LXD** para separar equipos | 2026-07-24 | Prepara el cluster para recibir más equipos sin que se pisen recursos entre sí |
| ADR-0008 | **Gateway + balanceador** para publicar servicios | 2026-07-28 | Permite publicar varios servicios detrás de un mismo punto de entrada, con un solo certificado TLS, sin depender de tocar el firewall del servidor cada vez |

📁 Detalle completo de cada decisión (alternativas evaluadas, consecuencias): [`docs/adr/`](adr/).

---

## 5. Cómo está el proyecto hoy (2026-07-30)

- ✅ **2 de 3 sitios geográficos** del cluster instalados y comunicados en red (Franco y Carpinelli). Falta el tercer sitio (Fernando) para completar la redundancia total.
- ✅ **Modelo estándar de arquitectura** definido y probado para publicar servicios nuevos con alta disponibilidad (gateway + balanceador).
- ✅ **Kanboard operativo** como sistema de gestión de tareas del equipo, con 2 proyectos ya migrados desde Planner bajo un estándar común, y una herramienta propia (TeamWorkload) para ver la carga de trabajo del equipo.
- 🟡 Kanboard hoy se accede por una **vía temporal** (pensada solo para una demo puntual) — la vía definitiva ya está diseñada (ADR-0008) pero falta aplicarla.
- 🔴 Aún no hay servicios de producción corriendo sobre el cluster (el foco hasta ahora fue dejar la base de infraestructura y el modelo de arquitectura listos).

---

## 6. Antes vs. Ahora

| Aspecto | Antes | Ahora |
|---|---|---|
| Sistema operativo base | CentOS 7 (sin soporte) | Ubuntu LTS en contenedores LXD |
| Modelo de despliegue | Un servidor = todos los servicios juntos | Un contenedor por servicio |
| Sitios geográficos activos | 0 | 2 de 3 (Franco, Carpinelli) |
| Red entre sitios | No existía | Funcional, cifrada (WireGuard + OVN) |
| Aislamiento entre equipos | No existía | Proyectos LXD dedicados por equipo |
| Cómo se publica un servicio | Sin definir / ad-hoc | Modelo estándar (gateway + balanceador), documentado y probado |
| Gestión de tareas del equipo | Microsoft Planner, sin estándar | Kanboard, con estándar de organización y herramienta propia (TeamWorkload) |

---

## 7. Kanboard: caso de uso ya en marcha

- Migrado desde Microsoft Planner como piloto para validar tanto el cluster LXD como el nuevo estándar de organización de tareas.
- **INFRAWORK** y **ADM-TECH** ya migrados y en uso.
- Plugin propio **TeamWorkload** desarrollado para dar visibilidad de carga de trabajo por persona — no es una funcionalidad de fábrica de Kanboard.
- Próximo paso ya identificado: **migrar VulnApp** y adaptar su organización a las necesidades específicas de ese proyecto, siguiendo el mismo estándar ya validado con INFRAWORK y ADM-TECH.

📁 Detalle: [`laboratorio/2026-07-25_migracion-planner-a-kanboard/`](../laboratorio/2026-07-25_migracion-planner-a-kanboard/) y [`proyectos/kanboard-team-workload/`](../proyectos/kanboard-team-workload/).

---

## 8. Próximos pasos

| Paso | Estado |
|---|---|
| Incorporar el tercer sitio (Fernando/FDO1) al cluster | 🔴 Pendiente |
| Aplicar el modelo gateway + balanceador para publicar Kanboard de forma definitiva (retirando el acceso temporal) | 🔴 Pendiente |
| Migrar **VulnApp** a Kanboard con organización a medida | 🔴 Próximo paso acordado con el equipo |
| Definir plan de migración de InfraFileRoom (CentOS 7, ~800 GB) | 🔴 Pendiente |
| Onboarding de equipos adicionales usando proyectos LXD dedicados | 🔴 Pendiente |

📁 Lista completa: [13_Linea_de_Tiempo.md](13_Linea_de_Tiempo.md).

---

## 9. Tiempo y esfuerzo dedicado

- **Duración hasta la fecha:** 35 días corridos (2026-06-25 → 2026-07-30).
- **Reuniones técnicas formales con el consultor (Norberto Núñez):** 3, cubriendo instalación inicial, incorporación del segundo sitio, y arquitectura de exposición de servicios.
- **Trabajo iterativo entre reuniones:** documentado en 20 entregas registradas sobre el repositorio del proyecto entre el 2026-06-25 y el 2026-07-30 — instalación, pruebas de Kanboard, desarrollo del plugin propio, investigación técnica y consolidación de documentación.
- **Cobertura de documentación técnica:** 17 documentos temáticos + 8 decisiones de arquitectura (ADR) formalmente registradas, además de bitácoras de laboratorio para cada experimento.

---

## Documentos relacionados

| Tema | Documento |
|---|---|
| Línea de tiempo técnica completa | [13_Linea_de_Tiempo.md](13_Linea_de_Tiempo.md) |
| Resumen ejecutivo del proyecto | [00_Resumen_Ejecutivo.md](00_Resumen_Ejecutivo.md) |
| Decisiones de arquitectura completas | [`docs/adr/`](adr/) |
| Riesgos abiertos | [11_Riesgos.md](11_Riesgos.md) |
| Historial de cambios del repositorio | [`CHANGELOG.md`](../CHANGELOG.md) |
