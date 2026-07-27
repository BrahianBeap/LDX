# Agregar (o quitar) una IP al acceso temporal de Kanboard

> Referencia rápida. Para el contexto completo, riesgos y rollback total,
> ver [`SOP-acceso-temporal-demo-kanboard.md`](SOP-acceso-temporal-demo-kanboard.md).
> Sigue siendo un acceso **temporal** — cada IP que se agregue acá hay
> que sumarla también a la tabla de "IPs autorizadas" del SOP.

**No hace falta tocar el proxy de LXD (`web-lan`)** — ya existe y escucha
en `10.143.11.228:8080` para cualquier IP que el firewall deje pasar. Acá
solo se agrega o quita el permiso de firewall por persona.

---

## Agregar una IP nueva

```bash
firewall-cmd --zone=work --add-rich-rule='rule family="ipv4" source address="<IP>/32" port port="8080" protocol="tcp" accept' --permanent
firewall-cmd --reload
```

**Validar:**
```bash
firewall-cmd --zone=work --list-rich-rules --permanent | grep "<IP>"
```
Debe aparecer la regla nueva, una sola vez.

---

## Quitar una IP

```bash
firewall-cmd --zone=work --remove-rich-rule='rule family="ipv4" source address="<IP>/32" port port="8080" protocol="tcp" accept' --permanent
firewall-cmd --reload
```

**Validar:**
```bash
firewall-cmd --zone=work --list-rich-rules --permanent | grep "<IP>"
```
No debe devolver nada.

---

Reemplazar `<IP>` por la IP fija de la persona (rango `10.150.60.0/24`,
VPN corporativa). El `--reload` no corta conexiones activas (ver SOP,
Paso 3, para el detalle de por qué).
