# ADR-0007 — Proyectos LXD como modelo de aislamiento multi-tenant

| Campo | Valor |
|---|---|
| **Número** | ADR-0007 |
| **Fecha** | 2026-07-24 |
| **Estado** | Aceptado |
| **Autores** | Norberto Núñez |
| **Revisores** | Marcos Casco, equipo técnico |
| **Reunión origen** | `reunion/segunda_reunion LXD _ Implementacion.vtt` |

---

## Contexto

Hasta este punto, todos los contenedores del cluster se crearon en el **proyecto `default`** de LXD — el espacio de nombres único que LXD provee de fábrica, sin límites de recursos ni separación de acceso entre usuarios.

El cluster fue concebido desde el inicio como una plataforma compartida: distintas áreas de la organización (el equipo actual, y a futuro posibles equipos como CCR, OMC o el área de transporte/AIT) van a necesitar desplegar sus propias cargas de trabajo sobre la misma infraestructura física, incluyendo migraciones futuras de sistemas EOL propios de esas áreas (mencionado como ejemplo: migración de VMs de NMS).

Sin un mecanismo de aislamiento:
- Cualquier usuario con acceso al grupo `lxd` puede ver y modificar **todos** los contenedores del cluster, sin importar de qué equipo son.
- No hay forma de limitar cuántos recursos (CPU, RAM, disco, cantidad de instancias) puede consumir un equipo dentro del total disponible del cluster.
- Un error o un uso descontrolado de un equipo puede agotar recursos que otros equipos necesitan.

---

## Problema

¿Cómo dar a distintos equipos acceso a la infraestructura compartida del cluster LXD sin que puedan ver o afectar los recursos de los demás equipos, y sin que un equipo pueda consumir más recursos de los que le corresponden?

---

## Alternativas evaluadas

### Opción A — Proyecto `default` único para todos los equipos

**Descripción:**
Continuar creando todos los contenedores, perfiles y redes en el proyecto `default`, sin segmentación adicional.

**Ventajas:**
- Es el comportamiento de fábrica de LXD, no requiere configuración adicional.
- Más simple de operar mientras el equipo es pequeño.

**Desventajas:**
- **No es multi-tenant.** Cualquier usuario con acceso ve y puede modificar los recursos de todos los demás.
- Sin límites de recursos por equipo: un equipo puede consumir toda la capacidad del cluster sin restricción.
- No escala organizacionalmente: agregar un nuevo equipo implica mezclar sus recursos con los de los equipos existentes.

---

### Opción B — Proyectos LXD (`lxc project`) con límites y grupos de acceso

**Descripción:**
LXD permite crear **proyectos** adicionales al `default`. Cada proyecto es un espacio de nombres separado con su propia lista de contenedores, perfiles y (opcionalmente) redes. Sobre cada proyecto se pueden definir:

- **Límites de recursos:** cantidad máxima de redes, CPUs totales, memoria, instancias, contenedores y VMs que ese proyecto puede consumir, independientemente de cuántos nodos tenga el cluster.
- **Grupos de identidad:** un grupo de usuarios (ej. `core`) puede restringirse para que solo tenga acceso al proyecto correspondiente (ej. `PRJ-Core`). Los usuarios de ese grupo ven únicamente los recursos de su proyecto — no ven el proyecto `default` ni los proyectos de otros equipos.

**Ventajas:**
- Aislamiento real de visibilidad y de acceso entre equipos.
- Límites de recursos configurables por proyecto, evitando que un equipo agote la capacidad compartida.
- Es una funcionalidad nativa de LXD — no requiere herramientas externas ni licenciamiento adicional.
- Permite incorporar nuevos equipos (identidades nuevas) sin reestructurar el cluster: se crea un proyecto nuevo, se define su perfil y límites, y se asocia un grupo de acceso.

**Desventajas:**
- Overhead administrativo: cada proyecto nuevo requiere crear su propio perfil, su propio contenedor gateway de servicios (ver [02_Arquitectura.md](../02_Arquitectura.md)) y definir explícitamente sus límites.
- Los límites deben ser definidos y acordados caso por caso — LXD no impone una política de tamaño por defecto.

---

## Decisión

**Se elige: Opción B — Proyectos LXD, con límites de recursos y grupos de acceso por equipo.**

A partir de esta reunión, se adopta como práctica estándar del equipo:

1. Todo trabajo nuevo de un equipo/área se hace en un **proyecto dedicado** (no en `default`), con nomenclatura `PRJ-<código de área>` (ejemplo usado en la demostración: proyecto del propio equipo, con perfil `presidente-franco-ss-gw` para su contenedor gateway de servicios).
2. Cada proyecto define explícitamente sus límites: cantidad de redes accesibles, CPU, memoria, cantidad de instancias, cantidad de contenedores y cantidad de VMs.
3. Se crea un **grupo de identidad** por proyecto (ejemplo: grupo `core`) y se le restringe el acceso exclusivamente a su proyecto correspondiente.

---

## Justificación

Los proyectos LXD son la única alternativa evaluada que resuelve simultáneamente los dos problemas planteados: aislamiento de visibilidad/acceso y control de consumo de recursos, sin dependencias externas ni cambios de arquitectura del cluster. Es, además, la forma en que LXD está diseñado para operar como plataforma multi-tenant, por lo que adoptarlo desde ahora evita una migración costosa más adelante cuando se sumen más equipos.

---

## Consecuencias

### Positivas
- La plataforma queda preparada para recibir nuevos equipos (multi-tenancy) sin rediseño.
- Un equipo no puede, ni por error ni por uso intensivo, agotar los recursos disponibles para los demás.
- Los equipos nuevos solo ven sus propios recursos — reduce superficie de error humano y mejora la seguridad operativa.

### Negativas / Compromisos aceptados
- Cada proyecto nuevo agrega trabajo de configuración (perfil, contenedor gateway de servicios, límites, grupo de acceso).
- Requiere que el equipo de plataforma defina explícitamente los límites de cada proyecto nuevo; no hay un valor por defecto seguro.

### Riesgos
- 🔴 **Pendiente de validación:** no existe todavía una política escrita de límites "estándar" por tamaño de equipo/proyecto — los límites se definieron ad-hoc para el primer proyecto de ejemplo durante la reunión.
- Si se crea un proyecto sin definir límites explícitos, hereda el comportamiento sin restricciones (mismo riesgo que la Opción A) — debe ser una verificación obligatoria al dar de alta un proyecto nuevo.

---

## Pendientes de seguimiento

- [ ] Definir una política estándar (o rangos recomendados) de límites de recursos por proyecto, en lugar de valores ad-hoc por reunión.
- [ ] Documentar el procedimiento completo de alta de un proyecto nuevo (perfil, contenedor gateway de servicios, límites, grupo) como parte de [06_Operacion.md](../06_Operacion.md).
- [ ] Evaluar si los proyectos deben tener redes OVN propias y separadas, o compartir la red OVN del proyecto `default` con aislamiento a nivel de dispositivo.

---

## Referencias

- [02_Arquitectura.md — Modelo de multi-tenancy](../02_Arquitectura.md)
- [05_Configuracion.md — Proyectos LXD](../05_Configuracion.md)
- [10_Decisiones.md](../10_Decisiones.md)
- Reunión origen: `reunion/segunda_reunion LXD _ Implementacion.vtt`
