# ADR-0010 — Correo saliente de los sistemas del área por el módulo de email de NTF

| Campo | Valor |
|---|---|
| **Número** | ADR-0010 |
| **Fecha** | 2026-10-29 |
| **Estado** | Aceptado (implementación parcial: destinatarios internos funcionan; los externos dependen del relay de Seguridad) |
| **Autores** | Norberto Núñez (propuesta), Elías Alfonzo |
| **Revisores** | — |
| **Reunión origen** | `reunion/2026-10-29_llamada-norberto-envio-correo-ntf.srt` (min. ~0:15-1:30 propuesta; ~26:00-31:30 prueba de salida; ~47:00-57:00 relay) |

---

## Contexto

Los sistemas del área que se están migrando a LXD necesitan enviar correo: ADM-TECH (notificaciones de reservas y movimientos), Infrawork y Tembiapó (avisos a contratistas). ✅ Hoy ADM-TECH no envía por sí mismo. Deja los correos en una cola de la base `Infraestructura`, y un cron de Apache en `tec-calidad05` los envía (ver [`laboratorio/2026-10-24_migracion-admtech-lxd/`](../../laboratorio/2026-10-24_migracion-admtech-lxd/README.md)). Esa dependencia desaparece con la migración.

✅ El plan inicial de Elías Alfonzo era:

1. Crear un servidor (contenedor) de correo propio.
2. Inventariarlo en Jerure.
3. Pedir a SDI una cuenta de envío por sistema.

SDI ya había confirmado que se podían tener varias cuentas en un mismo servidor.

✅ El cluster ya tiene **NTF**, el servicio de notificaciones de Norberto Núñez (contenedores `FDO-WS-1` y `PFR-WS-1`). Hoy envía SMS y también tiene un **módulo de email**, que Norberto usaba en SDATool y por el que recibe correos todos los días.

---

## Problema

¿Cómo envían correo los sistemas que corren en LXD, a destinatarios internos y externos, con el menor número de componentes, cuentas y trámites nuevos?

---

## Alternativas evaluadas

### Opción A — Servidor de correo propio con una cuenta por sistema

**Descripción:** un contenedor de correo nuevo (o `CAR-SystemSMTP`, el Postfix ya existente en `car.1`) como relay de salida, con una cuenta de envío pedida a SDI para cada sistema.

**Ventajas:**
- Cada sistema autentica con su propia cuenta.

**Desventajas:**
- Un componente más para inventariar, mantener y securizar.
- Un trámite en Jerure por cada sistema ("mucho protocolo otra vez", según Elías).
- Igual depende de un relay de Seguridad para llegar a destinatarios externos.

---

### Opción B — Módulo de email de NTF *(elegida)*

**Descripción:** cada sistema llama a la API de NTF con el correo armado (destinatarios, asunto, remitente, cuerpo HTML en base64, adjunto opcional). NTF lo entrega por SMTP al servidor de correo corporativo.

**Ventajas:**
- Ya existe y está probado. No hay componentes nuevos.
- **El remitente se define en cada llamada** (ej. `adm-tech@personal.com.py`). Cada sistema sale con su nombre sin configurar nada en el servidor.
- Un único punto de salida de correo del cluster, que se puede restringir por ACL a un solo contenedor.
- Sirve también para Tembiapó e Infrawork.

**Desventajas:**
- Los sistemas pasan a depender de NTF para enviar correo.
- El control de quién puede usar qué remitente queda del lado de NTF (ver Riesgos).

---

## Decisión

**Se elige:** Opción B — los sistemas del área envían correo a través del módulo de email de NTF. No se pide un servidor de correo nuevo.

---

## Justificación

✅ Norberto Núñez lo propuso y lo probaron en la misma llamada: un correo HTML con adjunto llegó a dos casillas internas. Evita crear y mantener otro servidor y pedir una cuenta por sistema. El único faltante (los destinatarios externos) existe igual en la Opción A, porque los dos caminos necesitan el relay SMTP de Seguridad.

---

## Consecuencias

### Positivas
- ADM-TECH puede pasar a producción sin esperar un servidor de correo. Esto destraba la Fase 5 de la migración.
- Un solo punto de salida de correo para todo el cluster, con una sola regla de firewall.

### Negativas / Compromisos aceptados
- ✅ El Exchange interno (`10.150.49.103:25`) **ya no hace relay hacia dominios externos**. Hasta tener el relay de Seguridad, solo llegan los correos a direcciones internas. La prueba a una casilla de Gmail no llegó, y NTF no informó el error ("eso es algo que hay que mejorar también").
- ✅ Los correos llegan a Outlook con el aviso "no se pudo comprobar la identidad del remitente". Ver [TRB-020](../07_Troubleshooting.md#trb-020--outlook-marca-los-correos-de-ntf-como-posible-phishing).

### Riesgos
- 🟡 Cualquier sistema que llegue a la API de NTF puede enviar con cualquier remitente. Norberto: "después tenemos que delimitar quiénes son las IP que van a poder hacer eso".
- Ver [RIE-023](../11_Riesgos.md#rie-023--correo-de-los-sistemas-sin-relay-hacia-destinatarios-externos).

---

## Pendientes de seguimiento

- [ ] Preguntar a Abel Díaz (o Nico) qué tema de ayuda de Jerure corresponde para pedir acceso al **relay SMTP de Seguridad**. Si no existe, cargar un ticket genérico. Norberto revisa el borrador antes de enviarlo.
- [ ] Con la IP y el puerto del relay, ajustar la ruta y la regla de `ACL-OVN-1`, y probar con un destinatario interno y uno externo.
- [ ] Verificar si la ruta y la regla agregadas durante la prueba quedaron persistentes (ver [05_Configuracion.md](../05_Configuracion.md#firewall-de-la-red-ovn_1-lxc-network-acl)).
- [ ] Definir qué IP de origen pueden usar la API de email de NTF y con qué remitentes.
- [ ] Hacer que NTF informe cuando un envío no se entrega.
- [ ] Copiar a la carpeta compartida el script de ejemplo de envío de email (Norberto Núñez).

---

## Referencias

- Componente: [03_Componentes.md — NTF](../03_Componentes.md#ntf-servicio-de-notificaciones-sms-y-email)
- Patrón de exposición de NTF: [ADR-0008](ADR-0008-gateway-balanceador-dos-etapas.md)
- Reunión origen: `reunion/2026-10-29_llamada-norberto-envio-correo-ntf.srt`
