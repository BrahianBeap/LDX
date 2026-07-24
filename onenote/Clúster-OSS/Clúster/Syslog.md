---
seccion: Clúster
pagina: Syslog
capturado: 2026-07-24T18:40:06.304Z
fuente: OneNote "Cluster-OSS" (Norberto Nunez)
---

Syslog 

lunes, 6 de julio de 2026 

17:07 

Rsyslog to SVATOOL-Loki - Syslog para los miembros del cluster 

# 

# External 

# 

echo 'action(type="omfwd" name="fw-To-Svatool-Loki" Target="10.150.31.68" Port="1514" Protocol="tcp" Template="RSYSLOG_SyslogProtocol23Format" queue.filename="fw-To-Svatool-Loki" queue.size="5000"  queue.type="fixedarray" queue.maxFileSize="10M" queue.saveOnShutdown="on")'  > /etc/rsyslog.d/To-Svatool-Loki.conf 

systemctl restart rsyslog 

 

Cambio conflictivo.