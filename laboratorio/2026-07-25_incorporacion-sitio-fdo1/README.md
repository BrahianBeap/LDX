# Incorporación de FDO1 (Fernando) al cluster

> **Fecha de inicio:** 2026-07-25
> **Ejecutor:** Elías Alfonzo (comandos corridos por él mismo, guiado)
> **Estado:** 🔴 Bloqueado — Fases 1-3 completadas (LXD unido al cluster), pero la interfaz OVN no levanta en `fdo-oss1` (causa raíz sin identificar, ver Fase 4 en [`bitacora.md`](bitacora.md))

---

## Objetivo

Ejecutar, paso a paso y dejando registro, la checklist de
[`docs/06_Operacion.md` — "Cómo incorporar un nuevo sitio al cluster"](../../docs/06_Operacion.md)
sobre el sitio real **Fernando (FDO1)**. A diferencia del experimento de
Kanboard (donde los comandos los corrió el asistente), acá **el usuario
ejecuta cada comando en su propia sesión** — este documento es la
bitácora de lo que se hizo, no un log de comandos ajenos.

**Por qué existe este documento además de la checklist genérica:** la
checklist de `06_Operacion.md` usa a FDO como ejemplo teórico. Esta
bitácora es la ejecución real, con los resultados reales de cada paso —
sirve como caso de referencia concreto para cuando se incorpore el
próximo sitio (IT, Ciudad del Este).

## Entorno

| Dato | Valor |
|---|---|
| Hostname real | `fdo-oss1` |
| IP de gestión (`nic_oam`) | `10.150.32.101/24` |
| Usuario de acceso | `alfonzel_local` (cuenta local, sin SSSD/LDAP todavía — eso llega en una fase posterior) |
| Sitio en la nomenclatura del proyecto | FDO |

## Progreso

Ver [`bitacora.md`](bitacora.md) para el detalle fase por fase. Resumen:

| Fase | Estado |
|---|---|
| Fase 0 — Prerrequisitos | ✅ Completada |
| Fase 1 — SO, LXD y MicroOVN | ✅ Completada (desbloqueada con puente NAT temporal por el gateway de Franco, mientras se tramita el alta propia de `fdo-oss1`) |
| Fase 2 — Malla WireGuard | ✅ Completada |
| Fase 3 — Unir a LXD | ✅ Completada |
| Fase 4 — Unir a OVN | 🔴 Bloqueada — interfaz OVN no levanta, causa raíz sin identificar |
| Fase 5 — Firewall, proxy, NTP, usuarios | 🟡 Parcialmente completada |
| Fase 6 — Gateways del sitio | 🔴 Pendiente (depende de la Fase 4) |
| Fase 7 — Verificación end-to-end | 🔴 Pendiente (depende de la Fase 4) |
