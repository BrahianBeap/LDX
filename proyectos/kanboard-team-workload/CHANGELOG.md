# CHANGELOG — Plugin TeamWorkload

Historial de versiones de este plugin. Formato igual al `CHANGELOG.md` de
la raíz del repositorio, para que sea igual de fácil de leer.

Este historial es propio del plugin — no del proyecto LDX (cluster LXD).
El `CHANGELOG.md` de la raíz queda reservado para cambios del cluster.

---

## Formato de entrada

| Campo | Descripción |
|---|---|
| **Fecha** | YYYY-MM-DD |
| **Documentos afectados** | Diseño, pruebas y código modificados o creados |
| **Resumen** | Descripción breve del cambio y su motivo |

---

## Historial

### 2026-07-26 — Investigación previa

**Documentos creados:**
- `docs/01_Investigacion.md` — investigación de soluciones existentes
  para ver la carga de trabajo de una persona en todos sus proyectos de
  Kanboard. Ningún plugin de terceros ni oficial resuelve la necesidad
  completa. Se encontró que el propio Core tiene una página oculta y sin
  documentar (`ProjectUserOverviewController`) que resuelve gran parte
  del problema, validada en vivo contra `PFR-KANBOARD-TEST`.

**Resumen:**
Antes de escribir una sola línea de código, se determinó que no
convenía instalar ningún plugin existente y que la arquitectura correcta
era un plugin propio, liviano, apoyado en modelos del Core ya existentes
en vez de un Controller nuevo desde cero.

---

### 2026-07-26 — Fase 1 (v1.0)

**Documentos creados:**
- `docs/decisiones/diseno-fase1.md` — arquitectura, flujo de datos,
  interfaz, modelo de permisos y riesgos, aprobados antes de escribir
  código.
- `docs/decisiones/pruebas-fase1.md` — resultado real de las 10 pruebas
  mínimas.

**Código:**
- Primera versión de `src/TeamWorkload/` (`Plugin.php`,
  `WorkloadController.php`, `Template/workload/show.php`,
  `Template/workload/sidebar.php`, `Locale/es_ES/translations.php`).

**Resumen:**
Vista de solo lectura: elegir una persona y ver sus tareas abiertas en
todos los proyectos a los que pertenece, agrupadas por proyecto, con
enlaces directos, restringida a administradores. Corrige dos defectos
reales confirmados en `ProjectUserOverviewController` del Core: usuario
inexistente (ya no cae a "mostrar todo") y tareas sin vencimiento (ya no
muestra la fecha `31/12/1969`). 9 de 10 pruebas pasaron — la prueba con
un usuario de rol `Standard` quedó pendiente porque no existe ninguna
cuenta con ese rol en el entorno de prueba.

---

### 2026-07-26 — v1.1

**Documentos creados:**
- `docs/decisiones/diseno-v1.1.md` — diseño del modo "👥 Todos", columna
  de responsable, resumen superior, y el camino de extensión documentado
  (sin implementar) para futuros modos de agrupación.
- `docs/decisiones/pruebas-v1.1.md` — resultado real de las 8 pruebas.

**Código:**
- `WorkloadController.php` extendido: modo "Todos" (reutilizando
  `UserModel::EVERYBODY_ID`), separación de la obtención de tareas y el
  agrupamiento, resumen numérico.
- `Template/workload/show.php`: columna "Responsable" y bloque de
  resumen, ambos condicionados al modo.
- `Locale/es_ES/translations.php`: 3 cadenas nuevas propias.

**Resumen:**
La vista individual se convirtió en una pequeña vista de gestión de
equipo: un modo "Todos" que muestra las tareas de todas las personas a
la vez (incluidas las sin asignar), con un resumen rápido (usuarios con
tareas, proyectos, tareas abiertas, sin asignar). No hizo falta ninguna
consulta SQL nueva — la misma consulta reutilizada desde la Fase 1 nunca
filtró por propietario; ese filtro lo agregaba el propio controlador por
fuera. Se encontró y corrigió un límite real de
`Request::getIntegerParam()` del Core (no acepta enteros negativos, por
lo que no podía leer `UserModel::EVERYBODY_ID = -1`). 8 de 8 pruebas
pasaron, sin regresión en el modo individual, los permisos ni el
rollback.

---

### 2026-07-27 — Reorganización de documentación

**Resumen:**
El plugin dejó de vivir en `laboratorio/` (dos experimentos separados) y
se promovió a `proyectos/kanboard-team-workload/`, con su propio
`README.md`, este `CHANGELOG.md`, un documento de arquitectura viviente
(`docs/00_Arquitectura.md`) y el registro histórico de decisiones movido
a `docs/decisiones/`. El `CHANGELOG.md` de la raíz del repositorio queda
reservado exclusivamente para cambios del proyecto LDX (cluster LXD); su
entrada sobre este plugin se retiró y su contenido pasó a este archivo.
No se modificó el contenido técnico de ningún documento, solo su
ubicación y los enlaces internos entre ellos.
