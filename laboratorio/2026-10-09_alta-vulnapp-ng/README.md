# Alta de VulnApp NG en PRJ-OSS (2026-10-09)

## Objetivo

Alojar **VulnApp NG** (reemplazo de una aplicación legacy de inventario de hosts/vulnerabilidades) en un solo sitio del cluster (Franco, `pfr.1`), sin alta disponibilidad, publicada por el gateway de ese sitio bajo `/vulnapp`. La decisión de arquitectura de la aplicación (dos contenedores, sin HA, DEC-042) se tomó en el repositorio de la aplicación (`DockerLab/vulnapp-ng`), no en este; aquí se documenta el lado de la plataforma LXD.

Previo a este trabajo se hizo una investigación de factibilidad **solo lectura** (sin crear nada), respondiendo primero 10 y luego 19 preguntas puntuales sobre el estado del cluster, para validar que alojar la app era viable antes de construir nada. Ese intercambio no quedó grabado como documento separado; el resultado se refleja directamente en las decisiones de este alta.

## Qué se creó en la plataforma

| Elemento | Detalle |
|---|---|
| Perfil `PRF-VULNAPP-DB` | Ubuntu 26.04, 2 vCPU, 2 GiB RAM, 20 GB disco, red `OVN_1` |
| Perfil `PRF-VULNAPP-APP` | Igual especificación, agrega la ruta `10.150.0.0/16` vía `192.168.0.6` (necesaria para llegar a SDI y al SMS) |
| Contenedor `PFR-VULNAPP-DB` | `192.168.0.13`, PostgreSQL 18, base `vulnapp` |
| Contenedor `PFR-VULNAPP-APP` | `192.168.0.14`, Gunicorn en el puerto 5000, código en `/opt/vulnapp` |
| 4 reglas nuevas en `ACL-OVN-1` | app→db (5432), gateway→app (5000), app→SDI (443), app→SMS (80) — ver [05_Configuracion.md — Firewall de la red `OVN_1`](../../docs/05_Configuracion.md#firewall-de-la-red-ovn_1-lxc-network-acl) |
| Bloque nuevo en `LB.conf` de `PFR-GW-SRV` | `ProxyPass /vulnapp` hacia `192.168.0.14:5000`, antes de la regla general de Kanboard |
| `snapshots.schedule`/`snapshots.expiry` en `PFR-VULNAPP-DB` | Mismo patrón que Kanboard: cada 6 h, retiene 7 días |

Comandos reales (perfiles completos, `lxc launch`, las 4 reglas de ACL) en el [paso 0 de la bitácora](bitacora.md#0-creación-de-la-plataforma-perfiles-contenedores-acl-snapshot).

La instalación **dentro** de los contenedores (PostgreSQL, el dump, el entorno virtual de Python, Gunicorn) la hacen los scripts del propio paquete de la aplicación (`vulnapp-ng/runbook/lxd/`, repositorio `DockerLab`) — no son parte de este repositorio y no se versionan acá.

## Resultado final

✅ Aplicación accesible en `https://10.143.11.8/vulnapp/login` (200) y `/vulnapp/dashboard` (redirige a `/vulnapp/login` conservando el prefijo, como se espera sin sesión). ✅ Kanboard, Loki y NTF siguen funcionando sin cambios en el mismo gateway. 🔴 La carga diaria desde la API de SDI (`03_instalar_carga.sh`) **no se ejecutó** — el contenedor no tiene salida hacia `10.150.58.116:443` (ver más abajo); la pasarela de SMS (`10.150.31.68:80`) sí responde.

## Tres problemas encontrados (dos en los scripts de la aplicación, uno en la plataforma)

Dos son bugs del paquete de instalación de la aplicación (repositorio `DockerLab/vulnapp-ng`, corregidos por su equipo); el tercero es un faltante de este gateway, corregido del lado de la plataforma.

1. **Reasignación de dueño de una secuencia vinculada a una columna** (script de base de datos). Intentaba `ALTER SEQUENCE ... OWNER TO` sobre *todas* las secuencias del esquema, incluidas las que PostgreSQL vincula automáticamente a una columna `SERIAL`/`IDENTITY` de su tabla — a esas no se les puede cambiar el dueño por separado (heredan el de la tabla). Ver [TRB-014 en 07_Troubleshooting.md](../../docs/07_Troubleshooting.md#trb-014--no-se-puede-reasignar-el-dueño-de-una-secuencia-vinculada-a-una-columna-serial-o-identity).
2. **Permisos insuficientes para que la aplicación cree su propia carpeta de `uploads/`** (script de la aplicación). El servicio corre como `www-data`, pero el directorio quedaba con el grupo en modo solo lectura/ejecución. Ver [TRB-016 en 07_Troubleshooting.md](../../docs/07_Troubleshooting.md#trb-016--permissionerror-al-crear-una-carpeta-propia-de-la-aplicación-dentro-de-un-árbol-de-solo-lectura-para-su-grupo).
3. **`mod_headers` no estaba habilitado en `PFR-GW-SRV`** (plataforma). El bloque nuevo necesitaba `RequestHeader set X-Forwarded-Proto "https"` para que la aplicación supiera que el usuario entró por HTTPS; sin el módulo, `apache2ctl configtest` rechaza la directiva. Ver [TRB-015 en 07_Troubleshooting.md](../../docs/07_Troubleshooting.md#trb-015--requestheader-falla-con-invalid-command-porque-mod_headers-no-está-habilitado).

## Pendiente

- 🔴 Conectividad hacia la API de SDI (`10.150.58.116:443`) bloqueada — ver [RIE-015 en 11_Riesgos.md](../../docs/11_Riesgos.md#rie-015--conectividad-de-vulnapp-ng-hacia-la-api-de-sdi-bloqueada). Requiere acción de Seguridad (ver detalle en la bitácora).
- 🔴 Mientras lo anterior no se resuelva, no se instala ni se activa `vulnapp-sdi.service`/`.timer` (paso 4 del runbook de la aplicación).

Ver el detalle completo, comando por comando, en [`bitacora.md`](bitacora.md).
