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

```
 Aplicación 608  PLATAFORMA-LXD-OSS  (707 #1047036)
        │
        ├── Servicio Kanboard-OSS  (452 #1083088)  ─┐
        │                                            ├─ host: activo 10041 fr-oss (10.143.11.8)
        └── Servicio Vulnapp-OSS   (452 #1083104)  ─┘     = gateway PFR-GW-SRV
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

## Pendientes

| # | Ticket | Pendiente | Estado |
|---|---|---|---|
| 1 | #1083104 Vulnapp-OSS | La descripción cargada habla del servidor viejo (`tec-calidad05`, PostgreSQL local, Apache). Corregirla para que diga que corre en `PFR-VULNAPP-APP` y `PFR-VULNAPP-DB`, publicada por el gateway | 🔴 Pendiente |
| 2 | #1083088 y #1083104 | "Permiso: Local" con "Administrador: SSO" no coinciden. Con usuarios locales, el administrador de accesos es OSS | 🔴 Pendiente |
| 3 | #1083088 Kanboard-OSS | El campo "Especificar" repite la descripción en lugar de detallar el permiso (usuarios locales; roles Administrador, Gerente y Usuario; permisos por proyecto). El tipo debería ser FRONTEND | 🔴 Pendiente |
| 4 | — | Evaluar con SDI si hay que declarar como servicios de tipo CONSOLA el acceso administrativo de los nodos: API de LXD (`8443/tcp`) y SSH (`22/tcp`), si se alcanzan desde la red corporativa | 🔴 Pendiente |
| 5 | #1083088 y #1083104 | Completar la fecha de finalización cuando se resuelvan | 🔴 Pendiente |
| 6 | #1047036 | La descripción de la aplicación 608 dice "dos sitios" y hoy son tres. Evaluar si corresponde actualizarla en Jerure | 🟡 A evaluar (observación del repositorio, no del ticket) |

---

## Documentos relacionados

| Tema | Documento |
|---|---|
| Procedimiento y criterio de inventario | [06_Operacion.md](06_Operacion.md#inventario-hacia-ciberseguridad-jerure-ip-de-servicio--puerto--url) |
| IP de entrada y de salida para permisos de firewall | [02_Arquitectura.md](02_Arquitectura.md#ip-que-ve-el-firewall-corporativo-entrada-y-salida) |
| Tickets abiertos y próximos pasos | [PENDIENTES.md](../PENDIENTES.md) |
