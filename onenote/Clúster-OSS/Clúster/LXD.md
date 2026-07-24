---
seccion: Clúster
pagina: LXD
capturado: 2026-07-24T18:40:05.000Z
fuente: OneNote "Cluster-OSS" (Norberto Nunez)
---

LXD 

Monday, July 6, 2026 

10:33 PM 

Install 

# snap proxy 

# lxd install 

snap install lxd --channel=stable 

snap refresh --hold lxd 

snap refresh lxd --cohort="+" 

 

pfr-oss 

lxd init 

Would you like to use LXD clustering? (yes/no) [default=no]: yes 

What IP address or DNS name should be used to reach this server? [default=10.143.11.228]: 

Are you joining an existing cluster? (yes/no) [default=no]: 

What member name should be used to identify this server in the cluster? [default=pfr-oss]: pfr.1 

Do you want to configure a new local storage pool? (yes/no) [default=yes]: 

Name of the storage backend to use (dir, lvm, zfs, btrfs) [default=zfs]: 

Create a new ZFS pool? (yes/no) [default=yes]: 

Would you like to use an existing empty block device (e.g. a disk or partition)? (yes/no) [default=no]: yes 

Path to the existing block device: /dev/sda6 

Do you want to configure a new remote storage pool? (yes/no) [default=no]: 

Would you like to connect to a MAAS server? (yes/no) [default=no]: 

Would you like to configure LXD to use an existing bridge or host interface? (yes/no) [default=no]: 

Would you like to create a new Fan overlay network? (yes/no) [default=yes]: no 

Would you like stale cached images to be updated automatically? (yes/no) [default=yes]: 

Would you like a YAML "lxd init" preseed to be printed? (yes/no) [default=no]: no 

# 

lxc cluster add car.1 

Member car-oss join token: 

<TOKEN_REDACTADO_LXD_MICROOVN> 

# 

 

car-oss 

lxd init 

Would you like to use LXD clustering? (yes/no) [default=no]: yes 

What IP address or DNS name should be used to reach this server? [default=192.168.91.116]: 

Are you joining an existing cluster? (yes/no) [default=no]: yes 

Do you have a join token? (yes/no/[token]) [default=no]: <TOKEN_REDACTADO_LXD_MICROOVN> 

All existing data is lost when joining a cluster, continue? (yes/no) [default=no] yes 

Choose "source" property for storage pool "local": /dev/mapper/ubuntu--vg-LXD 

Choose "zfs.pool_name" property for storage pool "local": local 

Would you like a YAML "lxd init" preseed to be printed? (yes/no) [default=no]: no 

 

Configuraciones comunes 

# Proxy LXD 

# 

# Puerto de gestión 

lxc config set core.https_address 0.0.0.0:8444 

snap restart lxd 

# Puerto de métricas 

lxc config set core.metrics_address 0.0.0.0:8555 

lxc config set core.metrics_authentication false 

# lxc auth  

lxc auth identity create tls/nunezno_browser --group admins 

TLS identity "tls/nunezno_browser" (a735dd6a-349d-4e69-a4a3-fc97fd0de646) pending identity token: 

<TOKEN_REDACTADO_LXD_MICROOVN> 

 

Cambio conflictivo.