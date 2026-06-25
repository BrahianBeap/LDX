# ADR-0003 — Elección de driver de almacenamiento: ZFS

| Campo | Valor |
|---|---|
| **Número** | ADR-0003 |
| **Fecha** | 2026-06-25 |
| **Estado** | Aceptado |
| **Autores** | Norberto Núñez |
| **Revisores** | Marcos Casco, equipo técnico |
| **Reunión origen** | `reunion/Llamada con Daniel y 3 personas más.vtt` |

---

## Contexto

LXD necesita un driver de almacenamiento (storage pool driver) para gestionar los datos de los contenedores e imágenes. La elección del driver afecta el rendimiento, la confiabilidad, las capacidades de snapshot y la complejidad operativa.

Cada nodo del cluster tiene un disco dedicado para LXD (`/dev/sda6`, 315 GB en PFR1).

---

## Problema

¿Qué driver de almacenamiento usar para el storage pool de LXD en este entorno?

---

## Alternativas evaluadas

### Opción A — ZFS

**Descripción:**
ZFS (Zettabyte File System) es un sistema de archivos avanzado con capacidades de storage pool integradas. En LXD, cada contenedor o imagen ocupa un dataset ZFS separado.

**Ventajas:**
- Snapshots de contenedores nativos e instantáneos (copy-on-write).
- Checksums de integridad de datos — detecta y reporta corrupción automáticamente.
- Clonación rápida de contenedores desde imágenes (copy-on-write, sin copia física).
- Compresión integrada del filesystem.
- Excelente integración con LXD (es el driver recomendado por Canonical para producción).

**Desventajas:**
- Requiere un kernel con módulo ZFS (en Ubuntu está disponible via DKMS).
- La recuperación de un pool ZFS degradado es más compleja que LVM.
- Mayor uso de RAM que LVM para las funciones avanzadas.

---

### Opción B — LVM (Logical Volume Manager)

**Descripción:**
LVM gestiona volúmenes lógicos sobre discos físicos. LXD crea un volumen LVM por contenedor.

**Ventajas:**
- Ampliamente conocido y documentado.
- Menor uso de RAM.

**Desventajas:**
- Los snapshots de LVM son más lentos y tienen overhead de escritura mayor.
- No tiene checksums de integridad de datos integrados.
- La clonación de contenedores es más lenta.

---

### Opción C — btrfs

**Descripción:**
btrfs es un sistema de archivos copy-on-write similar a ZFS.

**Ventajas:**
- Snapshots nativos.
- Buena integración con LXD.

**Desventajas:**
- Históricamente considerado menos maduro y estable que ZFS en entornos de producción.
- Menor recomendación en la documentación oficial de Canonical para LXD.

---

## Decisión

**Se elige: Opción A — ZFS sobre disco dedicado (`/dev/sda6`).**

---

## Justificación

ZFS fue elegido por su mejor integración con las operaciones de LXD (snapshots instantáneos, clonación copy-on-write) y por ser el driver recomendado por Canonical para entornos de producción.

La capacidad de detección de corrupción de datos mediante checksums es especialmente valiosa en un entorno donde los contenedores hospedan servicios productivos con datos críticos (InfraFileRoom, ~800 GB).

---

## Consecuencias

### Positivas
- Snapshots y clones de contenedores prácticamente instantáneos.
- Integridad de datos verificada automáticamente.
- Rendimiento óptimo para operaciones de LXD.

### Negativas / Compromisos aceptados
- Mayor uso de RAM para el propio ZFS.
- Requiere disco dedicado y exclusivo para LXD (no compartir con el sistema operativo).

### Riesgos
- La falla del pool ZFS es un incidente crítico. Mitigación: solicitar backup de VM a SBA/AIT. Ver [11_Riesgos.md](../11_Riesgos.md) para los riesgos de almacenamiento y backup.
- El disco `/dev/sda6` (315 GB en PFR1) debe ser monitoreado para evitar llenado del pool.

---

## Pendientes de seguimiento

- [ ] Confirmar el disco dedicado y su tamaño en CAR1 y FDO1 antes de instalar.
- [ ] Configurar alertas de uso del pool ZFS en Prometheus/Grafana.
- [ ] Solicitar backup de VM a SBA/AIT antes de crear contenedores de producción.

---

## Referencias

- [03_Componentes.md — ZFS](../03_Componentes.md)
- [04_Instalacion.md — Paso 2 (lxd init)](../04_Instalacion.md)
- [11_Riesgos.md — Riesgos de almacenamiento y backup](../11_Riesgos.md)
