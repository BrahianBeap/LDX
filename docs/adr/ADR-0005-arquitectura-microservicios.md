# ADR-0005 — Arquitectura de contenedores: un servicio por contenedor

| Campo | Valor |
|---|---|
| **Número** | ADR-0005 |
| **Fecha** | 2026-06-25 |
| **Estado** | Aceptado |
| **Autores** | Norberto Núñez |
| **Revisores** | Marcos Casco, Elías Alfonzo |
| **Reunión origen** | `reunion/Llamada con Daniel y 3 personas más.vtt` |

---

## Contexto

Históricamente, los servicios del equipo corrían en servidores (VMs) monolíticos: un servidor = Apache + PHP + base de datos + otros servicios. Al migrar a LXD, hay que decidir cómo estructurar los contenedores.

LXD soporta contenedores de sistema completo, lo que técnicamente permite hospedar múltiples servicios en un único contenedor.

---

## Problema

¿Se deben hospedar múltiples servicios en un mismo contenedor LXD, o usar un contenedor por servicio?

---

## Alternativas evaluadas

### Opción A — Un servicio por contenedor (microservicios)

**Descripción:**
Cada servicio (Apache/PHP, base de datos, caché, etc.) corre en su propio contenedor dedicado. Los servicios se comunican entre sí a través de la red OVN.

**Ventajas:**
- **Aislamiento de fallas:** si la base de datos tiene un problema, el servidor web sigue respondiendo.
- **Actualización independiente:** actualizar PHP no requiere reiniciar la base de datos.
- **Diagnóstico más simple:** los problemas son atribuibles a un componente específico.
- **Escalabilidad granular:** se puede agregar más instancias del servicio que lo necesita, sin duplicar todo el stack.
- **Portabilidad:** un contenedor-servicio puede moverse entre nodos sin impactar otros servicios.

**Desventajas:**
- Requiere configuración de red entre contenedores (OVN).
- Más contenedores para gestionar.
- La latencia entre servicios en contenedores distintos es mayor que en localhost.

---

### Opción B — Stack completo por contenedor

**Descripción:**
Un contenedor contiene Apache + PHP + base de datos + todos los servicios necesarios para una aplicación.

**Ventajas:**
- Simplicidad inicial: todo en un lugar.
- Comunicación entre servicios via localhost (sin latencia de red).

**Desventajas:**
- Reproduce el modelo monolítico que se está intentando superar.
- Actualizar cualquier componente puede requerir detener todo el stack.
- Fallas de un componente pueden afectar a todos los demás en el mismo contenedor.
- Sin aislamiento de recursos por servicio.

---

## Decisión

**Se elige: Opción A — Un servicio por contenedor.**

---

## Justificación

Norberto Núñez lo expresó explícitamente en la reunión:

> "Vamos a tratar de mantener esta metodología: tener contenedores separados para las bases de datos y contenedores separados para los frontends. [...] Eso te da maniobrabilidad: si vos tenés que hacer algo con tu frontend, cambiar algo acá, cambiar la versión de PHP, no tenés que reinstalar todo — tu base de datos se mantiene ahí separadita sola."

La arquitectura de microservicios es la razón de ser de adoptar LXD. Reproducir el modelo monolítico dentro de los contenedores elimina la mayoría de los beneficios del sistema.

---

## Consecuencias

### Positivas
- Fallas aisladas por servicio.
- Actualizaciones independientes de cada componente.
- Fundamento para escalar horizontalmente en el futuro.
- Diagnóstico de problemas más preciso.

### Negativas / Compromisos aceptados
- La red OVN es prerequisito para la comunicación entre contenedores de distintos nodos. Mientras OVN no esté operativo, los contenedores de un mismo nodo pueden comunicarse entre sí, pero no entre sitios.
- Gestionar múltiples contenedores requiere más disciplina operativa (naming conventions, documentación, monitoreo).

### Riesgos
- Sin OVN, los servicios solo pueden comunicarse si están en el mismo nodo. Esto es una limitación temporal que se resuelve con la habilitación de VLAN 411. Ver [11_Riesgos.md — RIE-001](../11_Riesgos.md).

---

## Pendientes de seguimiento

- [ ] Definir la topología de contenedores para InfraFileRoom (¿cuántos contenedores? ¿qué servicios?).
- [ ] Establecer convención de nombres para contenedores por servicio y aplicación.
- [ ] Documentar cómo los servicios en distintos contenedores se descubren entre sí en OVN.

---

## Referencias

- [02_Arquitectura.md](../02_Arquitectura.md)
- [09_FAQ.md — ¿Puedo tener múltiples servicios en un contenedor?](../09_FAQ.md)
- [12_Lecciones_Aprendidas.md — LL-006](../12_Lecciones_Aprendidas.md)
