# Migración de ADM-TECH al clúster LXD (relevamiento y diseño, 2026-10-24)

> Estado: **Fase 1 (relevamiento) completa · Fase 2 (diseño) propuesta, pendiente de aprobación · nada creado todavía.**
> El código y su documentación funcional viven en el repositorio de la aplicación (`gitlab.personal.com.py/oss_py/adm_tech/adm-tech`, carpeta `knowledge/`). Este documento cubre solo la **plataforma**. El plan de refactor del código está en ese repo: `knowledge/06_Roadmap/plan_migracion_lxd_php85.md`.

## Objetivo

Sacar ADM-TECH de `tec-calidad05` (VM CentOS 7 compartida con Infrawork, PHP 5.6 y PostgreSQL 10, todo sin soporte) y llevarlo a contenedores LXD en Franco (`pfr.1`): uno para la aplicación, otro para la base, y un volumen aparte para los archivos. Además, que las próximas actualizaciones de PHP o PostgreSQL se hagan sin repetir una migración (ver [06_Operacion.md — Actualizar la versión de PHP o PostgreSQL de una aplicación](../../docs/06_Operacion.md#actualizar-la-versión-de-php-o-postgresql-de-una-aplicación-azulverde)).

## Fase 1 — Relevamiento (✅ 2026-10-24, solo lectura)

Fuentes: consultas en `tec-calidad05` (`10.129.2.165`) con `alfonzel_opr`, consultas de solo lectura a PostgreSQL, y el repositorio `adm-tech` (242 commits, documentación en `knowledge/`). Ningún cambio en el servidor.

### Plataforma actual

| Componente | Versión | Soporte |
|---|---|---|
| SO | CentOS 7.7 | Sin soporte desde 06/2024 |
| Apache | 2.4.6 | — |
| PHP | 5.6.40 (paquetes remi) + ionCube Loader cargado | Sin soporte desde 12/2018 |
| PostgreSQL | 10.12 | Sin soporte desde 11/2022 |

Configuración de PHP relevante: `memory_limit=512M`, `upload_max_filesize=50M`, `post_max_size=50M`, `max_execution_time=0`, `short_open_tag=On`, `date.timezone=America/Asuncion`.

### Código (`/var/www/html/adm`)

- **~210 archivos PHP propios** (205 en la raíz, `migo_notificacion/`, `certificados/`). Los ~1.040 restantes son librerías de terceros en `assets/dist/plugins/` y `vendor/`.
- **Sin archivos cifrados con ionCube**: todo el código es modificable.
- Versionado en git (GitLab) y desplegado **copiando archivos a mano** al servidor.
- Detalle de lo que hay que corregir para PHP 8.5: en el plan del repo de la aplicación.

### Archivos (`/var/www/html/adm/archivos`)

| Dato | Valor |
|---|---|
| Tamaño | **7,2 GB**, 9.317 archivos (casi todo en `doc_reservas/`) |
| Tipos | PDF (5.768), XLSX (1.093), imágenes (~1.750), correos `.msg` (519), DOCX, CSV |
| Crecimiento | 2,2 MB en 2024 · 1,4 GB en 2025 · **5,9 GB en 2026 (hasta octubre)** — más de 7 GB/año y acelerando |
| Permisos | Dueño UID 1001, grupo `apache`, `2775` (setgid) |
| Riesgo | Hay un `.php` dentro (`doc_reservas/cambio_estado_backend.php`) que Apache ejecuta. Hay una corrección preparada y no aplicada (`zz-adm-archivos.conf`) |

### Base de datos (base `postgres`)

| Dato | Valor |
|---|---|
| Tamaño | **71 MB** (UTF8, `es_PY.UTF-8`) |
| Esquemas | `reserva` (83 tablas, 2 vistas, 56 secuencias, 11 funciones, 17 triggers), `aud` (1 tabla), `public` (1 tabla) |
| Tabla más grande | `reserva.historial` (26 MB, ~142.000 filas) |
| Extensiones | Solo `plpgsql`. Sin `dblink` ni FDW |
| Dueño de todos los objetos | `postgres` (superusuario). **La aplicación se conecta como superusuario** |

Riesgo de pasar a PostgreSQL 18: **bajo** (base chica, sin extensiones). Hay que probar las consultas de la aplicación contra la versión nueva.

### Dependencias externas (🔴 críticas para la migración)

Tomadas de `knowledge/01_Arquitectura/integraciones.md` del repo de la aplicación y verificadas en el código:

| Dependencia | Cómo funciona hoy | Qué implica al migrar |
|---|---|---|
| **Correo** | `enviarMail()` **no envía**: inserta en `Infraestructura.public.mail_historial` (otra base del mismo servidor) y registra adjuntos en `reserva.mail_adjunto`. ✅ Confirmado por el usuario (2026-10-24): **un cron de Apache en `tec-calidad05`** lee esa cola y envía | ✅ Decisión: **se pedirá un servidor de correo nuevo**. Diseño propuesto: ADM-TECH envía sus propios correos (cola en su base, cron dentro del contenedor, adjuntos desde el volumen) usando el servidor nuevo como relay SMTP. Así desaparece la dependencia de `Infraestructura` y del cron de `tec-calidad05`, que sigue funcionando para Infrawork. **Reemplazada el 2026-10-29:** no se pide un servidor nuevo; ADM-TECH envía por el módulo de email de NTF ([ADR-0010](../../docs/adr/ADR-0010-envio-correo-sistemas-via-ntf.md)) |
| **Datos de SAP** | Tablas de `reserva` con datos de SAP (MIGO 101/281, `fecha_salida_sap`, `adm_inicial_detalle`, `deposito_salida_detalle`) | 🟡 Según el usuario, probablemente **ningún proceso externo** las carga: la aplicación tiene pantallas de carga manual (`csv_cargar_*`, carga de MIGO 101/281). Confirmarlo en la Fase 3. Si es así, no hay nada que redirigir |
| **Login OAuth** | Contra `ciberseg.personal.com.py/ad/login/oauth/`, con `ADM_CLIENT_ID`/`SECRET` | La URL de retorno cambia de `infra.personal.com.py/adm` a `oss.personal.com.py/adm`: hay que actualizar la aplicación OAuth (ticket 623). El contenedor necesita salida HTTPS hacia `ciberseg.personal.com.py` |
| **Notificaciones MIGO** | Scripts en `migo_notificacion/`, pensados para cron. No se pudo ver quién los programa (no hay sudo) | Confirmar la programación real y recrearla en el contenedor |

### Hallazgos de seguridad

- El vhost de Apache con la contraseña de la base y el secreto de OAuth **es legible sin sudo** por usuarios operativos. En el relevamiento, una búsqueda los imprimió por accidente; se borraron de la salida local.
- El superusuario `postgres` usa una contraseña trivial y es el que usa la aplicación.

**Acción:** en la migración, rotar las dos credenciales y crear un usuario de base propio de la aplicación, sin privilegios de superusuario.

## Fase 2 — Diseño propuesto (🟡 pendiente de aprobación)

```
                 PFR-GW-SRV (10.143.11.8)  ── /adm ──┐
                 CAR/FDO-GW-SRV (Etapa 2)  ── /adm ──┤ proxy interno por OVN_1
                                                      ▼
 pfr.1 · PRJ-OSS ┌──────────────────────────────┐        ┌──────────────────────┐
                 │ PFR-ADMTECH-APP 192.168.0.16 │──5432──▶│ PFR-ADMTECH-DB       │
                 │ Ubuntu 26.04 · Apache + PHP 8.5│        │ 192.168.0.15 · PG 18 │
                 │ /var/www/adm/archivos ◀──┐   │        └──────────────────────┘
                 └──────────────────────────┼───┘
                          volumen admtech-archivos (ZFS "local", 40 GiB, PHP desactivado)
   Salidas: ciberseg.personal.com.py:443 (OAuth) · 10.129.2.165:5432 (Infraestructura, cola de correo)
```

| Elemento | Propuesta | Motivo |
|---|---|---|
| Proyecto LXD | `PRJ-OSS` | Mismo criterio que VulnApp NG |
| `PFR-ADMTECH-DB` | Ubuntu 26.04, **PostgreSQL 18 desde el repositorio oficial PGDG**, 1 vCPU / 1 GiB / raíz 10 GiB, IP fija `192.168.0.15` | PGDG permite elegir la versión de PostgreSQL sin depender del SO. Base de 71 MB |
| `PFR-ADMTECH-APP` | Ubuntu 26.04, Apache + `libapache2-mod-php` (PHP 8.5), 1 vCPU / 1 GiB / raíz 10 GiB, IP fija `192.168.0.16` | Criterio de Norberto: arrancar con poco y ajustar por uso real |
| Volumen `admtech-archivos` | Pool `local`, **40 GiB**, montado en la carpeta de adjuntos de la app | 7,2 GB hoy y +7 GB/año. Separa los datos del ciclo de vida del contenedor |
| Configuración | Vhost propio con `SetEnv` (o archivo de entorno con permisos `640 root:www-data`), **sin credenciales en el repo** | Reemplaza las variables del vhost compartido con Infrawork |
| Usuario de base | `admtech_app`, dueño del esquema `reserva`, sin superusuario | Hoy la app usa `postgres` |
| ACL `ACL-OVN-1` | `.16 → .15:5432`; gateways `.1,.2,.4 → .16:80`; `.16 → ciberseg.personal.com.py:443`; `.16 → servidor de correo nuevo:25/587` | Mínimo necesario, regla por par origen → destino. Con el envío propio ya no hace falta salir hacia `10.129.2.165:5432` |
| Correo | Cron dentro de `PFR-ADMTECH-APP` que procesa la cola de ADM-TECH y envía por SMTP (autenticado, TLS) al servidor de correo nuevo | Cola, adjuntos y envío en el mismo lugar |
| Gateway | `ProxyPass /adm http://192.168.0.16/adm` en `LB.conf` (procedimiento controlado) | Mismo patrón que `/vulnapp` |
| Snapshots | Base y volumen: cada 6 h, retención 7 días. App: antes de cada despliegue | Mismo criterio que Kanboard |
| Despliegue del código | Script que toma una **etiqueta git** del repo (no copia manual de archivos) | Saber siempre qué versión corre |

> **Corrección (verificado 2026-10-24):** `.16` **ya está en uso** por `CAR-SystemSMTP`. La app de producción pasa a **`192.168.0.17`** (el diagrama y la tabla de arriba dicen `.16`: leer `.17`). El entorno de desarrollo usa `.18` (DB) y `.19` (APP).

### Servidor SMTP ya existente en el clúster: `CAR-SystemSMTP`

Encontrado al verificar las IP (2026-10-24, solo lectura). No estaba documentado.

| Dato | Valor |
|---|---|
| Ubicación | `car.1`, proyecto `PRJ-OSS`, `192.168.0.16`, perfil `CAR-SystemSMTP` ("Perfil servicio SMTP de sistema") |
| Software | Postfix 3.10 escuchando en el puerto 25 |
| Configuración | Recibe correo para `oss.personal.com.py` (`mydestination`), con `transport_maps`; relay solo para localhost o clientes autenticados (SASL); `relayhost` vacío; certificado TLS *snakeoil* |
| Interpretación | 🟡 Es muy probablemente el **servidor de correo entrante** que propuso Norberto Núñez para los permisos de ingreso (reunión del 16/10) |

**Implicancia:** antes de pedir un servidor de correo nuevo, consultar a Norberto si `CAR-SystemSMTP` puede funcionar también como relay de **salida** para ADM-TECH (con autenticación SASL desde `.17` y `relayhost` hacia el relay de Seguridad). Puede que no haga falta pedir nada.

> ✅ **Respondido el 2026-10-29** (llamada con Norberto Núñez): no hace falta pedir nada ni usar `CAR-SystemSMTP`. ADM-TECH envía por el **módulo de email de NTF**, llamando a su API con el remitente `adm-tech@personal.com.py`. Por eso, en la tabla de arriba, la regla de ACL `.17 → servidor de correo nuevo` y el cron de envío propio ya no aplican: `enviarMail()` pasa a llamar a NTF. Los destinatarios externos dependen del relay SMTP de Seguridad, que está pendiente. Ver [ADR-0010](../../docs/adr/ADR-0010-envio-correo-sistemas-via-ntf.md) y [RIE-023](../../docs/11_Riesgos.md#rie-023--correo-de-los-sistemas-sin-relay-hacia-destinatarios-externos).

## Fases siguientes

| Fase | Contenido | Estado |
|---|---|---|
| 3. Entorno de desarrollo | Contenedores de prueba con PHP 8.5 y PostgreSQL 18, copia de la base y una muestra de archivos | ✅ Listo 2026-10-25 — `https://10.143.11.8/adm/` (solo 10.150.60.85). Ver [`bitacora_fase3.md`](bitacora_fase3.md) |
| 4. Modernización | Rama `feature/php85` en el repo de la aplicación (plan en su `knowledge/`) | 🟡 11 commits locales, desplegados en desarrollo; falta la prueba funcional del usuario |
| 5. Migración a producción | Crear la plataforma, copiar los archivos, dump y restore de la base, correo por NTF, corte | 🔴 Pendiente — ya no depende de un servidor de correo nuevo (ADR-0010). Falta adaptar `enviarMail()` a la API de NTF y, para destinatarios externos, el relay de Seguridad |
| 6. Cierre | Retirar ADM-TECH de `tec-calidad05`, inventario en Jerure (452, 707, OAuth 623) | 🟡 En curso — 452 #1083324 resuelto (28/10); OAuth 623 #1084774 abierto (28/10). Ver [18_Inventario_Ciberseguridad.md](../../docs/18_Inventario_Ciberseguridad.md) |

Detalle de las consultas ejecutadas: [`bitacora.md`](bitacora.md).
