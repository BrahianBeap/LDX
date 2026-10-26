# CHANGELOG — Portal OSS

## 2.0.1 — 2026-10-26

- El título "VulnApp NG" pasa a "Vulnapp" (pedido del usuario).

## 2.0.0 — 2026-10-26

- Publicada en la raíz de los 3 gateways (SHA-256 `a80c3041…`); backup de la versión 1.1.0 en `/root/index.html.bak-202610261858`. Vista previa `/portal-preview/` retirada.
- Rediseño completo con el concepto "la línea OSS": las herramientas son paradas de una misma línea. Parada llena = producción, anillo = desarrollo.
- Primera pantalla de escritorio: presentación breve del área y acceso directo a las 3 herramientas. "Qué hace OSS" (5 capacidades) va más abajo.
- Cada herramienta muestra qué permite hacer, su estado, cómo se ingresa (verificado en cada aplicación), sus avisos y un botón de acceso.
- Se aclara que el estado indica la etapa y no la disponibilidad en el momento.
- Datos separados del diseño: `src/apps.json` + `src/template.html` → `build.py` → `dist/index.html`. Se elimina `src/index.html`.
- Accesibilidad: enlace para saltar a las herramientas, foco visible, contraste en claro y oscuro, movimiento reducido.

## 1.1.0 — 2026-10-26

- Agregada ADM-TECH (`/adm/`) con la etiqueta "En desarrollo" (nuevo estilo `.pill-dev`, en ámbar).
- VulnApp NG pasa a "En desarrollo": todavía no tiene la consulta a la API de SDI (pedido del usuario).

## 1.0.0 — 2026-10-26

- Primera versión: Kanboard (`/kanboard/`) y VulnApp NG (`/vulnapp/`).
- Página estática autocontenida (sin recursos externos ni JavaScript), modo claro y oscuro.
- Publicada en `/var/www/html/index.html` de `PFR-GW-SRV`, `CAR-GW-SRV` y `FDO-GW-SRV`.
