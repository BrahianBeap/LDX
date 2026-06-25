# LDX — Base de Conocimiento Técnica

## ¿Qué es este repositorio?

Este repositorio contiene la **documentación técnica oficial del proyecto LDX**.

Su propósito es transformar el conocimiento tácito del equipo en documentación estructurada, reutilizable y mantenible, permitiendo que cualquier ingeniero pueda comprender, instalar, operar, mantener y ampliar la solución sin depender de quienes participaron en las reuniones originales.

---

## Filosofía

Este repositorio **no almacena únicamente documentación**. Almacena conocimiento.

Cada documento debe responder al menos una de estas preguntas:

| Pregunta | Documento principal |
|---|---|
| ¿Qué es? | [`01_Contexto.md`](docs/01_Contexto.md) |
| ¿Cómo funciona? | [`02_Arquitectura.md`](docs/02_Arquitectura.md) |
| ¿Cómo se instala? | [`04_Instalacion.md`](docs/04_Instalacion.md) |
| ¿Cómo se configura? | [`05_Configuracion.md`](docs/05_Configuracion.md) |
| ¿Cómo se opera? | [`06_Operacion.md`](docs/06_Operacion.md) |
| ¿Cómo se diagnostican problemas? | [`07_Troubleshooting.md`](docs/07_Troubleshooting.md) |
| ¿Qué decisiones se tomaron y por qué? | [`docs/adr/`](docs/adr/) |

---

## Estructura del repositorio

```
LDX/
│
├── README.md               ← este archivo
├── CLAUDE.md               ← instrucciones para el asistente IA
├── CHANGELOG.md            ← historial de cambios del repositorio
│
├── docs/                   ← documentación técnica oficial
│   ├── README.md           ← índice completo con estado de cada documento
│   └── adr/                ← Architecture Decision Records
│
├── reunion/                ← transcripciones y notas de reuniones
│
├── laboratorio/            ← experimentos y pruebas previas a documentación oficial
│
├── recursos/               ← plantillas y materiales de apoyo
│
├── diagramas/              ← diagramas de arquitectura y flujo
│
├── imagenes/               ← capturas de pantalla e imágenes de referencia
│
└── scripts/                ← scripts operativos documentados
```

---

## Flujo de trabajo para nuevas reuniones

### Paso 1 — Guardar la transcripción

Colocar el archivo `.vtt` o `.txt` en `reunion/`, siguiendo la convención de nombre:

```
reunion/YYYY-MM-DD_descripcion-breve.vtt
```

### Paso 2 — Analizar la reunión

Extraer del contenido:

- Nuevos conceptos y tecnologías
- Decisiones técnicas
- Arquitectura y componentes
- Comandos y configuraciones
- Problemas identificados
- Tareas y próximos pasos
- Buenas prácticas y riesgos

### Paso 3 — Comparar con la documentación existente

Revisar qué ya está documentado antes de escribir. Nunca duplicar información.

### Paso 4 — Actualizar únicamente los documentos afectados

Cada concepto tiene un único documento dueño. Si cambia la arquitectura, actualizar solo `docs/02_Arquitectura.md`. No copiar esa información en otros documentos.

### Paso 5 — Registrar el cambio

En [`CHANGELOG.md`](CHANGELOG.md), registrar:

- Fecha
- Reunión origen
- Documentos modificados
- Resumen del cambio

---

## Principios

| Principio | Descripción |
|---|---|
| Una única fuente de verdad | Cada concepto se documenta en un solo lugar |
| No duplicar | Usar enlaces Markdown entre documentos, nunca copiar |
| Explicar el "por qué" | No solo el "qué". Documentar contexto y razones |
| Documentar decisiones | Con contexto, alternativas y consecuencias. Ver [`docs/adr/`](docs/adr/) |
| Conocimiento permanente | Convertir conversaciones en documentación que perdure |
| Coherencia | Los documentos deben mantenerse consistentes entre sí |

---

## Objetivo final

Este repositorio debe permitir que cualquier ingeniero pueda:

- Comprender el sistema
- Instalarlo desde cero
- Operarlo correctamente
- Resolver incidentes
- Ampliar la plataforma
- Mantener la solución durante los próximos años

El conocimiento debe permanecer en la documentación, no en la memoria de quienes participaron en las reuniones.

---

## Ver también

- [Instrucciones para el asistente IA](CLAUDE.md)
- [Historial de cambios](CHANGELOG.md)
- [Índice de documentación técnica](docs/README.md)
- [Decisiones de arquitectura (ADR)](docs/adr/)
- [Reuniones procesadas](reunion/README.md)
- [Laboratorio de experimentos](laboratorio/README.md)
- [Plantilla de análisis de reunión](recursos/prompt_analisis_reunion.md)
