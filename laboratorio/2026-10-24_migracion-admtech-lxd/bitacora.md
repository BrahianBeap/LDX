# Bitácora — Relevamiento de ADM-TECH (2026-10-24)

Todo de **solo lectura**. Conexión a `tec-calidad05` (`10.129.2.165`) con `alfonzel_opr` (SSH) y a PostgreSQL con sesión `default_transaction_read_only=on`. No se usó sudo y no se modificó nada.

## 1. Servidor y código

```bash
cat /etc/redhat-release; php -v; /usr/sbin/httpd -v
rpm -qa | grep -i '^php'; php -m
php -i | grep -E '^(upload_max_filesize|post_max_size|memory_limit|max_execution_time|short_open_tag|date.timezone) '
du -xsh /var/www/html/adm /var/www/html/adm/*
find /var/www/html/adm/archivos -xdev -type f -printf '%TY %s\n'   # cantidad y MB por año
stat -c '%U:%G %a %n' /var/www/html/adm /var/www/html/adm/archivos
```

Resultados: ver [README.md](README.md#fase-1--relevamiento--2026-10-24-solo-lectura).

> **Advertencia:** una búsqueda de `adm` en `/etc/httpd/conf.d/` imprimió líneas `SetEnv` con valores secretos (contraseña de base y secreto OAuth). Se redactaron en la salida local. En los relevamientos siguientes, filtrar **solo los nombres** de las variables:
> ```bash
> grep -h -E '^\s*SetEnv\s' /etc/httpd/conf.d/<vhost>.conf | awk '{print $2}' | sort -u
> ```

## 2. Compatibilidad con PHP 8

Búsqueda sobre el código propio (excluyendo `archivos/` y `vendor/`). Hay que evitar dos falsos positivos: `each\(` también encuentra `foreach(` y `split\(` encuentra `str_split(`/`preg_split(`. Por eso se exige que no haya una letra antes:

```bash
grep -l -E '(^|[^a-zA-Z_])each\('  <archivos php>
grep -l -E '(^|[^a-zA-Z_])split\(' <archivos php>
grep -l -E 'ionCube|sg_load'      <archivos php>   # 0: no hay código cifrado
```

Resultados (verificados también en el repo): 14 archivos con `each()`, 20 con `split()`, 29 con etiquetas cortas `<?`, ~18 con `utf8_encode/decode`.

## 3. Base de datos

Consultas sobre `pg_class`, `pg_namespace`, `pg_proc`, `pg_trigger`, `pg_extension`, `pg_roles` (sin contraseñas), `pg_stat_activity` y `pg_foreign_server`. Ninguna lee filas de datos funcionales.

## 4. Repositorio de la aplicación

`C:\Users\alfonzel\Documents\GitHub\adm-tech` (solo lectura): `git log`, `git branch -a`, `.gitignore` y documentación de `knowledge/01_Arquitectura/` (`produccion.md`, `integraciones.md`). De ahí salen las dependencias de correo, SAP y OAuth.
