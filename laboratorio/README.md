# laboratorio/

Esta carpeta es el **área de staging del conocimiento técnico** del proyecto LDX.

Aquí se documentan experimentos, pruebas de concepto y validaciones antes de incorporarlos a la documentación oficial en `docs/`.

---

## ¿Qué va aquí?

- Pruebas de instalación o configuración en entornos de desarrollo
- Experimentos con tecnologías o herramientas candidatas
- Validaciones de procedimientos antes de documentarlos oficialmente
- Laboratorios de troubleshooting
- Scripts en desarrollo, sin validar en producción
- Notas de investigación técnica y análisis comparativos

---

## Diferencia entre `laboratorio/` y `docs/`

| `laboratorio/` | `docs/` |
|---|---|
| Conocimiento en validación | Conocimiento confirmado |
| Puede contener errores | Debe ser preciso y probado |
| Informal y exploratorio | Formal y estructurado |
| Puede estar incompleto | Debe ser autocontenido |
| Puede cambiar rápidamente | Cambios deben registrarse en CHANGELOG |
| No requiere todos los estándares | Debe cumplir todos los estándares de [`CLAUDE.md`](../CLAUDE.md) |

---

## Estructura sugerida para cada experimento

```
laboratorio/
└── YYYY-MM-DD_nombre-del-experimento/
    ├── README.md           ← objetivo, hipótesis, entorno y resultado
    ├── comandos.md         ← comandos utilizados con notas inline
    └── conclusiones.md     ← qué funcionó, qué no, qué aprendimos
```

**Ejemplo:**

```
laboratorio/
└── 2026-06-25_instalacion-nodo-ldx/
    ├── README.md
    ├── comandos.md
    └── conclusiones.md
```

---

## Proceso para promover a documentación oficial

Un experimento está listo para `docs/` cuando:

1. El procedimiento fue ejecutado exitosamente al menos una vez en condiciones reales.
2. El resultado es reproducible y predecible.
3. Los errores encontrados durante el experimento están documentados y resueltos.
4. Se identificó en qué documento de `docs/` corresponde incorporarlo.

**Pasos para promover:**

1. Crear o actualizar el documento correspondiente en [`docs/`](../docs/).
2. Si hay una decisión técnica relevante, crear un ADR en [`docs/adr/`](../docs/adr/).
3. Registrar el cambio en [`CHANGELOG.md`](../CHANGELOG.md).
4. Archivar el experimento en `laboratorio/` marcándolo como promovido, o eliminarlo si fue completamente incorporado.
