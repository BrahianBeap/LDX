---
seccion: Clúster
pagina: Wireguard
capturado: 2026-07-24T18:39:57.316Z
fuente: OneNote "Cluster-OSS" (Norberto Nunez)
---

Wireguard 

Monday, July 6, 2026 

10:18 PM 

Wireguard 

wg genkey | tee /etc/wireguard/private.key 

chmod 640 /etc/wireguard/private.key 

chown root:systemd-network /etc/wireguard/private.key 

chmod 750 /etc/wireguard  

chown root:systemd-network /etc/wireguard 

 

pfr-oss 

cat /etc/wireguard/private.key | wg pubkey | tee /etc/wireguard/public.key 

 

car-oss 

cat /etc/wireguard/private.key | wg pubkey | tee /etc/wireguard/public.key 

 

Cambio conflictivo.