# CHANGELOG — Historial de cambios del repositorio LDX

Este archivo registra todos los cambios importantes del repositorio: nuevos documentos, actualizaciones significativas y decisiones sobre la estructura.

---

## Formato de entrada

Cada entrada debe incluir:

| Campo | Descripción |
|---|---|
| **Fecha** | YYYY-MM-DD |
| **Fuente** | Reunión, laboratorio, implementación, decisión de equipo |
| **Documentos afectados** | Lista de archivos modificados o creados |
| **Resumen** | Descripción breve del cambio y su motivo |

---

## Historial

### 2026-06-25 (primera entrada)

**Fuente:** Inicialización del repositorio — decisión de equipo

**Documentos afectados:**
- `README.md` — creado (refactorizado de `README.txt`)
- `CLAUDE.md` — creado (refactorizado de `CLAUDE.txt`)
- `CHANGELOG.md` — creado
- `reunion/README.md` — creado
- `reunion/Llamada con Daniel y 3 personas más.vtt` — movido desde raíz
- `docs/README.md` — creado
- `docs/adr/ADR-0001-template.md` — creado
- `laboratorio/README.md` — creado
- `recursos/prompt_analisis_reunion.md` — creado (renombrado de `promt_inicial.txt`)

**Estructura de carpetas creada:**
`docs/`, `docs/adr/`, `reunion/`, `laboratorio/`, `recursos/`, `diagramas/`, `imagenes/`, `scripts/`

**Resumen:**
Inicialización del repositorio LDX como base de conocimiento técnica oficial. Los archivos originales en formato `.txt` fueron refactorizados a `.md` y reorganizados según sus responsabilidades: `README.md` cubre la orientación humana (qué es el repo, estructura, flujo de trabajo y principios); `CLAUDE.md` cubre las instrucciones para el asistente IA (estándares de documentación, clasificación y proceso de análisis de reuniones). La duplicación existente entre ambos archivos fue eliminada distribuyendo el contenido según la audiencia de cada documento. Se incorporó `docs/adr/` para registrar decisiones de arquitectura (estándar ADR de Michael Nygard) y `laboratorio/` como área de staging para experimentos.

---

### 2026-06-25 (segunda entrada)

**Fuente:** Análisis completo de `reunion/Llamada con Daniel y 3 personas más.vtt` — Primera reunión de instalación del cluster LXD (participantes: Norberto Núñez, Marcos Casco, Daniel Medina, Elías Alfonzo, Rocío Duarte).

**Documentos creados:**
- `docs/00_Resumen_Ejecutivo.md` — Visión general, estado actual y objetivos del proyecto
- `docs/01_Contexto.md` — Contexto de negocio, por qué existe el proyecto, equipos involucrados
- `docs/02_Arquitectura.md` — Arquitectura del cluster: sitios, redes, storage, diagramas ASCII
- `docs/03_Componentes.md` — Descripción de cada componente (LXD, MicroOVN, ZFS, firewalld, cloud-init, etc.)
- `docs/04_Instalacion.md` — Procedimiento completo de instalación paso a paso (9 pasos)
- `docs/05_Configuracion.md` — Configuración de proxy, cloud-init, perfiles, dispositivos proxy, firewall
- `docs/06_Operacion.md` — Gestión de contenedores, imágenes, perfiles, migración, backup
- `docs/07_Troubleshooting.md` — 8 fichas de problemas conocidos con diagnóstico y solución
- `docs/08_Glosario.md` — Diccionario completo de términos técnicos del proyecto
- `docs/09_FAQ.md` — Preguntas frecuentes sobre LXD, cloud-init, red y seguridad
- `docs/10_Decisiones.md` — Resumen ejecutivo de 4 decisiones de arquitectura con links a ADRs
- `docs/11_Riesgos.md` — 8 riesgos identificados con severidad y acciones requeridas
- `docs/12_Lecciones_Aprendidas.md` — 9 lecciones tácitas extraídas de la instalación inicial
- `docs/13_Linea_de_Tiempo.md` — Hitos completados y roadmap pendiente
- `docs/14_Manual_Operativo.md` — Checklist de salud, monitoreo, escalamiento de incidentes

**ADRs creados:**
- `docs/adr/ADR-0002-red-ovn-vs-ubuntu-fan.md` — OVN elegido sobre Ubuntu Fan (incompatibilidad /29)
- `docs/adr/ADR-0003-storage-zfs.md` — ZFS elegido sobre LVM y btrfs
- `docs/adr/ADR-0004-autenticacion-tls-tokens.md` — Autenticación via TLS tokens + certificados
- `docs/adr/ADR-0005-arquitectura-microservicios.md` — Un servicio por contenedor

**Archivos actualizados:**
- `docs/README.md` — Índice actualizado con todos los documentos en estado "Completo"
- `reunion/README.md` — VTT marcado como "Analizada"

**Resumen:**
Primera generación completa de documentación técnica a partir del análisis de la reunión inaugural. El cluster LXD está en fase inicial: PFR1 instalado, CAR1 y FDO1 pendientes. OVN no funcional aún (requiere VLAN 411). Toda la información marcada como 🔴 Pendiente de validación debe ser confirmada con el equipo en la próxima reunión.

---

### 2026-06-25 (tercera entrada)

**Fuente:** Revisión arquitectónica independiente — análisis crítico desde perspectiva de consultor externo senior (Arquitecto Empresarial, SRE, Platform Engineer, Cloud Architect).

**Documentos creados:**
- `docs/15_Revision_Arquitectonica.md` — Auditoría técnica integral: análisis crítico de HA, red, almacenamiento, seguridad, operación, observabilidad, DR, backup, automatización, escalabilidad, deuda técnica, preguntas sin respuesta y recomendaciones priorizadas (Crítico / Alto / Medio / Bajo)

**Archivos actualizados:**
- `docs/README.md` — Doc 15 agregado al índice
- `CHANGELOG.md` — Esta entrada

**Resumen:**
Auditoría externa independiente del sistema en su estado actual. Conclusión principal: el sistema no está listo para producción por 7 SPOFs identificados, OVN no funcional, pool ZFS insuficiente para InfraFileRoom, y ausencia de DR, observabilidad y automatización. Se documentaron 7 ítems críticos a completar antes de producción, 10 ítems de prioridad alta y comparación completa contra mejores prácticas de Canonical, Google SRE, CNCF e infraestructura empresarial.

---

### 2026-06-25 (cuarta entrada)

**Fuente:** Auditoría interna de calidad del Knowledge Base — revisión completa de los 26 archivos del repositorio.

**Documentos creados:**
- `docs/16_Auditoria_Knowledge_Base.md` — Informe de auditoría: fortalezas, debilidades, 10 conjuntos de contenido duplicado, 8 inconsistencias (1 error técnico en diagrama de dependencias), 7 riesgos de mantenimiento, 17 recomendaciones y plan de mejora en 4 prioridades.

**Archivos actualizados:**
- `docs/README.md` — Doc 16 agregado al índice
- `CHANGELOG.md` — Esta entrada

**Resumen:**
La mayor amenaza identificada es el contenido duplicado: 10 conjuntos de conceptos técnicos explicados en 2-6 lugares distintos. Se identificó también un error técnico en el diagrama de dependencias de `13_Linea_de_Tiempo.md` (VLAN 411 no es prerequisito de instalación de nodos), un anchor roto en `14_Manual_Operativo.md`, y 4 términos técnicos usados pero no definidos en el glosario (Dqlite, quórum, split-brain, live migration).

---

### 2026-06-25 (quinta entrada)

**Fuente:** Fase de refinamiento y consolidación — aplicación de todas las mejoras identificadas en `docs/16_Auditoria_Knowledge_Base.md`.

**Errores objetivos corregidos:**
- `docs/08_Glosario.md` — 6 términos nuevos agregados: Dqlite, live migration, quórum, RPO, RTO, split-brain
- `docs/13_Linea_de_Tiempo.md` — Corregido error técnico: diagrama ahora muestra instalación de nodos y VLAN 411 como acciones paralelas e independientes (antes VLAN 411 aparecía incorrectamente como prerequisito de instalación de nodos)
- `docs/14_Manual_Operativo.md` — Reparado anchor roto (`#trb-004` movido de texto de display a href del enlace)
- `docs/adr/ADR-0003-storage-zfs.md` — Corregida referencia imprecisa a RIE-006 en sección Referencias; reemplazada por enlace genérico a `11_Riesgos.md`
- `README.md` — Eliminada nota obsoleta sobre descripción pendiente de LDX (la descripción ya existe en `docs/`)
- `docs/README.md` — Corregida atribución de fuente: aclarado que docs 15 y 16 son informes de análisis independiente, no derivados de la reunión VTT

**Duplicaciones eliminadas:**
- `docs/12_Lecciones_Aprendidas.md` — 5 lecciones consolidadas (LL-001, LL-002, LL-003, LL-005, LL-008, LL-009): se conservan los párrafos narrativos "¿Qué pasó?" y las citas directas de Norberto; las re-explicaciones de reglas ya documentadas se reemplazaron por una oración concisa + enlace al documento dueño (07_Troubleshooting.md, 05_Configuracion.md, 06_Operacion.md)
- `docs/09_FAQ.md` — 8 respuestas convertidas a portal de navegación: "¿Cloud-init se ejecuta en cada reinicio?", "Modifiqué el perfil...", "¿Los contenedores migran automáticamente?", "¿Por qué no funciona la red entre nodos?", "¿Puedo acceder a la Web UI desde fuera?", "¿Por qué se usa un proxy HTTP?", "¿Por qué se descartó Ubuntu Fan?", "¿Por qué ZFS?" — cada una reemplazada por 1-2 oraciones + enlace al documento dueño (07_Troubleshooting.md, 05_Configuracion.md, 11_Riesgos.md, ADR-0002, ADR-0003)

**Resumen:**
Fase de aplicación de la auditoría. Se corrigieron todos los errores objetivos (Prioridad 1) y se eliminaron las duplicaciones identificadas (Prioridad 2). El repositorio queda con una única fuente de verdad por concepto: los documentos 07, 05, 06, 11 y los ADRs son ahora los únicos lugares donde se documentan las reglas técnicas; los demás documentos enlazan a ellos.

---

### 2026-07-24 (sexta entrada)

**Fuente:** Análisis completo de `reunion/segunda_reunion LXD _ Implementacion.vtt` — Segunda reunión de implementación del cluster LXD (participantes: Norberto Núñez, Marcos Casco, Elías Alfonzo, Rocío Duarte, Daniel Medina, Andrés Semidei, Fernando Fleitas).

**ADRs creados:**
- `docs/adr/ADR-0006-wireguard-underlay-ovn-multisitio.md` — WireGuard elegido como transporte underlay para el túnel de datos de OVN entre sitios en Capa 3 separada (el túnel nativo de OVN es bloqueado por la red corporativa entre Franco y Carpinelli y no cifra el tráfico). Aclara además que la VLAN de servicio no necesita ser idéntica entre sitios — solo el nombre de la interfaz.
- `docs/adr/ADR-0007-proyectos-lxd-multitenancy.md` — Proyectos LXD (`lxc project`) con límites de recursos y grupos de identidad adoptados como modelo estándar de aislamiento multi-tenant, en previsión de futuros equipos (CCR, OMC, AIT/transporte).

**Archivos actualizados (todos los documentos 00–14 y ADR-0002):**
- `docs/00_Resumen_Ejecutivo.md`, `docs/01_Contexto.md`, `docs/02_Arquitectura.md`, `docs/03_Componentes.md` — incorporación de CAR1 al cluster, modelo de proyectos, gateways de servicio por sitio
- `docs/04_Instalacion.md` — procedimiento de unión de un nuevo miembro al cluster vía token, `snap refresh --hold`, configuración de WireGuard, renombrado de interfaces por MAC con `netplan`
- `docs/05_Configuracion.md` — configuración de proyectos LXD y sus límites, WireGuard (claves, peers, rutas), reenvío de logs a Loki externo vía `rsyslog`
- `docs/06_Operacion.md`, `docs/07_Troubleshooting.md` — TRB-009 (bloqueos intermitentes del cluster por desincronización de reloj/NTP), TRB-010 (bloqueo del cluster por versiones de LXD desincronizadas)
- `docs/08_Glosario.md` — términos nuevos: WireGuard, proyecto LXD, IPVLAN, gateway de servicios, Loki, Dqlite (uso ampliado)
- `docs/09_FAQ.md`, `docs/10_Decisiones.md` — referencias a ADR-0006 y ADR-0007
- `docs/11_Riesgos.md` — riesgo de configuración manual de WireGuard no persistida en `netplan`; puerto 8444 de CAR1 pendiente de alta de servicio
- `docs/12_Lecciones_Aprendidas.md` — LL-011 (`snap refresh --hold` obligatorio en cluster)
- `docs/13_Linea_de_Tiempo.md` — CAR1 unido al cluster, pendientes de FDO1 e IT
- `docs/14_Manual_Operativo.md` — ajustes menores de coherencia
- `docs/adr/ADR-0002-red-ovn-vs-ubuntu-fan.md` — actualizado para reflejar que el transporte entre sitios requiere WireGuard como underlay (ver ADR-0006)
- `reunion/README.md` — segunda reunión agregada a la tabla de reuniones disponibles
- `docs/README.md` — ADR-0006 y ADR-0007 agregados al índice; nota de fuente actualizada para reflejar ambas reuniones

**Resumen:**
Segunda generación de documentación técnica, a partir de la reunión donde se incorporó CAR1 (Carpinelli) como segundo miembro del cluster. Los hallazgos más relevantes: el túnel de datos nativo de OVN no funciona entre sitios en Capa 3 separada (confirmado por segunda vez, tras un intento fallido el año anterior) y se resolvió con una malla WireGuard como underlay; se adoptó el modelo de proyectos LXD para multi-tenancy de cara a futuros equipos; se documentó el incidente real de bloqueo del cluster por desincronización de reloj entre Carpinelli y Fernando. Persisten pendientes de validación: persistencia de la IP de WireGuard en `netplan`, alta de servicio del puerto 8444 de CAR1, y confirmación de la directiva de reenvío `rsyslog` → Loki.

---

### 2026-07-26 (séptima entrada)

**Fuente:** Migración manual de Microsoft Planner ("Proyectos OSS") a Kanboard — trabajo iterativo en `laboratorio/2026-07-25_migracion-planner-a-kanboard/`.

**Documentos creados:**
- `laboratorio/2026-07-25_migracion-planner-a-kanboard/estandar-organizacion-kanboard.md` — estándar de organización consolidado para toda migración futura a Kanboard: un proyecto por sistema/producto, flujo de columnas definido por tipo de proyecto (no por proyecto individual), convención de nombres de tarea `<Módulo> - <Funcionalidad>`, tags reservados a clasificación funcional/técnica, subtareas solo para acciones concretas de trabajo, comentarios para reuniones/decisiones/avances cronológicos, y metodología de ejecución (carga 100% manual del usuario en la interfaz de Kanboard).

**Archivos actualizados:**
- `laboratorio/2026-07-25_migracion-planner-a-kanboard/README.md` — mapeo de conceptos y progreso actualizados al nuevo estándar
- `laboratorio/2026-07-25_migracion-planner-a-kanboard/bitacora.md` — INFRAWORK y ADM-TECH registrados como migrados

**Resumen:**
Tras un primer enfoque descartado (un único proyecto "Proyectos OSS" con tags por etiqueta de Planner), se adoptó un modelo de un proyecto de Kanboard por sistema. INFRAWORK se migró como piloto y quedó como plantilla de referencia para todo proyecto de tipo Desarrollo (flujo de 5 columnas: Pendiente de Análisis → Listo para Desarrollo → En Curso → En Revisión → Realizados). ADM-TECH se migró en segundo lugar con la misma metodología, confirmando el estándar entre proyectos del mismo tipo. Quedan pendientes: VulnApp, Portal OSS, SOC, y la decisión sobre a qué proyecto nuevo mapear las etiquetas pequeñas de Planner sin destino asignado (NCE, NCE-FAN, ODCIMLISY, Video Wall, OSS, TEMBIAPO-SIGAT, Tembiapo OS, y las tareas sin etiqueta) — aplazada explícitamente por el usuario.

---

> **Nota (2026-07-27):** este archivo quedó reservado exclusivamente
> para cambios del proyecto LDX (cluster LXD). El trabajo sobre el
> plugin propio de Kanboard "TeamWorkload" (investigación, Fase 1, v1.1)
> tenía una entrada acá que se retiró — su historial completo vive ahora
> en [`proyectos/kanboard-team-workload/CHANGELOG.md`](proyectos/kanboard-team-workload/CHANGELOG.md).

---

### 2026-10-06 (octava entrada)

**Fuente:** Verificación en vivo del cluster (solo lectura, SSH a `pfr-oss`, `car-oss` y `fdo-oss`) — `laboratorio/2026-10-06_verificacion-viva-cluster/`, a pedido de Elías Alfonzo, para confirmar el estado real del cluster contra lo documentado desde la incorporación de FDO1 en agosto.

**Documentos creados:**
- `laboratorio/2026-10-06_verificacion-viva-cluster/README.md` — objetivo, método (SSH + `paramiko`, estrictamente solo lectura) y resumen de hallazgos
- `laboratorio/2026-10-06_verificacion-viva-cluster/bitacora.md` — salida completa de los comandos ejecutados en los 3 hosts

**Documentos actualizados:**
- `docs/11_Riesgos.md` — RIE-002 (3/3 nodos `ONLINE`) y RIE-013 (OVN en Fernando) marcados 🟡 posiblemente resueltos, con nota de verificación; movidos en la tabla resumen de severidad
- `docs/07_Troubleshooting.md` — TRB-012 marcado 🟡 posiblemente resuelto, causa raíz original aún sin confirmar
- `docs/13_Linea_de_Tiempo.md` — nueva sección "Verificación en vivo del cluster"; filas de FDO1/OVN y Loki+MinIO actualizadas
- `docs/03_Componentes.md` — estado de MicroOVN actualizado; notas sobre contenedores encontrados sin documentar (`C-Mimir-1`) en Prometheus y Grafana
- `docs/14_Manual_Operativo.md` — checklist de "Loki + MinIO propio del proyecto" actualizado con el estado real de los contenedores
- `docs/00_Resumen_Ejecutivo.md` — corregido "2 de 3 sitios" (desactualizado desde antes de esta verificación) a 3 sitios, con el calificador 🟡 correspondiente

**Resumen:**
Relevamiento de solo lectura que encontró evidencia directa de que el cluster tiene sus 3 nodos (`pfr.1`, `car.1`, `fdo.1`) `ONLINE` y que Fernando (FDO1) ya aloja un contenedor (`FDO-WS-1`) conectado a la red OVN — contradiciendo el estado "bloqueado" documentado desde agosto (RIE-013/TRB-012). También se encontraron dos elementos sin documentar previamente: un contenedor `C-Mimir-1` (observabilidad, propósito no confirmado) y un contenedor `CAR-KANBOARD` detenido (posible segundo intento de migrar Kanboard al modelo definitivo). Ningún hallazgo fue confirmado formalmente con el equipo/Norberto Núñez — todos quedan marcados 🟡 o 🔴 según corresponda, con la verificación formal como pendiente explícito.

---

### 2026-10-08 (novena entrada)

**Fuente:** Migración de Kanboard al modelo gateway + balanceador (trabajo de infraestructura en vivo, comandos ejecutados por Elías Alfonzo vía SSH) — `laboratorio/2026-10-08_migracion-kanboard-gateway-balanceador/`, para cerrar el pendiente explícito del ADR-0008 y retirar el acceso temporal de Kanboard habilitado en julio.

**Documentos creados:**
- `laboratorio/2026-10-08_migracion-kanboard-gateway-balanceador/README.md` — objetivo, hallazgos y resultado final
- `laboratorio/2026-10-08_migracion-kanboard-gateway-balanceador/bitacora.md` — cada paso con comandos y salidas reales, incluyendo los dos intentos fallidos antes de la solución final

**Documentos actualizados:**
- `docs/adr/ADR-0008-gateway-balanceador-dos-etapas.md` — pendiente de migración de Kanboard cerrado; nueva sección documentando el hallazgo de trabajo sin registrar (Apache embebido en `PFR-GW-SRV` desde el 2026-09-18, atribuido tentativamente a Norberto Núñez) y la observación de que el "modelo estándar" del ADR (balanceador separado) nunca se usó en la práctica — los 3 servicios reales (Loki, NTF, Kanboard) usan la variante embebida
- `docs/05_Configuracion.md` — nuevo patrón documentado: "Apps sin soporte de subpath detrás del balanceador" (con el caso de Kanboard como ejemplo), siguiendo el estándar de documentación de comandos; corregido el ejemplo de ruteo por URL/path que usaba a Kanboard como caso (reemplazado por Loki, que sí soporta el patrón)
- `docs/03_Componentes.md` — sección de "balanceador embebido" actualizada con los casos de Loki y Kanboard, además de NTF
- `docs/13_Linea_de_Tiempo.md` — hito cerrado en la tabla de pendientes; nueva sección narrativa con el detalle del trabajo; aclaración parcial sobre `CAR-KANBOARD` (confirmado por el usuario como intento abandonado, sin contenido)
- `laboratorio/2026-07-27_exploracion-rutas-firewall-pfr-oss/SOP-acceso-temporal-demo-kanboard.md` — marcado como superado, con referencia al reemplazo definitivo

**Resumen:**
Antes de crear infraestructura nueva, se encontró que `PFR-GW-SRV` ya tenía un balanceador Apache embebido (no documentado, con fecha de modificación del 18 de septiembre) sirviendo Loki y NTF, con un intento inconcluso de Kanboard apuntando a un hostname inexistente. Se reutilizó esa infraestructura en vez de crear el contenedor balanceador separado que proponía originalmente el ADR-0008. El primer intento de ruteo por path (`/kanboard`) falló porque Kanboard no soporta subpath (sin opción de "base URL" en su configuración) — se probó también un puerto dedicado (8080) vía `forward-port`, que funcionó correctamente a nivel de firewalld pero quedó bloqueado por un firewall corporativo externo a mitad de camino. La solución final fue servir Kanboard directamente en la raíz del `VirtualHost` del gateway, con `/kanboard` y `/kamboard` como alias de redirección simple (usando una exclusión `ProxyPass ... !` para que el redirect tuviera prioridad sobre el proxy). Se validó que Loki y NTF siguen funcionando sin cambios, se retiró el acceso temporal (dispositivo LXD confirmado eliminado; reglas de firewall del host reportadas como eliminadas por el usuario, sin verificación independiente posible por falta de privilegios root en esa cuenta), y se avisó al equipo del nuevo acceso.

---

### 2026-10-08 (décima entrada)

**Fuente:** Backup y recuperación ante desastre (DR) para Kanboard — `laboratorio/2026-10-08_backup-dr-kanboard/`, trabajo de infraestructura en vivo a continuación de la migración de acceso del mismo día.

**Documentos creados:**
- `laboratorio/2026-10-08_backup-dr-kanboard/README.md` — por qué se descartó la replicación completa (frontend x3 + Postgres) a favor de snapshot + copia cruzada, y el procedimiento de recuperación real
- `laboratorio/2026-10-08_backup-dr-kanboard/bitacora.md` — cada paso con comandos y salidas reales, incluyendo el intento de automatización que quedó bloqueado

**Documentos actualizados:**
- `docs/11_Riesgos.md` — RIE-006 (sin política de backup) actualizado: primer caso concreto resuelto para Kanboard, con la aclaración explícita de que el riesgo general del cluster sigue abierto

**Resumen:**
Se evaluó y descartó explícitamente la replicación completa de Kanboard (frontend en los 3 sitios + Postgres centralizado) por sobredimensionada para un servicio de ~5-6 usuarios — decisión de costo/beneficio ya registrada en el ADR-0008. En su lugar, se armó snapshot automático nativo de LXD (cada 6h, expira a los 7 días) sobre `PFR-KANBOARD-TEST`, más un script que sincroniza una copia fría a `car.1` (otro sitio), probado de punta a punta: se arrancó la copia, se confirmó que Kanboard carga igual, y se verificó (comparando hashes) que el snapshot efectivamente congela un punto en el tiempo distinto del original en evolución. Se armó también la ruta de respaldo en el gateway de Carpinelli (apuntando por nombre, no IP, a la copia), validando que no rompe Loki. La automatización de la sincronización periódica quedó bloqueada: el host no tiene `cron` instalado y la alternativa de `systemd --user` tampoco sirve sin habilitar "linger" — ambas soluciones requieren una acción puntual de alguien con acceso root, pendiente.

---

### 2026-10-09 (undécima entrada)

**Fuente:** HTTPS para Kanboard reusando el certificado compartido (trabajo de infraestructura en vivo, comandos ejecutados por Elías Alfonzo vía SSH) — `laboratorio/2026-10-09_https-kanboard-certificado-compartido/`, continuación directa de la migración del día anterior.

**Documentos creados:**
- `laboratorio/2026-10-09_https-kanboard-certificado-compartido/README.md` — por qué no hacía falta pedir un certificado nuevo, y el resultado final validado en 4 casos
- `laboratorio/2026-10-09_https-kanboard-certificado-compartido/bitacora.md` — cada paso con comandos y salidas reales, incluyendo el intento que falló en tiempo real (sintaxis válida, comportamiento incorrecto) antes de llegar al fix

**Documentos actualizados:**
- `docs/adr/ADR-0008-gateway-balanceador-dos-etapas.md` — nueva sección documentando el hallazgo (no hace falta certificado nuevo, el existente ya sirve) y el error descartado
- `docs/05_Configuracion.md` — nuevo patrón reutilizable: "mTLS opcional por defecto, obligatorio solo en rutas específicas" (con el intento fallido explícitamente documentado para no repetirlo), siguiendo el estándar de documentación de comandos
- `docs/13_Linea_de_Tiempo.md` — nueva sección narrativa con el detalle del trabajo

**Resumen:**
Antes de pedir certificados nuevos para los 3 gateways, se investigó el estado actual: no hay DNS configurado para ninguna de las 3 IPs de servicio (ni para el nombre que ya tiene el certificado existente), pero el certificado sí existe — el mismo archivo, idéntico, ya desplegado en los 3 gateways desde el 3 de septiembre, sin SAN. Se confirmó que la exigencia de certificado de cliente (mTLS) que protege a NTF es una directiva de Apache independiente del certificado de servidor, lo que permitió reusar el mismo certificado para Kanboard sin pedir uno nuevo. El primer intento (relajar `SSLVerifyClient` de `require` a `none` por `<Location>`) tuvo sintaxis válida pero falló en tiempo real — la dirección correcta fue la inversa: vhost en `optional`, con `require` explícito solo en la ruta de NTF. Validado en los 4 casos relevantes (Loki HTTP sin cambios, Kanboard HTTP redirige a HTTPS, Kanboard HTTPS funciona sin certificado, NTF HTTPS sigue exigiendo certificado) y confirmado desde el navegador real del usuario. Queda pendiente el DNS y confirmar que las PCs del equipo confían en la CA interna.

---

### 2026-10-09 (duodécima entrada)

**Fuente:** Alta de VulnApp NG en PRJ-OSS — instalación de plataforma y de aplicación en vivo (comandos ejecutados por Elías Alfonzo vía SSH), precedida por una investigación de factibilidad solo lectura — `laboratorio/2026-10-09_alta-vulnapp-ng/`.

**Documentos creados:**
- `laboratorio/2026-10-09_alta-vulnapp-ng/README.md` — qué se creó en la plataforma, resultado final y qué quedó pendiente
- `laboratorio/2026-10-09_alta-vulnapp-ng/bitacora.md` — cada paso con comandos y salidas reales, incluidos los dos intentos fallidos antes de llegar a un paquete corregido, y la verificación de alcance hacia SDI/SMS

**Documentos actualizados:**
- `docs/05_Configuracion.md` — nueva sección "Firewall de la red OVN_1 (`lxc network acl`)": se documenta por primera vez `ACL-OVN-1` completa (reglas preexistentes, encontradas sin registro en este repositorio, más las 4 nuevas de este alta)
- `docs/03_Componentes.md` — nota de "balanceador embebido" actualizada: VulnApp NG es el cuarto servicio en usar ese patrón en `PFR-GW-SRV`
- `docs/07_Troubleshooting.md` — TRB-014 (PostgreSQL: no se puede reasignar el dueño de una secuencia vinculada a una columna), TRB-015 (`mod_headers` no habilitado bloquea `RequestHeader`), TRB-016 (`PermissionError` al crear una carpeta propia de la app en un árbol de solo lectura para su grupo)
- `docs/11_Riesgos.md` — RIE-015 nuevo: conectividad de VulnApp NG hacia la API de SDI bloqueada fuera de este cluster, pendiente de Seguridad/Redes; tabla de severidades actualizada
- `docs/adr/ADR-0008-gateway-balanceador-dos-etapas.md` — nueva sección de actualización (cuarto caso de la variante embebida) y dos pendientes nuevos en la lista de seguimiento
- `docs/13_Linea_de_Tiempo.md` — nueva sección narrativa con el detalle del trabajo

**Resumen:**
Se alojó VulnApp NG (reemplazo de un sistema legacy, decisión tomada en el repositorio de la propia aplicación) en dos contenedores en Franco, sin alta disponibilidad. El paquete de instalación falló dos veces en su primera corrida contra datos reales — exactamente como anticipaba su propio README ("los scripts no se probaron todavía en LXD"): una secuencia de PostgreSQL vinculada a una columna no admite reasignación de dueño por separado, y la aplicación no podía crear su propia carpeta de `uploads/` por permisos de grupo. Ambos se reportaron completos sin editar nada, y se corrigieron del lado de la aplicación. Al publicar en el gateway, `mod_headers` no estaba habilitado en `PFR-GW-SRV` — se restauró el backup automáticamente antes de que el error llegara a afectar a Kanboard/Loki/NTF, se habilitó el módulo y se reintentó con éxito, validado tanto en loopback como desde afuera del contenedor. Se aprovechó la investigación para documentar por primera vez `ACL-OVN-1`, el firewall de la red `OVN_1`, que ya existía sin ningún registro en este repositorio. Quedó pendiente, fuera del alcance de este cluster, la conectividad hacia la API de SDI: la ACL y el ruteo de LXD están correctos, pero el tráfico se pierde después del primer salto del contenedor — se avisó como un riesgo nuevo para que Seguridad/Redes lo resuelva antes de activar la carga diaria de datos.

---

### 2026-10-10 (decimotercera entrada)

**Fuente:** Re-verificación de la documentación existente contra el estado real del cluster, a pedido explícito del usuario, al volver a explicar el alta de VulnApp NG con más detalle para el equipo.

**Documentos actualizados:**
- `docs/02_Arquitectura.md` — tabla de direccionamiento IP de `OVN_1` corregida: `.11` ya no es "primer balanceador (`PFR-LB`)" (nunca quedó persistente, esa IP se reasignó a `C-Colector-1`), y `.12`–`.99` ya no es "sin asignar" (`.12` `C-Loki-1`, `.13`/`.14` VulnApp NG) — verificado con `lxc list --all-projects` contra los 3 sitios
- `docs/07_Troubleshooting.md` — TRB-017 nuevo: `lxc launch`/`lxc init` se cuelgan sin error al ejecutarse por SSH sin terminal (stdin sin cerrar), encontrado automatizando la creación de los contenedores de VulnApp NG
- `laboratorio/2026-10-09_alta-vulnapp-ng/bitacora.md` — se completó con el paso 0 (creación de perfiles, contenedores, ACL y snapshot), que había quedado afuera porque se hizo en la sesión anterior a la que registró el resto de la bitácora; reconstruido a partir del estado real del cluster, no de memoria
- `laboratorio/2026-10-09_alta-vulnapp-ng/README.md` — enlace nuevo al paso 0 de la bitácora

**Resumen:**
Al explicar en detalle, para alguien nuevo en el equipo, cómo se crearon los contenedores de VulnApp NG (perfiles, `lxc launch`, reglas de ACL), se terminó reconstruyendo esa parte directamente desde el cluster real (`lxc profile show`, `lxc config show`, `lxc network acl show`) en vez de confiar en la memoria de la sesión anterior — ese ejercicio encontró que la tabla de IPs de `OVN_1` en `02_Arquitectura.md` ya no describía la realidad: dos de los rangos que decía "reservado" o "primer balanceador" ya tenían contenedores reales adentro desde hacía tiempo. Se corrigió la tabla con lo verificado en vivo, y se dejó una nota explícita de que no está confirmado si existe un criterio formal de asignación dentro de ese rango más allá de "la siguiente IP libre". De paso, se terminó de registrar en la bitácora el paso de plataforma (perfiles, contenedores, ACL, snapshot) que había quedado sin documentar en este repositorio porque se hizo antes de que se resumiera la conversación de esa sesión — y se documentó, como hallazgo aparte y reutilizable, el bug de `lxc launch`/`lxc init` colgándose cuando se ejecutan por SSH sin terminal.

---

### 2026-10-10 (decimocuarta entrada)

**Fuente:** Análisis completo (Fases 1-4 de `CLAUDE.md`) de la parte técnica de `reunion/2026-10_llamada-abel-balanceadores-ntf-loki.vtt` — transcripción encontrada en la carpeta de Descargas del usuario, no versionada hasta ahora. Un fragmento puntual ya se había usado el mismo día para confirmar la autoría de Norberto Núñez del `LB.conf` (ver la entrada anterior); esta vez se procesó el resto del contenido relevante a LXD.

**Documentos creados:**
- `reunion/2026-10_llamada-abel-balanceadores-ntf-loki.vtt` — copiado a este repositorio con la convención de nombres de `reunion/`

**Documentos actualizados:**
- `docs/02_Arquitectura.md` — nueva sección "Nombre de dominio compartido entre sitios (FQDN + DNS round-robin)": el diseño acordado para el DNS pendiente (un mismo FQDN resolviendo, por round-robin, a las 3 IPs de servicio)
- `docs/14_Manual_Operativo.md` — corrección importante en "Logs de aplicación: Loki + MinIO propio del proyecto": `C-Loki-1` ya está desplegado y en uso (no solo planificado), pero su backend real es un servicio S3 externo al cluster (infraestructura de IT), no `MinIO` propio como decía el plan — ese plan queda marcado como probablemente superado
- `docs/05_Configuracion.md` — nota de actualización en "Buckets de almacenamiento S3": aclara que Loki, en la práctica, no usa esta capacidad propia de LXD
- `docs/adr/ADR-0008-gateway-balanceador-dos-etapas.md` — enlace cruzado hacia el nuevo diseño de FQDN
- `docs/11_Riesgos.md` — RIE-016 nuevo: acceso temporal del escáner de vulnerabilidades por lista de IPs, sin fecha de retiro acordada
- `docs/13_Linea_de_Tiempo.md` — nueva idea sin asignar: usar Loki para monitorear los balanceadores
- `reunion/README.md` — la reunión pasa de "no analizada" a "analizada completa", con la llamada superpuesta sobre un corte de energía en terreno descartada explícitamente por no ser contenido de LXD

**Resumen:**
Se procesó el resto de la reunión que el mismo día ya había aportado la confirmación de autoría de Norberto Núñez sobre `LB.conf`. Encontró tres cosas que ameritaban corregir documentación existente: el diseño de DNS compartido entre los 3 sitios (round-robin, no un balanceador de DNS centralizado) estaba acordado de palabra pero nunca escrito; el backend de almacenamiento del Loki propio del proyecto resultó ser un servicio S3 externo administrado por Norberto Núñez desde hace tiempo (reutilizado de un trabajo anterior con métricas), no el `MinIO` propio que el plan documentado en el repositorio todavía describía como pendiente; y un acceso temporal por IP para el escáner de vulnerabilidades del equipo de seguridad, sin fecha de retiro acordada, que se agregó como riesgo nuevo. También quedó registrada, sin tarea concreta, una idea de Marcos Casco (usar Loki para monitorear los propios balanceadores). La llamada se superpone, a partir del minuto ~4, con una conversación no relacionada sobre un corte de energía en terreno — se identificó y se descartó a propósito, igual que en análisis anteriores de este tipo de transcripciones.

---

### 2026-10-10 (decimoquinta entrada)

**Fuente:** Verificación en vivo del contenedor de Kanboard (`PFR-KANBOARD-TEST`), a pedido explícito del usuario — el stack real de la aplicación no estaba documentado en el repositorio.

**Documentos actualizados:**
- `docs/03_Componentes.md` — ficha nueva "Kanboard (gestión de tareas)": la ficha estándar del componente más una tabla de stack verificada en vivo (sistema operativo, servidor web, runtime de PHP, motor de base de datos, versión de la aplicación, plugins instalados, snapshot, recursos)

**Resumen:**
Kanboard nunca había tenido su propia ficha en `03_Componentes.md` — solo se lo mencionaba de paso en la nota de "balanceador embebido". Se conectó al contenedor real y se relevó el stack completo: Ubuntu 26.04, Apache 2.4.66 con `mod_php` (no PHP-FPM), PHP 8.5.4, base de datos **SQLite** (un solo archivo de ~2 MB, no MySQL ni PostgreSQL aunque Kanboard los soporta), versión de la aplicación **1.2.46** (junio 2025), con 6 plugins instalados (incluido `TeamWorkload`, ya registrado como tarea completada en Kanboard). Se encontró además que el contenedor no tiene límites explícitos de CPU/memoria en su perfil — corre sin techo propio sobre los recursos libres del nodo `pfr.1` — y se dejó anotado como hallazgo, sin crear todavía un riesgo formal en `11_Riesgos.md` a la espera de confirmar si amerita uno.

**Actualización (mismo día):** se agregaron los números reales de uso — disco (520 MB de 5 GB asignados, único límite que el contenedor sí tiene) y memoria (271 MB en uso, medido por LXD vía cgroups, sin ningún límite puesto), más el contexto del host (`pfr.1`: 15 GiB de RAM con 9.4 GiB disponibles; *pool* ZFS `local` con 320 GB libres de 326 GB). Con ese margen, el límite de memoria ausente es un riesgo latente, no uno activo hoy — queda marcado en la ficha como pendiente de corregir, con el mismo criterio que ya se usó en VulnApp NG (2 vCPU / 2 GiB).

---

### 2026-10-10 (decimosexta entrada)

**Fuente:** Verificación en vivo de capacidad en los 3 sitios del cluster, a pedido del usuario — necesitaba datos precisos antes de empezar a migrar otros sistemas al cluster.

**Documentos creados:**
- `laboratorio/2026-10-10_capacidad-cluster/README.md` — resumen por sitio (CPU, RAM, disco libres) y hallazgos para la planificación
- `laboratorio/2026-10-10_capacidad-cluster/bitacora.md` — comandos exactos y salidas reales contra los 3 miembros del cluster, inventario completo de los 13 contenedores corriendo con su stack, uso real y límites

**Documentos actualizados:**
- `docs/06_Operacion.md` — nueva sección reutilizable "Verificar la capacidad disponible del cluster (CPU, RAM, disco)", con los comandos exactos (incluido por qué `--target`, por qué no usar `free`/`df` de adentro del contenedor cuando no tiene límite, y los errores frecuentes encontrados al armar este mismo relevamiento)
- `docs/11_Riesgos.md` — RIE-017 nuevo: 3 contenedores con `limits.memory` de 1 GiB que ya mostraron uso de swap

**Resumen:**
Se midió en vivo, sin necesidad de abrir sesión SSH a cada sitio por separado (LXD enruta las consultas con `--target` y con `lxc info`/`lxc exec` normales), la capacidad real de los 3 miembros del cluster. Disco no es una restricción en ningún sitio (entre 310 y 378 GiB libres); Franco tiene el triple de CPU que Carpinelli o Fernando; RAM es el recurso más parejo, ninguno en estado crítico. El hallazgo más accionable: 3 contenedores (`CAR-GW-OAM`, `FDO-GW-SRV`, `FDO-WS-1`) ya usaron swap dentro de su límite de 1 GiB — señal de que ese límite les queda justo, antes incluso de sumarles más carga. Se documentó también el procedimiento completo como referencia reutilizable, ya que el usuario pidió explícitamente los comandos exactos para poder repetir este tipo de verificación por su cuenta.

---

### 2026-09-16 (decimoséptima entrada)

**Fuente:** Relevamiento e implementación realizados el 16/09/2026 sobre `tec-calidad05` (`10.129.2.165`), incorporados al repositorio posteriormente — trabajo previo del usuario, hecho con otra herramienta, que no tenía todavía un lugar fijado dentro de la estructura del repositorio.

**Documentos creados:**
- `laboratorio/2026-09-16_relevamiento-backup-tec-calidad05/README.md` — índice y resumen de ambos trabajos
- `laboratorio/2026-09-16_relevamiento-backup-tec-calidad05/` — carpeta completa con la evidencia original: relevamiento de capacidad y consumo por aplicación (`04`, `07`, `08` y sus CSV de respaldo), e implementación verificada del backup nocturno de PostgreSQL para ADM-TECH (`implementacion_backup_admtech.md`, `verificacion_backup_admtech.md` como etapa intermedia), más los scripts y salidas crudas de cada paso

**Resumen:**
`tec-calidad05` es una VM VMware con CentOS 7 ajena al cluster LXD (aloja Infrawork, ADM-TECH y una versión legacy de VulnApp) — se incorpora a este repositorio porque el equipo centraliza acá toda la infraestructura, no solo la de LXD. El relevamiento de capacidad encontró el filesystem raíz al 88.8% (82.79 GiB disponibles, no crítico todavía pero a vigilar) y dejó pendiente de confirmar con el responsable si `/var/www/html/adm` corresponde efectivamente a ADM-TECH. La implementación del backup de PostgreSQL quedó verificada de punta a punta: script instalado, cron diario a las 02:30, primer respaldo corrido con checksum SHA-256 y catálogo comprobados (`pg_restore --list`), sin exponer ninguna credencial en los documentos (verificado explícitamente por los propios scripts de generación de reportes). Queda pendiente, si se decide mantener este servidor documentado de forma permanente, promover una ficha de componente y el procedimiento de backup a `docs/`.
---

### 2026-10-12 (decimoctava entrada)

**Fuente:** Relevamiento técnico de solo lectura de `PFR-GW-SRV` para su alta en el inventario de Ciberseguridad (Jerure), a pedido del usuario. Seguimiento de los tickets hasta el 2026-10-16.

**Documentos creados:**
- `laboratorio/2026-10-12_alta-jerure-pfr-gw-srv/README.md` — objetivo, estado de los tickets #1076072 (tema 447) y #1076134 (tema 939), y hallazgos
- `laboratorio/2026-10-12_alta-jerure-pfr-gw-srv/bitacora.md` — datos cargados en el formulario, servicios y puertos, verificación de IP propia, DNS y respuesta a SDI

**Documentos actualizados:**
- `docs/07_Troubleshooting.md` — TRB-018 (la verificación de SDI por SSH a la IP de servicio de un gateway falla por diseño)
- `docs/03_Componentes.md` — gateway de servicios: SSH deshabilitado verificado y su consecuencia en las altas de Jerure
- `docs/11_Riesgos.md` — RIE-021 (`PFR-GW-SRV` sin snapshots ni backup)

**Resumen:**
Se confirmó que `10.143.11.8` es una IP propia del contenedor (ipvlan L2, estática), por lo que correspondía el tema 447 y no el 857. El registro previo 632 (DNSv6-home-21) sobre la misma IP se dejó intacto, por recomendación de SDI. El ticket de agregar la IP al activo `fr-oss` quedó resuelto el 16/10. El alta del servidor virtual sigue en verificación de SDI: su prueba por SSH falló porque el gateway no tiene SSH por diseño, y se acordó que la verificación se haga con `lxc exec` desde el host de gestión. El relevamiento también encontró que el gateway no tiene snapshots ni registro DNS.

---

### 2026-10-16 (decimonovena entrada)

**Fuente:** Escaneo Nessus de Seguridad de la Información (adjunto al ticket Jerure #1076134) y cambios aplicados en vivo, con autorización explícita del usuario y rollback preparado.

**Documentos creados:**
- `laboratorio/2026-10-16_hardening-gateways-nessus/README.md` — detecciones, tratamiento, estado de los 3 gateways, Etapa 1 completada y Etapa 2 pendiente
- `laboratorio/2026-10-16_hardening-gateways-nessus/bitacora.md` — comandos, verificaciones antes y después, hashes y rollback de cada cambio
- `recursos/kanboard-api/` — referencia de la API JSON-RPC de Kanboard (`KANBOARD_API.md`), colección Postman con 16 solicitudes y README. Sin tokens

**Documentos actualizados:**
- `docs/05_Configuracion.md` — regla nueva de `ACL-OVN-1` (CAR/FDO → VulnApp NG); bloqueo de ICMP timestamp en la zona `external`; bloqueo de archivos de la aplicación (`web.config`); parámetro `--forwarded-allow-ips` de Gunicorn; estado real del mTLS en CAR/FDO; verificación de métricas sin autenticación
- `docs/06_Operacion.md` — procedimiento nuevo "Modificar el LB.conf de un gateway de forma controlada"
- `docs/07_Troubleshooting.md` — TRB-019 (401 en la API de Kanboard con un token personal)
- `docs/11_Riesgos.md` — RIE-018 (métricas de LXD sin autenticación), RIE-019 (certificados TLS no confiables y cifrados heredados), RIE-020 (gateways CAR/FDO no homogéneos, bloquean el DNS); resumen de severidades
- `docs/03_Componentes.md` — diferencias entre los 3 gateways; ficha de Kanboard (API y archivos de fábrica expuestos)
- `docs/02_Arquitectura.md` — requisitos previos antes de pedir el DNS `oss.personal.com.py`
- `docs/adr/ADR-0008-gateway-balanceador-dos-etapas.md` — actualización del 16/10 y pendientes nuevos
- `docs/13_Linea_de_Tiempo.md` — hitos del 12 y 16/10 y acciones pendientes

**Resumen:**
De 13 detecciones de criticidad media, se cerraron 2 en `10.143.11.8`: ICMP timestamp (bloqueado en los 3 gateways) y `/web.config` de Kanboard (bloqueado en PFR; en CAR y FDO no estaba expuesto). Las 11 restantes son certificados (CA interna en el gateway, certificado propio de LXD en el host) y quedaron como riesgo a tratar. La verificación encontró que el endpoint de métricas de LXD no exige autenticación, y que los gateways de CAR y FDO no son iguales al de PFR: exigen certificado en todo el sitio y apuntan a Kanboard detenidos. Esto bloquea el plan de DNS compartido. Se completó la Etapa 1 de la homogeneización (ACL, Gunicorn y `mod_headers`) sin impacto visible, salvo unos segundos de reinicio de VulnApp NG. La Etapa 2 (`LB.conf` de CAR y FDO) queda pendiente de coordinar con Norberto Núñez por el riesgo sobre NTF.

---

### 2026-10-24 (vigésima entrada)

**Fuente:** Reuniones con Norberto Núñez, Marcos Casco y Daniel Medina (2026-10-16 y 2026-10-24), más el seguimiento de los tickets Jerure de certificado (#1078719) y DNS (#1079305).

**Documentos creados:**
- `docs/adr/ADR-0009-dns-fqdn-compartido-y-nombres-por-sitio.md` — nombre compartido `oss.personal.com.py` por round-robin, con nombres propios por sitio para clientes con restricción de ruta (caso Comap → Fernando)
- `PENDIENTES.md` — resumen priorizado de trabajo en curso, para retomar

**Documentos actualizados:**
- `reunion/README.md` — dos reuniones nuevas registradas y analizadas (las transcripciones todavía no se copiaron a la carpeta)
- `docs/05_Configuracion.md` — procedimiento estándar de Norberto para operar contenedores (`lxc file push/pull`, `lxc exec -n`)
- `docs/06_Operacion.md` — inventario hacia Jerure con IP de servicio + puerto + URL, y los dos niveles del checklist de alta (servidor y servicio)
- `docs/07_Troubleshooting.md` — TRB-017: `-n` como solución nativa, confirmada por Norberto
- `docs/11_Riesgos.md` — RIE-019: avance del certificado y coordinación obligatoria con Tembiapó
- `docs/02_Arquitectura.md`, `docs/10_Decisiones.md`, `docs/README.md` — referencias al ADR-0009
- `docs/13_Linea_de_Tiempo.md` — lo definido en las dos reuniones y las acciones nuevas (Infrawork/ADM-TECH, bases centralizadas y S3, correo entrante, OSRM, prueba de SMS)

**Resumen:**
Las dos reuniones cierran tres definiciones. Primero, las aplicaciones se inventarían en Jerure con la IP de servicio del gateway, el puerto y la URL, no con la IP del contenedor. Segundo, el DNS compartido tiene una excepción: los clientes que solo alcanzan un sitio (Comap) necesitan un nombre propio hacia ese sitio; se registró como ADR-0009. Tercero, el cambio de certificado no puede hacerse sin coordinar con Tembiapó, que consume NTF por Fernando confiando en el certificado actual. Además, se decidió migrar Infrawork y ADM-TECH al clúster arrancando con 1 CPU, dejando FileRoom (~800 GB) en tec-calidad05, y se habilitó centralizar las bases del área en el servidor de Norberto, con un servicio S3 ya disponible. En DNS, `oss.personal.com.py` ya resuelve a `10.143.11.8`; las IP de Carpinelli y Fernando se suman después de la Etapa 2.

---

### 2026-10-24 (vigesimoprimera entrada)

**Fuente:** Relevamiento de solo lectura de ADM-TECH en `tec-calidad05` y en su repositorio (`adm-tech`), a pedido del usuario, para planificar su migración al clúster.

**Documentos creados:**
- `laboratorio/2026-10-24_migracion-admtech-lxd/README.md` — plataforma actual, código, archivos, base, dependencias externas críticas, hallazgos de seguridad y diseño propuesto (Fase 2)
- `laboratorio/2026-10-24_migracion-admtech-lxd/bitacora.md` — consultas ejecutadas y la advertencia sobre secretos impresos por accidente

**Documentos actualizados:**
- `docs/06_Operacion.md` — procedimiento "Actualizar la versión de PHP o PostgreSQL de una aplicación (azul/verde)" (🟡 diseño, no ejecutado)
- `PENDIENTES.md` — sección de migraciones con el estado de ADM-TECH

**Fuera de este repositorio:** en el repo de la aplicación se creó `knowledge/06_Roadmap/plan_migracion_lxd_php85.md` (plan del refactor), sin commit.

**Resumen:**
ADM-TECH corre con PHP 5.6 y PostgreSQL 10. Como Ubuntu 26.04 solo trae PHP 8.5, el código tiene que modernizarse antes del pase. El trabajo es acotado: ~35 archivos propios con funciones eliminadas o etiquetas cortas, más la actualización de dos librerías. La base es chica (71 MB). Los archivos pesan 7,2 GB y crecen más de 7 GB por año, por eso el volumen se dimensionó en 40 GiB. Dos dependencias bloquean el corte: el proceso externo que envía los correos (lee una cola en la base `Infraestructura` y adjunta archivos) y el ETL de SAP que carga tablas de la base, ambos sin identificar. El relevamiento también confirmó que la aplicación se conecta como superusuario y que sus credenciales son legibles en el vhost de Apache; se propone rotarlas en la migración.

### 2026-10-26 (vigesimosegunda entrada)

**Fuente:** Implementación supervisada (Kanboard bajo `/kanboard/`) y prueba de conectividad de solo lectura hacia la API de SDI, a pedido del usuario.

**Documentos creados:**
- `laboratorio/2026-10-26_kanboard-subruta/README.md`: paso 1 (alias `/kanboard` y ajuste de `.htaccess` en `PFR-KANBOARD-TEST`) y paso 2 (rutas del `LB.conf` de `PFR-GW-SRV`, `mod_rewrite`), con la tabla antes/después y el rollback

**Documentos actualizados:**
- `docs/02_Arquitectura.md`: nueva sección "IP que ve el firewall corporativo: entrada y salida" (doble NAT por GW-OAM y `lxdbr_OAM`; la salida usa la IP de gestión del host); IP de gestión y de servicio de Fernando completadas
- `docs/11_Riesgos.md`: avance de RIE-015 (ticket #1083155, vence 31/05/2027)
- `PENDIENTES.md`: ticket #1083155

**Resumen:**
Kanboard pasó a publicarse en `https://10.143.11.8/kanboard/` y la raíz quedó libre para un portal de aplicaciones (pendiente). Los enlaces viejos redirigen a la ruta nueva y la API vieja sigue respondiendo. Solo en Franco; CAR y FDO se alinean en la Etapa 2. La prueba hacia la API de SDI confirmó que la ACL del cluster ya permite el tráfico y que el bloqueo está en el firewall corporativo. También mostró que, para el firewall, los contenedores salen con la IP de gestión del host de cada sitio y no con la del GW-OAM, porque `lxdbr_OAM` hace un segundo NAT.

### 2026-10-26 (vigesimotercera entrada)

**Fuente:** Tickets de Jerure aportados por el usuario (707 #1047036; 452 #1083088 y #1083104) y criterio de inventario acordado por el equipo.

**Documentos creados:**
- `docs/18_Inventario_Ciberseguridad.md`: estado del inventario en Ciberseguridad (aplicación 608 `PLATAFORMA-LXD-OSS` y servicios `Kanboard-OSS` y `Vulnapp-OSS`), con los pendientes de corrección de los 452

**Documentos actualizados:**
- `docs/06_Operacion.md`: subsección "Criterio de inventario acordado"; URL de ejemplo de Kanboard corregida a `/kanboard/`
- `docs/README.md`: índice con el documento 18
- `PENDIENTES.md`: los dos 452, con enlace a los pendientes del documento 18

**Resumen:**
La plataforma está inventariada como aplicación 608 (707 resuelto el 2026-08-18). Kanboard y VulnApp NG se dieron de alta como servicios (452) asociados a la 608 y al activo 10041 `fr-oss` (`10.143.11.8`), el gateway que los publica. Los contenedores no se inventarían por separado. Quedan correcciones pendientes en los dos 452 y una evaluación con SDI sobre declarar el acceso administrativo de los nodos (8443, 22) como servicios de tipo CONSOLA.

### 2026-10-26 (vigesimocuarta entrada)

**Fuente:** Copia impresa del ticket 451 #1078719 y archivos del certificado entregados por Natalia Cardozo (Ciberseguridad), verificados localmente con `openssl` (solo partes públicas).

**Documentos creados:**
- `laboratorio/2026-10-26_certificado-lets-encrypt/README.md`: historial y cierre del ticket, datos del certificado, verificación y plan de instalación en los 3 gateways (no aplicado)

**Documentos actualizados:**
- `docs/11_Riesgos.md`: avance de RIE-019 (certificado recibido); nuevo RIE-022 (certificado de 90 días sin renovación automática); resumen de severidades
- `PENDIENTES.md`: #1078719 resuelto; paso 1 de "Certificado y DNS" completado

**Resumen:**
Natalia Cardozo cerró el ticket #1078719 el 2026-10-22 con un certificado Let's Encrypt para `oss.personal.com.py` (SAN incluido) que vence el 2027-01-20. La cadena valida y la clave privada corresponde al certificado. La instalación en los 3 gateways sigue pendiente de coordinar con Tembiapó (NTF por Fernando). En el mismo cambio se reemplaza la línea de cifrados heredada. Como el certificado dura 90 días, se registró el riesgo de vencimiento sin renovación automática.

### 2026-10-26 (vigesimoquinta entrada)

**Fuente:** Ventana de cambio aplicada en vivo (certificado de los gateways), con Daniel Medina (Tembiapó) presente; relevamiento y ajuste del cliente Tembiapó.

**Documentos actualizados:**
- `laboratorio/2026-10-26_certificado-lets-encrypt/README.md`: lado cliente Tembiapó (CA fijada; `ntf-ca.crt`; cambio de Daniel Medina en 6 lugares), precarga en los 3 gateways, instalación aplicada con verificación y rollback
- `docs/11_Riesgos.md`: avance de RIE-019 (certificado instalado)
- `PENDIENTES.md`: pasos 2 a 4 de "Certificado y DNS" completados; 778 listo para cerrar

**Resumen:**
Tembiapó validaba NTF solo contra la CA interna, así que se creó en su servidor `ntf-ca.crt` (AutoridadOSS + ISRG Root X1) y Daniel Medina apuntó a ese archivo los 6 lugares que envían SMS. Después se instaló el certificado Let's Encrypt en `PFR-GW-SRV`, `CAR-GW-SRV` y `FDO-GW-SRV`, y en el mismo cambio se dejaron solo TLS 1.2/1.3 y cifrados fuertes. Las 3 IP validan el certificado y las rutas de PFR quedaron sin cambios. Tembiapó siguió enviando SMS (POST /ntf 200 a los 15 segundos del reload en Fernando).

### 2026-10-26 (vigesimosexta entrada)

**Fuente:** Cambio aplicado en vivo en los 3 gateways, a pedido del usuario.

**Documentos actualizados:**
- `laboratorio/2026-10-26_certificado-lets-encrypt/README.md`: redirección de HTTP a HTTPS y del acceso por IP al nombre `oss.personal.com.py`, con los clientes de máquina excluidos, la verificación y el rollback

**Resumen:**
Con el certificado nuevo, el acceso por IP muestra una advertencia, y el puerto 80 de PFR redirigía justamente a la IP. Ahora, en los 3 gateways, el puerto 80 lleva todo a `https://oss.personal.com.py/` salvo Loki. En el 443, los navegadores (`GET`/`HEAD`) que entran por IP se redirigen al nombre, salvo `/ntf`, `/loki`, `/supervisionge` y la API de Kanboard. De paso, CAR dejó de publicar Kanboard por HTTP sin cifrar. Grafana, Comap y Tembiapó siguen recibiendo los mismos códigos que antes.

### 2026-10-26 (vigesimoséptima entrada)

**Fuente:** Ticket de Jerure cargado por el usuario (778 #1083298) y exportes de vulnerabilidades de Grafana de los 3 gateways.

**Documentos actualizados:**
- `PENDIENTES.md`: ticket #1083298 para seguimiento; la aceptación de riesgo del 16/10 queda superada
- `laboratorio/2026-10-26_certificado-lets-encrypt/README.md`: tabla de los 6 hallazgos y la evidencia adjunta
- `docs/11_Riesgos.md`: avance de RIE-019

**Resumen:**
Los hallazgos de certificado no confiable y CA no reconocida de `fr-oss`, `car-oss` y `fdo-dns-lxd` (IDs de Grafana 41817, 41818, 40608, 40609, 41771 y 41772) se informaron como resueltos, con la salida de `openssl` contra las 3 IP como evidencia. Queda que Seguridad cierre el ticket y que el próximo escaneo los dé de baja.

### 2026-10-26 (vigesimoctava entrada)

**Fuente:** Implementación a pedido del usuario.

**Documentos creados:**
- `proyectos/portal-oss/` (`src/index.html`, `README.md`, `CHANGELOG.md`): portal de la raíz de `oss.personal.com.py` con Kanboard y VulnApp NG

**Documentos actualizados:**
- `PENDIENTES.md`: portal publicado; push del 26/10 hecho

**Resumen:**
La raíz que quedó libre al mover Kanboard a `/kanboard/` ahora muestra el Portal OSS: una página estática sin recursos externos que lista las dos aplicaciones activas y propias de la plataforma LXD. Se publicó en `/var/www/html/index.html` de los 3 gateways, reemplazando la página por defecto de Apache (backup en `/root/index.html.bak-20261026`). Responde 200 en `https://oss.personal.com.py/`.

### 2026-10-26 (vigesimonovena entrada)

**Fuente:** Cambio aplicado a pedido del usuario y ticket de Jerure 452 #1083324.

**Documentos actualizados:**
- `laboratorio/2026-10-24_migracion-admtech-lxd/bitacora_fase3.md`: `/adm/` abierto a cualquier IP (se quitó el `Require ip 10.150.60.85` en `PFR-GW-SRV`), con el riesgo del ingreso de desarrollo y el rollback
- `docs/18_Inventario_Ciberseguridad.md`: servicio `ADM-TECH-OSS` (#1083324) y sus pendientes
- `PENDIENTES.md`: advertencia del ingreso de desarrollo expuesto; #1083324

**Resumen:**
El entorno de desarrollo de ADM-TECH en LXD quedó accesible desde cualquier IP, por decisión del responsable (los datos no son oficiales). El ingreso de desarrollo sigue activo y hay que quitarlo antes de usar datos oficiales. El servicio se dio de alta como `ADM-TECH-OSS`, asociado a la aplicación 608 y al activo `fr-oss`, igual que Kanboard y VulnApp NG.

### 2026-10-26 (trigésima entrada)

**Fuente:** Pedido de rediseño del usuario.

**Documentos actualizados:**
- `proyectos/portal-oss/`: versión 2.0.0 (concepto "la línea OSS", datos en `src/apps.json`, generación con `build.py`), publicada como vista previa en `https://oss.personal.com.py/portal-preview/` (solo `PFR-GW-SRV`)

**Resumen:**
Se rediseñó el portal para que cualquier persona entienda en la primera pantalla dónde está, qué herramienta necesita, cuál está en producción y cuál en pruebas, y cómo ingresar. Los datos de ingreso de cada aplicación se verificaron contra la aplicación real. El portal anterior sigue en la raíz hasta la aprobación.

### 2026-10-26 (trigésima primera entrada)

**Fuente:** Aprobación del usuario.

**Resumen:**
El Portal OSS 2.0.0 pasó de la vista previa a la raíz `https://oss.personal.com.py/` en los 3 gateways (backup de la versión anterior en `/root/index.html.bak-202610261858`), y se retiró `/portal-preview/`. Los enlaces a Kanboard, VulnApp NG y ADM-TECH se verificaron después del cambio.

### 2026-10-26 (trigésima segunda entrada)

**Fuente:** Pedido y aprobación del usuario; implementación con entorno de prueba.

**Documentos creados:**
- `laboratorio/2026-10-26_kanboard-tema-osstheme/README.md`: relevamiento, entorno de prueba `PFR-KANBOARD-PRUEBA` (`/kanboard-prueba/`), pase a producción con respaldos, rollback y pendientes

**Documentos actualizados:**
- `PENDIENTES.md`

**Resumen:**
Kanboard tiene ahora la identidad visual de OSS mediante el plugin propio `OssTheme` (código en el repositorio de Kanboard del usuario): inicio de sesión nuevo, cabecera, tarjetas con el título primero y vencimientos con texto, y colores para los temas claro, oscuro y automático. No toca el núcleo ni la base. Se probó en una copia aislada y se pasó a producción después de respaldar (snapshot, aplicación, base y adjuntos). Se desactivaron Customizer y Essential, que reemplazaban las mismas plantillas.

### 2026-10-26 a 2026-10-28 (trigésima tercera entrada)

**Fuente:** Escaneo de vulnerabilidades de Jerure (ticket 452 #1083324), tickets 778 #1083416 y 623 #1084774; implementación en `PFR-GW-SRV` a pedido del usuario.

**Documentos creados:**
- `laboratorio/2026-10-26_hsts-pfr-gw-srv/README.md`: verificación previa, cambio, verificación, rollback y seguimiento de los tickets
- `laboratorio/2026-10-26_hsts-pfr-gw-srv/evidencia_hsts_43743_20261026.txt`: evidencia adjuntada al ticket #1083416

**Documentos actualizados:**
- `docs/18_Inventario_Ciberseguridad.md`: `ADM-TECH-OSS` inventariado (IDs 32989 y 32990), circuito de aprobación, aplicación OAuth 623 #1084774
- `PENDIENTES.md`

**Resumen:**
El escaneo hecho durante el alta de `ADM-TECH-OSS` informó el hallazgo 43743 (falta HSTS en `10.143.11.8:443`). Se agregó `Strict-Transport-Security: max-age=300` en el `VirtualHost` 443 de `PFR-GW-SRV`, con backup propio y verificación de rutas antes y después. El hallazgo se declaró resuelto en #1083416 y el reescaneo del 28/10 no informó nada. Falta subir `max-age` a `31536000` el 02/11/2026, compromiso escrito en el ticket. El 28/10 se completó el alta del servicio y se pidió una aplicación OAuth **nueva** para `https://oss.personal.com.py/adm/`: la de producción no sirve, porque `index.php` no envía `redirect_uri`.

### 2026-10-29 (trigésima cuarta entrada)

**Fuente:** Llamada con Norberto Núñez (`reunion/2026-10-29_llamada-norberto-envio-correo-ntf.srt`).

**Documentos creados:**
- `docs/adr/ADR-0010-envio-correo-sistemas-via-ntf.md`
- `reunion/2026-10-29_llamada-norberto-envio-correo-ntf.srt` (transcripción original)

**Documentos actualizados:**
- `docs/03_Componentes.md`: ficha del componente NTF y uso de su API de email
- `docs/05_Configuracion.md`: regla de `ACL-OVN-1` hacia el Exchange y ruta agregadas en la llamada (pendientes de verificación)
- `docs/07_Troubleshooting.md`: TRB-020, TRB-021 y TRB-022
- `docs/10_Decisiones.md`, `docs/11_Riesgos.md` (RIE-023), `docs/13_Linea_de_Tiempo.md`
- `laboratorio/2026-10-24_migracion-admtech-lxd/README.md`, `reunion/README.md`, `PENDIENTES.md`

**Resumen:**
Los sistemas del área (ADM-TECH, Infrawork, Tembiapó) envían correo por el módulo de email de NTF, sin pedir un servidor de correo nuevo ni una cuenta por sistema. Se probó en vivo: llegó un correo HTML con adjunto a casillas internas, después de abrir la salida hacia el Exchange `10.150.49.103:25` solo para el contenedor de NTF. Quedan dos problemas: el Exchange ya no hace relay hacia destinatarios externos, por lo que hay que pedir el relay SMTP de Seguridad, y Outlook marca los correos como sospechosos.
