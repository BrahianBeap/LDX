# Incorporación de FDO1 (Fernando) al cluster

> **Fecha de inicio:** 2026-07-25
> **Ejecutor:** Elías Alfonzo (comandos corridos por él mismo, guiado)
> **Estado:** 🔴 Bloqueado — `fdo-oss1` no tiene salida autorizada al proxy corporativo (ver Fase 1 en [`bitacora.md`](bitacora.md))

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
| Fase 1 — SO, LXD y MicroOVN | 🔴 Bloqueada (Paso 0 hecho; proxy configurado pero sin salida autorizada a internet — pendiente de red/seguridad) |
| Fase 2 — Malla WireGuard | 🔴 Pendiente |
| Fase 3 — Unir a LXD | 🔴 Pendiente |
| Fase 4 — Unir a OVN | 🔴 Pendiente |
| Fase 5 — Firewall, proxy, NTP, usuarios | 🔴 Pendiente |
| Fase 6 — Gateways del sitio | 🔴 Pendiente |
| Fase 7 — Verificación end-to-end | 🔴 Pendiente |
