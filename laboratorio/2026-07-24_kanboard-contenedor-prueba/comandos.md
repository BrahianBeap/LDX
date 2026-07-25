# Comandos — de cero a Kanboard accesible por navegador

Todos los comandos marcados con 🖥️ **host** se ejecutan por SSH en `pfr-oss`
(`10.143.11.228`), usuario `alfonzel_opr`. Los marcados con 📦 **PC local**
se ejecutan en la PC de Windows, fuera del cluster.

---

## 1. Revisar qué imágenes hay disponibles en el proyecto destino

🖥️ **host**

```bash
lxc image list --project PRJ-OSS
```

**Por qué:** en LXD, si el proyecto tiene `features.images: true` (el valor
por defecto), **cada proyecto tiene su propio catálogo de imágenes** — una
imagen que existe en `default` no es visible desde `PRJ-OSS` aunque esté en
el mismo servidor. Hay que usar una imagen que ya esté presente en el
proyecto donde se va a crear el contenedor (o copiarla con
`lxc image copy`).

**Resultado relevante:** ya había una imagen Ubuntu 26.04 LTS minimal
(fingerprint `40eba84d6225`) cacheada en `PRJ-OSS` — la misma que se usó
para crear `PFR-OSS-GW-SRV`.

---

## 2. Crear el contenedor

🖥️ **host**

```bash
lxc launch 40eba84d6225 PFR-KANBOARD-TEST --project PRJ-OSS --target pfr.1
```

**Parámetros:**

| Parámetro | Función |
|---|---|
| `40eba84d6225` | Fingerprint de la imagen base (Ubuntu 26.04 minimal) |
| `PFR-KANBOARD-TEST` | Nombre del contenedor nuevo |
| `--project PRJ-OSS` | En qué proyecto se crea |
| `--target pfr.1` | En qué miembro del cluster corre (Franco, el mismo del host donde estamos parados) |

> ⚠️ **Error que salió acá:** al principio agregué también `--network OVN_1`
> pensando que hacía falta declarar la red. Eso rompió todo con:
> `Error: Failed start validation for device "eth-1": Instance DNS name
> "pfr-kanboard-test" conflict between "eth-1" and "eth0"...` — porque el
> perfil `default` del proyecto `PRJ-OSS` **ya trae** una interfaz `eth0`
> conectada a `OVN_1` (así se crearon `C-PFR-1`/`C-CAR-1` antes). Pasar
> `--network` de nuevo crea una segunda interfaz duplicada. **No hace falta
> el flag si el perfil ya la trae.**

**Cómo verificar:**
```bash
lxc list --project PRJ-OSS
# PFR-KANBOARD-TEST debe aparecer RUNNING con una IP 192.168.0.x
```

**Rollback:** `lxc delete PFR-KANBOARD-TEST --project PRJ-OSS --force`

---

## 3. Darle salida a internet al contenedor (proxy corporativo)

Un contenedor nuevo en `OVN_1` **no tiene salida a internet** por defecto —
hay que decirle explícitamente que use el proxy corporativo, igual que
todos los demás contenedores del proyecto (ver
[`05_Configuracion.md`](../../docs/05_Configuracion.md)).

🖥️ **host** (ejecutado dentro del contenedor con `lxc exec`)

```bash
lxc exec PFR-KANBOARD-TEST --project PRJ-OSS -- bash -c "
echo 'Acquire::http::Proxy \"http://10.150.32.100:3128\";' > /etc/apt/apt.conf.d/99proxy.conf
echo 'Acquire::https::Proxy \"http://10.150.32.100:3128\";' >> /etc/apt/apt.conf.d/99proxy.conf
"
```

Esto solo le dice a `apt` **qué proxy usar** — todavía no le dice **cómo
llegar** a esa IP, que está fuera de la red `OVN_1`. Para eso:

```bash
lxc exec PFR-KANBOARD-TEST --project PRJ-OSS -- ip route add 10.150.32.100/32 via 192.168.0.6
```

**Por qué `192.168.0.6`:** es la IP del contenedor `PFR-GW-OAM` (el gateway
de operación y mantenimiento de Franco) en la red `OVN_1`. Ese contenedor sí
tiene salida hacia la red de gestión del host, y por lo tanto hacia el
proxy. Es el mismo patrón que usa el perfil oficial `PRF-PFR-OSS-GW-SRV`
(ver [`05_Configuracion.md`](../../docs/05_Configuracion.md)).

> 🔴 **Importante — esto NO es persistente.** `ip route add` se pierde en
> el próximo reinicio del contenedor (nos pasó: después de mover el
> contenedor de proyecto y hacer `lxc restart`, hubo que volver a agregar
> esta ruta). Para que sobreviva reinicios, hay que agregarla al
> `cloud-init.network-config` del perfil o a un netplan dentro del
> contenedor — no se hizo en esta prueba porque era solo para testear.

**Cómo verificar:**
```bash
lxc exec PFR-KANBOARD-TEST --project PRJ-OSS -- apt-get update
# Debe descargar los índices de paquetes sin errores de "Unable to connect"
```

---

## 4. Instalar el stack (Apache + PHP + SQLite)

🖥️ **host**

```bash
lxc exec PFR-KANBOARD-TEST --project PRJ-OSS -- apt-get install -y \
  apache2 php libapache2-mod-php php-sqlite3 php-mbstring php-gd php-curl php-xml

lxc exec PFR-KANBOARD-TEST --project PRJ-OSS -- a2enmod rewrite setenvif
```

**Resultado esperado:** PHP 8.5.4 (versión que trae Ubuntu 26.04 LTS por
defecto), Apache cambia automáticamente de `mpm_event` a `mpm_prefork`
(obligatorio para `mod_php`).

**Por qué estas extensiones de PHP:**

| Extensión | Para qué la necesita Kanboard |
|---|---|
| `php-sqlite3` (incluye `pdo_sqlite`) | Motor de base de datos elegido para esta prueba |
| `php-mbstring` | Manejo de strings multi-byte (obligatorio, Kanboard no arranca sin esto) |
| `php-gd` | Generación/manipulación de imágenes (avatares, adjuntos) |
| `php-curl` | Llamadas HTTP salientes (webhooks, verificación de plugins) |
| `php-xml` | Importación/exportación de datos, algunas integraciones |

**Cómo verificar:**
```bash
lxc exec PFR-KANBOARD-TEST --project PRJ-OSS -- systemctl is-active apache2
# "active"
lxc exec PFR-KANBOARD-TEST --project PRJ-OSS -- php -m | grep -iE "sqlite|mbstring|curl|xml|gd"
# deben listarse todas
```

---

## 5. Copiar el código de Kanboard (PC → host → contenedor)

El cliente `lxc` de la PC de Windows **no está configurado como remoto**
contra la API del cluster, así que no se puede hacer `lxc file push`
directo desde ahí. Se hace en dos saltos.

### 5.1 — PC → host, con `pscp` (PuTTY)

📦 **PC local**

```
pscp -pw <PASSWORD> -r "C:\Users\alfonzel\Documents\GitHub\LXD\kamban\kanboard" alfonzel_opr@10.143.11.228:/tmp/
```

> ⚠️ Si el destino se escribe como `.../tmp/kanboard` (en vez de
> `.../tmp/`) da error `unable to open ...: failure` — hay que apuntar a la
> carpeta **padre** y dejar que `pscp` cree la subcarpeta con el nombre de
> origen.

### 5.2 — host → contenedor, con `lxc file push`

🖥️ **host**

```bash
lxc file push -r /tmp/kanboard PFR-KANBOARD-TEST/var/www/ --project PRJ-OSS
rm -rf /tmp/kanboard
```

**Resultado:** el código queda en `/var/www/kanboard` dentro del
contenedor.

**Cómo verificar:**
```bash
lxc exec PFR-KANBOARD-TEST --project PRJ-OSS -- find /var/www/kanboard -type f | wc -l
# Debe coincidir con la cantidad de archivos de origen (en esta prueba: 3163)
```

---

## 6. Permisos para que Kanboard pueda escribir su base de datos y plugins

🖥️ **host**

```bash
lxc exec PFR-KANBOARD-TEST --project PRJ-OSS -- bash -c "
chown -R www-data:www-data /var/www/kanboard
chmod -R u+rwX /var/www/kanboard/data /var/www/kanboard/plugins
"
```

**Por qué:** Apache corre como `www-data`. Kanboard necesita escribir en
`data/` (ahí vive `db.sqlite`, la caché y los archivos adjuntos) y en
`plugins/` (instalación de plugins desde la interfaz web). Sin esto, la
aplicación puede cargar pero falla al intentar escribir.

---

## 7. Elegir SQLite en vez de MySQL para esta prueba

🖥️ **host**

```bash
lxc exec PFR-KANBOARD-TEST --project PRJ-OSS -- sed -i \
  "s/define('DB_DRIVER', 'mysql')/define('DB_DRIVER', 'sqlite')/" \
  /var/www/kanboard/config.php
```

**Por qué:** el `config.php` original apunta a `DB_DRIVER = 'mysql'`
(con credenciales de desarrollo `kanboard`/`kanboard`), lo que hubiera
requerido instalar y asegurar un servidor MySQL/MariaDB solo para la
prueba. SQLite no necesita servidor aparte — el archivo `data/db.sqlite`
que ya venía copiado desde la instalación local se usa directamente.

> Esto edita **solo la copia dentro del contenedor** — el `config.php`
> original en la PC del usuario no se toca.

---

## 8. Configurar el vhost de Apache

Se creó localmente un archivo `kanboard.conf`:

```apache
<VirtualHost *:80>
    DocumentRoot /var/www/kanboard
    <Directory /var/www/kanboard>
        Options -Indexes +FollowSymLinks
        AllowOverride All
        Require all granted
    </Directory>
    ErrorLog ${APACHE_LOG_DIR}/kanboard-error.log
    CustomLog ${APACHE_LOG_DIR}/kanboard-access.log combined
</VirtualHost>
```

`AllowOverride All` es necesario porque Kanboard trae su propio `.htaccess`
con reglas de `mod_rewrite` (ya habilitado en el paso 4).

Se subió igual que el código (📦 `pscp` a `/tmp/`, luego 🖥️
`lxc file push` a `/etc/apache2/sites-available/kanboard.conf`), y se
activó:

```bash
lxc exec PFR-KANBOARD-TEST --project PRJ-OSS -- bash -c "
a2dissite 000-default
a2ensite kanboard
systemctl restart apache2
"
```

**Cómo verificar (desde dentro del contenedor, sin depender de la red):**
```bash
lxc exec PFR-KANBOARD-TEST --project PRJ-OSS -- curl -sI http://127.0.0.1/
# HTTP/1.1 302 Found ... Location: /?controller=AuthController&action=login
```

---

## 9. Exponerlo para poder verlo desde el navegador

Acá es donde el plan original cambió. Ver
[conclusiones.md](conclusiones.md) para el detalle de **por qué**; esta
sección son los comandos que sí funcionaron, en orden final.

### 9.1 — Mover el contenedor al proyecto `default`

`PRJ-OSS` prohíbe dispositivos `proxy` (proyecto restringido, ver
[ADR-0007](../../docs/adr/ADR-0007-proyectos-lxd-multitenancy.md)). En vez
de aflojar esa restricción para todo el proyecto, el contenedor de prueba
se movió a `default`:

```bash
lxc stop PFR-KANBOARD-TEST --project PRJ-OSS
lxc move PFR-KANBOARD-TEST PFR-KANBOARD-TEST --project PRJ-OSS --target-project default
lxc start PFR-KANBOARD-TEST --project default
```

> ⚠️ `lxc move` entre proyectos con el contenedor corriendo falla:
> `Unable to perform live container migration. CRIU isn't installed`. Hay
> que **detenerlo primero** (migración offline, sin necesidad de CRIU).

> 🔴 **Los perfiles son por-proyecto.** Al mover el contenedor, se queda
> sin el dispositivo de red (venía del perfil `default` de `PRJ-OSS`, que
> no existe en `default`). Hay que agregarlo a mano:
> ```bash
> lxc config device add PFR-KANBOARD-TEST eth0 nic network=OVN_1 --project default
> lxc restart PFR-KANBOARD-TEST --project default
> ```

### 9.2 — Agregar el dispositivo proxy de LXD (solo loopback)

```bash
lxc config device add PFR-KANBOARD-TEST web-public proxy \
  bind=host listen=tcp:127.0.0.1:8080 connect=tcp:127.0.0.1:80 \
  --project default
```

**Por qué `127.0.0.1` y no la IP pública del host:** el usuario
`alfonzel_opr` **no tiene `sudo`** en `pfr-oss` (`is not allowed to run
sudo on pfr-oss`), así que no se puede correr `firewall-cmd` para abrir un
puerto nuevo hacia la red corporativa. Bindeando solo a loopback, no hace
falta tocar el firewall del host en absoluto — el acceso se resuelve con un
túnel SSH (ver paso 10), que usa el puerto 22 ya permitido.

**Cómo verificar (desde el host):**
```bash
curl -sI http://127.0.0.1:8080/
# Debe dar el mismo 302 que el paso 8
```

---

## 10. Acceder desde el navegador de la PC del usuario

📦 **PC local** — abrir un túnel SSH que reenvía el puerto local al
loopback del host:

```
plink -ssh -pw <PASSWORD> -L 8080:127.0.0.1:8080 alfonzel_opr@10.143.11.228 -N
```

> Hay que **presionar Enter** en esa ventana cuando aparece "Access
> granted. Press Return to begin session." — si no, el túnel no queda
> completamente activo y el navegador da `ERR_CONNECTION_REFUSED`.

Con el túnel abierto (dejar esa ventana corriendo), abrir en el navegador:

```
http://localhost:8080
```

---

## 11. Encontrar las credenciales de acceso

El `data/db.sqlite` copiado ya tenía datos reales (no era una base vacía).
Para saber qué usuario probar, se consultó directamente con PHP (sin
necesitar instalar el cliente `sqlite3`, ya que `pdo_sqlite` ya estaba
instalado):

```bash
lxc exec PFR-KANBOARD-TEST --project default -- php -r '
$db = new PDO("sqlite:/var/www/kanboard/data/db.sqlite");
foreach ($db->query("SELECT id, username, email, role, is_ldap_user FROM users") as $row) {
    print_r($row);
}'
```

**Resultado:** una sola cuenta, `username: admin`, `role: app-admin`,
`is_ldap_user: 0`. Login exitoso con `admin` / `admin`.
