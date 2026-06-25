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
| `Llamada con Daniel y 3 personas más.vtt` | 🔴 Pendiente de validación | Norberto Núñez, Marcos Casco, Daniel Medina, Elías Alfonzo, Rocío Duarte | ✅ Analizada — documentación en [`docs/`](../docs/) |
