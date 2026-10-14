# Relevamiento y backup de tec-calidad05 (2026-09-16)

> **Nota:** este servidor **no es parte del clúster LXD** — es una VM VMware con CentOS 7 que aloja Infrawork, ADM-TECH y una versión legacy de VulnApp. Se documenta en LDX porque el equipo centraliza acá toda la infraestructura, LXD y no-LXD.

## Objetivo

Dos trabajos relacionados sobre `tec-calidad05` (`10.129.2.165`):

1. Relevar capacidad (CPU, RAM, disco) y consumo por aplicación, para tener una base real antes de decisiones de capacidad.
2. Implementar un backup nocturno automatizado de la base PostgreSQL de ADM-TECH, que no lo tenía.

## Resultado

### 1. Relevamiento de capacidad

| Recurso | Valor |
|---|---|
| CPU | 4 vCPU (VM), uso puntual 0.9%, histórico del día 0.6% |
| RAM | 7.64 GiB total, 1.88 GiB usada (24.6%) |
| Disco `/` | 746.98 GiB total, 663.48 GiB usado — 🔴 **88.8%, sobre el umbral de alerta** |
| Swap | 2.00 GiB total, 0.21 GiB usada |

Detalle completo, con metodología y qué quedó `N/D` (sin acceso suficiente para confirmar), en [`04_evidencias_tec-calidad05.md`](04_evidencias_tec-calidad05.md) y [`07_evidencias_consumo_aplicaciones.md`](07_evidencias_consumo_aplicaciones.md). Resumen tabulado para planilla en [`08_resumen_para_planilla.md`](08_resumen_para_planilla.md), con el consumo por aplicación (Infrawork, ADM-TECH, VulnApp legacy).

🔴 **Hallazgo a seguir**: el filesystem raíz está al 88.8%, con 82.79 GiB disponibles — no es crítico todavía, pero conviene monitorear el crecimiento antes de que se vuelva un problema.

🟡 **Pendiente de confirmar con el responsable**: si `/var/www/html/adm` corresponde efectivamente a ADM-TECH (coincide por nombre, no se confirmó formalmente).

### 2. Backup nocturno de ADM-TECH — ✅ implementado y verificado

| Elemento | Detalle |
|---|---|
| Script | `/usr/local/sbin/backup_admtech.sh` (root:root, 755) |
| Destino | `/var/backups/postgresql/admtech` (postgres:postgres, 700) — fuera del DocumentRoot web y del alcance de la limpieza de Infrawork |
| Programación | `30 2 * * *` como usuario `postgres`, vía `/etc/cron.d/backup-admtech` |
| Primer respaldo | Ejecutado y verificado el 16/09/2026 11:11 — dump de 4.42 MiB, checksum SHA-256 y catálogo (`pg_restore --list`) comprobados |
| Retención | 30 días, borrado restringido a pares propios del script |

Detalle completo del procedimiento, comandos ejecutados y evidencia, en [`implementacion_backup_admtech.md`](implementacion_backup_admtech.md) — es el documento vigente. [`verificacion_backup_admtech.md`](verificacion_backup_admtech.md) es una etapa intermedia (checklist previo a instalar, estado "NO LISTO" en su momento) conservada como historial; no describe el estado final.

**Pendiente**: observar la primera ejecución automática (la próxima estaba calculada para el 17/09/2026 02:30) y confirmar que llegan las notificaciones por `MAILTO=root`.

## Cómo se trabajó

Acceso de solo lectura para el relevamiento (usuario `alfonzel_opr`, sin sudo) y acceso root vía `sudo -n su` únicamente para la instalación del backup, con credenciales SSH/PostgreSQL manejadas por variables de entorno y archivos temporales eliminados por `trap` — nunca escritas en argumentos, historial o archivos persistentes. Los scripts de generación de reportes (`report.py`, `report2.py`, `scripts_backup.sh`) verifican que ningún secreto haya quedado en los documentos antes de darlos por válidos.

## Archivos de esta carpeta

| Archivo | Contenido |
|---|---|
| `01`–`03_*.csv` | Datos crudos del relevamiento de capacidad (servidores, discos, aplicaciones) |
| `04_evidencias_tec-calidad05.md` | Evidencia y metodología del relevamiento de capacidad |
| `05`–`06_*.csv` | Datos crudos de consumo por aplicación y tamaño de bases PostgreSQL |
| `07_evidencias_consumo_aplicaciones.md` | Evidencia y metodología del consumo por aplicación |
| `08_resumen_para_planilla.md` | Resumen tabulado, listo para pasar a planilla |
| `implementacion_backup_admtech.md` | Procedimiento e implementación verificada del backup (documento vigente) |
| `verificacion_backup_admtech.md` | Checklist previo a la instalación (etapa intermedia, histórico) |
| `*.sh`, `*.py`, `*.txt`, `*.cron` | Scripts y salidas crudas de cada paso, referenciados desde los `.md` anteriores |

## Pendiente de promover a `docs/`

Este relevamiento todavía no tiene una ficha propia en `docs/` (tec-calidad05 no está documentado ahí como componente, y el procedimiento de backup tampoco está en `docs/06_Operacion.md`). Si se decide mantener este servidor como infraestructura documentada de forma permanente, falta ese paso — no se hizo acá para no mezclarlo con el trabajo de relevamiento en sí.
