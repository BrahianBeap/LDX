# Pendientes — por dónde retomar

> Actualizado al **2026-10-26**. Resumen de trabajo en curso para retomar rápido.
> El detalle de cada riesgo está en [`docs/11_Riesgos.md`](docs/11_Riesgos.md) y los hitos en [`docs/13_Linea_de_Tiempo.md`](docs/13_Linea_de_Tiempo.md).
> Al cerrar un ítem, tacharlo acá y registrarlo en [`CHANGELOG.md`](CHANGELOG.md).

## 0. Primero, al retomar

- [x] **Push** de los commits del 26/10 (`b773dff`, `e545b5f`, `bbc8c39`, `7aeb757`) hecho el 26/10.
- [x] **Copiar las 2 transcripciones** de Descargas a `reunion/` con los nombres registrados en [`reunion/README.md`](reunion/README.md) (copiadas el 26/10, hash verificado).
- [ ] Revisar el estado de los tickets Jerure abiertos (tabla de la sección 1).

## 1. Tickets Jerure en curso

| Ticket | Tema | Estado al 24/10 | Próximo paso |
|---|---|---|---|
| #1076072 | 447 Alta servidor virtual `PFR-GW-SRV` | 🟡 En verificación de SDI | Si Abel insiste con SSH: la verificación se hace con `lxc exec` desde `10.143.11.228` ([TRB-018](docs/07_Troubleshooting.md)) |
| #1078719 | 451 Certificado `oss.personal.com.py` | ✅ Resuelto 22/10 (Natalia Cardozo). Let's Encrypt, vence **2027-01-20** | Instalado el 26/10 en los 3 gateways. Renovación: Ciberseguridad reabre el ticket cada 3 meses ([RIE-022](docs/11_Riesgos.md)). Detalle: [`laboratorio/2026-10-26_certificado-lets-encrypt/`](laboratorio/2026-10-26_certificado-lets-encrypt/) |
| #1079305 | 741 DNS `oss.personal.com.py` | 🟡 Cargada solo `10.143.11.8` (Abel) | Pedir `192.168.91.117` y `10.11.11.12` **recién después de la Etapa 2** |
| #1083298 | 778 Gestión de vulnerabilidades: hallazgos de certificado de los 3 gateways, **RESUELTO** (IDs Grafana 41817, 41818 `fr-oss`; 40608, 40609 `car-oss`; 41771, 41772 `fdo-dns-lxd`) | 🟡 Abierto 26/10 14:59 | Seguir hasta que Seguridad lo cierre y el próximo escaneo los dé de baja. Si aparece "nombre de host incorrecto" (escaneo por IP), responder que el servicio se publica como `oss.personal.com.py`. Evidencia: `evidencia_certificado_oss_20261026.txt` |
| Gestión de vulnerabilidades (778), aceptación del 16/10 | Aceptación de riesgo de certificados | 🟡 Revisión al 16/11/2026 | Queda superada por #1083298: cerrarla con esa referencia. LXD (8443/8444/8555): aceptación aparte, revisión semestral |
| #1083088, #1083104, #1083324 | 452 Alta de servicios `Kanboard-OSS`, `Vulnapp-OSS` y `ADM-TECH-OSS` | 🟡 Pendiente de aprobación / Abierto (26/10) | Correcciones pendientes (descripción de VulnApp, administrador de accesos, tipo y permiso de Kanboard): ver [18_Inventario_Ciberseguridad.md](docs/18_Inventario_Ciberseguridad.md#pendientes) |
| #1083155 | Firewall VulnApp NG → API SDI `10.150.58.116:443` (origen: IP de gestión de los 3 hosts) | 🟡 Abierto 26/10 | Cuando lo aprueben, repetir la prueba de `/health` desde `PFR-VULNAPP-APP` e instalar el servicio de carga ([RIE-015](docs/11_Riesgos.md)). **Vence 31/05/2027**: pedir renovación antes |
| #1075028 | Acceso BD Oxígeno | ✅ Habilitado 14/10 | — |
| #1076134 | 939 IP de servicio al activo `fr-oss` | ✅ Resuelto 16/10 | — |

## 2. Certificado y DNS (orden obligatorio)

1. [x] Recibir el certificado (#1078719): entregado el 22/10, verificado el 26/10 (cadena OK, clave coincide, SAN `oss.personal.com.py`).
2. [x] **Tembiapó primero** (único cliente de NTF, confirmado por Norberto el 24/10): hoy fija la CA (`CURLOPT_CAINFO` = solo `AutoridadOSS`) y se cortaría con el certificado nuevo. `ntf-ca.crt` creado y probado el 26/10 (HTTP 200). Daniel Medina cambió la ruta en los **6** lugares del servidor (4 `enviar_sms.php` + `'cainfo'` de `class_fs.php` y `class_ingreso.php`), verificado el 26/10; SMS real OK antes y después del cambio (26/10) ([detalle](laboratorio/2026-10-26_certificado-lets-encrypt/README.md#lado-del-cliente-tembiapó-10111124-relevado-el-2026-10-26)).
3. [x] **Coordinar la ventana con Daniel Medina (Tembiapó) y Marcos Casco antes del reload.** Tembiapó consume NTF por Fernando (`10.11.11.12`) y hoy confía en el certificado de `AutoridadOSS` (reunión del 24/10). ✅ Hecha el 26/10 con Daniel Medina presente.
4. [x] Instalar el certificado en los **3 gateways a la vez** (`lxc file push` + `apache2ctl configtest` + `systemctl reload apache2`), con el procedimiento de [06_Operacion.md — Modificar el LB.conf de un gateway de forma controlada](docs/06_Operacion.md). En el mismo cambio, reemplazar la línea `SSLCipherSuite` heredada ([RIE-019](docs/11_Riesgos.md)). ✅ **Instalado el 26/10** en PFR, CAR y FDO (TLS 1.2/1.3, cifrados nuevos); detalle en [`laboratorio/2026-10-26_certificado-lets-encrypt/`](laboratorio/2026-10-26_certificado-lets-encrypt/).
   - Hecho además el 26/10: redirección de HTTP a HTTPS y del acceso por IP al nombre en los 3 gateways (ver la bitácora del certificado).
   - [x] Informar los hallazgos como resueltos: ticket 778 **#1083298** (26/10). Falta que Seguridad lo cierre y que el escaneo los dé de baja.
   - [ ] **Renovación:** Ciberseguridad reabre el ticket de Jerure cada 3 meses. Cuando llegue (antes del 20/01/2027), instalar en los 3 gateways ([RIE-022](docs/11_Riesgos.md)).
   - [ ] Opcional: HSTS (`max-age` corto al principio); pasar las redirecciones de 302 a 301; quitar `AutoridadOSS` de `ntf-ca.crt` en Tembiapó.
   - [ ] Sincronizar el repo de Tembiapó con producción (tarea de Daniel Medina).
5. [ ] **Etapa 2:** reescribir los `LB.conf` de `CAR-GW-SRV` y `FDO-GW-SRV` con el modelo de PFR: Kanboard y VulnApp NG por **proxy interno** hacia `192.168.0.106` / `192.168.0.14:5000` (no `Redirect`), `require` explícito en `/ntf` y `/supervisionge`, y bloqueo de `web.config`. Antes, probar el cliente de NTF con Norberto ([RIE-020](docs/11_Riesgos.md)).
6. [ ] Pedir a Abel que sume las IP de CAR y FDO al DNS.
7. [ ] Definir el nombre propio para Comap (`/supervisionge`, solo hacia Fernando).

## 3. Inventario (checklist de alta)

- [ ] Recorrer el checklist completo para los **3 servidores** (hosts `fr-oss`, Carpinelli y Fernando). Falta conocer el nombre y la IP de gestión de Carpinelli y Fernando, y si ya existen como activos en Jerure.
- [ ] Por cada servicio (Kanboard, VulnApp NG; NTF y Loki a confirmar con Norberto): 452 Alta de servicios, 707 Alta de aplicaciones, 623 OAuth + grupos AD, pase a producción.
- [ ] Inventariar cada aplicación con **IP de servicio + 443 + URL** (`https://oss.personal.com.py/<app>`), no con la IP del contenedor (indicación de Norberto, 16/10).
- [x] VulnApp NG: regla de firewall hacia la API de SDI `10.150.58.116:443` ([RIE-015](docs/11_Riesgos.md)): pedida en #1083155 (26/10).
- [ ] Armar el **Gantt** (borrador en la conversación del 22/10) cuando estén las fechas de los tickets de nivel servidor (535, 404, 500, IPAM, SIEM) y la de la 2.ª reunión.

## 4. Seguridad y operación del clúster

- [ ] Métricas de LXD sin autenticación: confirmar con Observabilidad quién las lee, registrar su certificado y activar `core.metrics_authentication` ([RIE-018](docs/11_Riesgos.md)).
- [ ] Snapshots programados para los 3 gateways ([RIE-021](docs/11_Riesgos.md)).
- [ ] Subir `limits.memory` de `CAR-GW-OAM`, `FDO-GW-SRV` y `FDO-WS-1` ([RIE-017](docs/11_Riesgos.md)).
- [ ] Ponerle límites de CPU y memoria a `PFR-KANBOARD-TEST`.
- [ ] Avisar al mantenedor de VulnApp NG que `02_instalar_app.sh` debe generar `--forwarded-allow-ips` con las 3 IP de los gateways.
- [ ] Revisar si se retira el reenvío heredado `8080/tcp → 192.168.0.106` en `PFR-GW-SRV`.
- [ ] Usar `lxc exec -n` en todas las automatizaciones (consejo de Norberto, causa de [TRB-017](docs/07_Troubleshooting.md)).

## 4b. Kanboard en `/kanboard/` y portal

- [x] **Portal de aplicaciones** en la raíz (`/var/www/html/index.html` de los gateways): **Kanboard y VulnApp NG** (las activas y propias de LXD). ✅ Publicado el 26/10 en los 3 gateways; código en [`proyectos/portal-oss/`](proyectos/portal-oss/) ([bitácora](laboratorio/2026-10-26_kanboard-subruta/README.md)).
- [ ] Cargar en Kanboard la URL de la aplicación `https://oss.personal.com.py/kanboard/` (hoy vacía), para que los enlaces de correo y Telegram usen el nombre.
- [ ] Actualizar la colección de Postman de [`recursos/kanboard-api/`](recursos/kanboard-api/) a `/kanboard/jsonrpc.php`, y avisar a los clientes de la API; después retirar el `ProxyPass /jsonrpc.php` temporal.
- [ ] Al actualizar Kanboard de versión: volver a agregar `RewriteCond %{REQUEST_FILENAME} !-d` en su `.htaccess`.
- [x] Tema **OssTheme** en producción (26/10); Customizer y Essential desactivados. Pendientes de prueba manual y retiro de `PFR-KANBOARD-PRUEBA` + `/kanboard-prueba/`: ver [`laboratorio/2026-10-26_kanboard-tema-osstheme/`](laboratorio/2026-10-26_kanboard-tema-osstheme/).

## 5. Migraciones y cargas nuevas

- [ ] **ADM-TECH → LXD** (plan en [`laboratorio/2026-10-24_migracion-admtech-lxd/`](laboratorio/2026-10-24_migracion-admtech-lxd/README.md), refactor en el repo `adm-tech`: `knowledge/06_Roadmap/plan_migracion_lxd_php85.md`):
  - [x] Fase 1: relevamiento (24/10).
  - [ ] Aprobar el diseño de la Fase 2: `PFR-ADMTECH-APP` / `PFR-ADMTECH-DB` en `PRJ-OSS`, volumen de 40 GiB, IP `.15`/`.16` (confirmar libres).
  - [ ] **Correo saliente:** antes de pedir un servidor nuevo, preguntarle a Norberto si **`CAR-SystemSMTP`** (Postfix ya existente en `car.1`, `192.168.0.16`) puede hacer de relay de salida para ADM-TECH. Si no, pedir el servidor nuevo (relay SMTP autenticado con TLS, saliendo por el relay de Seguridad). ADM-TECH pasa a enviar sus propios correos (hoy lo hace un cron de Apache en tec-calidad05).
  - [x] ~~Fase 3: entorno de desarrollo~~ — listo el 25/10 ([bitácora](laboratorio/2026-10-24_migracion-admtech-lxd/bitacora_fase3.md)).
  - [ ] **Probar ADM-TECH en `https://10.143.11.8/adm/`** (login usuario/clave) y revisar los 11 commits de `feature/php85` (worktree `adm-tech-php85`, sin push; sale de `fix/seguridad-tanda2`, no de `master`).
  - [ ] ⚠️ **`/adm/` abierto a cualquier IP desde el 26/10 con el ingreso de desarrollo activo** (decisión del usuario). Antes de usar datos oficiales o del pase: quitar las `SetEnv ADM_*` del vhost `adm-dev.conf` ([bitácora](laboratorio/2026-10-24_migracion-admtech-lxd/bitacora_fase3.md#acceso-abierto-a-cualquier-ip-2026-10-26)).
  - [ ] Pendiente del refactor: Composer y actualización de librerías (confirmar si se completó), PHPCompatibility/PHPStan en limpio.
  - [ ] Confirmar que ningún proceso externo carga los datos de SAP (el usuario cree que no; serían cargas manuales desde la app).
  - [ ] Fase 3: entorno de desarrollo (PHP 8.5 + PG 18). Fase 4: rama `feature/php85`.
  - [ ] Actualizar la aplicación OAuth a la URL `oss.personal.com.py/adm` (ticket 623) y rotar credenciales.
- [ ] Contenedores de **Infrawork** (después de ADM-TECH, mismo esquema). **FileRoom (~800 GB) queda en tec-calidad05** por ahora.
- [ ] Evaluar centralizar las bases de datos del área en el servidor de Norberto, y usar su servicio **S3** (bucket ya creado, credenciales en PasswordSafe).
- [ ] Prueba de envío de SMS por NTF desde Infrawork (quedó pendiente un OK; Norberto revisa el correo).
- [ ] Análisis de contratos con LLM (Legales/Compras vs. PDF): probar localmente primero.
- [ ] A cargo de otros, con impacto en capacidad: servidor de correo entrante para permisos de ingreso (Norberto, requiere puerto 25 con TLS) y contenedor OSRM con Docker (pedido de Marcos).

## 6. Reporte de Torreras (tarea Kanboard #175)

- [ ] Fecha estimada de on air: confirmar la fuente con Ingeniería.
- [ ] Armar el script de extracción en modo solo lectura (Oxígeno + Infraestructura) que genere la tabla, los gráficos y el listado del slide 5. El modelo está acordado en el comentario de la tarea #175 (14/10).
- [ ] Unificación de nombres en Infrawork (Claro → SITE LATAM, LATI, ATIS): **no tocar** sin adaptar antes el código de pagos y devengamiento.

## 7. Documentación pendiente

- [x] ~~Reuniones del 16/10 y 24/10 (Fases 2-4)~~ — documentadas el 24/10 (ADR-0009, 05/06/07/10/11/13, índice de reuniones).
- [ ] Revisar a mano los ~20 enlaces internos antiguos que marcó el chequeo del 16/10 (ej. `#trb-012`).
