---
seccion: Clúster
pagina: NTP
capturado: 2026-07-24T18:40:03.732Z
fuente: OneNote "Cluster-OSS" (Norberto Nunez)
---

NTP 

lunes, 6 de julio de 2026 

17:03 

NTP 

cat > /etc/systemd/timesyncd.conf <<HERE 

[Time] 

NTP=10.150.31.136 10.143.11.16 

HERE 

systemctl restart systemd-timesyncd 

Cambio conflictivo.