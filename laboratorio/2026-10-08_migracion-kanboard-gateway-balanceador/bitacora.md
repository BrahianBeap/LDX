# Bitácora — Migración de Kanboard al modelo gateway + balanceador

Ver contexto, objetivo y resultado final en [README.md](README.md). Esta bitácora documenta cada paso, en orden, con comandos reales y salidas reales.

---

## Paso 1 — Verificar si ya existía algo armado (solo lectura)

Antes de crear un contenedor balanceador nuevo, se revisó si `PFR-GW-SRV` (el gateway de servicios de Franco) ya tenía Apache corriendo — resultado: **sí**.

```bash
lxc exec PFR-GW-SRV --project PRJ-OSS -- dpkg -l | grep -i apache
lxc exec PFR-GW-SRV --project PRJ-OSS -- ss -tlnp
lxc exec PFR-GW-SRV --project PRJ-OSS -- cat /etc/apache2/sites-enabled/*.conf
```

**Resultado:** Apache 2.4.66 instalado y activo en los puertos 80 y 443. El archivo habilitado (`LB.conf`, symlink desde `sites-available/`) ya contenía:
- Balanceador para Loki (`/loki/loki/api/v1`, restringido por IP a Norberto Núñez y una IP de "Observabilidad")
- Balanceador para NTF (`/ntf`, dentro del `VirtualHost *:443`, con `SSLVerifyClient require` — certificado de cliente obligatorio)
- Una línea suelta: `ProxyPass /kanboard http://CAR-kanboard-1/`

```bash
lxc exec PFR-GW-SRV --project PRJ-OSS -- stat -c '%y %n' /etc/apache2/sites-available/LB.conf
# 2026-09-18 21:58:32 — sin ningún registro en este repositorio
```

```bash
lxc exec PFR-GW-SRV --project PRJ-OSS -- getent hosts CAR-kanboard-1   # no resuelve
lxc exec PFR-GW-SRV --project PRJ-OSS -- getent hosts CAR-KANBOARD     # sí resuelve: CAR-KANBOARD.lxd
```

**Conclusión:** `CAR-kanboard-1` es un nombre roto/desactualizado — probablemente una referencia a un intento anterior, nunca terminado (el contenedor real `CAR-KANBOARD` está vacío y `STOPPED`, confirmado por el usuario: "se creó para migrarlo, pero no tiene nada ahora"). 🔴 Quién hizo este trabajo y con qué plan sigue sin confirmar formalmente — se asume Norberto Núñez por descarte, no confirmado por él.

---

## Paso 2 — Primer intento: `/kanboard` con el prefijo pelado (falló)

```bash
lxc exec PFR-GW-SRV --project PRJ-OSS -- cp /etc/apache2/sites-available/LB.conf /etc/apache2/sites-available/LB.conf.bak-20261008
lxc exec PFR-GW-SRV --project PRJ-OSS -- sed -i '/Require ip 10.11.11.23/,/<\/Location>/{/<\/Location>/{a\
    # Kanboard - acceso para todo el equipo, sin restriccion de IP
a\
    ProxyPass /kanboard http://192.168.0.106:80/
a\
    ProxyPassReverse /kanboard http://192.168.0.106:80/
}
}' /etc/apache2/sites-available/LB.conf
lxc exec PFR-GW-SRV --project PRJ-OSS -- apache2ctl configtest   # Syntax OK
lxc exec PFR-GW-SRV --project PRJ-OSS -- systemctl reload apache2
```

**Prueba desde el navegador:** `http://10.143.11.8/kanboard` → cargó, pero el login de Kanboard redirigió a `http://10.143.11.8/?controller=AuthController&action=login` (perdiendo el prefijo `/kanboard`) y terminó mostrando la página default de Apache (`DocumentRoot /var/www/html`, sin relación con Kanboard).

**Causa raíz:** Kanboard genera sus redirecciones/links como rutas absolutas desde `/` — no tiene ninguna opción de "base URL" configurable (`grep -i "url|base|path" config.php` no mostró nada relevante). Cuando Apache le pela el prefijo `/kanboard` antes de reenviar, el backend no tiene forma de saber que debería incluir ese prefijo en sus propias respuestas.

**Rollback aplicado:**
```bash
lxc exec PFR-GW-SRV --project PRJ-OSS -- cp /etc/apache2/sites-available/LB.conf.bak-20261008 /etc/apache2/sites-available/LB.conf
lxc exec PFR-GW-SRV --project PRJ-OSS -- apache2ctl configtest
lxc exec PFR-GW-SRV --project PRJ-OSS -- systemctl reload apache2
```

---

## Paso 3 — Segundo intento: puerto dedicado 8080 vía forward-port (bloqueado por red externa)

```bash
lxc exec PFR-GW-SRV --project PRJ-OSS -- firewall-cmd --zone=external --add-forward-port=port=8080:proto=tcp:toaddr=192.168.0.106:toport=80 --permanent
lxc exec PFR-GW-SRV --project PRJ-OSS -- firewall-cmd --reload
```

**Verificación técnica (todo OK a nivel local):**
```bash
lxc exec PFR-GW-SRV --project PRJ-OSS -- nft list ruleset | grep -A2 8080
# meta nfproto ipv4 tcp dport 8080 dnat ip to 192.168.0.106:80   ← regla NAT correcta

curl -sI --connect-timeout 5 http://10.143.11.8:8080   # desde el host pfr-oss: 302 Found, OK
```

**Pero desde el navegador del usuario (red externa):** `ERR_CONNECTION_REFUSED`, incluso después de agregar explícitamente el puerto a la zona (`firewall-cmd --zone=external --add-port=8080/tcp --permanent`).

**Conclusión:** el forward-port funciona correctamente a nivel de LXD/firewalld del gateway — el bloqueo está en un firewall corporativo intermedio, entre la red del usuario y la red de servicio de `pfr-oss` (VLAN 411), que aparentemente solo permite 80/443 hacia ese segmento. Esto coincide con el trámite de "alta de servicio formal" que seguía pendiente desde julio (ver [RIE-009 en 11_Riesgos.md](../../docs/11_Riesgos.md)). Se descartó este camino para no depender de un trámite externo.

---

## Paso 4 — Solución final: Kanboard en la raíz del gateway

En vez de pelearle al problema de subpath, se decidió que Kanboard **sea** lo que responde en la raíz del `VirtualHost *:80` — exactamente la misma situación que tenía con el acceso directo viejo (sin ningún prefijo de por medio), solo que ahora pasando por el gateway en el puerto 80 (ya confirmado alcanzable) en vez del host directo en el 8080.

```bash
lxc exec PFR-GW-SRV --project PRJ-OSS -- sed -i '0,/<\/VirtualHost>/{s|</VirtualHost>|    ProxyPass / http://192.168.0.106:80/\n    ProxyPassReverse / http://192.168.0.106:80/\n</VirtualHost>|}' /etc/apache2/sites-available/LB.conf
lxc exec PFR-GW-SRV --project PRJ-OSS -- apache2ctl configtest   # Syntax OK
lxc exec PFR-GW-SRV --project PRJ-OSS -- systemctl reload apache2
```

**Verificación:**
```bash
lxc exec PFR-GW-SRV --project PRJ-OSS -- curl -sI http://localhost/
# HTTP/1.1 302 Found, Location: /?controller=AuthController&action=login — correcto, "/" ya es Kanboard
```

Confirmado también que Loki no quedó tapado por la nueva regla catch-all (tiene prioridad por ser más específica):
```bash
lxc exec PFR-GW-SRV --project PRJ-OSS -- curl -sI http://localhost/loki/loki/api/v1/status/buildinfo
# HTTP/1.1 403 Forbidden — correcto, el ACL de IP sigue activo (localhost no está autorizado)
```

**Prueba real del usuario, desde su navegador:** `http://10.143.11.8/` → Kanboard cargó completo, con sesión y proyectos visibles (`KB JOAJU`, `INFRAWORK`, etc.). ✅

---

## Paso 5 — Alias `/kanboard` y `/kamboard` (por conveniencia/typo), sin romper nada

Pedido explícito del usuario: que entrar por `/kanboard` (o el typo común `/kamboard`) también funcione, redirigiendo a la raíz.

**Primer intento — `Redirect` simple (no tomó efecto):**
```bash
lxc exec PFR-GW-SRV --project PRJ-OSS -- sed -i '0,/<\/VirtualHost>/{s|<\/VirtualHost>|    Redirect /kanboard /\n    Redirect /kamboard /\n</VirtualHost>|}' /etc/apache2/sites-available/LB.conf
```

Resultado: seguía resolviendo vía el `ProxyPass /` catch-all (ya definido antes en el archivo), no vía el `Redirect` — el navegador terminaba viendo la respuesta de Kanboard (con sus cookies `KB_SID` propias), no una redirección simple de Apache. Funcionalmente no rompía nada (Kanboard igual contesta con `/` sin importar el path de entrada), pero cualquier navegación posterior bajo `/kanboard/algo` se perdía, porque esas rutas sí se reenviaban al backend buscando contenido que no existe ahí.

**Fix — excluir `/kanboard` y `/kamboard` del `ProxyPass /` para que el `Redirect` sí tome el control:**
```bash
lxc exec PFR-GW-SRV --project PRJ-OSS -- sed -i 's|    ProxyPass / http://192.168.0.106:80/|    ProxyPass /kanboard !\n    ProxyPass /kamboard !\n    ProxyPass / http://192.168.0.106:80/|' /etc/apache2/sites-available/LB.conf
lxc exec PFR-GW-SRV --project PRJ-OSS -- apache2ctl configtest   # Syntax OK
lxc exec PFR-GW-SRV --project PRJ-OSS -- systemctl reload apache2
```

**Verificación:**
```bash
lxc exec PFR-GW-SRV --project PRJ-OSS -- curl -sI http://localhost/kanboard
# HTTP/1.1 302 Found, Location: http://localhost/ — esta vez sin cabeceras de Kanboard,
# confirmando que es el Redirect de Apache el que responde, antes de tocar el backend
```

Confirmado en el navegador: `http://10.143.11.8/kanboard` → rebota limpio a `/` → Kanboard funcional, navegación interna sin perderse en ningún lado.

> **Nota (aclarada con el usuario):** una vez en `/`, ningún link interno de Kanboard vuelve a mostrar `/kanboard` en la URL — es el comportamiento esperado, no se puede evitar sin tocar el código de Kanboard (que no soporta subpath). Se evaluó pedir un nombre de dominio interno (ej. `http://kanboard.interno/`) como mejora cosmética futura — explícitamente pospuesto por el usuario.

---

## Paso 6 — Retirar el acceso viejo

### 6a. Dispositivo `web-lan` del contenedor (sin necesitar root)

```bash
lxc config device remove PFR-KANBOARD-TEST web-lan --project default
```

Verificado: `lxc config device show PFR-KANBOARD-TEST --project default` solo lista `eth0`, `root` y `web-public` (el túnel SSH administrativo, intencionalmente conservado). Verificado también a nivel de red: `ss -tlnp | grep 8080` en el host ya no muestra ningún listener en `10.143.11.228:8080`, solo en `127.0.0.1:8080`.

### 6b. Reglas de firewall del host (necesita root — `su -`, esta cuenta no tiene `sudo` en `pfr-oss`)

Comandos entregados al usuario (ver el SOP de julio, sección "Rollback", para el detalle completo):

```bash
firewall-cmd --zone=work --remove-rich-rule='rule family="ipv4" source address="10.150.60.92/32" port port="8080" protocol="tcp" accept' --permanent
firewall-cmd --zone=work --remove-rich-rule='rule family="ipv4" source address="10.150.60.66/32" port port="8080" protocol="tcp" accept' --permanent
firewall-cmd --zone=work --remove-rich-rule='rule family="ipv4" source address="10.150.60.94/32" port port="8080" protocol="tcp" accept' --permanent
firewall-cmd --zone=work --remove-rich-rule='rule family="ipv4" source address="10.150.60.85/32" port port="8080" protocol="tcp" accept' --permanent
firewall-cmd --zone=work --remove-rich-rule='rule family="ipv4" source address="10.150.60.99/32" port port="8080" protocol="tcp" accept' --permanent
firewall-cmd --zone=work --remove-rich-rule='rule family="ipv4" source address="10.150.60.202/32" port port="8080" protocol="tcp" accept' --permanent
firewall-cmd --reload
```

🟡 **Reportado por el usuario como aplicado, no verificado de forma independiente.** El intento de verificación en vivo (de solo lectura) falló por falta de privilegio:

```bash
firewall-cmd --zone=work --list-rich-rules | grep 8080
# Authorization failed. Make sure polkit agent is running or run the application as superuser.
```

Pendiente confirmar con alguien que tenga acceso root en `pfr-oss`.

---

## Resultado final

Ver tabla de resultados en [README.md](README.md).

## Mensaje enviado al equipo

El usuario avisó al grupo (6 personas autorizadas desde la demo de julio) del nuevo link (`http://10.143.11.8/`), aclarando que las credenciales no cambian y que el link viejo dejaría de funcionar.
