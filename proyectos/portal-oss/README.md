# Portal OSS

Página de inicio de `https://oss.personal.com.py/`. Lleva a las herramientas que el área de Sistemas de Soporte a la Operación (OSS) publica en la plataforma LXD, explica en qué etapa está cada una y cómo se ingresa.

## Concepto: "la línea OSS"

Una sola línea conecta al área con cada herramienta, como un recorrido con paradas:

- **Parada llena:** herramienta en producción. **Anillo:** en desarrollo (pruebas). El estado se distingue por forma y por color, así no depende solo del color.
- Al pasar el mouse o el foco del teclado por una herramienta, se ilumina su tramo de la línea.
- En escritorio, la primera pantalla muestra la presentación breve (izquierda) y todas las herramientas con su botón (derecha). La sección "Qué hace OSS" va más abajo, para no demorar el acceso.
- En teléfono, las herramientas van antes que los consejos de ingreso.

> **Nota:** el estado indica la **etapa** de la herramienta (producción o desarrollo), no si está funcionando en este momento. La página lo aclara al pie de la lista.

## Estructura

| Archivo | Qué es |
|---|---|
| `src/apps.json` | **Datos de las aplicaciones.** Lo único que hay que tocar para agregar, quitar o cambiar una herramienta |
| `src/template.html` | Diseño, textos fijos y estilos. El marcador `<!--APPS-->` se reemplaza por la lista |
| `build.py` | Genera `dist/index.html` a partir de los dos anteriores (Python 3, sin librerías externas) |
| `dist/index.html` | **El archivo que se publica.** Es estático, sin dependencias externas. Usa una pequeña ayuda en JavaScript (el texto "Abriendo…" al hacer clic), pero funciona igual sin ella |

## Aplicaciones listadas (2026-10-26)

| Aplicación | Ruta | Estado | Ingreso (verificado) |
|---|---|---|---|
| Kanboard | `/kanboard/` | Producción | Usuario y contraseña de Kanboard (`LDAP_AUTH` desactivado en su `config.php`) |
| Vulnapp | `/vulnapp/` | Desarrollo, hasta que funcione la consulta a la API de SDI (firewall #1083155) | Pantalla propia "VulnApp — Iniciar sesión" |
| ADM-TECH | `/adm/` | Desarrollo, datos no oficiales | Ingreso de prueba; "Iniciar sesión con Active Directory" sin habilitar todavía para esta URL (ticket 623) |

Criterio del usuario: aplicaciones propias de LXD. No se listan servicios internos (NTF, Loki) ni herramientas que no estén publicadas en estas rutas.

## Agregar o cambiar una aplicación

1. Editar `src/apps.json`:
   ```json
   {
     "nombre": "Nombre visible",
     "ruta": "/ruta/",
     "estado": "produccion",
     "que_permite": "Qué permite hacer, empezando por un verbo.",
     "ingreso": "Con qué usuario se entra.",
     "aviso": "Opcional: advertencia que el usuario debe ver antes de entrar."
   }
   ```
   `estado` admite `produccion` o `desarrollo`. Las herramientas se agrupan solas por estado.
2. Generar: `python -I build.py` (desde esta carpeta).
3. Revisar `dist/index.html` en el navegador.
4. Publicar (abajo) y registrar el cambio en [`CHANGELOG.md`](CHANGELOG.md).

## Publicar

Desde el host de gestión `pfr-oss` (`10.143.11.228`), con `dist/index.html` copiado a `/tmp/portal-index.html`.

**Vista previa** (solo Franco, no reemplaza el portal):
```bash
lxc file push -p --uid 0 --gid 0 --mode 0644 /tmp/portal-index.html PFR-GW-SRV/var/www/html/portal-preview/index.html --project PRJ-OSS
lxc exec PFR-GW-SRV --project PRJ-OSS -n -- chmod 0755 /var/www/html/portal-preview < /dev/null
```
> **Advertencia:** `lxc file push -p` crea las carpetas con permisos `0750` y Apache responde `403`. Por eso el `chmod 0755`.

Se revisa en `https://oss.personal.com.py/portal-preview/`.

**Producción** (los 3 gateways):
```bash
for g in PFR-GW-SRV CAR-GW-SRV FDO-GW-SRV; do
  lxc exec $g --project PRJ-OSS -n -- sh -c 'cp -p /var/www/html/index.html /root/index.html.bak-$(date +%Y%m%d%H%M)' < /dev/null
  lxc file push --uid 0 --gid 0 --mode 0644 /tmp/portal-index.html $g/var/www/html/index.html --project PRJ-OSS
done
rm -f /tmp/portal-index.html
```

No hace falta recargar Apache: es un archivo estático.

**Verificar:**
```bash
curl -s https://oss.personal.com.py/ | grep -o '<title>[^<]*'      # <title>Portal OSS
```
Y abrir cada botón: `/kanboard/` y `/vulnapp/` deben llevar a su login (302), `/adm/` debe responder 200.

**Rollback:** copiar el backup más reciente de `/root/index.html.bak-*` a `/var/www/html/index.html` en cada gateway.

## Accesibilidad y entorno

- **Sin dependencias externas:** sin fuentes web, librerías ni CDN, porque es un portal interno. Tipografía del sistema: Bahnschrift para títulos y Segoe UI para texto en Windows, con alternativas en otros sistemas.
- **Tema:** claro u oscuro según la preferencia del sistema.
- **Teclado:** enlace "Ir a las herramientas" al principio y foco visible en todos los enlaces.
- **Movimiento:** con movimiento reducido activado, no hay animaciones.
- **Revisión visual:** en escritorio (1440 px) y teléfono (375 px), claro y oscuro.
