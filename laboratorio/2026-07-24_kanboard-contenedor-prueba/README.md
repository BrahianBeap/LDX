# Experimento: contenedor de prueba para Kanboard

> **Fecha:** 2026-07-24
> **Autor:** Elías Alfonzo (con asistencia de Claude Code)
> **Estado:** ✅ Éxito — accesible y funcional vía navegador

---

## Objetivo

Levantar la instalación local de Kanboard
(`C:\Users\alfonzel\Documents\GitHub\LXD\kamban\kanboard`, v1.2.46) como un
contenedor LXD en el cluster real (`pfr-oss`, `10.143.11.228`), para poder
probarlo vía navegador antes de decidir cómo se convierte en un servicio
permanente.

## Hipótesis de partida

- Que se podía crear un contenedor nuevo en el proyecto `PRJ-OSS` (el de
  nuestro equipo), conectarlo a la red `OVN_1`, instalarle Apache+PHP, copiar
  el código de Kanboard desde esta PC, y verlo por navegador apuntando
  directo a la IP del contenedor.

## Resultado

**Parcialmente distinto a lo previsto, pero funcional.** Dos supuestos
iniciales resultaron incorrectos y hubo que ajustar sobre la marcha (ver
[conclusiones.md](conclusiones.md) para el detalle de cada uno):

1. La IP de `OVN_1` (`192.168.0.0/24`) **no es alcanzable directamente**
   desde una PC fuera del cluster — es una red virtualizada interna.
2. El proyecto `PRJ-OSS` **prohíbe dispositivos `proxy`** (por diseño, ver
   [ADR-0007](../../docs/adr/ADR-0007-proyectos-lxd-multitenancy.md)), así
   que el contenedor de prueba se recreó en el proyecto `default`
   (sin restricciones) solo para poder exponerlo.

La forma final que funcionó: contenedor en el proyecto `default`, expuesto
únicamente a `127.0.0.1:8080` del host (no a la red pública), accedido desde
la PC del usuario vía un **túnel SSH** (`ssh -L 8080:127.0.0.1:8080`). Esto
evitó necesitar `sudo`/`firewall-cmd` en el host, algo que la cuenta usada
(`alfonzel_opr`) no tiene permitido en `pfr-oss`.

Login verificado con éxito: usuario `admin` / contraseña `admin` (la única
cuenta que existía en el `data/db.sqlite` copiado desde la instalación
local).

## Entorno

| Ítem | Valor |
|---|---|
| Host | `pfr-oss` (`10.143.11.228`), miembro `pfr.1` del cluster |
| Proyecto LXD final | `default` (se intentó primero `PRJ-OSS`, ver conclusiones) |
| Imagen base | Ubuntu 26.04 LTS "minimal" (fingerprint `40eba84d6225`, ya presente en `PRJ-OSS`) |
| Nombre del contenedor | `PFR-KANBOARD-TEST` |
| Red | `OVN_1` (`192.168.0.0/24`) |
| Stack instalado | Apache 2.4.66 + PHP 8.5.4 + SQLite |
| Fuente de la app | Copia directa de `C:\Users\alfonzel\Documents\GitHub\LXD\kamban\kanboard` (no descarga) |

## Archivos de este experimento

- [`comandos.md`](comandos.md) — cada comando ejecutado, en orden, con notas de qué hace y por qué.
- [`conclusiones.md`](conclusiones.md) — qué funcionó, qué no, y las lecciones para la próxima vez.

## Próximo paso sugerido (no hecho todavía)

Si este servicio pasa de prueba a algo permanente, falta:
- Persistir la ruta hacia el proxy corporativo (hoy se agregó con `ip route add`, se pierde al reiniciar el contenedor — ver conclusiones).
- Decidir la base de datos definitiva (¿seguir con SQLite o migrar a MySQL, como tenía originalmente el `config.php`?).
- Definir si esto vive en `PRJ-OSS` (requeriría wireear el camino oficial del gateway de servicios) o se queda como una excepción documentada en `default`.
- Si se documenta como procedimiento oficial, promoverlo a `docs/06_Operacion.md` siguiendo el proceso de [`laboratorio/README.md`](../README.md).
