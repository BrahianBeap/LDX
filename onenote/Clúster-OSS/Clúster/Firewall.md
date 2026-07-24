---
seccion: Clúster
pagina: Firewall
capturado: 2026-07-24T18:39:59.978Z
fuente: OneNote "Cluster-OSS" (Norberto Nunez)
---

Firewall 

Monday, July 6, 2026 

10:17 PM 

Firewall 

zone=work 

firewall-cmd --set-default-zone trusted 

firewall-cmd --zone ${zone} --change-interface nic_oam 

firewall-cmd --zone ${zone} --remove-service ssh 

firewall-cmd --zone ${zone} --remove-service dhcpv6-client 

# Cluster LXD 

firewall-cmd --zone ${zone} --add-rich-rule 'rule family="ipv4" source address="10.143.11.228/32"  port port="8443" protocol="tcp" accept' 

firewall-cmd --zone ${zone} --add-rich-rule 'rule family="ipv4" source address="192.168.91.116/32" port port="8443" protocol="tcp" accept' 

# OVN PFR 

firewall-cmd --zone ${zone} --add-rich-rule 'rule family="ipv4" source address="10.143.11.228/32"  port port="6641" protocol="tcp" accept' 

firewall-cmd --zone ${zone} --add-rich-rule 'rule family="ipv4" source address="10.143.11.228/32"  port port="6642" protocol="tcp" accept' 

firewall-cmd --zone ${zone} --add-rich-rule 'rule family="ipv4" source address="10.143.11.228/32"  port port="6643" protocol="tcp" accept' 

firewall-cmd --zone ${zone} --add-rich-rule 'rule family="ipv4" source address="10.143.11.228/32"  port port="6644" protocol="tcp" accept' 

firewall-cmd --zone ${zone} --add-rich-rule 'rule family="ipv4" source address="10.143.11.228/32"  port port="6686" protocol="tcp" accept' 

firewall-cmd --zone ${zone} --add-rich-rule 'rule family="ipv4" source address="10.143.11.228/32"  port port="6081" protocol="udp" accept' 

# OVN CAR 

firewall-cmd --zone ${zone} --add-rich-rule 'rule family="ipv4" source address="192.168.91.116/32"  port port="6641" protocol="tcp" accept' 

firewall-cmd --zone ${zone} --add-rich-rule 'rule family="ipv4" source address="192.168.91.116/32"  port port="6642" protocol="tcp" accept' 

firewall-cmd --zone ${zone} --add-rich-rule 'rule family="ipv4" source address="192.168.91.116/32"  port port="6643" protocol="tcp" accept' 

firewall-cmd --zone ${zone} --add-rich-rule 'rule family="ipv4" source address="192.168.91.116/32"  port port="6644" protocol="tcp" accept' 

firewall-cmd --zone ${zone} --add-rich-rule 'rule family="ipv4" source address="192.168.91.116/32"  port port="6686" protocol="tcp" accept' 

firewall-cmd --zone ${zone} --add-rich-rule 'rule family="ipv4" source address="192.168.91.116/32"  port port="6081" protocol="udp" accept' 

# Wireward 

firewall-cmd --zone ${zone} --add-rich-rule 'rule family="ipv4" source address="10.143.11.228/32"  port port="51820" protocol="udp" accept' 

# Puentes SSH 

firewall-cmd --zone ${zone} --add-rich-rule 'rule family="ipv4" source address="10.150.31.133/32" port port="22" protocol="tcp" accept' 

firewall-cmd --zone ${zone} --add-rich-rule 'rule family="ipv4" source address="10.150.48.68/32" port port="22" protocol="tcp" accept' 

firewall-cmd --zone ${zone} --add-rich-rule 'rule family="ipv4" source address="10.150.48.79/32" port port="22" protocol="tcp" accept' 

# Prometheus node exporter desde SVATOOL 

firewall-cmd --zone ${zone} --add-rich-rule 'rule family="ipv4" source address="10.150.31.68/32" port port="9100" protocol="tcp" accept' 

# Prometheus lxd exporter desde SVATOOL 

firewall-cmd --zone ${zone} --add-rich-rule 'rule family="ipv4" source address="10.150.31.68/32" port port="8555" protocol="tcp" accept' 

# NB Norberto Núñez 

firewall-cmd --zone ${zone} --add-rich-rule 'rule family="ipv4" source address="10.150.60.92/32" port port="22" protocol="tcp" accept' 

firewall-cmd --zone ${zone} --add-rich-rule 'rule family="ipv4" source address="10.150.60.92/32" port port="8444" protocol="tcp" accept' 

# NB OSS Rocio 

firewall-cmd --zone ${zone} --add-rich-rule 'rule family="ipv4" source address="10.150.60.66/32" port port="8444" protocol="tcp" accept' 

firewall-cmd --zone ${zone} --add-rich-rule 'rule family="ipv4" source address="10.150.60.66/32" port port="22" protocol="tcp" accept' 

# NB OSS Daniel 

firewall-cmd --zone ${zone} --add-rich-rule 'rule family="ipv4" source address="10.150.60.94/32" port port="8444" protocol="tcp" accept' 

firewall-cmd --zone ${zone} --add-rich-rule 'rule family="ipv4" source address="10.150.60.94/32" port port="22" protocol="tcp" accept' 

# NB OSS Elias 

firewall-cmd --zone ${zone} --add-rich-rule 'rule family="ipv4" source address="10.150.60.85/32" port port="8444" protocol="tcp" accept' 

firewall-cmd --zone ${zone} --add-rich-rule 'rule family="ipv4" source address="10.150.60.85/32" port port="22" protocol="tcp" accept' 

# Guardar los cambios 

firewall-cmd --runtime-to-permanent 

 

Cambio conflictivo.