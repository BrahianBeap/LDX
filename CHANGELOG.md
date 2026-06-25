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

### 2026-06-25

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
Inicialización del repositorio LDX como base de conocimiento técnica oficial.
Se estableció la estructura de carpetas, las convenciones de documentación y los primeros archivos de configuración.

Los archivos originales en formato `.txt` fueron refactorizados a `.md` y reorganizados según sus responsabilidades:
- `README.md` cubre la orientación humana: qué es el repo, su estructura, flujo de trabajo y principios.
- `CLAUDE.md` cubre las instrucciones para el asistente IA: estándares de documentación, clasificación de información y proceso de análisis de reuniones.

La duplicación existente entre ambos archivos fue eliminada distribuyendo el contenido según la audiencia de cada documento.

Se incorporó `docs/adr/` para registrar decisiones de arquitectura siguiendo el estándar ADR (Michael Nygard).
Se incorporó `laboratorio/` como área de staging para experimentos antes de incorporarlos a `docs/`.
