# onenote/

Esta carpeta contiene una copia de trabajo, sanitizada, del OneNote técnico
("Clúster-OSS") que Norberto Núñez usa como bitácora de configuración del
cluster LXD. Es una fuente cruda, análoga a las transcripciones de
[`reunion/`](../reunion/) — no reemplaza a `docs/`, que es la única fuente
de verdad curada del proyecto.

---

## Origen y método de captura

El notebook vive en SharePoint/OneDrive corporativo y requiere autenticación
Microsoft 365; no hay un conector con permisos de administrador disponible
para leerlo por API. La captura se hizo el **2026-07-24** mediante
automatización de navegador (Playwright + Edge, con la sesión ya autenticada
del usuario), recorriendo cada sección y página del notebook y extrayendo el
texto visible de cada una. El script queda guardado en
[`scripts/onenote-scraper/`](../scripts/onenote-scraper/) para repetir la
captura cuando el notebook se actualice.

**Limitaciones conocidas de este método:**
- Es una foto del contenido al momento de la captura — no se actualiza sola.
  Para refrescarlo hay que repetir la captura.
- Solo se extrae texto; no se capturan dibujos, imágenes ni tablas con
  formato complejo (las tablas de planificación de IP se aplanan a texto).
- Depende de la estructura interna (no oficial) de OneNote Online — si
  Microsoft cambia esa interfaz, el script de captura puede dejar de
  funcionar y requerir ajustes.

## Política de redacción de secretos

**Nunca se commitea un secreto real a este repositorio, ni siquiera siendo
privado.** Antes de copiar el contenido capturado a esta carpeta, se
reemplazan por placeholders:

- Tokens de join de `lxc cluster add` / `microovn cluster join` / `lxc auth
  identity create` → `<TOKEN_REDACTADO_LXD_MICROOVN>`
- Claves públicas WireGuard → `<CLAVE_PUBLICA_WIREGUARD_PFR1>` /
  `<CLAVE_PUBLICA_WIREGUARD_CAR1>` (las claves privadas nunca se imprimen ni
  se capturan — cada host las genera localmente y no salen del host)

Información de topología real (IPs de hosts, hostnames de servidores
internos como el de LDAP, nombres de usuario) se mantiene sin redactar,
siguiendo la misma convención que ya usa el resto de `docs/` (por ejemplo,
la IP real de PFR1 aparece en texto plano en varios documentos y ADRs).

Si en una futura captura aparece un nuevo tipo de secreto no cubierto por
esta lista (contraseñas, API keys, certificados privados), **debe
redactarse antes de commitear**, ampliando este criterio.

## Qué hacer con este contenido

1. Leer las páginas relevantes para la reunión/tema que se esté procesando.
2. Contrastarlas contra `docs/` siguiendo las fases de análisis de
   [`CLAUDE.md`](../CLAUDE.md) — esta carpeta es *fuente*, no *documentación
   final*.
3. Actualizar `docs/` (y crear ADRs si corresponde) con lo que esta fuente
   confirma, corrige o agrega.
4. Registrar el cambio en [`CHANGELOG.md`](../CHANGELOG.md).

## Estructura capturada (2026-07-24)

| Sección | Páginas |
|---|---|
| Clúster | Proxy, Paquetes, Wireguard, Netplan, Firewall, OVN, Storage, NTP, LXD, Syslog, SSSD, Usuarios |
| Planning | Planning IP OVN_1, Planning IP Hosts, Planning wg0, Planning interfaces VM |
| Proyectos | Proyecto PRJ-OSS, Proyecto default |
| Varios | Cloud-init user-data |
