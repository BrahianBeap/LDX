---
seccion: Clúster
pagina: Proxy
capturado: 2026-07-24T18:39:54.766Z
fuente: OneNote "Cluster-OSS" (Norberto Nunez)
---

Proxy 

lunes, 6 de julio de 2026 

17:03 

Proxy SDI para repos de Canonical 

proxy_sdi=http://10.150.32.100:3128 

no_proxy=10.0.0.0/8,192.168.0.0/16,172.16.0.0/12,169.254.0.0/16 

# APT 

cat > /etc/apt/apt.conf.d/99proxy.conf <<HERE 

Acquire::http::Proxy "$proxy_sdi"; 

Acquire::https::Proxy "$proxy_sdi"; 

HERE 

# SNAP 

snap set system proxy.http=$proxy_sdi 

snap set system proxy.https=$proxy_sdi 

# LXD 

lxc config set core.proxy_http  $proxy_sdi 

lxc config set core.proxy_https $proxy_sdi 

lxc config set core.proxy_ignore_hosts $no_proxy 

Cambio conflictivo.