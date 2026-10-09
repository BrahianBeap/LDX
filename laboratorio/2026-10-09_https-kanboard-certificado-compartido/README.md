# HTTPS para Kanboard reusando el certificado compartido (sin debilitar mTLS de NTF)

> **Fecha:** 2026-10-09
> **Ejecutor:** Elías Alfonzo (comandos corridos a mano por SSH, guiado por Claude Code)
> **Estado:** ✅ Completado y validado funcionalmente
> **Objetivo:** Exponer Kanboard por HTTPS (puerto 443) sin pedir un certificado nuevo, reutilizando el que ya existe para NTF, **sin debilitar la exigencia de certificado de cliente (mTLS) que protege a NTF**. De paso, forzar que el puerto 80 redirija a HTTPS para todo excepto Loki.

---

## Punto de partida

Después de migrar Kanboard al gateway (ver [`laboratorio/2026-10-08_migracion-kanboard-gateway-balanceador/`](../2026-10-08_migracion-kanboard-gateway-balanceador/)), surgió la pregunta de si hacía falta pedir certificados nuevos para los 3 gateways del cluster. El análisis previo (ver [ADR-0008 — Actualización](../../docs/adr/ADR-0008-gateway-balanceador-dos-etapas.md)) encontró que:

- **No hay DNS configurado** para ninguna de las 3 IPs de servicio de los gateways (`10.143.11.8`, `192.168.91.117`, `10.11.11.12`), ni siquiera para el nombre que ya tiene el certificado existente (`oss.personal.com.py`) — todo devuelve `NXDOMAIN`.
- **El certificado ya existe**, es el mismo archivo exacto en los 3 gateways (confirmado por hash MD5), para `CN=oss.personal.com.py`, emitido por la CA interna `AutoridadOSS`, sin SAN, válido hasta 2027-09-03.
- Ese certificado hoy solo se usa en el `VirtualHost *:443` que exige certificado de cliente (`SSLVerifyClient require`) para NTF — pero esa exigencia es una directiva de Apache separada del certificado en sí, no una propiedad del archivo.

**Conclusión del análisis:** no hace falta pedir un certificado nuevo para exponer Kanboard por HTTPS — el mismo certificado sirve, el problema es solo de configuración de Apache (cómo convive con la exigencia de mTLS de NTF en el mismo puerto).

## Qué se armó

1. Se reutilizó el certificado existente (`/etc/ssl/certs/server.crt`) en el mismo `VirtualHost *:443` de `PFR-GW-SRV` que ya servía a NTF.
2. Se agregó la misma lógica de ruteo de Kanboard (raíz del vhost + alias `/kanboard`/`/kamboard`) que ya funcionaba en el puerto 80, ahora también en el 443.
3. Se resolvió el conflicto de exigencia de certificado de cliente: en vez de `SSLVerifyClient require` a nivel de todo el vhost (lo que exigiría certificado hasta para Kanboard), se cambió a `SSLVerifyClient optional` a nivel de vhost, con `SSLVerifyClient require` explícito **solo** dentro del `<Location '/ntf'>`.
4. Se cambió el puerto 80 para que **redirija a HTTPS** en vez de servir Kanboard directo — excepto Loki, que se dejó intacto en HTTP (lo sigue consultando Grafana ahí, no había motivo para forzarlo a cambiar).

## El error encontrado en el camino (y por qué importa para el futuro)

El primer intento — envolver las reglas de Kanboard dentro de un `<Location "/">` con `SSLVerifyClient none`, dejando el resto del vhost en `require` — **falló en tiempo de ejecución**, aunque la sintaxis era válida. El servidor seguía pidiendo certificado incluso para la raíz.

**Causa:** `SSLVerifyClient` se evalúa en gran parte **durante el saludo inicial de TLS**, antes de que Apache sepa qué URL se está pidiendo. El mecanismo de "subir" la exigencia en un path específico (`require` dentro de una ruta, con el vhost en algo más permisivo) está bien soportado — es exactamente el patrón que ya usa `/ntf`. Pero el camino inverso (vhost en `require`, tratar de "bajarlo" a `none` en un path) no funciona de forma confiable, mucho menos con TLS 1.3 (confirmado en este mismo cluster: Apache 2.4.66 + OpenSSL 3.5.5 usando TLS 1.3 por defecto). Quedó documentado como patrón general reusable en [05_Configuracion.md](../../docs/05_Configuracion.md#mtls-opcional-por-defecto-obligatorio-solo-en-rutas-especificas).

Ver el detalle completo, comando por comando, en [bitacora.md](bitacora.md).

## Resultado final (los 4 casos probados)

| Caso | Resultado |
|---|---|
| Loki por HTTP (`/loki/loki/api/v1`) | ✅ Sin cambios — `403 Forbidden` para origen no autorizado, protección intacta |
| Kanboard por HTTP (`http://10.143.11.8/`) | ✅ Redirige (`302`) a `https://10.143.11.8/` |
| Kanboard por HTTPS (`https://10.143.11.8/`) | ✅ Carga el login de Kanboard, **sin pedir certificado de cliente** |
| NTF por HTTPS sin certificado (`https://10.143.11.8/ntf`) | ✅ Sigue rechazando (`403 Forbidden`) — mTLS intacto |

Confirmado también desde el navegador real del usuario: carga Kanboard por HTTPS, con la advertencia de certificado esperada (nombre no coincide con la IP, CA no reconocida por el navegador — ambas cosas se resuelven cuando se consiga el DNS, ver pendiente abajo).

## Pendiente

- 🔴 Pedir DNS para `oss.personal.com.py` (o decidir un esquema de nombres por sitio, lo que implicaría pedir un certificado nuevo con SAN — el actual no tiene).
- 🔴 Confirmar si las PCs del equipo ya confían en la CA `AutoridadOSS` (si es la CA corporativa estándar, probablemente sí).
- Replicar este mismo cambio en `CAR-GW-SRV` y `FDO-GW-SRV` si se decide exponer Kanboard (u otro servicio) por HTTPS ahí también — hoy solo se aplicó en Franco.
