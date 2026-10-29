# Inventario en Ciberseguridad (Jerure)

Estado de lo que la plataforma LXD de OSS tiene dado de alta en el inventario de Ciberseguridad: la plataforma como aplicación (707) y cada servicio publicado (452).

Este documento registra el **estado**. El procedimiento y el criterio para inventariar están en [06_Operacion.md — Inventario hacia Ciberseguridad (Jerure)](06_Operacion.md#inventario-hacia-ciberseguridad-jerure-ip-de-servicio--puerto--url).

**Estado al:** 2026-10-26. ✅ Todos los datos se tomaron de los tickets de Jerure, salvo donde se indica otra cosa.

---

## Resumen

| Tipo | Ticket | Nombre | Estado | URL |
|---|---|---|---|---|
| Aplicación (707) | #1047036 | `PLATAFORMA-LXD-OSS` (aplicación **608**, PROD) | ✅ Resuelto | — |
| Servicio (452) | #1083088 | `Kanboard-OSS` | 🟡 Pendiente de aprobación | `https://oss.personal.com.py/kanboard/` |
| Servicio (452) | #1083104 | `Vulnapp-OSS` (VulnApp NG) | 🟡 Abierto | `https://oss.personal.com.py/vulnapp/` |
| Servicio (452) | #1083324 | `ADM-TECH-OSS` (entorno de desarrollo) | ✅ Resuelto (inventariado 28/10) | `https://oss.personal.com.py/adm/` |
| OAuth AD (623) | #1084774 | Aplicación OAuth de `ADM-TECH-OSS` (servicio 32989) | 🟡 Abierto (28/10) | Retorno `https://oss.personal.com.py/adm/` |

```
 Aplicación 608  PLATAFORMA-LXD-OSS  (707 #1047036)
        │
        ├── Servicio Kanboard-OSS  (452 #1083088)  ─┐
        ├── Servicio Vulnapp-OSS   (452 #1083104)  ─┼─ host: activo 10041 fr-oss (10.143.11.8)
        └── Servicio ADM-TECH-OSS  (452 #1083324)  ─┘     = gateway PFR-GW-SRV
                 └── Aplicación OAuth AD (623 #1084774)
```

---

## Aplicación: PLATAFORMA-LXD-OSS (707, ticket #1047036)

| Campo | Valor |
|---|---|
| Aplicación | `PLATAFORMA-LXD-OSS`. Quedó en el inventario como aplicación **608**, entorno **PROD** |
| Descripción | Plataforma de virtualización y contenerización basada en LXD, administrada por OSS, en un clúster distribuido entre dos sitios. Usuarios directos: administradores técnicos de OSS; los usuarios finales solo acceden a las aplicaciones publicadas. Cada aplicación conserva su propia autenticación, autorización y publicación. El acceso administrativo a LXD se restringe al personal autorizado, desde la red corporativa |
| BPO | `cascoma` |
| Criticidad | ALTA |
| Creado | 2026-08-18 13:10 |
| Estado | Resuelto |
| Copia impresa | `Ticket-1047036.pdf` (en las descargas del usuario; no está en el repositorio) |

**Circuito de aprobación:**

| Paso | Responsable | Resultado | Fecha |
|---|---|---|---|
| 1 | Salvador Deu | Aprobó | 2026-08-18 13:56 |
| 2 | Julio César Acosta | Aprobó | 2026-08-18 18:46 |
| 3 | Seguridad de la Información | "Fue realizado el inventario" | 2026-08-18 18:50 |

> **Nota:** 🟡 la descripción registrada dice "dos sitios". Hoy el clúster tiene tres (Franco, Carpinelli y Fernando, ver [02_Arquitectura.md](02_Arquitectura.md)). Ver pendientes.

---

## Servicio: Kanboard-OSS (452, ticket #1083088)

| Campo | Valor |
|---|---|
| Creado | 2026-10-26 10:33 |
| Estado | Pendiente de aprobación |
| Finalizado | — |
| Tipo | OTRO (corresponde FRONTEND, ver pendientes) |
| URL | `https://oss.personal.com.py/kanboard/` |
| Aplicación | 608 `PLATAFORMA-LXD-OSS` |
| BPO y soporte | `alfonzel` (Elias Alfonzo) |
| Host | Activo **10041**, `fr-oss` (`10.143.11.8`): el gateway `PFR-GW-SRV` que lo publica |
| Puertos | `443/tcp` https; `80/tcp` redirige a https |
| Criticidad | Alta |
| Permiso | Local |
| Administrador de accesos | SSO (ver pendientes) |

**Endpoints declarados:**

| Método | Ruta | Uso |
|---|---|---|
| `GET` | `/kanboard/` | Interfaz web |
| `POST` | `/kanboard/jsonrpc.php` | API JSON-RPC 2.0, con usuario de servicio y token |

---

## Servicio: Vulnapp-OSS (VulnApp NG) (452, ticket #1083104)

| Campo | Valor |
|---|---|
| Creado | 2026-10-26 10:51 |
| Estado | Abierto |
| Finalizado | — |
| Tipo | FRONTEND |
| URL | `https://oss.personal.com.py/vulnapp/` |
| Aplicación | 608 `PLATAFORMA-LXD-OSS` |
| BPO y soporte | `alfonzel` (Elias Alfonzo) |
| Host | Activo **10041**, `fr-oss` (`10.143.11.8`) |
| Puerto | `443/tcp` https (publicado por el gateway) |
| Criticidad | Alta |
| Permiso | Local |
| Administrador de accesos | SSO (ver pendientes) |

**Contenedores** (proyecto LXD `PRJ-OSS`, nombrados en la descripción del servicio, no inventariados por separado):

| Contenedor | IP | Función |
|---|---|---|
| `PFR-VULNAPP-APP` | `192.168.0.14` | Aplicación (Gunicorn en el puerto 5000) |
| `PFR-VULNAPP-DB` | `192.168.0.13` | PostgreSQL 18. No se publica fuera del clúster |

**Dependencia externa:** consume la API de Ciberseguridad `https://ciberseg3.sis.personal.net.py/vulnapp-sdi-services` (`10.150.58.116:443`). El acceso desde el clúster todavía no funciona: falta el permiso de firewall, pedido en el ticket **#1083155** (ver [RIE-015](11_Riesgos.md#rie-015--conectividad-de-vulnapp-ng-hacia-la-api-de-sdi-bloqueada)).

---

## Servicio: ADM-TECH-OSS (452, ticket #1083324)

| Campo | Valor |
|---|---|
| Creado | 2026-10-26 15:28 |
| Estado | ✅ Resuelto |
| Finalizado | 2026-10-28 17:50 (inventariado por Seguridad de la Información) |
| Registros de inventario | **ID 32989** `TCP/443 (ADM-TECH-OSS)` y **ID 32990** `TCP/80 (ADM-TECH-OSS)`, ambos sobre `10.143.11.8` |
| Copia impresa | `Ticket-1083324.pdf` (en las descargas del usuario; no está en el repositorio) |
| Tipo | FRONTEND |
| URL | `https://oss.personal.com.py/adm/` |
| Aplicación | 608 `PLATAFORMA-LXD-OSS` |
| BPO | `alfonzel` |
| Soporte | Elias Alfonzo (`alfonzel`), 0972768056, elias.alfonzo@personal.com.py |
| Host | Activo **10041**, `fr-oss` (`10.143.11.8`) |
| Puertos | `443/tcp` https; `80/tcp` http (redirige a https) |
| Criticidad | Alta |
| Permiso | ActiveDirectory |
| Administrador de accesos | OSS |

**Descripción registrada:** ADM-TECH modernizado (PHP 8.5 y PostgreSQL 18) que reemplazará al de `tec-calidad05`. Hoy es un entorno de desarrollo y prueba, con copia de los datos de producción y sin envío de correos. Se publica por `PFR-GW-SRV` y corre en `DEV-ADMTECH-APP` (`192.168.0.19`, Apache y PHP 8.5) y `DEV-ADMTECH-DB` (`192.168.0.18`, PostgreSQL 18, solo accesible desde la aplicación). Autenticación por OAuth de SDI con grupos de AD; la URL de retorno está pendiente (ticket 623).

**Endpoints declarados:**

| Método | Ruta | Uso |
|---|---|---|
| `GET` | `/adm/` | Pantalla de inicio de sesión (redirige al OAuth de SDI) |
| `GET` | `/adm/index.php?code=...` | Retorno del OAuth de SDI |
| `GET` | `/adm/sing-in-backend.php` | Validación de grupos de AD y apertura de sesión |
| `GET` | `/adm/main.php` | Aplicación (requiere sesión) |

**Circuito de aprobación:**

| Paso | Responsable | Resultado | Fecha |
|---|---|---|---|
| 1 | Abel Díaz | Aprobó | 2026-10-26 18:17 |
| 2 | Salvador Deu | Aprobó (aprobación masiva) | 2026-10-28 10:12 |
| 3 | Julio César Acosta | Aprobó | 2026-10-28 17:36 |
| 4 | Elias Alfonzo (BPO) | Aprobó | 2026-10-28 17:41 |
| 5 | Seguridad de la Información | Inventarió el servicio (IDs 32989 y 32990) | 2026-10-28 17:50 |

**Aplicación OAuth (623, ticket #1084774, abierto desde 2026-10-28 18:51):**

| Campo | Valor |
|---|---|
| Aplicación | `32989 \| TCP/443 (ADM-TECH-OSS)` |
| URL de redirección | `https://oss.personal.com.py/adm/` |
| ¿Solo autenticación? | NO: los grupos de AD definen el rol (DEC-010 del repo `adm-tech`) |
| Grupos de AD | `ADMTECH_TEC_ADMIN`, `ADMTECH_TEC_MATERIALES`, `ADMTECH_TEC_LOGISTICA`, `ADMTECH_TEC_REQUIRENTE`, `ADMTECH_TEC_AUDITORIA` |

✅ Se pidió una aplicación **nueva** en lugar de reutilizar la de producción (servicio 23141, `infra.personal.com.py/adm/`). El motivo es que `index.php` llama a `.../oauth/authorize/?client_id=...` sin `redirect_uri`, y SDI devuelve al usuario a la única URL registrada para ese client_id. Con la aplicación de producción, el login terminaría en `tec-calidad05`. Además, así se rotan las credenciales, porque el secreto actual quedó expuesto en ese servidor.

**Escaneo durante el alta:** Jerure escaneó `10.143.11.8` (26/10 16:04) e informó un solo hallazgo: **43743** *HSTS Missing From HTTPS Server*, criticidad Baja. Se corrigió el mismo día y se declaró RESUELTO en el ticket 778 **#1083416**. El hallazgo no bloqueó la aprobación. Ver [`laboratorio/2026-10-26_hsts-pfr-gw-srv/`](../laboratorio/2026-10-26_hsts-pfr-gw-srv/).

> **Nota:** desde el 2026-10-26 `/adm/` es accesible desde cualquier IP, con el ingreso de desarrollo activo (decisión del responsable). Ver la [bitácora de la Fase 3](../laboratorio/2026-10-24_migracion-admtech-lxd/bitacora_fase3.md#acceso-abierto-a-cualquier-ip-2026-10-26).

---

## Pendientes

| # | Ticket | Pendiente | Estado |
|---|---|---|---|
| 1 | #1083104 Vulnapp-OSS | La descripción cargada habla del servidor viejo (`tec-calidad05`, PostgreSQL local, Apache). Corregirla para que diga que corre en `PFR-VULNAPP-APP` y `PFR-VULNAPP-DB`, publicada por el gateway | 🔴 Pendiente |
| 2 | #1083088 y #1083104 | "Permiso: Local" con "Administrador: SSO" no coinciden. Con usuarios locales, el administrador de accesos es OSS | 🔴 Pendiente |
| 3 | #1083088 Kanboard-OSS | El campo "Especificar" repite la descripción en lugar de detallar el permiso (usuarios locales; roles Administrador, Gerente y Usuario; permisos por proyecto). El tipo debería ser FRONTEND | 🔴 Pendiente |
| 4 | — | Evaluar con SDI si hay que declarar como servicios de tipo CONSOLA el acceso administrativo de los nodos: API de LXD (`8443/tcp`) y SSH (`22/tcp`), si se alcanzan desde la red corporativa | 🔴 Pendiente |
| 5 | #1083088 y #1083104 | Completar la fecha de finalización cuando se resuelvan | 🔴 Pendiente |
| 7 | #1083324 ADM-TECH-OSS | El campo "Especificar" quedó solo con el primer párrafo. Completar con los grupos de AD, el alta automática en el primer ingreso y el ingreso de prueba que se elimina antes del pase | 🔴 Pendiente |
| 8 | #1083324 ADM-TECH-OSS | Al pasar a producción: actualizar la descripción (contenedores `PFR-ADMTECH-*`, sin ingreso de prueba, datos oficiales). 🟡 El ticket ya está resuelto, así que probablemente haga falta un ticket nuevo para modificar el registro (confirmar con Seguridad cómo se actualiza un servicio ya inventariado) | 🔴 Pendiente |
| 6 | #1047036 | La descripción de la aplicación 608 dice "dos sitios" y hoy son tres. Evaluar si corresponde actualizarla en Jerure | 🟡 A evaluar (observación del repositorio, no del ticket) |

---

## Documentos relacionados

| Tema | Documento |
|---|---|
| Procedimiento y criterio de inventario | [06_Operacion.md](06_Operacion.md#inventario-hacia-ciberseguridad-jerure-ip-de-servicio--puerto--url) |
| IP de entrada y de salida para permisos de firewall | [02_Arquitectura.md](02_Arquitectura.md#ip-que-ve-el-firewall-corporativo-entrada-y-salida) |
| Tickets abiertos y próximos pasos | [PENDIENTES.md](../PENDIENTES.md) |
