# 15 — Revisión Arquitectónica Independiente

> **Tipo de documento:** Auditoría técnica independiente
> **Audiencia:** Arquitectos, infraestructura, operaciones, seguridad, gerencia técnica
> **Propósito:** Evaluar críticamente el diseño actual antes del paso a producción. Este documento no describe la arquitectura — la cuestiona.
>
> **Advertencia:** Este documento contiene críticas directas a decisiones tomadas. El objetivo no es invalidar el trabajo realizado, sino identificar riesgos reales antes de que impacten en producción.

---

## Índice

1. [Veredicto ejecutivo](#1-veredicto-ejecutivo)
2. [Alta disponibilidad — La promesa vs la realidad](#2-alta-disponibilidad--la-promesa-vs-la-realidad)
3. [Arquitectura — Análisis crítico](#3-arquitectura--análisis-crítico)
4. [Red — El cuello de botella central](#4-red--el-cuello-de-botella-central)
5. [Almacenamiento — Riesgos no documentados](#5-almacenamiento--riesgos-no-documentados)
6. [Seguridad — Superficie de ataque](#6-seguridad--superficie-de-ataque)
7. [Operación — Deuda operativa](#7-operación--deuda-operativa)
8. [Observabilidad — Punto ciego](#8-observabilidad--punto-ciego)
9. [Disaster Recovery — Sin plan real](#9-disaster-recovery--sin-plan-real)
10. [Backup — Estrategia incompleta](#10-backup--estrategia-incompleta)
11. [Escalabilidad — Limitaciones no evaluadas](#11-escalabilidad--limitaciones-no-evaluadas)
12. [Deuda técnica catalogada](#12-deuda-técnica-catalogada)
13. [Preguntas que nadie hizo](#13-preguntas-que-nadie-hizo)
14. [Comparación con buenas prácticas de industria](#14-comparación-con-buenas-prácticas-de-industria)
15. [Recomendaciones por prioridad](#15-recomendaciones-por-prioridad)

---

## 1. Veredicto ejecutivo

**Este sistema, en su estado actual, no está listo para producción.**

No es un juicio sobre la calidad técnica del trabajo realizado ni sobre las personas involucradas. Es una evaluación del estado objetivo del sistema al momento de esta auditoría.

| Dimensión | Estado | Calificación |
|---|---|---|
| Alta disponibilidad real | 1 nodo activo de 3 planificados | ❌ No existe |
| Red de contenedores | OVN no funcional | ❌ No existe |
| Estrategia de backup | Informal, sin política ni pruebas | ⚠️ Insuficiente |
| Seguridad | Hardening no completado | ⚠️ Incompleto |
| Observabilidad | Prometheus sin configurar | ⚠️ Incompleto |
| Disaster Recovery | Sin plan documentado ni probado | ❌ No existe |
| Automatización | Operación 100% manual | ❌ No existe |
| Documentación técnica | Completa para lo instalado | ✅ Adecuada |

**Conclusión:** El equipo instaló correctamente el primer nodo y documentó bien el proceso. El problema no es lo que se hizo, sino lo que aún falta para que esto sea una plataforma de producción confiable. La distancia entre "primer nodo funcional" y "cluster productivo con HA" es mayor de lo que la reunión inicial sugirió.

---

## 2. Alta disponibilidad — La promesa vs la realidad

### 2.1 El cluster actual no tiene alta disponibilidad

El proyecto se presenta como un "cluster LXD distribuido en 3 sitios geográficos". Esta descripción es **aspiracional**, no descriptiva del estado actual.

**Estado real:**
- Un único nodo activo (PFR1).
- Todos los contenedores están en PFR1.
- Si PFR1 falla, todos los servicios caen.
- No hay failover automático.
- No hay failover manual (no hay nodo destino).

Esto no es un cluster de alta disponibilidad. Es un servidor único con software de clustering instalado.

### 2.2 El quorum de LXD (Dqlite) con un solo nodo

LXD usa **Dqlite** (SQLite distribuido) para la base de datos del cluster. Dqlite requiere quórum para operaciones de escritura.

| Nodos totales | Quórum requerido | Nodos que pueden fallar |
|---|---|---|
| 1 (estado actual) | 1 | 0 |
| 3 (estado planificado) | 2 | 1 |
| 5 | 3 | 2 |

**Con 1 nodo activo, el cluster no puede sobrevivir ninguna falla.** Si PFR1 se cae antes de que CAR1 y FDO1 estén agregados, el cluster queda en estado indeterminado y puede requerir intervención manual para recuperarse. La base de datos del cluster existe únicamente en PFR1.

**Pregunta crítica no respondida:** ¿Qué sucede si PFR1 cae durante el proceso de agregar CAR1 al cluster? ¿Puede CAR1 terminar su proceso de join? ¿Se pierde el estado del cluster?

### 2.3 Con 3 nodos distribuidos en 3 sitios: el peor diseño de quórum posible

Paradójicamente, el diseño de 3 nodos en 3 sitios diferentes, que suena a máxima redundancia, crea la **peor relación posible entre tolerancia a fallas y quórum**.

```
Escenario: Corte de enlace entre sitios

  PFR1 ──X── CAR1 ──── FDO1
  
  PFR1 cree estar aislado → intenta seguir siendo líder
  CAR1 + FDO1 tienen quórum → eligen nuevo líder
  
  Resultado: split-brain potencial
```

Con 1 nodo por sitio y 3 sitios:
- Perder 1 sitio = perder 1 de 3 nodos = cluster sigue funcionando ✅
- Perder 2 sitios = perder 2 de 3 nodos = **cluster queda en modo read-only** ❌
- Partición de red entre sitios = **riesgo de split-brain**

Para infraestructura distribuida geográficamente, la práctica de la industria recomienda número impar de nodos con **al menos 2 nodos por sitio** o usar un **witness/árbitro** en un cuarto sitio.

### 2.4 No existe migración automática de contenedores

Si un nodo falla, sus contenedores **no migran automáticamente** a otro nodo. La migración es manual y requiere:
1. Que el nodo destino esté disponible.
2. Que los datos del contenedor (ZFS) sean transferibles (lo cual tarda).
3. Intervención humana.

**El tiempo de inactividad de un servicio ante la falla de un nodo es: desde que falla hasta que un operador detecta, evalúa y migra manualmente.** En horario no laboral, esto puede ser horas.

---

## 3. Arquitectura — Análisis crítico

### 3.1 Puntos únicos de falla (SPOF)

| Componente | SPOF | Impacto | Mitigación actual |
|---|---|---|---|
| PFR1 (único nodo activo) | Sí | Total — todos los servicios caen | Ninguna |
| VMware (SBA/AIT) | Sí | Sin VMs, sin cluster | Ninguna |
| Cristian (administrador VMware) | Sí | Bloquea toda habilitación de red | Ninguna |
| Nicolás (proxy HTTP) | Sí | Contenedores sin internet | Ninguna |
| Norberto Núñez (conocimiento técnico) | Sí | Operación sin referencia | Documentación (parcial) |
| Pool ZFS en /dev/sda6 | Sí | Todos los contenedores de PFR1 pierden datos | Backup VMware (informal) |
| Enlace de red entre sitios | Sí | Partición del cluster | Ninguna |

**Hay 7 SPOFs identificados.** Para un sistema de producción, el objetivo debería ser cero SPOFs o SPOFs con RTO documentado y aceptado explícitamente por la organización.

### 3.2 Dependencia crítica de VMware

Toda la plataforma LXD corre sobre VMs VMware gestionadas por un equipo externo (SBA/AIT). Esto crea una dependencia estructural que nunca fue evaluada en la reunión.

**Implicaciones:**
- Las VMs no pueden ser redimensionadas sin pasar por SBA/AIT.
- Las interfaces de red no pueden habilitarse sin Cristian.
- Los snapshots y backups de VMs son responsabilidad de SBA/AIT.
- Los tiempos de respuesta de SBA/AIT no están documentados como SLA.

**Riesgo crítico:** Si Cristian no habilita VLAN 411, OVN nunca funcionará. El proyecto LXD tiene su requisito más importante (la red de contenedores) bloqueado por una dependencia externa sin SLA.

### 3.3 Ausencia de separación de planos de control

En infraestructura empresarial, los siguientes planos deben estar separados:

| Plano | Descripción | Estado en LXD |
|---|---|---|
| Gestión de VMs | SSH, administración de OS | Comparte interfaz /29 |
| Cluster LXD | API ports 8443/8444 | Comparte interfaz /29 |
| Datos de contenedores | Tráfico de servicios | VLAN 411 (no habilitada) |
| Almacenamiento | Replicación de storage | No existe |
| Monitoreo | Métricas y logs | No separado |

Actualmente, la gestión de VMs, la API del cluster y el acceso de operadores comparten la **misma interfaz /29**. Esto no es un problema menor de arquitectura — es una violación del principio de separación de responsabilidades en red.

### 3.4 Sin plan de capacidad

No existe documentación sobre:
- Cuántos contenedores puede hospedar un nodo (límite de RAM/CPU de las VMs).
- Cuánto espacio ocupará cada servicio en ZFS.
- Cuándo se necesitará expandir el storage pool.
- Cuándo se necesitarán más nodos por sitio.

InfraFileRoom tiene 800 GB de datos. El pool ZFS de PFR1 tiene 315 GB. **Los datos de InfraFileRoom no caben en el pool actual del nodo.**

---

## 4. Red — El cuello de botella central

### 4.1 OVN: la funcionalidad más importante no está operativa

El diferenciador técnico principal del diseño (contenedores comunicándose entre sitios) no existe todavía. El cluster en su estado actual es funcionalmente equivalente a un servidor único con algunas herramientas de gestión.

**Sin OVN:**
- Los contenedores de PFR1 pueden comunicarse entre sí (misma VM).
- Los contenedores de PFR1 NO pueden comunicarse con contenedores de CAR1 o FDO1.
- Los servicios que necesitan múltiples componentes (web + base de datos) deben estar en el mismo nodo.
- La alta disponibilidad de servicios entre sitios es imposible.

**El proyecto no debería entrar en producción hasta que OVN sea funcional** y validado con pruebas de conectividad cross-site.

### 4.2 La subred /29 de gestión: un problema que crecerá

Una subred /29 tiene 6 direcciones IP utilizables. Analicemos el uso actual y proyectado:

| IP | Uso |
|---|---|
| .1 | Gateway de red |
| .2 | PFR1 (instalado) |
| .3 | CAR1 (pendiente) |
| .4 | FDO1 (pendiente) |
| .5 | 🔴 Disponible (solo 2 quedan) |
| .6 | 🔴 Disponible |

Con 3 sitios y 1 VM por sitio, el /29 está prácticamente lleno. Si en el futuro se necesita:
- Un cuarto sitio: sin espacio.
- Un segundo nodo por sitio (para redundancia dentro del sitio): sin espacio.
- Un servidor de monitoreo dedicado: sin espacio.
- Un servidor de logs centralizado: sin espacio.

**Esta restricción de red no fue discutida como un limitante a largo plazo.** Es una restricción estructural que puede bloquear el crecimiento del cluster.

### 4.3 Sin DNS para contenedores

La documentación no menciona cómo los contenedores se descubren entre sí. En una arquitectura de microservicios donde la base de datos está en un contenedor y el frontend en otro, ¿cómo sabe el frontend la IP de la base de datos?

Opciones no evaluadas:
- DNS interno del cluster LXD (LXD provee un DNS integrado por red OVN).
- Archivo `/etc/hosts` estático (frágil, no escalable).
- DNS corporativo con registros por contenedor.
- Service discovery (Consul, etc.).

Sin DNS, la comunicación entre contenedores requiere IPs hardcodeadas, lo que hace el sistema extremadamente frágil ante reinicios o migraciones.

### 4.4 Sin estrategia de direccionamiento IP para OVN

Cuando OVN sea funcional, los contenedores necesitarán IPs en la red OVN. No existe documentación sobre:
- Qué rango de IPs se usará para los contenedores.
- Si las IPs serán estáticas o dinámicas (DHCP via OVN).
- Cómo se asignarán IPs a contenedores de diferentes aplicaciones.
- Si habrá segmentación de red entre contenedores de distintas aplicaciones.

### 4.5 Firewall: reglas por IP personal (no escalable)

Las reglas actuales de firewall son del tipo "permitir la IP de Daniel" y "permitir la IP de Rocío". Este enfoque tiene problemas serios:

- Las IPs personales cambian (trabajo remoto, VPN, hotspots).
- Con 10 operadores, hay 10 reglas frágiles.
- No hay proceso documentado para agregar o remover acceso.
- No hay integración con un sistema de identidad corporativo.
- Si un operador sale de la empresa, su IP debe removerse manualmente.

**Práctica recomendada:** Acceso via VPN corporativa que autentica por identidad, no por IP.

### 4.6 El dispositivo proxy LXD: riesgos no documentados

El dispositivo proxy LXD (workaround temporal) tiene riesgos que no aparecen en la documentación:

- Un error de configuración (`bind` invertido) puede exponer servicios internos del contenedor hacia la red de gestión, haciéndolos accesibles desde fuera del cluster.
- No hay restricción de qué puertos pueden ser redirigidos.
- No hay logging del tráfico que pasa por los dispositivos proxy.
- No hay proceso documentado para auditarlos ni removerlos cuando OVN esté listo.

---

## 5. Almacenamiento — Riesgos no documentados

### 5.1 Sin replicación de datos entre nodos

El storage ZFS es **local a cada nodo**. No existe replicación entre nodos. Las implicaciones son:

- Si el pool ZFS de PFR1 falla, **todos los datos de los contenedores de PFR1 se pierden**.
- Migrar un contenedor a otro nodo requiere transferir todos sus datos via red (puede tomar horas para contenedores grandes).
- No hay sincronización de datos de contenedores entre sitios.
- Un contenedor en CAR1 y un contenedor en FDO1 no pueden compartir almacenamiento.

Para InfraFileRoom con 800 GB, una migración de contenedor entre nodos tarda **horas** dependiendo del ancho de banda entre sitios.

### 5.2 La capacidad del pool es insuficiente para InfraFileRoom

| Ítem | Tamaño |
|---|---|
| Pool ZFS en PFR1 | 315 GB |
| Datos de InfraFileRoom | ~800 GB |
| Déficit | **~485 GB** |

InfraFileRoom no puede ser migrado a PFR1 sin ampliar el pool. Esto requiere:
- Agregar un disco a la VM en VMware (coordinación con SBA/AIT).
- Expandir el pool ZFS.
- Proceso que no fue discutido.

### 5.3 Sin política de scrubs ZFS

ZFS detecta y corrige (cuando es posible) errores de datos mediante checksums. Pero la detección proactiva requiere ejecutar **scrubs periódicos** que leen todo el pool y verifican la integridad.

Sin scrubs programados, la corrupción silenciosa de datos puede pasar desapercibida por meses hasta que se accede al dato corrupto.

**Práctica recomendada:** `zpool scrub` semanal o mensual, monitoreado via Prometheus.

### 5.4 Sin monitoreo de uso del pool

No hay alerta cuando el pool ZFS se llena. ZFS con pool > 80% de uso tiene degradación de rendimiento significativa. Con pool > 95%, el sistema se comporta de manera impredecible.

Para 315 GB de pool con múltiples contenedores, este límite puede alcanzarse más rápido de lo esperado.

### 5.5 Sin snapshot policy

LXD + ZFS soporta snapshots instantáneos y automáticos de contenedores. Estos snapshots permiten restaurar un contenedor a un estado anterior en segundos.

Esta funcionalidad no fue mencionada ni configurada. Sin snapshots automáticos, la única opción de "deshacer" un cambio en producción es restaurar un backup completo de la VM.

---

## 6. Seguridad — Superficie de ataque

### 6.1 El grupo `lxd` equivale a root en el host

La documentación menciona esto como advertencia, pero las implicaciones completas no fueron exploradas:

Un usuario en el grupo `lxd` puede:
- Crear un contenedor con `/` del host montado como volumen.
- Acceder a todos los archivos del host desde dentro del contenedor.
- Leer `/etc/shadow`, claves SSH, certificados privados.
- Ejecutar comandos como root en el host mediante un contenedor privilegiado.

**No existe documentación sobre:**
- Quién tiene acceso SSH a las VMs (que es acceso root real).
- Qué usuarios están en el grupo `lxd` en PFR1.
- Si hay usuarios de servicio no necesarios en ese grupo.
- Política de revocación de acceso cuando un operador sale.

### 6.2 Secretos expuestos en cloud-init user-data

Los perfiles LXD con cloud-init `user-data` son visibles para cualquier usuario en el grupo `lxd`. Si en el futuro se agregan contraseñas de base de datos, claves API o tokens en los perfiles (práctica común), quedan expuestos a todos los operadores con acceso LXD.

**La documentación no aborda gestión de secretos.** Para producción, las credenciales deben manejarse mediante:
- Vault (HashiCorp Vault).
- Variables de entorno en runtime (no en cloud-init).
- Secrets de LXD (disponible en versiones recientes).

### 6.3 Certificados TLS auto-firmados sin política de rotación

La Web UI usa certificados TLS auto-firmados. Para un entorno inicial esto es aceptable, pero:

- **¿Cuándo expiran los certificados de usuario?** No documentado.
- **¿Cómo se rota el certificado del servidor?** No documentado.
- **¿Cómo se detecta un certificado expirado?** No existe alerta.
- **¿Qué pasa cuando un operador abandona la empresa?** No hay proceso de revocación.

Un certificado de operador no revocado es una puerta de acceso permanente para una persona que ya no debería tener acceso.

### 6.4 Acceso SSH a las VMs: el vector de ataque ignorado

La Web UI y el CLI de LXD tienen autenticación documentada. Pero el acceso SSH a las VMs Ubuntu que hospedan LXD **nunca fue mencionado en la reunión**.

Quién tiene acceso SSH a PFR1 tiene acceso root efectivo al cluster completo. La documentación ignora completamente este vector:

- ¿Qué usuarios tienen acceso SSH?
- ¿Se usa autenticación por clave o por contraseña?
- ¿Hay fail2ban o protección ante fuerza bruta?
- ¿Se auditan los accesos SSH?

### 6.5 Sin audit logging

No existe documentación sobre logging de:
- Quién accedió a la Web UI y cuándo.
- Qué operaciones realizó cada operador.
- Qué contenedores fueron creados, modificados o eliminados.
- Qué cambios de configuración se realizaron.

Para un sistema de producción, el audit logging es un requisito de seguridad y compliance, no una mejora opcional. LXD tiene capacidades de audit logging que no fueron configuradas.

### 6.6 AppArmor/seccomp: no mencionados pero presentes

LXD aplica perfiles AppArmor y seccomp por defecto a los contenedores. Esto es positivo y no requiere configuración adicional. Sin embargo:

- No hay documentación de qué perfiles se aplican.
- No hay proceso para verificar que los perfiles están activos.
- Si se usan contenedores "privilegiados" (sin perfiles de seguridad), esto es un riesgo crítico no documentado.

### 6.7 Puertos expuestos sin documentación completa

| Puerto | Servicio | Expuesto a | Documentado |
|---|---|---|---|
| 8443 | LXD cluster/UI | Red local (con reglas firewall) | ✅ |
| 8444 | LXD admin | Red local | ✅ |
| 22 | SSH | 🔴 No documentado | ❌ |
| Puertos de contenedores vía proxy | Servicios de app | 🔴 No documentado | ❌ |
| Puerto Prometheus | Métricas | 🔴 No documentado | ❌ |

---

## 7. Operación — Deuda operativa

### 7.1 Operación 100% manual

Todo en este sistema requiere intervención humana:

- Crear contenedores: manual (UI o CLI).
- Migrar contenedores: manual.
- Crear y rotar imágenes: manual.
- Actualizar el OS base: manual.
- Configurar nuevos operadores: manual (token + firewall + grupo).
- Responder a fallas: manual.
- Agregar nuevos nodos: manual.

No existe ningún grado de automatización para operaciones recurrentes. En producción, la operación manual introduce:
- Tiempo de respuesta limitado por disponibilidad humana.
- Variabilidad y errores en procedimientos repetitivos.
- Imposibilidad de responder a eventos fuera de horario laboral.

### 7.2 Riesgo de personas clave (key man risk)

| Persona | Conocimiento crítico | Qué pasa si no está disponible |
|---|---|---|
| Norberto Núñez | Arquitectura LXD, OVN, troubleshooting | El equipo no puede resolver problemas complejos |
| Cristian (VMware) | VLAN 411, VM management | OVN nunca se habilita, no se pueden agregar VMs |
| Nicolás (seguridad) | Proxy HTTP | Contenedores sin internet si el proxy cae |
| Marcos Casco | Coordinación, contactos | Solicitudes sin gestionar |

**El proyecto LXD tiene 4 personas críticas únicas.** Si Cristian está de vacaciones o sale de la empresa, la VLAN 411 puede no habilitarse por semanas. Si Norberto no está disponible, el equipo no puede resolver fallas de OVN.

### 7.3 Sin entorno de staging

No existe mención de un entorno de testing o staging. Los cambios de configuración (perfiles, cloud-init, dispositivos) se prueban directamente en el entorno productivo.

En producción, una prueba de cloud-init mal configurada destruye el contenedor y requiere recrearlo. Si ese contenedor tiene servicios activos, hay downtime.

### 7.4 Sin control de versiones para la configuración

Los perfiles LXD, las configuraciones de contenedores y los cloud-init templates no están en ningún sistema de control de versiones (git, etc.). Un cambio accidental en un perfil que afecta a múltiples contenedores no tiene:
- Historial de cambios.
- Posibilidad de revertir.
- Proceso de review.

### 7.5 Sin proceso de actualización de contenedores

Los contenedores Ubuntu creados con cloud-init tienen una imagen base que fue descargada en un momento específico. Con el tiempo:
- Los paquetes quedan desactualizados.
- Las vulnerabilidades de seguridad se acumulan.
- La imagen base de Ubuntu en el servidor de imágenes de Canonical se actualiza, pero los contenedores existentes no.

No hay proceso documentado para:
- Actualizar los paquetes dentro de contenedores existentes.
- Recrear contenedores con imágenes base actualizadas.
- Verificar vulnerabilidades en imágenes existentes.

---

## 8. Observabilidad — Punto ciego

### 8.1 El sistema de producción está funcionalmente ciego

Al momento de esta auditoría:
- Prometheus: mencionado durante lxd init, pero sin configuración de servidor externo.
- Grafana: sin configuración documentada.
- Alertas: no existen.
- Log aggregation: no existe.
- Dashboard de salud: no existe.

**No hay forma de saber si el cluster está saludable sin hacer `lxc cluster list` manualmente.** No hay forma de detectar que un contenedor falló a las 3 AM. No hay forma de saber si el pool ZFS está al 95% de capacidad.

### 8.2 Métricas faltantes críticas

Incluso cuando Prometheus esté configurado, las siguientes métricas no fueron discutidas:

| Métrica | Importancia | Estado |
|---|---|---|
| % uso del pool ZFS | Crítica — previene llenado catastrófico | ❌ No configurada |
| Estado de salud del nodo | Crítica — detecta nodos OFFLINE | ❌ No configurada |
| RAM/CPU por contenedor | Alta — detecta contenedores problemáticos | ❌ No configurada |
| Estado de cloud-init | Alta — detecta fallos silenciosos | ❌ No configurada |
| Conectividad OVN | Crítica — cuando OVN esté activo | ❌ No configurada |
| Expiración de certificados TLS | Alta — previene outage por certificado vencido | ❌ No configurada |

### 8.3 Sin correlación de logs

Cuando un servicio falla en un contenedor, los logs relevantes están en:
- `/var/log/cloud-init.log` (dentro del contenedor).
- Los logs de la aplicación (dentro del contenedor).
- Los logs de LXD en el host (`snap logs lxd`).
- Los logs de firewalld.
- Los logs de OVN.

Sin un sistema de log aggregation (ELK, Loki, etc.), el diagnóstico de una falla requiere acceder manualmente a múltiples lugares en múltiples nodos.

---

## 9. Disaster Recovery — Sin plan real

### 9.1 No existe un plan de DR

La documentación de backup y recovery es informativa pero no constituye un plan de DR. Un plan de DR debe incluir:

- **RTO (Recovery Time Objective):** ¿Cuánto tiempo puede estar caído el servicio?
- **RPO (Recovery Point Objective):** ¿Cuántos datos puede perder la organización?
- **Runbooks de recuperación:** pasos exactos para cada escenario de falla.
- **Responsables:** quién ejecuta cada paso y cómo contactarlos.
- **Pruebas:** calendario de simulacros y resultados.

Nada de esto existe.

### 9.2 Escenarios de falla sin respuesta

| Escenario | Plan de recuperación | RTO estimado |
|---|---|---|
| PFR1 cae (VM problema temporal) | Reiniciar VM (solicitar a SBA/AIT) | Desconocido |
| PFR1 cae (disco /dev/sda6 muerto) | Restaurar backup VMware (si existe) | Desconocido (horas/días) |
| Pool ZFS corrupto | Restaurar backup VMware | Desconocido |
| Corrupción de la base de datos Dqlite | 🔴 Sin plan documentado | Desconocido |
| Pérdida del sitio Franco completo | Sin contenedores alternativos | Indeterminado |
| Error humano: borró contenedor equivocado | Restaurar desde imagen (si existe) o backup VM | Desconocido |

### 9.3 La corrupción de Dqlite es el escenario más crítico no documentado

La base de datos Dqlite de LXD contiene el estado completo del cluster: qué contenedores existen, sus configuraciones, perfiles, imágenes, redes. Si esta base de datos se corrompe:

- LXD no sabe qué contenedores existían.
- Los datos en ZFS pueden seguir existiendo, pero LXD no los reconoce.
- La recuperación requiere reconstrucción manual de la configuración.

LXD sí tiene mecanismos de snapshot de la base de datos Dqlite, pero no fueron mencionados ni configurados.

---

## 10. Backup — Estrategia incompleta

### 10.1 La estrategia actual en términos de RPO/RTO

| Tipo de backup | Frecuencia | Responsable | RPO | RTO |
|---|---|---|---|---|
| Backup VMware de VM | 🔴 No solicitado formalmente aún | SBA/AIT | Desconocido | Desconocido |
| Exportación manual de imagen | 🔴 No programado | Operador | Desde el último export manual | Minutos (para restaurar) |
| Snapshot ZFS de contenedor | 🔴 No configurado | — | N/A | N/A |
| Backup de base de datos Dqlite | 🔴 No configurado | — | N/A | N/A |

**No existe una sola estrategia de backup que sea:**
- Automática.
- Probada.
- Con RTO/RPO definido.
- Con procedimiento de restauración documentado.

### 10.2 El backup de VM de VMware no es suficiente solo

El backup de la VM en VMware es una red de seguridad válida, pero tiene limitaciones:
- La granularidad es la VM completa, no un contenedor individual.
- Restaurar la VM completa implica downtime de todos los contenedores en esa VM.
- La frecuencia del backup depende de SBA/AIT, no del equipo LXD.
- Nunca fue probado un proceso de restauración.

### 10.3 Sin pruebas de restauración

Una estrategia de backup que nunca fue probada no es una estrategia de backup — es una esperanza.

**Regla del sector:** un backup no probado es equivalente a no tener backup.

---

## 11. Escalabilidad — Limitaciones no evaluadas

### 11.1 Proyección de contenedores por nodo

LXD soporta decenas o cientos de contenedores por nodo, pero el límite práctico depende de:
- RAM de la VM: no documentada para PFR1.
- CPU de la VM: no documentada.
- IOPS del pool ZFS.
- Ancho de banda de red.

Sin saber las especificaciones de las VMs, no es posible saber cuántos contenedores caben.

### 11.2 El /29 bloquea el crecimiento de nodos

Como se indicó en la sección de red, el /29 está prácticamente lleno con 3 nodos. Agregar un cuarto sitio o un segundo nodo por sitio requeriría cambios en la red corporativa — un proceso potencialmente largo y burocrático.

### 11.3 OVN tiene límites de escala propios

OVN escala bien, pero a medida que el cluster crece:
- La tabla de flujos OVN crece con el número de contenedores y redes.
- La sincronización del plano de control OVN introduce latencia.
- La configuración de OVN se vuelve más compleja.

Sin un ingeniero con experiencia en OVN a gran escala, el cluster puede encontrar problemas de rendimiento que no son evidentes con pocos contenedores.

### 11.4 El modelo de un perfil global no escala bien

El enfoque actual (un perfil con configuración de proxy LXD) funciona para pocos contenedores. Con 100 contenedores de 20 aplicaciones diferentes, se necesitan perfiles por aplicación, por entorno, por versión. La gestión manual de perfiles se vuelve inmanejable.

---

## 12. Deuda técnica catalogada

| ID | Ítem | Origen | Urgencia |
|---|---|---|---|
| DT-001 | Dispositivos proxy LXD en perfiles y contenedores | Workaround temporal por falta de OVN | Alta — debe removerse cuando OVN funcione |
| DT-002 | IPs de operadores hardcodeadas en firewall | Sin VPN, sin sistema de identidad | Alta — primera persona que cambia de IP rompe su acceso |
| DT-003 | cloud-init con configuración de proxy HTTP embebida | Workaround temporal | Alta — debe actualizarse cuando OVN funcione |
| DT-004 | Certificados TLS auto-firmados sin rotación | Estado inicial | Media — problema futuro cuando expiren |
| DT-005 | Operación 100% manual (creación de contenedores, configuración) | Sin automatización | Alta — error humano es inevitable |
| DT-006 | Sin control de versiones de perfiles y configuraciones LXD | Falta de proceso | Alta — cualquier cambio es irreversible sin historial |
| DT-007 | Pool ZFS de 315 GB insuficiente para InfraFileRoom | Subestimación de capacidad | Crítica — bloquea migración de InfraFileRoom |
| DT-008 | Sin DNS para contenedores | No discutido | Alta — sin DNS no hay microservicios reales |
| DT-009 | Imágenes de contenedores con paquetes desactualizados | Sin política de actualización | Media — acumulación de vulnerabilidades |
| DT-010 | Sin gestión de secretos | No discutido | Alta — cualquier credencial en cloud-init es texto plano visible |

---

## 13. Preguntas que nadie hizo

Esta sección contiene las preguntas más importantes que no aparecieron en la reunión inicial. Un consultor externo las haría en la primera sesión.

### Sobre la base de datos del cluster

**¿Qué sucede con la base de datos Dqlite si PFR1 falla antes de agregar más nodos?**
El estado del cluster (qué contenedores existen, sus configuraciones, perfiles) existe únicamente en PFR1. Si PFR1 falla antes de que CAR1 esté en el cluster, ¿puede recuperarse el estado del cluster? ¿O hay que reconfigurarlo desde cero?

**¿Hay snapshots automáticos de la base de datos Dqlite?**
LXD soporta esto. ¿Está habilitado?

### Sobre la migración de InfraFileRoom

**¿Cuánto tiempo llevará la migración de 800 GB de datos?**
Migrar 800 GB entre sistemas sin downtime es una operación delicada que requiere planificación específica. ¿Cuántas horas puede estar InfraFileRoom inaccesible? ¿Existe un plan de migración cero-downtime?

**¿Qué versión de la aplicación InfraFileRoom corre en CentOS 7?**
¿Es compatible con Ubuntu 24.04? ¿Tiene dependencias del sistema operativo específicas de CentOS?

**¿Quién valida que InfraFileRoom funciona correctamente en el nuevo contenedor antes de dar de baja el CentOS 7?**

### Sobre otros servicios en CentOS 7

**¿Cuántos otros servicios corren en CentOS 7 además de InfraFileRoom?**
La reunión solo mencionó InfraFileRoom, pero el documento de contexto menciona "servidores corriendo CentOS 7" en plural. ¿Cuántos son? ¿Cuál es el inventario completo?

### Sobre los límites de recursos

**¿Tienen los contenedores límites de CPU y RAM?**
Sin límites de recursos (`limits.cpu`, `limits.memory` en LXD), un contenedor puede consumir todos los recursos del nodo y afectar a todos los demás contenedores. Esto no fue discutido.

**¿Cuáles son las especificaciones de las VMs (RAM, CPU)?**
No hay documentación de las especificaciones de PFR1. ¿Cuánta RAM tiene? ¿Cuántos CPUs? ¿Cuántos contenedores caben razonablemente?

### Sobre el ciclo de vida de los contenedores

**¿Cómo se actualiza una imagen de contenedor en producción?**
Modificar el perfil y recrear el contenedor implica downtime. Para servicios críticos, ¿cuál es el proceso de actualización sin downtime?

**¿Cómo se manejan las actualizaciones de seguridad del OS dentro de los contenedores?**
`unattended-upgrades` dentro de los contenedores, o actualización manual, o recreación periódica de contenedores con imágenes actualizadas — ninguna estrategia fue discutida.

### Sobre seguridad

**¿Quién tiene acceso SSH a las VMs? ¿Con qué credenciales?**
Esta pregunta es más importante que la autenticación de la Web UI. SSH a la VM es acceso root efectivo.

**¿Cómo se rotan las credenciales del grupo `lxd`?**
Si un operador es removido, ¿se revoca su certificado TLS en LXD? ¿Se remueve de todos los nodos?

**¿Qué pasa si se filtran los tokens de primer acceso?**
Los tokens de LXD tienen tiempo de expiración, pero ¿cuánto? ¿Cómo se invalidan tokens comprometidos?

### Sobre dependencias externas

**¿Cuál es el SLA de SBA/AIT para responder solicitudes?**
Si el pool ZFS se llena y se necesita ampliar el disco urgentemente, ¿en cuánto tiempo responde SBA/AIT?

**¿Qué pasa si Cristian (VMware) no está disponible durante semanas?**
La habilitación de VLAN 411 — y por tanto OVN — depende de una sola persona. No hay plan de contingencia documentado.

**¿El equipo de seguridad (Nicolás) puede deshabilitar el proxy HTTP unilateralmente?**
La conversación en la reunión sugiere que el proxy fue habilitado sin especificar duración. Si Nicolás lo deshabilita, todos los contenedores pierden acceso a internet inmediatamente.

### Sobre multi-tenancy

**¿El cluster hosteará servicios de distintas áreas de la organización?**
Si múltiples equipos usan el mismo cluster, ¿cómo se aíslan sus contenedores? ¿Hay cuotas de recursos por equipo? ¿Hay segmentación de red entre aplicaciones de distintos equipos?

### Sobre compliance y auditoría

**¿Existen requisitos de compliance que apliquen a los servicios que se migrarán?**
Si InfraFileRoom maneja datos sensibles, puede haber requisitos de cifrado en reposo, logs de auditoría, o certificaciones que afecten el diseño.

---

## 14. Comparación con buenas prácticas de industria

### 14.1 LXD / Canonical

| Práctica recomendada | Estado en el proyecto |
|---|---|
| Mínimo 3 nodos para producción (quórum) | ⚠️ Diseñado para 3, actualmente 1 |
| Separar red de gestión de red de datos | ⚠️ En progreso (VLAN 411 pendiente) |
| ZFS como driver de storage | ✅ Implementado |
| Snapshots automáticos de contenedores | ❌ No configurados |
| Límites de recursos por contenedor | ❌ No configurados |
| TLS para todas las comunicaciones | ✅ Implementado |

**Fuente:** Documentación oficial de Canonical LXD y best practices de Canonical

### 14.2 Site Reliability Engineering (Google SRE)

| Práctica SRE | Estado en el proyecto |
|---|---|
| SLOs definidos para cada servicio | ❌ No existen |
| Error budgets | ❌ No existen |
| Runbooks documentados para cada falla conocida | ⚠️ Troubleshooting básico, sin runbooks completos |
| Postmortems sin culpa | ❌ No hay proceso |
| Automatización de operaciones repetitivas | ❌ Todo manual |
| Alertas basadas en síntomas, no causas | ❌ Sin alertas |
| Pruebas de disaster recovery | ❌ No planificadas |

**Fuente:** "Site Reliability Engineering" (Google, Beyer et al., O'Reilly)

### 14.3 Infraestructura Empresarial

| Práctica | Estado en el proyecto |
|---|---|
| Infrastructure as Code (IaC) | ❌ No existe |
| Control de versiones para configuración | ❌ No existe |
| Separación de entornos (dev/staging/prod) | ❌ No existe |
| Change management process | ❌ No existe |
| CMDB o inventario de activos | ❌ No existe |
| Gestión de identidades centralizada | ❌ No existe |
| Least privilege para todos los accesos | ⚠️ Parcialmente (lxd group documentado como riesgo) |

### 14.4 Cloud Native Computing Foundation (CNCF)

| Práctica | Estado en el proyecto |
|---|---|
| Contenedores inmutables | ⚠️ Parcialmente (cloud-init, pero pueden modificarse en runtime) |
| Configuración declarativa | ⚠️ Perfiles LXD son declarativos, pero sin versionado |
| Observabilidad (logs, métricas, trazas) | ❌ Incompleta |
| Health checks automáticos | ❌ No configurados |
| Service discovery | ❌ Sin DNS para contenedores |
| Gestión de secretos | ❌ No existe |

---

## 15. Recomendaciones por prioridad

### Crítico — Debe completarse antes de entrar a producción

| # | Recomendación | Por qué es crítica |
|---|---|---|
| C-01 | **Agregar CAR1 y FDO1 al cluster antes de cualquier despliegue productivo** | Con 1 nodo, no hay HA real. Una falla = pérdida total del servicio. |
| C-02 | **Habilitar VLAN 411 y validar OVN funcionando con tráfico real entre sitios** | Sin OVN, los contenedores no pueden comunicarse entre sitios. La HA entre sitios es imposible. |
| C-03 | **Solicitar y confirmar backup de VMs a SBA/AIT antes de mover servicios productivos** | Sin backup validado, una falla de disco = pérdida permanente de datos. |
| C-04 | **Ampliar el pool ZFS de PFR1 a 1 TB o más antes de migrar InfraFileRoom** | 315 GB no alcanza para 800 GB de datos. La migración es imposible en el estado actual. |
| C-05 | **Definir y documentar RTO/RPO para cada servicio a migrar** | Sin RTO/RPO, no hay forma de saber si el sistema cumple los requisitos del negocio. |
| C-06 | **Implementar límites de recursos por contenedor (`limits.cpu`, `limits.memory`)** | Sin límites, un contenedor puede tumbar el nodo completo afectando todos los servicios. |
| C-07 | **Establecer proceso de acceso SSH a VMs con documentación de quién tiene acceso** | El acceso SSH es el vector de ataque más crítico y más ignorado. |

### Alto — Debe completarse en las primeras semanas de operación

| # | Recomendación | Por qué es importante |
|---|---|---|
| A-01 | **Implementar DNS para contenedores** (vía OVN integrado o CoreDNS) | Sin DNS, los microservicios no pueden comunicarse de forma confiable. Las IPs cambian. |
| A-02 | **Configurar snapshots automáticos de contenedores** (`lxc config set CONTENEDOR snapshots.schedule`) | Los snapshots son la primera línea de defensa ante errores humanos. |
| A-03 | **Implementar scrubs ZFS semanales** y alertar sobre su resultado | La integridad de datos no se detecta sin scrubs activos. |
| A-04 | **Configurar alertas de capacidad del pool ZFS** (alertar al 70% y 85%) | Sin alertas, el llenado del pool ocurre de forma sorpresiva. |
| A-05 | **Implementar Prometheus + Grafana con alertas básicas** (nodo offline, pool lleno, contenedor caído) | Sin observabilidad, los problemas se descubren cuando ya impactan a usuarios. |
| A-06 | **Documentar y ejecutar al menos un simulacro de DR** (apagar PFR1 y verificar procedimiento de recuperación) | El DR no probado es una hipótesis, no un plan. |
| A-07 | **Establecer proceso de revocación de acceso** (TLS + firewall + SSH + lxd group) | Sin proceso, los ex-operadores retienen acceso indefinidamente. |
| A-08 | **Reemplazar firewall por IP con acceso VPN** | Las reglas por IP personal son frágiles y no escalan. |
| A-09 | **Documentar inventario de servicios CentOS 7** a migrar con sus dependencias y requisitos de compatibilidad | No se puede planificar la migración sin conocer el alcance completo. |
| A-10 | **Configurar log aggregation centralizada** (Loki, Elasticsearch, o equivalente) | Diagnosticar problemas distribuidos sin logs centralizados puede tomar horas. |

### Medio — Mejoras recomendables a mediano plazo

| # | Recomendación |
|---|---|
| M-01 | Implementar Infrastructure as Code (Ansible para configuración de nodos, cloud-init templates en git) |
| M-02 | Establecer entorno de staging (al menos un nodo de testing separado) |
| M-03 | Implementar gestión de secretos (HashiCorp Vault o equivalente) |
| M-04 | Establecer política de actualización de imágenes base de contenedores |
| M-05 | Documentar plan de capacidad a 12 meses (nodos, storage, contenedores) |
| M-06 | Implementar health checks automáticos para servicios dentro de contenedores |
| M-07 | Evaluar segundo nodo por sitio para redundancia intra-sitio |
| M-08 | Establecer CMDB o inventario de activos actualizado (qué contenedor corre qué servicio, dónde, con qué recursos) |
| M-09 | Implementar certificados TLS firmados por CA interna (en lugar de auto-firmados) |
| M-10 | Definir SLOs para los servicios migrados (disponibilidad, latencia, RPO/RTO) |

### Bajo — Optimizaciones futuras

| # | Recomendación |
|---|---|
| B-01 | Evaluar replicación de storage cross-site (ZFS send/receive, o Ceph) |
| B-02 | Implementar automatización de despliegues (CI/CD para crear/actualizar contenedores) |
| B-03 | Evaluar container image scanning para detectar vulnerabilidades |
| B-04 | Evaluar runtime security (Falco u equivalente) |
| B-05 | Documentar arquitectura de red OVN completa una vez estabilizada |
| B-06 | Evaluar estrategia de multi-tenancy si el cluster crece a múltiples equipos |
| B-07 | Establecer un proceso formal de postmortems para incidentes |

---

## Conclusión

El equipo realizó una instalación técnicamente correcta del primer nodo LXD y produjo documentación de calidad sobre lo implementado. Eso es positivo y no debe subestimarse.

Sin embargo, la distancia entre "primer nodo instalado" y "plataforma de producción con alta disponibilidad" es significativa. Los riesgos más críticos son:

1. **La falta de HA real:** un solo nodo activo significa que cualquier falla es un outage total.
2. **OVN no funcional:** el requisito técnico central del sistema no existe aún.
3. **Sin plan de DR probado:** no se sabe cómo recuperar nada si algo falla.
4. **Capacidad insuficiente para InfraFileRoom:** 315 GB vs 800 GB es un bloqueador técnico.
5. **Dependencias externas sin SLA:** Cristian, Nicolás y SBA/AIT son SPOFs organizacionales.

La recomendación es: **no migrar ningún servicio productivo hasta completar al menos los ítems Críticos (C-01 a C-07)** de la sección de recomendaciones.

---

## Referencias

| Documento | Relevancia |
|---|---|
| [02_Arquitectura.md](02_Arquitectura.md) | Base para el análisis de arquitectura |
| [11_Riesgos.md](11_Riesgos.md) | Riesgos previamente identificados (complementados aquí) |
| [13_Linea_de_Tiempo.md](13_Linea_de_Tiempo.md) | Hitos pendientes que afectan esta revisión |
| [10_Decisiones.md](10_Decisiones.md) | Decisiones de arquitectura evaluadas |
| [adr/ADR-0002-red-ovn-vs-ubuntu-fan.md](adr/ADR-0002-red-ovn-vs-ubuntu-fan.md) | Decisión de red con sus consecuencias |
