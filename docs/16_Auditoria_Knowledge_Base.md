# 16 — Auditoría de Calidad del Knowledge Base

> **Tipo de documento:** Informe de auditoría interna
> **Alcance:** Todos los archivos del repositorio LDX al 2026-06-25
> **Propósito:** Evaluar la calidad, coherencia y mantenibilidad del Knowledge Base completo. No genera documentación nueva. No modifica documentos existentes.

---

## Índice

1. [Fortalezas](#1-fortalezas)
2. [Debilidades](#2-debilidades)
3. [Duplicaciones](#3-duplicaciones)
4. [Inconsistencias](#4-inconsistencias)
5. [Riesgos de mantenimiento](#5-riesgos-de-mantenimiento)
6. [Recomendaciones](#6-recomendaciones)
7. [Plan de mejora del repositorio](#7-plan-de-mejora-del-repositorio)

---

## 1. Fortalezas

### 1.1 Separación de responsabilidades generalmente respetada

Cada documento tiene una responsabilidad declarada y la respeta. El propósito de `03_Componentes.md` no se mezcla con el de `04_Instalacion.md`, y el de `07_Troubleshooting.md` no repite procedimientos de `06_Operacion.md`. La intención del principio está lograda.

### 1.2 Sistema de clasificación aplicado de forma consistente

Los indicadores ✅/🟡/🔴 se usan en todos los documentos que lo requieren. No hay afirmaciones sin clasificar sobre hechos técnicos. Esto es especialmente valioso en un KB construido a partir de una sola reunión donde muchos datos están pendientes de confirmación.

### 1.3 Navegación por enlaces relativos

Ningún documento copia el contenido de otro. Se usan enlaces relativos para referencias cruzadas en toda la base. Las "secciones de documentos relacionados" al final de cada archivo son correctas y funcionales.

### 1.4 Estándares de documentación aplicados correctamente en los casos principales

Los comandos en `04_Instalacion.md` y `06_Operacion.md` siguen el estándar completo de 8 campos (Objetivo, Comando, Explicación, Parámetros, Resultado esperado, Verificación, Errores frecuentes, Rollback).

Las fichas de componentes en `03_Componentes.md` siguen la tabla de 9 campos del estándar de arquitectura.

Las fichas de troubleshooting en `07_Troubleshooting.md` siguen los 6 campos del estándar.

### 1.5 ADRs profesionales y completos

Los cuatro ADRs (0002 a 0005) siguen fielmente la plantilla de Michael Nygard: contexto, problema, alternativas evaluadas, decisión, justificación, consecuencias y pendientes de seguimiento. Las alternativas descartadas están explicadas, no solo mencionadas.

### 1.6 Glosario comprensivo

`08_Glosario.md` cubre 30+ términos del proyecto en orden alfabético. La mayoría de conceptos técnicos usados en el KB tienen una definición de referencia en este documento.

### 1.7 Contexto histórico preservado

`12_Lecciones_Aprendidas.md` captura conocimiento tácito de la instalación inicial que de otra forma se perdería. La cita directa de Norberto Núñez en `ADR-0005` ("Vamos a tratar de mantener esta metodología...") preserva el razonamiento original en voz del autor.

---

## 2. Debilidades

### 2.1 El concepto más importante del KB se explica en tres lugares distintos

El comportamiento "cloud-init solo se ejecuta en el primer arranque" está documentado como:
- Sección de limitaciones en `05_Configuracion.md`
- Ficha TRB-002 en `07_Troubleshooting.md`
- Lección LL-003 en `12_Lecciones_Aprendidas.md`
- Dos respuestas en `09_FAQ.md`
- Nota en `06_Operacion.md`

Son seis apariciones del mismo concepto con el mismo contenido. Ver sección [3. Duplicaciones](#3-duplicaciones) para el análisis completo.

### 2.2 `04_Instalacion.md` mezcla instalación con configuración y operación

El documento se presenta como "procedimiento de instalación", pero sus últimos cuatro pasos son de otras responsabilidades:

| Paso | Contenido real | Documento dueño correcto |
|---|---|---|
| Paso 5 (firewall) | Configuración | `05_Configuracion.md` |
| Paso 6 (proxy HTTP) | Configuración | `05_Configuracion.md` |
| Paso 7 (grupo lxd) | Gestión de usuarios / operación | `06_Operacion.md` |
| Paso 8 (Web UI) | Acceso operativo | `06_Operacion.md` o `14_Manual_Operativo.md` |

Solo los pasos 1-4 son estrictamente "instalación" (snap install lxd, lxd init, snap install microovn, microovn cluster bootstrap). Los pasos 5-8 duplican contenido de otros documentos.

### 2.3 `03_Componentes.md` rompe el estándar en dos componentes

Prometheus y Grafana no tienen campo "Cómo verificar" funcional — solo tienen 🔴 Pendiente. Esto es el único lugar del KB donde el estándar de documentación de componentes no se cumple. No hay comando de verificación documentado para estos componentes.

### 2.4 `15_Revision_Arquitectonica.md` no pertenece al mismo nivel que los docs 00-14

Los documentos 00-14 son documentación técnica del sistema. El documento 15 es un informe de auditoría de consultoría. Tienen audiencias parcialmente diferentes, propósitos distintos y cadencias de actualización incompatibles. Numerarlo en serie implica que se actualiza igual que la arquitectura, cuando en realidad debería ser un snapshot temporal.

### 2.5 `10_Decisiones.md` es una capa redundante sobre los ADRs

El documento existe para ofrecer un "resumen ejecutivo" de las decisiones. Pero para cada decisión incluye 2-3 párrafos que parafrasean el ADR correspondiente. Un lector que quiera entender la decisión termina leyendo dos documentos con el mismo contenido. El riesgo: cuando el ADR se actualice, el resumen en 10_Decisiones.md puede no actualizarse.

### 2.6 Diagrama de dependencias incorrecto en `13_Linea_de_Tiempo.md`

```
VLAN 411 habilitada
       │
       ├──► Instalar CAR1 y FDO1 ──► Unir al cluster
```

Esta dependencia es incorrecta. La instalación de LXD en CAR1 y FDO1 y su incorporación al cluster **no depende de VLAN 411**. Se puede instalar LXD y unir los nodos al cluster sin VLAN 411. La dependencia real es:

```
VLAN 411 habilitada ──► Configurar OVN ──► Red cross-site funcional
```

La instalación de nodos (CAR1, FDO1) es independiente de VLAN 411 y puede hacerse en paralelo.

### 2.7 `README.md` (raíz) tiene una nota obsoleta

La siguiente nota nunca fue eliminada tras el análisis de la primera reunión:

> "La descripción detallada de LDX (qué es, qué problema resuelve, arquitectura) se incorporará tras el análisis de la primera reunión."

La reunión fue analizada y la descripción existe en `docs/`. Esta nota introduce confusión para un lector nuevo.

### 2.8 El `CHANGELOG.md` tiene estructura rota

Los tres primeros bloques de entrada (2026-06-25, segunda entrada, tercera entrada) son correctos. Sin embargo, existe un bloque de texto flotante al final del archivo, después de la tercera entrada, que corresponde a notas de contexto de la primera entrada. Este bloque quedó estructuralmente desconectado del historial al agregar entradas nuevas. Un editor futuro no sabrá a qué entrada pertenece.

---

## 3. Duplicaciones

Las duplicaciones se ordenan de mayor a menor impacto en el mantenimiento.

### DUP-001 — Cloud-init: primer arranque, no re-ejecuta

**Impacto:** Crítico — es el concepto técnico más repetido del KB.

| Documento | Sección |
|---|---|
| `05_Configuracion.md` | "Limitación importante" en cloud-init user-data |
| `06_Operacion.md` | Nota en "Detener, iniciar y reiniciar contenedores" |
| `07_Troubleshooting.md` | TRB-002 completa (causa, diagnóstico, solución, prevención) |
| `09_FAQ.md` | "¿Cloud-init se ejecuta en cada reinicio del contenedor?" |
| `09_FAQ.md` | "Modifiqué el perfil, ¿se aplican los cambios al contenedor existente?" |
| `12_Lecciones_Aprendidas.md` | LL-003 con explicación completa y pasos |

El concepto debería vivir en `05_Configuracion.md` y los demás documentos deberían enlazarlo.

---

### DUP-002 — Dispositivo proxy: `bind` define dónde está el socket `listen`

**Impacto:** Alto — aparece en tres documentos con tablas similares.

| Documento | Sección |
|---|---|
| `05_Configuracion.md` | Ambas secciones de proxy device con tabla de parámetros |
| `07_Troubleshooting.md` | TRB-003 con tabla de referencia rápida |
| `12_Lecciones_Aprendidas.md` | LL-002 con tabla y explicación |

Las tres tablas son prácticamente idénticas. La definición debería vivir en `05_Configuracion.md`.

---

### DUP-003 — Header `#cloud-config` obligatorio en user-data

**Impacto:** Alto.

| Documento | Sección |
|---|---|
| `03_Componentes.md` | Buenas prácticas de cloud-init |
| `05_Configuracion.md` | Advertencia en la sección de perfiles |
| `07_Troubleshooting.md` | TRB-001 con código YAML correcto e incorrecto |
| `12_Lecciones_Aprendidas.md` | LL-001 con código YAML correcto e incorrecto |

TRB-001 y LL-001 tienen el mismo bloque de código YAML.

---

### DUP-004 — Advertencia grupo `lxd` = acceso root

**Impacto:** Medio.

| Documento | Sección |
|---|---|
| `04_Instalacion.md` | Advertencia en Paso 7 |
| `06_Operacion.md` | Advertencia en "Agregar usuarios al grupo lxd" |
| `09_FAQ.md` | "¿Es seguro agregar a alguien al grupo lxd?" |

La advertencia en `09_FAQ.md` es una re-explicación de lo ya dicho en `04` y `06`.

---

### DUP-005 — Comando `usermod -aG lxd` con procedimiento

**Impacto:** Medio.

| Documento | Sección |
|---|---|
| `04_Instalacion.md` | Paso 7 completo con verificación |
| `06_Operacion.md` | Sección "Agregar usuarios al grupo lxd" |
| `14_Manual_Operativo.md` | "Cómo agregar un nuevo operador — Acceso CLI" |

El mismo comando con similar contexto aparece tres veces.

---

### DUP-006 — Regla de firewall `firewall-cmd --add-rich-rule`

**Impacto:** Medio.

| Documento | Sección |
|---|---|
| `04_Instalacion.md` | Paso 5 (con explicación completa de parámetros) |
| `05_Configuracion.md` | Sección "Configuración de firewall (firewalld)" |
| `14_Manual_Operativo.md` | "Cómo agregar un nuevo operador — Acceso al firewall" |

El comando aparece con explicación en `04` y `05`, y sin explicación en `14`.

---

### DUP-007 — Modo incógnito para Web UI

**Impacto:** Medio.

| Documento | Sección |
|---|---|
| `04_Instalacion.md` | Nota en Paso 8 |
| `07_Troubleshooting.md` | TRB-004 completa |
| `12_Lecciones_Aprendidas.md` | LL-005 completa |
| `14_Manual_Operativo.md` | Paso 4 en "Qué hacer si no se puede acceder a la Web UI" |

TRB-004 y LL-005 cubren el mismo incidente con el mismo nivel de detalle.

---

### DUP-008 — Verificación post-contenedor: `cloud-init status` + `ss -ntlp`

**Impacto:** Bajo.

| Documento | Sección |
|---|---|
| `06_Operacion.md` | "Verificación después de crear" |
| `07_Troubleshooting.md` | Comandos de diagnóstico rápido |
| `12_Lecciones_Aprendidas.md` | LL-008 |
| `14_Manual_Operativo.md` | "Verificar que cloud-init terminó" y "Verificar servicios activos" |

---

### DUP-009 — Dispositivo proxy es temporal; OVN es la solución permanente

**Impacto:** Bajo — aunque es un dato correcto, la advertencia se repite en demasiados lugares.

| Documento | Sección |
|---|---|
| `05_Configuracion.md` | Advertencia en ambas secciones de proxy device |
| `12_Lecciones_Aprendidas.md` | LL-009 |
| `09_FAQ.md` | "¿Por qué se usa un proxy HTTP en el contenedor?" |

---

### DUP-010 — Justificación de ZFS vs LVM

**Impacto:** Bajo.

| Documento | Sección |
|---|---|
| `10_Decisiones.md` | Decisión 2, párrafo de razón principal |
| `ADR-0003` | Secciones completas de alternativas, decisión y justificación |
| `09_FAQ.md` | "¿Por qué ZFS?" |

`10_Decisiones.md` y el FAQ re-explican lo que el ADR ya documenta.

---

## 4. Inconsistencias

### INC-001 — Diagrama de dependencias de `13_Linea_de_Tiempo.md` (error técnico)

El diagrama muestra VLAN 411 como prerequisito de la instalación de CAR1 y FDO1:

```
VLAN 411 habilitada
       │
       ├──► Instalar CAR1 y FDO1  ← ❌ Incorrecto
```

Técnicamente, la instalación de LXD y la incorporación de nodos al cluster no requieren VLAN 411. Esta dependencia es incorrecta y puede causar que el equipo espere innecesariamente a que VLAN 411 esté lista para instalar los nodos.

---

### INC-002 — `10_Decisiones.md` indica "alternativas pendientes de validación" para la decisión 3

La tabla del resumen dice para autenticación: "🔴 Pendiente de validación otras alternativas". Pero `ADR-0004` documenta dos alternativas (Opción A y Opción B). Hay información que existe en el ADR pero no se refleja en el resumen.

---

### INC-003 — `ADR-0003` referencia de riesgo incorrecta

En la sección Consecuencias/Riesgos, `ADR-0003` dice:
> "La falla del pool ZFS es un incidente crítico. Mitigación: solicitar backup de VM a SBA/AIT. Ver [11_Riesgos.md — RIE-006](11_Riesgos.md)."

RIE-006 trata sobre "Sin política de backup documentada". El riesgo específico de falla del pool ZFS es más cercano a RIE-002 (el único nodo activo) o debería ser su propio ítem de riesgo. La referencia a RIE-006 es imprecisa.

---

### INC-004 — `CHANGELOG.md` usa campos distintos al formato declarado

El encabezado del CHANGELOG declara 4 campos: Fecha, Fuente, Documentos afectados, Resumen.

Las entradas reales usan: Fuente, Documentos creados, ADRs creados, Archivos actualizados, Resumen.

El campo "Documentos afectados" fue dividido en tres sub-campos sin actualizar el formato declarado.

---

### INC-005 — `09_FAQ.md` contiene respuestas que pertenecen a otros documentos

Varias respuestas del FAQ tienen su dueño natural en otro documento y deberían ser solo un enlace:

| Pregunta del FAQ | Dueño correcto del contenido |
|---|---|
| ¿Por qué no funciona la red entre contenedores de distintos nodos? | `11_Riesgos.md` (RIE-001) |
| ¿Los contenedores migran automáticamente si cae un nodo? | `11_Riesgos.md` o `13_Linea_de_Tiempo.md` |
| ¿Puedo acceder a la Web UI desde fuera de la red local? | `11_Riesgos.md` (RIE-005) |
| ¿Por qué se descartó Ubuntu Fan? | `ADR-0002` |
| ¿Por qué ZFS? | `ADR-0003` |

---

### INC-006 — `14_Manual_Operativo.md` tiene una referencia de anchor rota

La sección "Qué hacer si no se puede acceder a la Web UI" contiene:

```markdown
[07_Troubleshooting.md#trb-004](07_Troubleshooting.md)
```

El anchor `#trb-004` está en el texto visible pero **no en el href**. El enlace apunta al inicio del documento, no a la ficha TRB-004. La forma correcta sería:

```markdown
[TRB-004 en 07_Troubleshooting.md](07_Troubleshooting.md#trb-004)
```

---

### INC-007 — `docs/README.md` atribuye todos los documentos a una sola fuente

El encabezado de `docs/README.md` dice:

> "Fuente primaria: `reunion/Llamada con Daniel y 3 personas más.vtt` — Primera reunión de instalación y configuración del cluster."

Esto es correcto para los documentos 00-14, pero **no es correcto para el documento 15** (`15_Revision_Arquitectonica.md`), que no proviene de la reunión sino de un análisis independiente. La atribución global se volverá más inexacta con cada nueva reunión procesada.

---

### INC-008 — `03_Componentes.md` rompe el estándar de documentación de componentes

Los componentes Prometheus y Grafana no tienen un campo "Cómo verificar" con un comando real. Están marcados como 🔴 Pendiente, lo que es aceptable como estado, pero el estándar de CLAUDE.md establece que el campo debe existir siempre.

---

## 5. Riesgos de mantenimiento

### MANT-001 — Las duplicaciones requieren actualizaciones paralelas (riesgo crítico)

Cuando cambie cualquier comportamiento de cloud-init (ejemplo: nueva sintaxis en Ubuntu 26.04), habrá que actualizar `05_Configuracion.md`, `07_Troubleshooting.md`, `09_FAQ.md` y `12_Lecciones_Aprendidas.md` simultáneamente. Si se actualiza solo uno, el KB queda con información contradictoria.

El mismo riesgo aplica para: dispositivo proxy, firewall, y procedimiento de Web UI.

---

### MANT-002 — `15_Revision_Arquitectonica.md` envejecerá rápidamente

El documento contiene afirmaciones como "Este sistema no está listo para producción" y "OVN no funcional". En cuanto OVN esté activo y los nodos estén instalados, el documento será desactualizado pero seguirá siendo el número 15 en el índice, indistinguible de la documentación técnica vigente.

No existe mecanismo en el repositorio para marcar un documento de auditoría como "snapshot histórico" vs "documentación vigente".

---

### MANT-003 — `10_Decisiones.md` y los ADRs pueden divergir

El documento 10 parafrasea a los ADRs. Si un ADR se actualiza (por ejemplo, si OVN fuera reemplazado por otra tecnología), el resumen en `10_Decisiones.md` puede no actualizarse. El resultado es que ambos documentos existan pero con información contradictoria sobre la misma decisión.

---

### MANT-004 — Status OVN/VLAN 411 está hardcodeado en 9 documentos

El estado "OVN pendiente de VLAN 411" aparece en:
`00_Resumen_Ejecutivo.md`, `01_Contexto.md`, `02_Arquitectura.md`, `09_FAQ.md`, `11_Riesgos.md`, `13_Linea_de_Tiempo.md`, `14_Manual_Operativo.md`, `15_Revision_Arquitectonica.md`, y los ADRs.

Cuando OVN esté funcional, todos estos documentos necesitarán actualización. No hay un mecanismo centralizado para rastrear qué documentos dependen de este estado.

---

### MANT-005 — Términos técnicos críticos no están en el glosario

El documento `15_Revision_Arquitectonica.md` introduce tres términos que no están definidos en `08_Glosario.md`:

| Término | Usado en | Estado en glosario |
|---|---|---|
| Dqlite | `15_Revision_Arquitectonica.md` | ❌ No definido |
| quórum (de cluster) | `15_Revision_Arquitectonica.md` | ❌ No definido |
| split-brain | `15_Revision_Arquitectonica.md` | ❌ No definido |
| live migration | `06_Operacion.md`, `09_FAQ.md` | ❌ No definido |

Si se agregan más documentos técnicos (como el doc 15) sin actualizar el glosario, el KB perderá cobertura progresivamente.

---

### MANT-006 — `ADR-0001-template.md` en la carpeta de decisiones

La plantilla ADR vive en `docs/adr/` junto a las decisiones reales. Un lector que liste los archivos de `docs/adr/` verá la plantilla mezclada con los ADRs activos. Si el repositorio llega a tener 20+ ADRs, encontrar la plantilla requiere leer nombres de archivo para distinguirla.

---

### MANT-007 — El CHANGELOG tiene texto flotante que perderá contexto

El bloque de texto que comienza con "Los archivos originales en formato `.txt` fueron refactorizados..." al final del CHANGELOG está desconectado de su entrada. Con el tiempo, cuando haya más entradas intermedias, nadie sabrá a qué cambio corresponde ese texto. Es un riesgo de confusión para futuras contribuciones.

---

## 6. Recomendaciones

Las recomendaciones se presentan en tres niveles: estructurales (afectan el repositorio en conjunto), de contenido (afectan documentos específicos), y de proceso (afectan cómo se mantiene el KB).

### Recomendaciones estructurales

**REC-01 — Crear `docs/auditoria/` o `docs/informes/` para documentos de auditoría**

`15_Revision_Arquitectonica.md` y `16_Auditoria_Knowledge_Base.md` no son documentación técnica del sistema. Son informes puntuales que envejecen de forma diferente. Moverlos a una subcarpeta separada (`docs/informes/` o `docs/auditoria/`) los distingue visualmente de la documentación vigente y permite marcarlos con fecha de generación.

**REC-02 — Mover `ADR-0001-template.md` a `recursos/`**

La plantilla ADR es un recurso para generar ADRs, no un ADR en sí. Debería vivir en `recursos/ADR-template.md`, que es la carpeta designada para plantillas y materiales de apoyo.

**REC-03 — Unificar `00_Resumen_Ejecutivo.md` y `01_Contexto.md`**

Ambos documentos explican "qué es el proyecto, qué problema resuelve". Tienen audiencias similares y contenido que se solapa. La distinción entre "resumen ejecutivo" y "contexto del proyecto" es difusa. Unificarlos en un único `00_Introduccion.md` con secciones diferenciadas eliminaría el solapamiento.

**REC-04 — Eliminar la nota obsoleta de `README.md`**

Eliminar el párrafo que dice "La descripción detallada de LDX [...] se incorporará tras el análisis de la primera reunión." La primera reunión fue analizada. La nota es confusa para cualquier lector.

### Recomendaciones de contenido

**REC-05 — Definir un único dueño para el concepto de cloud-init primer arranque**

El documento dueño debe ser `05_Configuracion.md`. Los demás documentos (`07_Troubleshooting.md`, `12_Lecciones_Aprendidas.md`, `09_FAQ.md`) deben enlazar a la sección correspondiente de `05_Configuracion.md` en lugar de re-explicar el concepto.

**REC-06 — Consolidar las fichas de incidente sobre cloud-init**

`TRB-002` en `07_Troubleshooting.md` y `LL-003` en `12_Lecciones_Aprendidas.md` documentan el mismo incidente. Mantener solo la ficha TRB-002 en Troubleshooting, y reemplazar LL-003 con una referencia: *"Ver TRB-002 en [07_Troubleshooting.md](07_Troubleshooting.md)."*

La misma lógica aplica para TRB-004/LL-005 (modo incógnito) y TRB-003/LL-002 (proxy bind).

**REC-07 — Corregir el diagrama de dependencias en `13_Linea_de_Tiempo.md`**

El diagrama actual es técnicamente incorrecto (ver INC-001). La instalación de CAR1 y FDO1 puede hacerse independientemente de VLAN 411.

**REC-08 — Agregar cuatro términos al glosario**

Dqlite, quórum, split-brain y live migration deben tener entradas en `08_Glosario.md`. Son términos técnicos usados en documentos existentes y relevantes para la audiencia del KB.

**REC-09 — Corregir la referencia de anchor rota en `14_Manual_Operativo.md`**

Cambiar `[07_Troubleshooting.md#trb-004](07_Troubleshooting.md)` a `[TRB-004](07_Troubleshooting.md#trb-004)`.

**REC-10 — Separar los pasos 5-8 de `04_Instalacion.md`**

Los pasos 1-4 son instalación. Los pasos 5-8 son configuración y operación. Mover el contenido de los pasos 5-8 a `05_Configuracion.md` y `14_Manual_Operativo.md` según corresponda, y reemplazar esos pasos en `04_Instalacion.md` con referencias: *"Ver configuración de firewall en [05_Configuracion.md](05_Configuracion.md)."*

**REC-11 — Corregir la referencia de riesgo en `ADR-0003`**

Reemplazar la referencia a RIE-006 por RIE-002 (nodo único sin redundancia) cuando el contexto habla de falla del pool ZFS.

**REC-12 — Reorganizar `09_FAQ.md` como puerta de entrada, no como fuente de información**

Las respuestas del FAQ que re-explican contenido de otros documentos deben convertirse en respuestas de 1-2 oraciones con enlace al documento dueño. Por ejemplo: *"¿Por qué ZFS? Porque provee snapshots integrados y mejor integración con LXD. Ver la decisión completa en [ADR-0003](adr/ADR-0003-storage-zfs.md)."*

**REC-13 — Agregar campo "Cómo verificar" a Prometheus y Grafana en `03_Componentes.md`**

Aunque la configuración está pendiente, se puede documentar el comando de verificación provisional: `snap services prometheus` o equivalente, marcado con 🔴 Pendiente.

**REC-14 — Reparar la estructura del `CHANGELOG.md`**

Mover el bloque de texto flotante ("Los archivos originales en formato `.txt`...") al interior de la primera entrada (2026-06-25), como parte de su sección "Resumen".

### Recomendaciones de proceso

**REC-15 — Establecer checklist de actualización al documentar reuniones futuras**

Cuando una reunión confirme el estado de OVN, el checklist debe incluir: qué documentos contienen referencias a "OVN no funcional" y cuáles deben actualizarse. El número de documentos afectados (9+) hace que sea fácil omitir alguno sin un checklist explícito.

**REC-16 — Agregar columna "Fuente" al índice de `docs/README.md`**

A medida que se procesen más reuniones, los documentos tendrán múltiples fuentes. Una columna "Última actualización" o "Fuente" en el índice permite saber qué documentos están desactualizados respecto a reuniones recientes.

**REC-17 — Definir política de documentos de auditoría**

Establecer que los documentos de tipo "auditoría" o "informe" lleven una fecha de validez en su encabezado y que se archiven en lugar de actualizarse. Por ejemplo: `15_Revision_Arquitectonica.md` debería llevar `> **Válido a:** 2026-06-25` y no actualizarse — en lugar de eso, generarse una nueva auditoría cuando el sistema cambie.

---

## 7. Plan de mejora del repositorio

Las acciones se priorizan por impacto en la calidad del KB.

### Prioridad 1 — Correcciones técnicas (hacer antes de la próxima reunión)

| Acción | Archivo afectado | Descripción |
|---|---|---|
| Corregir diagrama | `13_Linea_de_Tiempo.md` | Eliminar la dependencia incorrecta VLAN 411 → instalación de nodos |
| Reparar anchor | `14_Manual_Operativo.md` | Corregir el enlace `#trb-004` en el href |
| Eliminar nota obsoleta | `README.md` | Remover el placeholder sobre descripción pendiente |
| Reparar CHANGELOG | `CHANGELOG.md` | Mover el bloque flotante a la primera entrada |
| Corregir referencia ADR | `ADR-0003` | Cambiar referencia a RIE-006 por la referencia correcta |

### Prioridad 2 — Glosario y estándares (hacer en la próxima sesión de documentación)

| Acción | Archivo afectado | Descripción |
|---|---|---|
| Agregar 4 términos | `08_Glosario.md` | Dqlite, quórum, split-brain, live migration |
| Agregar verificación provisional | `03_Componentes.md` | Comandos placeholder para Prometheus y Grafana |
| Corregir inconsistencia autenticación | `10_Decisiones.md` | Actualizar nota de alternativas para reflejar ADR-0004 |
| Corregir atribución de fuente | `docs/README.md` | Ajustar el bloque de fuente primaria para no incluir doc 15 |

### Prioridad 3 — Consolidación de duplicados (hacer cuando el equipo tenga tiempo de deuda técnica)

| Acción | Descripción | Impacto |
|---|---|---|
| Consolidar cloud-init primer arranque | Definir `05_Configuracion.md` como dueño; los demás enlazan | Reduce 6 ocurrencias a 1 + 5 enlaces |
| Consolidar fichas de incidentes | TRB-002 absorbe LL-003; TRB-004 absorbe LL-005; TRB-003 absorbe LL-002 | Simplifica `12_Lecciones_Aprendidas.md` |
| Consolidar proxy bind | Definir `05_Configuracion.md` como dueño de la tabla | Reduce 3 ocurrencias a 1 + 2 enlaces |
| Simplificar firewall command | Único punto en `05_Configuracion.md`; los demás enlazan | Reduce 3 ocurrencias a 1 + 2 enlaces |

### Prioridad 4 — Reestructuración (para sesión de refactorización dedicada)

| Acción | Descripción | Beneficio |
|---|---|---|
| Crear `docs/informes/` | Mover docs 15 y 16 a subcarpeta de informes | Distingue auditorías de documentación técnica |
| Mover template ADR | `docs/adr/ADR-0001-template.md` → `recursos/ADR-template.md` | Limpia la lista de ADRs activos |
| Evaluar unificar docs 00 y 01 | Fusionar Resumen Ejecutivo + Contexto en un único `00_Introduccion.md` | Elimina solapamiento de propósito |
| Recortar `09_FAQ.md` | Convertir respuestas largas en 1-2 oraciones + enlace al dueño | Convierte FAQ en portal de navegación |
| Separar pasos 5-8 de instalación | Mover configuración y operación de `04_Instalacion.md` a sus documentos dueños | Respeta la separación de responsabilidades |

---

## Resumen ejecutivo de la auditoría

| Dimensión | Estado | Nota principal |
|---|---|---|
| Separación de responsabilidades | ✅ Buena | Respetada en general; excepciones en doc 04 y 15 |
| Duplicaciones | ⚠️ Significativa | 10 conjuntos de contenido duplicado identificados |
| Consistencia interna | ⚠️ Aceptable | 8 inconsistencias; 1 es un error técnico (INC-001) |
| Cobertura del glosario | ⚠️ Incompleta | 4 términos técnicos usados pero no definidos |
| Calidad de enlaces | ⚠️ Casi completa | 1 anchor roto en `14_Manual_Operativo.md` |
| Estándares de documentación | ✅ Mayormente cumplidos | Excepción en Prometheus/Grafana en doc 03 |
| Riesgos de mantenimiento | 🔴 Altos | 7 riesgos identificados, 1 crítico (duplicaciones) |
| Estructura de repositorio | ⚠️ Mejorable | CHANGELOG roto, note obsoleta, template en lugar incorrecto |

**La mayor amenaza a largo plazo para este KB no es la falta de documentación, sino el contenido duplicado.** Con 10 conjuntos de duplicados activos, cada actualización de un concepto técnico requerirá editar múltiples archivos simultáneamente. A medida que el proyecto avance y se procesen más reuniones, la probabilidad de que los documentos diverjan se acumula. Las prioridades 1 y 3 del plan de mejora abordan esto directamente.
