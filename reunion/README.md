# reunion/

Esta carpeta contiene las transcripciones y grabaciones de reuniones técnicas del proyecto LDX.

---

## ¿Qué va aquí?

- Archivos `.vtt` de transcripciones automáticas (grabaciones de videollamadas)
- Archivos `.txt` o `.md` con notas o minutas de reuniones
- Cualquier material de referencia producido durante una reunión

---

## Convención de nombres

```
YYYY-MM-DD_descripcion-breve.vtt
YYYY-MM-DD_descripcion-breve.md
```

**Ejemplos:**

```
2026-06-25_arquitectura-inicial-ldx.vtt
2026-07-10_revision-instalacion-nodos.vtt
2026-08-01_post-mortem-incidente-produccion.md
```

Usar guiones medios (`-`) en lugar de espacios. Evitar caracteres especiales.

---

## Qué hacer después de colocar un archivo aquí

1. Usar la plantilla de análisis en [`recursos/prompt_analisis_reunion.md`](../recursos/prompt_analisis_reunion.md).
2. Analizar completamente la reunión siguiendo las fases definidas en [`CLAUDE.md`](../CLAUDE.md).
3. Los documentos generados se incorporan a [`docs/`](../docs/).
4. Las decisiones técnicas importantes generan un nuevo ADR en [`docs/adr/`](../docs/adr/).
5. Registrar el cambio en [`CHANGELOG.md`](../CHANGELOG.md).

---

## Reuniones disponibles

| Archivo | Fecha | Participantes | Estado |
|---|---|---|---|
| `Llamada con Daniel y 3 personas más.vtt` | ✅ 2026-06-25 (confirmada por nombre de archivo de la grabación: `...-20260625_105957-...`) | Norberto Núñez, Marcos Casco, Daniel Medina, Elías Alfonzo, Rocío Duarte | ✅ Analizada — documentación en [`docs/`](../docs/). Grabación (`.mp4`) revisada visualmente además de la transcripción — ver notas "obtenido visualmente del video" en [`04_Instalacion.md`](../docs/04_Instalacion.md) y [`05_Configuracion.md`](../docs/05_Configuracion.md) |
| `segunda_reunion LXD _ Implementacion.vtt` | 🔴 Pendiente de validación | Norberto Núñez, Marcos Casco, Elías Alfonzo, Rocío Duarte, Daniel Medina, Andrés Semidei, Fernando Fleitas | ✅ Analizada — documentación en [`docs/`](../docs/) |
| `2026-10_llamada-abel-balanceadores-ntf-loki.vtt` | 🟡 Sin fecha exacta confirmada (archivo recibido el 2026-10-09; el contenido es anterior a la migración de Kanboard del 2026-10-08, a juzgar por lo que se explica) | Norberto Núñez, Elías Alfonzo, Marcos Casco (participantes identificados en la transcripción interviniendo sobre temas de LXD; puede haber más sin intervención registrada). Una llamada superpuesta sobre un corte de energía en terreno (minutos ~4-22 aprox.) involucra además a Julio y otro personal de campo, sin relación con LXD | ✅ Analizada completa (Fases 1-4) — la parte de LXD (diseño de FQDN/balanceadores, mecanismo de `LB.conf`, backend real de Loki, idea de monitorear balanceadores con Loki, acceso temporal del escáner de vulnerabilidades) está documentada en [02_Arquitectura.md](../docs/02_Arquitectura.md#nombre-de-dominio-compartido-entre-sitios-fqdn--dns-round-robin), [ADR-0008](../docs/adr/ADR-0008-gateway-balanceador-dos-etapas.md#actualización--migración-de-kanboard-2026-10-08), [14_Manual_Operativo.md](../docs/14_Manual_Operativo.md#logs-de-aplicación-loki--minio-propio-del-proyecto), [05_Configuracion.md](../docs/05_Configuracion.md#buckets-de-almacenamiento-s3-backend-de-lokimimir), [11_Riesgos.md](../docs/11_Riesgos.md#rie-016--acceso-temporal-del-escáner-de-vulnerabilidades-por-lista-de-ips-sin-fecha-de-retiro) y [13_Linea_de_Tiempo.md](../docs/13_Linea_de_Tiempo.md). La llamada superpuesta sobre el corte de energía en terreno se descartó a propósito, por no ser contenido de LXD |
| `2026-10-16_llamada-marcos-norberto-inventario-dns-certificado.vtt` (original: `Llamada con Marcos y 1 persona más.vtt`) | 🟡 Recibida el 2026-10-16; fecha exacta de la llamada sin confirmar | Norberto Núñez, Marcos Casco, Elías Alfonzo | ✅ Analizada completa (Fases 1-4) — inventario por IP de servicio + URL en [06_Operacion.md](../docs/06_Operacion.md#inventario-hacia-ciberseguridad-jerure-ip-de-servicio--puerto--url); DNS con nombres por sitio en [ADR-0009](../docs/adr/ADR-0009-dns-fqdn-compartido-y-nombres-por-sitio.md); procedimiento `lxc file`/`lxc exec -n` en [05_Configuracion.md](../docs/05_Configuracion.md#procedimiento-estándar-para-operar-contenedores-norberto-núñez-2026-10-16); correo entrante y OSRM en [13_Linea_de_Tiempo.md](../docs/13_Linea_de_Tiempo.md). La charla sobre consumo de tokens de IA (min. ~40-44) se descartó por no ser contenido de LXD. 🔴 El `.vtt` todavía no fue copiado a esta carpeta |
| `2026-10-24_llamada-daniel-norberto-recursos-s3-certificado-ntf.vtt` (original: `Llamada con Daniel y 2 personas más.vtt`) | 🟡 Recibida el 2026-10-24; fecha exacta sin confirmar (posterior al pedido del certificado, #1078719 del 2026-10-16) | Norberto Núñez, Marcos Casco, Elías Alfonzo, Daniel Medina | ✅ Analizada completa (Fases 1-4) — coordinación del certificado con Tembiapó en [RIE-019](../docs/11_Riesgos.md#rie-019--certificados-tls-no-confiables-y-configuración-tls-heredada-en-gateways-y-hosts); Infrawork/ADM-TECH, FileRoom, bases centralizadas y S3 en [13_Linea_de_Tiempo.md](../docs/13_Linea_de_Tiempo.md); confirmación del proxy interno en [ADR-0009](../docs/adr/ADR-0009-dns-fqdn-compartido-y-nombres-por-sitio.md). La mención de un tercero que no quiere inventariar su aplicación se dejó fuera por no ser una acción del equipo. 🔴 El `.vtt` todavía no fue copiado a esta carpeta |
