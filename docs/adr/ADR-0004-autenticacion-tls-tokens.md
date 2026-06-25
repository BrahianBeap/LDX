# ADR-0004 — Autenticación de operadores: TLS tokens + certificados de navegador

| Campo | Valor |
|---|---|
| **Número** | ADR-0004 |
| **Fecha** | 2026-06-25 |
| **Estado** | Aceptado |
| **Autores** | Norberto Núñez |
| **Revisores** | Marcos Casco, equipo técnico |
| **Reunión origen** | `reunion/Llamada con Daniel y 3 personas más.vtt` |

---

## Contexto

La Web UI de LXD necesita un mecanismo de autenticación para que los operadores accedan al cluster de forma segura. LXD provee múltiples opciones de autenticación nativas.

El equipo tiene múltiples operadores (Daniel Medina, Elías Alfonzo, Rocío Duarte) que necesitan acceso independiente y revocable.

---

## Problema

¿Qué mecanismo de autenticación usar para el acceso de operadores a la Web UI de LXD?

---

## Alternativas evaluadas

### Opción A — TLS tokens + certificados de navegador (nativo LXD)

**Descripción:**
Cada operador genera un certificado TLS en su navegador. Un administrador genera un token de un solo uso para el primer acceso. El token vincula el certificado del navegador con el cluster.

**Ventajas:**
- Nativo en LXD — sin dependencias externas.
- Cada operador tiene su propio certificado, revocable individualmente.
- La autenticación es mutua TLS — el servidor verifica al cliente y el cliente verifica al servidor.
- El token de primer acceso tiene tiempo de expiración.

**Desventajas:**
- El proceso de setup por operador requiere seguir pasos específicos (modo incógnito, instalación del certificado).
- Si el operador pierde el certificado, necesita repetir el proceso.

---

### Opción B — Autenticación basada en certificados CA

**Descripción:**
Configurar una CA (Certificate Authority) propia y firmar certificados de cliente para cada operador.

**Ventajas:**
- Control centralizado de certificados.

**Desventajas:**
- Requiere infraestructura adicional (CA propia).
- Mayor complejidad operativa.
- 🔴 No fue mencionada como alternativa evaluada en la reunión — incluida solo para completitud.

---

## Decisión

**Se elige: Opción A — TLS tokens + certificados de navegador.**

---

## Justificación

El mecanismo nativo de LXD es suficiente para el equipo actual. Cada operador tiene un certificado propio, lo que permite revocar acceso individual sin afectar a otros operadores. No requiere infraestructura adicional.

---

## Consecuencias

### Positivas
- Sin dependencias externas para autenticación.
- Acceso revocable por operador.
- Cifrado en tránsito garantizado (TLS).

### Negativas / Compromisos aceptados
- El proceso de onboarding de un nuevo operador requiere pasos manuales (generar token, instalar certificado).
- Si un operador cambia de navegador o dispositivo, debe repetir el proceso.

### Riesgos
- Tokens no caducan automáticamente si no se configuran límites de tiempo — verificar política de expiración.
- El acceso actual es solo desde red local (sin VPN). Si se obtiene acceso físico a la red, se puede intentar acceder a la UI. Las rich rules de firewall mitigan esto parcialmente.

---

## Pendientes de seguimiento

- [ ] Verificar política de expiración de tokens en LXD.
- [ ] Documentar el proceso de revocación de acceso a un operador.
- [ ] Evaluar autenticación adicional (VPN) cuando se configure acceso remoto.

---

## Referencias

- [04_Instalacion.md — Paso 8 (acceso Web UI)](../04_Instalacion.md)
- [14_Manual_Operativo.md — Cómo agregar un nuevo operador](../14_Manual_Operativo.md)
- [07_Troubleshooting.md — TRB-004](../07_Troubleshooting.md)
