# Migración de Kanboard al modelo gateway + balanceador

> **Fecha:** 2026-10-08
> **Ejecutor:** Elías Alfonzo (comandos corridos a mano por SSH, guiado por Claude Code — ver nota de método abajo)
> **Estado:** ✅ Completado y validado funcionalmente
> **Objetivo:** Cerrar el pendiente explícito del [ADR-0008](../../docs/adr/ADR-0008-gateway-balanceador-dos-etapas.md) — retirar el acceso temporal a Kanboard (redirección directa a nivel de host, `10.143.11.228:8080`) y migrarlo al modelo definitivo de gateway + balanceador, para que todo el equipo acceda por el camino oficial.

---

## Nota de método

Durante esta sesión, el permiso de Claude Code para escribir directamente por shell remoto (SSH) estaba bloqueado por el clasificador de modo automático. Todos los comandos de escritura (editar `LB.conf`, `apache2ctl`, `systemctl reload`, `firewall-cmd`, `lxc config device remove`) los corrió el usuario a mano, copiando los comandos exactos indicados y pegando los resultados de vuelta para interpretarlos. Los comandos de **solo lectura** del relevamiento inicial sí se corrieron en vivo desde Claude Code (vía `paramiko`).

---

## Punto de partida

- `PFR-KANBOARD-TEST` (proyecto `default`, host `pfr.1`) seguía siendo el único Kanboard con contenido real, expuesto por dos dispositivos `proxy` de LXD:
  - `web-public`: `127.0.0.1:8080` → contenedor `:80` (vía túnel SSH, acceso administrativo)
  - `web-lan`: `10.143.11.228:8080` → contenedor `:80` (acceso directo habilitado para la demo de julio, ver [SOP-acceso-temporal-demo-kanboard.md](../2026-07-27_exploracion-rutas-firewall-pfr-oss/SOP-acceso-temporal-demo-kanboard.md), ahora retirado y marcado como superado)
- El [ADR-0008](../../docs/adr/ADR-0008-gateway-balanceador-dos-etapas.md) (julio) definió el modelo de reemplazo, pero nunca se había aplicado a Kanboard — quedaba explícito como pendiente.

## Hallazgo importante: ya había trabajo sin documentar

Antes de crear nada nuevo, se revisó si `PFR-GW-SRV` ya tenía algo armado — **sí tenía**. El archivo `/etc/apache2/sites-available/LB.conf` (modificado el **2026-09-18**, sin ningún registro en este repositorio) ya incluía:

- Un balanceador embebido para **Loki** (`/loki/loki/api/v1`, restringido por IP)
- Un balanceador embebido para **NTF** (`/ntf`, puerto 443, con mTLS — certificado de cliente obligatorio)
- Una línea suelta y rota: `ProxyPass /kanboard http://CAR-kanboard-1/` — el hostname `CAR-kanboard-1` no existe (el contenedor real se llama `CAR-KANBOARD`, sin el `-1`, y está vacío/detenido)

🟡 Se asume que fue Norberto Núñez quien hizo este trabajo (confirmado verbalmente por el usuario, no documentado en ningún lado por quien lo hizo). Quedó como pendiente de confirmación formal. Ver el detalle completo de esta investigación en [bitacora.md](bitacora.md).

Esto cambió el enfoque: en vez de crear un contenedor balanceador nuevo (`PFR-LB`, el "primer ejemplo" original del ADR-0008, que nunca llegó a persistirse), se reutilizó `PFR-GW-SRV` como balanceador embebido — el mismo patrón ya usado de facto para Loki y NTF.

## El problema no trivial: Kanboard no soporta subpath

El primer intento (`ProxyPass /kanboard` con el prefijo "pelado" hacia la raíz del backend) **rompió** — Kanboard genera todas sus redirecciones y links internos como rutas absolutas desde `/` (confirmado: no tiene ninguna opción de "base URL" en `config.php`), así que cualquier despliegue bajo un subpath pierde el prefijo apenas el usuario navega. Ver el diagnóstico completo y la solución final (Kanboard en la raíz del gateway + `Redirect`/`ProxyPass !` para los alias `/kanboard` y `/kamboard`) en [bitacora.md](bitacora.md).

## Resultado final

| Acceso | Resultado |
|---|---|
| `http://10.143.11.8/` | ✅ Kanboard funcional, para todo el equipo, sin restricción de IP |
| `http://10.143.11.8/kanboard` | ✅ Redirige limpio a la raíz (alias de conveniencia) |
| `http://10.143.11.8/kamboard` | ✅ Mismo redirect (cubre el typo común) |
| `http://10.143.11.228:8080/` (acceso viejo) | ✅ Retirado — dispositivo `web-lan` eliminado, las 6 reglas de firewall del host también (🟡 reportado por el usuario, no verificado de forma independiente — la cuenta usada no tiene privilegios para consultar `firewall-cmd` en el host) |
| Loki (`/loki/loki/api/v1`) y NTF (`/ntf`, :443) | ✅ Verificados intactos, sin verse afectados por los cambios |

## Documentos actualizados a partir de este trabajo

- [ADR-0008](../../docs/adr/ADR-0008-gateway-balanceador-dos-etapas.md) — pendiente cerrado, nota sobre el patrón embebido como uso de facto, hallazgo del trabajo sin documentar
- [13_Linea_de_Tiempo.md](../../docs/13_Linea_de_Tiempo.md) — hito actualizado
- [05_Configuracion.md](../../docs/05_Configuracion.md) — nuevo patrón documentado: apps sin soporte de subpath detrás del balanceador
- [03_Componentes.md](../../docs/03_Componentes.md) — variante embebida actualizada con los nuevos casos confirmados
- [SOP-acceso-temporal-demo-kanboard.md](../2026-07-27_exploracion-rutas-firewall-pfr-oss/SOP-acceso-temporal-demo-kanboard.md) — marcado como superado
- [CHANGELOG.md](../../CHANGELOG.md)

## Pendiente

- 🔴 Confirmar formalmente con Norberto Núñez qué es `CAR-kanboard-1`/`CAR-KANBOARD` y si el trabajo del 2026-09-18 en `LB.conf` tiene algo más planeado que no se haya aplicado.
- 🔴 Verificar con privilegios de root (que esta cuenta no tiene) que las 6 reglas de firewall del host quedaron efectivamente eliminadas.
- 🟡 Re-evaluar si el ADR-0008 debería actualizar su "modelo estándar" — en la práctica, los 3 servicios reales (Loki, NTF, Kanboard) usan la variante embebida, no un balanceador separado.
