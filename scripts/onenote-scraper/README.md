# onenote-scraper

Captura de solo lectura del OneNote técnico ("Clúster-OSS") que Norberto
Núñez usa como bitácora del cluster LXD, para poder incorporar su
contenido a [`docs/`](../../docs/) sin depender de un conector Microsoft
365 con permisos de administrador (no disponible en este tenant).

Funciona abriendo una ventana real de Microsoft Edge controlada por
Playwright, reutilizando la sesión ya autenticada del usuario en ese
navegador — no hay ningún token ni contraseña embebido en el script.

## Cuándo usarlo

Cuando Norberto actualice el OneNote y se quiera refrescar el contexto de
la base de conocimiento. No es un proceso automático/programado — es una
captura puntual que después hay que revisar y contrastar manualmente
contra `docs/` siguiendo las fases de análisis de
[`CLAUDE.md`](../../CLAUDE.md).

## Requisitos

- Node.js (probado con v24) y npm.
- Microsoft Edge instalado (el script lo lanza con `channel: 'msedge'`,
  reutilizando el navegador ya instalado del sistema en vez de descargar
  un Chromium propio).
- Acceso ya autorizado al notebook con la cuenta de Windows/Edge del
  usuario que ejecuta el script (si Edge no tiene sesión iniciada, se abre
  una ventana y hay que loguearse ahí manualmente — el script espera hasta
  6 minutos a que la sesión quede lista antes de continuar).

## Instalación

```bash
cd scripts/onenote-scraper
npm install
```

Esto instala la librería `playwright` (no descarga navegadores propios,
usa el Edge del sistema).

## Uso

```bash
# 1. Capturar todas las secciones y páginas del notebook a texto plano
node scrape_all.js "<URL_DEL_NOTEBOOK_ONENOTE>" ./output

# 2. Sanitizar: reemplaza tokens de join (lxd/microovn) y claves publicas
#    de WireGuard conocidas por placeholders, antes de que el contenido
#    toque el repositorio
node redact.js
```

`redact.js` lee de `./output` y escribe en `./sanitized`, e imprime una
verificación final de que no quedó ningún token/clave sin redactar.

**Después de correr `redact.js`, revisar manualmente el contenido de
`./sanitized` antes de copiarlo a `onenote/` en el repo** — la lista de
patrones a redactar (tokens tipo `eyJ...`, claves WireGuard conocidas) es
la que se necesitó la primera vez; si en una captura futura aparece un
tipo de secreto nuevo (contraseña, API key, certificado privado), hay que
agregarlo a `redact.js` antes de commitear. Ver la política completa en
[`onenote/README.md`](../../onenote/README.md).

## Cómo funciona (por si hay que mantenerlo)

OneNote Online no tiene una API pública de solo-lectura simple, y su
contenido real vive dentro de un iframe anidado
(`onenote.officeapps.live.com/o/onenoteframe.aspx`), no en el documento
principal. Dentro de ese frame, `scrape_all.js` usa selectores basados en
**roles ARIA** (mucho más estables que las clases CSS hasheadas de Fluent
UI que Microsoft regenera en cada build):

| Elemento | Selector |
|---|---|
| Lista de secciones | `#NavPaneSectionList [role="treeitem"]` |
| Lista de páginas de la sección activa | `#PageList [role="button"].navItem` |
| Contenido de la página abierta | `#EditorContainer` (se usa `.innerText`) |

Si Microsoft cambia esta estructura interna, el script puede dejar de
encontrar estos elementos — en ese caso, repetir el proceso de
exploración manual (abrir la página, listar elementos con `role`, ver
`document.getElementById(...)`) para encontrar los nuevos selectores.

## Limitaciones conocidas

- Solo extrae texto (`innerText`) — no imágenes, dibujos, ni formato de
  tablas complejo (las tablas de planificación de IP se aplanan a texto).
- Es una automatización de una interfaz no documentada oficialmente por
  Microsoft — puede romperse con actualizaciones de OneNote Online.
- No hay reintentos automáticos si Microsoft muestra un diálogo
  inesperado (ej. MFA, aviso de nueva sesión) — en ese caso hay que
  cerrar el diálogo manualmente en la ventana de Edge mientras el script
  espera.
