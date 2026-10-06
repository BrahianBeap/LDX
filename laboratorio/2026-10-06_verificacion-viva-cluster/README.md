# Verificación en vivo del cluster (solo lectura)

> **Fecha:** 2026-10-06
> **Ejecutor:** Elías Alfonzo (asistido por Claude Code, vía SSH)
> **Estado:** ✅ Completado
> **Objetivo:** Confirmar contra los 3 servidores reales (`pfr-oss`, `car-oss`, `fdo-oss`) el estado documentado del cluster, después de varias semanas sin una revisión en vivo.

---

## Por qué se hizo

La documentación en `docs/` tenía varios puntos marcados como pendientes o bloqueados (RIE-002, RIE-013, TRB-012) desde la incorporación de Fernando (FDO1) en agosto, sin una revisión posterior. El usuario ya tenía acceso de sistema operativo a los 3 hosts (`alfonzel_opr`) y pidió un vistazo general en modo **estrictamente solo lectura** — sin crear, modificar ni borrar nada en el cluster.

## Método

Conexión SSH (autenticación por contraseña) a los 3 hosts desde la PC del usuario, usando un script Python (`paramiko`) para ejecutar una batería fija de comandos de solo lectura y capturar la salida. No se usó `sudo` en ningún comando que lo requiriera interactivamente — donde era necesario (ej. `microovn status`), el comando falló por falta de contraseña de `sudo` y se dejó así, documentado como limitación.

> ⚠️ **Nota de seguridad:** la contraseña fue compartida por el usuario en texto plano en el chat de la sesión. Se recomendó rotarla y migrar estos 3 hosts a autenticación por clave SSH, como ya existe para otros accesos documentados en `~/.ssh/config`.

Comandos ejecutados (idénticos en los 3 hosts salvo donde se indica):

```bash
hostname && uptime
cat /etc/os-release
ip -4 -brief addr
df -h
snap list | grep -Ei 'lxd|microovn|core'
lxc cluster list
lxc list                      # proyecto default
lxc list --project PRJ-OSS    # solo corrido una vez, desde pfr-oss (vista de cluster es la misma desde cualquier nodo)
lxc storage list
lxc network list
lxc network list --project PRJ-OSS
lxc project list
```

Ver la salida completa en [`bitacora.md`](bitacora.md).

## Resultado — resumen

| Hallazgo | Clasificación |
|---|---|
| Los 3 nodos (`pfr.1`, `car.1`, `fdo.1`) están `ONLINE` en `lxc cluster list` | ✅ Confirmado |
| `FDO-WS-1` (contenedor de aplicación NTF) corre en `fdo.1` con IP en la red `OVN_1` | ✅ Confirmado |
| El bloqueo de OVN en Fernando (RIE-013 / TRB-012) parece resuelto | 🟡 Inferencia razonable — no se confirmó causa ni momento de la resolución |
| Causa raíz original del bloqueo de OVN (TRB-012) | 🔴 Sigue sin identificarse |
| Contenedores de observabilidad (`C-Loki-1`, `Minio-1`, `C-Grafana-1`, `C-Mimir-1`, `C-Colector-1`) creados en `PRJ-OSS` | 🟡 Avance parcial — solo Loki y el colector están `RUNNING` |
| Contenedor `C-Mimir-1` | 🔴 Sin documentar en ningún plan anterior |
| Contenedor `CAR-KANBOARD` (`STOPPED`, en `car.1`) | 🔴 Sin documentar — propósito desconocido |

Se actualizaron en consecuencia: [`11_Riesgos.md`](../../docs/11_Riesgos.md) (RIE-002, RIE-013), [`07_Troubleshooting.md`](../../docs/07_Troubleshooting.md) (TRB-012), [`13_Linea_de_Tiempo.md`](../../docs/13_Linea_de_Tiempo.md), [`03_Componentes.md`](../../docs/03_Componentes.md) (MicroOVN, Prometheus, Grafana), [`14_Manual_Operativo.md`](../../docs/14_Manual_Operativo.md) (checklist de Loki+MinIO) y [`00_Resumen_Ejecutivo.md`](../../docs/00_Resumen_Ejecutivo.md).

## Pendiente

- Confirmar formalmente con Norberto Núñez / el equipo cómo y cuándo se resolvió el bloqueo de OVN en Fernando (RIE-013/TRB-012), para poder cerrarlo sin el calificador 🟡.
- Averiguar qué es `CAR-KANBOARD` y si reemplaza a `PFR-KANBOARD-TEST`.
- Averiguar qué es `C-Mimir-1` y si forma parte del plan de observabilidad.
- Repetir esta verificación con acceso a `sudo` (o una cuenta con permisos) para confirmar el estado interno de MicroOVN en Fernando.
