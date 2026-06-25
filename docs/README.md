# docs/ — Documentación técnica oficial de LDX

Este directorio contiene la documentación técnica oficial del proyecto LDX.

> **Estado actual:** Pendiente del análisis de la primera reunión. Los documentos se generarán tras procesar [`reunion/Llamada con Daniel y 3 personas más.vtt`](../reunion/).

---

## Índice de documentos

| N° | Documento | Descripción | Estado |
|---|---|---|---|
| 00 | `00_Resumen_Ejecutivo.md` | Qué es LDX, qué problema resuelve, objetivos y alcance | Pendiente |
| 01 | `01_Contexto.md` | Contexto del negocio, necesidad cubierta, beneficios | Pendiente |
| 02 | `02_Arquitectura.md` | Arquitectura completa, diagramas, componentes y flujo | Pendiente |
| 03 | `03_Componentes.md` | Descripción detallada de cada componente del sistema | Pendiente |
| 04 | `04_Instalacion.md` | Procedimiento completo de instalación paso a paso | Pendiente |
| 05 | `05_Configuracion.md` | Parámetros, archivos de configuración y buenas prácticas | Pendiente |
| 06 | `06_Operacion.md` | Cómo operar el sistema en producción | Pendiente |
| 07 | `07_Troubleshooting.md` | Problemas frecuentes, diagnóstico y soluciones | Pendiente |
| 08 | `08_Glosario.md` | Diccionario de términos técnicos del proyecto | Pendiente |
| 09 | `09_FAQ.md` | Preguntas frecuentes | Pendiente |
| 10 | `10_Decisiones.md` | Resumen ejecutivo de decisiones técnicas (ver también `adr/`) | Pendiente |
| 11 | `11_Riesgos.md` | Riesgos técnicos, operativos y de seguridad identificados | Pendiente |
| 12 | `12_Lecciones_Aprendidas.md` | Conocimiento tácito extraído de reuniones y experiencia | Pendiente |
| 13 | `13_Linea_de_Tiempo.md` | Cronología del proyecto y sus hitos | Pendiente |
| 14 | `14_Manual_Operativo.md` | Procedimientos operativos, monitoreo y escalamiento | Pendiente |

---

## Decisiones de arquitectura (ADR)

Las decisiones técnicas importantes se documentan como Architecture Decision Records en:

```
docs/adr/
```

| Archivo | Decisión | Estado |
|---|---|---|
| [`ADR-0001-template.md`](adr/ADR-0001-template.md) | Plantilla base | Plantilla |

---

## Convenciones

- Cada documento tiene **una única responsabilidad**. No mezclar temas.
- No duplicar información entre documentos. Usar enlaces relativos.
- Cada afirmación debe clasificarse como ✅ confirmada, 🟡 inferencia o 🔴 pendiente de validación.
- Ver [`CLAUDE.md`](../CLAUDE.md) para los estándares completos de documentación.
- Registrar todo cambio importante en [`CHANGELOG.md`](../CHANGELOG.md).
