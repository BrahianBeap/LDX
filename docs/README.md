# docs/ — Documentación técnica oficial de LXD

Este directorio contiene la documentación técnica oficial del proyecto LXD.

> **Fuente:** Los documentos 00–14 se generaron a partir de [`reunion/Llamada con Daniel y 3 personas más.vtt`](../reunion/) (primera reunión) y se actualizaron con [`reunion/segunda_reunion LXD _ Implementacion.vtt`](../reunion/) (segunda reunión — WireGuard/OVN multisitio, proyectos LXD multi-tenant, incorporación de CAR1 al cluster). Los documentos 15 y 16 son informes de análisis independiente.

---

## Índice de documentos

| N° | Documento | Descripción | Estado |
|---|---|---|---|
| 00 | [`00_Resumen_Ejecutivo.md`](00_Resumen_Ejecutivo.md) | Qué es LXD, qué problema resuelve, objetivos y alcance | ✅ Completo |
| 01 | [`01_Contexto.md`](01_Contexto.md) | Contexto del negocio, necesidad cubierta, equipos involucrados | ✅ Completo |
| 02 | [`02_Arquitectura.md`](02_Arquitectura.md) | Arquitectura completa, diagramas, redes, almacenamiento | ✅ Completo |
| 03 | [`03_Componentes.md`](03_Componentes.md) | Descripción detallada de cada componente del sistema | ✅ Completo |
| 04 | [`04_Instalacion.md`](04_Instalacion.md) | Procedimiento completo de instalación paso a paso | ✅ Completo |
| 05 | [`05_Configuracion.md`](05_Configuracion.md) | Proxy, cloud-init, perfiles, dispositivos, firewall | ✅ Completo |
| 06 | [`06_Operacion.md`](06_Operacion.md) | Gestión de contenedores, imágenes, perfiles, backup | ✅ Completo |
| 07 | [`07_Troubleshooting.md`](07_Troubleshooting.md) | Problemas frecuentes, diagnóstico y soluciones | ✅ Completo |
| 08 | [`08_Glosario.md`](08_Glosario.md) | Diccionario completo de términos técnicos del proyecto | ✅ Completo |
| 09 | [`09_FAQ.md`](09_FAQ.md) | Preguntas frecuentes | ✅ Completo |
| 10 | [`10_Decisiones.md`](10_Decisiones.md) | Resumen ejecutivo de decisiones técnicas (ver también `adr/`) | ✅ Completo |
| 11 | [`11_Riesgos.md`](11_Riesgos.md) | Riesgos técnicos, operativos y de seguridad identificados | ✅ Completo |
| 12 | [`12_Lecciones_Aprendidas.md`](12_Lecciones_Aprendidas.md) | Conocimiento tácito extraído de la primera reunión | ✅ Completo |
| 13 | [`13_Linea_de_Tiempo.md`](13_Linea_de_Tiempo.md) | Hitos completados y próximos pasos | ✅ Completo |
| 14 | [`14_Manual_Operativo.md`](14_Manual_Operativo.md) | Checklist de salud, monitoreo, escalamiento | ✅ Completo |
| 15 | [`15_Revision_Arquitectonica.md`](15_Revision_Arquitectonica.md) | Auditoría técnica independiente — crítica, riesgos, recomendaciones priorizadas | ✅ Completo |
| 16 | [`16_Auditoria_Knowledge_Base.md`](16_Auditoria_Knowledge_Base.md) | Auditoría de calidad del KB — duplicaciones, inconsistencias, plan de mejora | ✅ Completo |

---

## Decisiones de arquitectura (ADR)

Las decisiones técnicas importantes se documentan como Architecture Decision Records en:

```
docs/adr/
```

| Archivo | Decisión | Estado |
|---|---|---|
| [`ADR-0001-template.md`](adr/ADR-0001-template.md) | Plantilla base | Plantilla |
| [`ADR-0002-red-ovn-vs-ubuntu-fan.md`](adr/ADR-0002-red-ovn-vs-ubuntu-fan.md) | Red SDN: OVN via MicroOVN elegido sobre Ubuntu Fan | Aceptado |
| [`ADR-0003-storage-zfs.md`](adr/ADR-0003-storage-zfs.md) | Storage driver: ZFS elegido sobre LVM y btrfs | Aceptado |
| [`ADR-0004-autenticacion-tls-tokens.md`](adr/ADR-0004-autenticacion-tls-tokens.md) | Autenticación Web UI: TLS tokens + certificados de navegador | Aceptado |
| [`ADR-0005-arquitectura-microservicios.md`](adr/ADR-0005-arquitectura-microservicios.md) | Arquitectura: un servicio por contenedor | Aceptado |
| [`ADR-0006-wireguard-underlay-ovn-multisitio.md`](adr/ADR-0006-wireguard-underlay-ovn-multisitio.md) | WireGuard como transporte underlay para OVN entre sitios en Capa 3 | Aceptado |
| [`ADR-0007-proyectos-lxd-multitenancy.md`](adr/ADR-0007-proyectos-lxd-multitenancy.md) | Proyectos LXD como modelo de aislamiento multi-tenant | Aceptado |

---

## Convenciones

- Cada documento tiene **una única responsabilidad**. No mezclar temas.
- No duplicar información entre documentos. Usar enlaces relativos.
- Cada afirmación debe clasificarse como ✅ confirmada, 🟡 inferencia o 🔴 pendiente de validación.
- Ver [`CLAUDE.md`](../CLAUDE.md) para los estándares completos de documentación.
- Registrar todo cambio importante en [`CHANGELOG.md`](../CHANGELOG.md).
