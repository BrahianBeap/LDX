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