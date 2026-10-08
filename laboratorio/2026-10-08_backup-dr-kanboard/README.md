# Backup y recuperación ante desastre (DR) para Kanboard

> **Fecha:** 2026-10-08
> **Ejecutor:** Elías Alfonzo (comandos corridos a mano por SSH, guiado por Claude Code)
> **Estado:** 🟡 Parcialmente completado — snapshot + copia cruzada probados y funcionando; automatización bloqueada por falta de privilegio root en el host
> **Objetivo:** Dar a Kanboard una resiliencia real y del tamaño correcto frente a la pérdida de su nodo/sitio (Franco), sin construir la replicación completa (frontend x3 + Postgres) que se evaluó y se descartó por sobredimensionada para un servicio de ~5-6 usuarios. Ver [11_Riesgos.md — RIE-006](../../docs/11_Riesgos.md#rie-006--sin-política-de-backup-documentada), el riesgo general de "sin política de backup" que este trabajo empieza a cerrar, al menos para este servicio.

---

## Por qué este enfoque y no replicación completa

Se evaluó explícitamente (y se descartó) replicar el frontend de Kanboard en los 3 sitios con una base de datos Postgres centralizada — es el patrón que sí tiene sentido para un servicio sin estado como NTF, pero para Kanboard (con estado: tareas, usuarios, comentarios) implica migrar de SQLite a Postgres, resolver réplica activa-pasiva de la base, y mantener 3 frontends sincronizados. Para 5-6 usuarios, ese costo no se justifica — fue una decisión explícita de costo/beneficio del usuario, ya registrada en [ADR-0008 — Actualización](../../docs/adr/ADR-0008-gateway-balanceador-dos-etapas.md#actualización--migración-de-kanboard-2026-10-08).

En su lugar, se usó una estrategia de **snapshot + copia a otro sitio + standby frío**, nativa de LXD, con un RTO (tiempo de recuperación) de minutos y un RPO (pérdida de datos aceptable) acotado por la frecuencia del snapshot.

## Qué se armó

1. **Snapshot automático nativo de LXD** en `PFR-KANBOARD-TEST`, cada 6 horas, con expiración a los 7 días — sin script propio, lo gestiona LXD solo.
2. **Script de sincronización cruzada** (`~/kanboard-dr-sync.sh` en `pfr-oss`, corrido como `alfonzel_opr`): toma un snapshot fijo (`dr-sync`, se reemplaza en cada corrida) y lo copia como contenedor **parado** (`PFR-KANBOARD-DR`) en `car.1` — un sitio físicamente distinto.
3. **Ruta de respaldo (fría) en el gateway de Carpinelli** (`CAR-GW-SRV`): mismo patrón de Apache que en `PFR-GW-SRV` (ver [laboratorio/2026-10-08_migracion-kanboard-gateway-balanceador/](../2026-10-08_migracion-kanboard-gateway-balanceador/)), apuntando por **nombre** (no IP) a `PFR-KANBOARD-DR` — no responde nada mientras ese contenedor esté parado, que es la situación normal.

Todo esto se probó de punta a punta: se arrancó `PFR-KANBOARD-DR`, se confirmó que Kanboard cargaba (`curl` devolvió el mismo `302` de login), y se comparó el hash del `db.sqlite` contra el original (no coincidió — **esperado**, porque el original siguió recibiendo actividad después del snapshot; confirma que el snapshot efectivamente congela un punto en el tiempo, no un error).

## Lo que quedó pendiente (bloqueado, no por decisión)

🔴 **Automatizar la corrida periódica del script de sincronización.** El host `pfr-oss` no tiene `cron` instalado, y la alternativa sin paquetes nuevos (`systemctl --user`, timers de usuario) tampoco sirve porque la sesión de usuario tiene `Linger=no` — los servicios de usuario mueren al cerrar la sesión SSH. Ninguna de las dos rutas funciona sin una acción puntual de alguien con acceso root (`su -`) en el host:

```bash
# Opción A (recomendada, más simple)
apt-get install -y cron

# Opción B (sin instalar nada nuevo)
loginctl enable-linger alfonzel_opr
```

Mientras tanto, el script **funciona perfecto corrido a mano** — se recomienda ejecutarlo manualmente de vez en cuando (ver [bitacora.md](bitacora.md)) hasta que se resuelva el acceso root, idealmente en la misma sesión donde se limpien también las reglas de firewall del acceso viejo de Kanboard (ver [`laboratorio/2026-10-08_migracion-kanboard-gateway-balanceador/`](../2026-10-08_migracion-kanboard-gateway-balanceador/)) — un solo pedido de root para las dos cosas.

## Procedimiento de recuperación real (si Franco se cae)

1. Conectarse por SSH **directo a `car-oss` o `fdo-oss`** (no a `pfr-oss`, que estaría caído).
2. `lxc start PFR-KANBOARD-DR --project default`
3. Avisarle al equipo que la URL cambia temporalmente a la IP de servicio de `CAR-GW-SRV` (no es automático — es un paso manual).
4. Cuando Franco vuelva: decidir si se restaura `PFR-KANBOARD-TEST` desde el snapshot más reciente, o se promueve `PFR-KANBOARD-DR` como el nuevo contenedor principal (a definir según cuánto tiempo haya estado caído y si hubo escrituras nuevas en el standby, cosa que no debería pasar si nadie lo usó mientras tanto).

Ver el detalle completo, comando por comando, en [bitacora.md](bitacora.md).
