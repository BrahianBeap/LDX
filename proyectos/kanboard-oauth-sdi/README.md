# Plugin "OAuth2" — ingreso a Kanboard con la cuenta de AD (OAuth de SDI)

> **Fecha de inicio:** 2026-10-30
> **Estado:** ✅ v1.0.1 instalada en `PFR-KANBOARD-TEST` (producción). Ingreso con AD probado por el responsable el 2026-10-30.

## Objetivo

Que el equipo ingrese a Kanboard (`https://oss.personal.com.py/kanboard/`) con su cuenta de AD, usando la aplicación OAuth `Kanboard-OSS` que SDI creó en el ticket 623 **#1085317** (id 48). Desde el 2026-10-30 es el **único** ingreso: el login con contraseña está deshabilitado y oculto (ver [instalacion-v1.0.md](docs/decisiones/instalacion-v1.0.md#8-solo-ingreso-con-ad-formulario-oculto-y-admin-sin-contraseña-)).

## Por qué un plugin propio

El plugin oficial `OAuth2` de Kanboard no es compatible con el OAuth de SDI. El detalle está en [`docs/00_Arquitectura.md`](docs/00_Arquitectura.md#por-qué-no-sirve-el-plugin-oficial).

La carpeta se llama `OAuth2` porque la URL de retorno registrada en SDI es `?controller=OAuthController&action=handler&plugin=OAuth2`. Kanboard envía esa URL al plugin de la carpeta `plugins/OAuth2`. Con este nombre no hace falta pedir otra URL a SDI.

## Documentación

| Documento | Contenido |
|---|---|
| [`docs/00_Arquitectura.md`](docs/00_Arquitectura.md) | Cómo funciona el plugin, cómo vincula los usuarios y qué dependencias tiene |
| [`docs/decisiones/instalacion-v1.0.md`](docs/decisiones/instalacion-v1.0.md) | Cambios hechos en el cluster para la v1.0, con backups y rollback |
| [`CHANGELOG.md`](CHANGELOG.md) | Historial de versiones |
| [`src/OAuth2/`](src/OAuth2/) | Código fuente. Se despliega tal cual en `/var/www/kanboard/plugins/OAuth2/` |

## Configuración

El plugin no hace nada si faltan estas dos constantes en `/var/www/kanboard/config.php`:

```php
// Ingreso con AD por el OAuth de SDI (623 #1085317). Plugin plugins/OAuth2.
define('SDI_OAUTH_CLIENT_ID', '<client_id>');
define('SDI_OAUTH_CLIENT_SECRET', '<client_secret>');
```

> **Advertencia:** el `client_secret` **no** se guarda en este repositorio. Con el secreto cargado, `config.php` tiene que quedar con permisos `640` (era `664`, legible por cualquier usuario del contenedor; corregido el 2026-10-30).

## Pendientes conocidos

1. ✅ SDI **no** devuelve el parámetro `state` (visto el 2026-10-30). El plugin lo tolera (ver la arquitectura).
2. 🟡 La vinculación por correo funcionó para `elias.alfonzo`. Falta confirmarla con el resto del equipo.
3. Pedir a SDI que regenere el `client_secret`, que se vio en una captura de pantalla compartida.
