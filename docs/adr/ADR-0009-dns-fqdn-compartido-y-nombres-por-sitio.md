# ADR-0009 — DNS: un nombre compartido por round-robin, con nombres propios por sitio para casos puntuales

| Campo | Valor |
|---|---|
| **Número** | ADR-0009 |
| **Fecha** | 2026-10-16 |
| **Estado** | Aceptado (parcialmente implementado: el nombre compartido existe y apunta solo a Franco) |
| **Autores** | Norberto Núñez (propuesta), Elías Alfonzo |
| **Revisores** | Marcos Casco |
| **Reunión origen** | `reunion/2026-10-16_llamada-marcos-norberto-inventario-dns-certificado.vtt` (min. ~5:00-10:30) |

---

## Contexto

El clúster tiene 3 sitios (Franco, Carpinelli y Fernando), cada uno con su gateway de servicios y su IP de servicio: `10.143.11.8`, `192.168.91.117` y `10.11.11.12`. Las aplicaciones del área (Kanboard, VulnApp NG, NTF, Loki) se publican a través de esos gateways. El diseño de un nombre único repartido entre los 3 sitios ya se había acordado de palabra (ver [02_Arquitectura.md](../02_Arquitectura.md#nombre-de-dominio-compartido-entre-sitios-fqdn--dns-round-robin)), pero no estaba resuelto qué hacer con los clientes que solo tienen ruta hacia uno de los sitios.

---

## Problema

¿Cómo nombrar los servicios para que cualquier usuario llegue por cualquier sitio, sin romper a los clientes que solo pueden alcanzar un sitio puntual?

---

## Alternativas evaluadas

### Opción A — Un solo nombre para todo, con round-robin

**Descripción:** `oss.personal.com.py` con tres registros A, uno por sitio. El DNS devuelve las tres IP rotando el orden.

**Ventajas:**
- Una sola dirección para el usuario.
- Si un sitio se cae, se saca su registro y el servicio sigue por los otros dos.

**Desventajas:**
- Un cliente que solo tiene ruta hacia un sitio falla, en promedio, **1 de cada 3 veces**: el DNS le puede devolver cualquiera de las tres IP.

---

### Opción B — Un nombre por sitio, sin nombre compartido

**Descripción:** un nombre distinto para cada sitio, sin round-robin.

**Ventajas:**
- Comportamiento predecible: cada nombre lleva siempre al mismo sitio.

**Desventajas:**
- Cada usuario queda atado a un sitio y no hay reparto ni continuidad si ese sitio cae.

---

### Opción C — Nombre compartido por defecto, más nombres propios por sitio cuando hace falta

**Descripción:** `oss.personal.com.py` con round-robin para el caso general. Para los clientes que solo alcanzan un sitio, un nombre adicional que apunta exclusivamente a ese sitio (ej. un nombre de Fernando para Comap).

**Ventajas:**
- El caso general conserva el reparto y la continuidad.
- Los casos con restricción de ruta funcionan siempre.

**Desventajas:**
- Más nombres y certificados para mantener.

---

## Decisión

**Se elige:** Opción C — nombre compartido por defecto, con nombres propios por sitio para los casos con restricción de ruta.

---

## Justificación

Norberto Núñez lo planteó con un caso real: los equipos **Comap** (grupos electrógenos) se conectan por la red móvil, que solo tiene rutas hacia la IP de Fernando. Si se les configura el nombre compartido, fallarían una de cada tres veces. Hoy Comap envía sus traps directamente por IP, por eso no falla. Pero si se quiere pasar a un nombre, ese nombre tiene que apuntar solo a Fernando (`/supervisionge` en `FDO-GW-SRV`).

Norberto también aclaró que, en DNS, **cada nombre es independiente**: aunque uno sea subdominio de otro (ej. `fdo.oss.personal.com.py`), no depende de `oss.personal.com.py`. Ambos pueden convivir, y el compartido sigue apuntando a los tres sitios.

La decisión final sobre qué servicios usan cada nombre es del equipo dueño de la plataforma ("son sugerencias mías, ustedes son dueños de la plataforma").

---

## Consecuencias

### Positivas
- Los usuarios usan una sola dirección: `https://oss.personal.com.py/<aplicación>`.
- Las aplicaciones que solo corren en Franco (Kanboard, VulnApp NG) se atienden desde cualquier gateway por **proxy interno** hacia sus contenedores (no por redirección al navegador), validado por Norberto el 2026-10-24.

### Negativas / Compromisos aceptados
- Cada nombre adicional por sitio debe incluirse en el certificado (SAN) o requerir uno propio.
- Las aplicaciones que corren en un solo nodo dejan de estar disponibles desde todos los sitios si ese nodo cae; el round-robin solo cubre la caída de un gateway.

### Riesgos
- Si se agregan las IP de Carpinelli y Fernando al DNS antes de homogeneizar sus `LB.conf`, 2 de cada 3 accesos fallan. Ver [RIE-020](../11_Riesgos.md#rie-020--gateways-de-car-y-fdo-no-homogéneos-con-pfr-bloquean-el-dns-compartido).

---

## Pendientes de seguimiento

- [x] Alta de `oss.personal.com.py` en el DNS interno (ticket #1079305): cargado solo `10.143.11.8` (Abel Díaz, 2026-10-21). Abel confirmó que el esquema de varios registros A es posible.
- [ ] Sumar `192.168.91.117` y `10.11.11.12` después de la Etapa 2 de los gateways.
- [ ] Definir el nombre propio de Fernando para Comap y decidir si entra como SAN en el certificado del ticket #1078719.
- [ ] TTL de 300 segundos, para que sacar un sitio del DNS se refleje en minutos.

---

## Referencias

- [02_Arquitectura.md — Nombre de dominio compartido entre sitios](../02_Arquitectura.md#nombre-de-dominio-compartido-entre-sitios-fqdn--dns-round-robin)
- [ADR-0008 — Gateway y balanceador en dos etapas](ADR-0008-gateway-balanceador-dos-etapas.md)
- Reunión origen: `reunion/2026-10-16_llamada-marcos-norberto-inventario-dns-certificado.vtt`
- Confirmación del proxy interno: `reunion/2026-10-24_llamada-daniel-norberto-recursos-s3-certificado-ntf.vtt` (min. ~1:15-1:40)
