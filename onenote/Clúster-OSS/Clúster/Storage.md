---
seccion: Clúster
pagina: Storage
capturado: 2026-07-24T18:40:02.475Z
fuente: OneNote "Cluster-OSS" (Norberto Nunez)
---

Storage 

sábado, 4 de julio de 2026 

09:17 

 

Disco 

Antes 

root@car-oss:~# lsblk 

NAME                      MAJ:MIN RM   SIZE RO TYPE MOUNTPOINTS 

loop0                       7:0    0  50.1M  1 loop /snap/snapd/27406 

loop1                       7:1    0    74M  1 loop /snap/core22/2411 

loop2                       7:2    0 117.6M  1 loop /snap/lxd/38767 

loop3                       7:3    0  66.8M  1 loop /snap/core24/1643 

loop4                       7:4    0  21.3M  1 loop /snap/microovn/1088 

sda                         8:0    0   500G  0 disk 

|-sda1                      8:1    0     1G  0 part /boot/efi 

|-sda2                      8:2    0     2G  0 part /boot 

`-sda3                      8:3    0 496.9G  0 part 

  `-ubuntu--vg-ubuntu--lv 252:0    0   100G  0 lvm  / 

sr0                        11:0    1  1024M  0 rom 

Averiguar cuanto queda de espacio libre para la creación del siguiente volumen lógico 

vgs 

  VG        #PV #LV #SN Attr   VSize    VFree 

  ubuntu-vg   1   2   0 wz--n- <496.95g 396.40g 

Creación de /dev/sda 

lvcreate --size 396GiB ubuntu-vg --type linear --name LXD 

Después 

root@car-oss:~# lsblk 

NAME                      MAJ:MIN RM   SIZE RO TYPE MOUNTPOINTS 

loop0                       7:0    0  50.1M  1 loop /snap/snapd/27406 

loop1                       7:1    0    74M  1 loop /snap/core22/2411 

loop2                       7:2    0 117.6M  1 loop /snap/lxd/38767 

loop3                       7:3    0  66.8M  1 loop /snap/core24/1643 

loop4                       7:4    0  21.3M  1 loop /snap/microovn/1088 

sda                         8:0    0   500G  0 disk 

|-sda1                      8:1    0     1G  0 part /boot/efi 

Storage 

sábado, 4 de julio de 2026 

09:17 

 

Disco 

Antes 

root@car-oss:~# lsblk 

NAME                      MAJ:MIN RM   SIZE RO TYPE MOUNTPOINTS 

loop0                       7:0    0  50.1M  1 loop /snap/snapd/27406 

loop1                       7:1    0    74M  1 loop /snap/core22/2411 

loop2                       7:2    0 117.6M  1 loop /snap/lxd/38767 

loop3                       7:3    0  66.8M  1 loop /snap/core24/1643 

loop4                       7:4    0  21.3M  1 loop /snap/microovn/1088 

sda                         8:0    0   500G  0 disk 

|-sda1                      8:1    0     1G  0 part /boot/efi 

|-sda2                      8:2    0     2G  0 part /boot 

`-sda3                      8:3    0 496.9G  0 part 

  `-ubuntu--vg-ubuntu--lv 252:0    0   100G  0 lvm  / 

sr0                        11:0    1  1024M  0 rom 

Averiguar cuanto queda de espacio libre para la creación del siguiente volumen lógico 

vgs 

  VG        #PV #LV #SN Attr   VSize    VFree 

  ubuntu-vg   1   2   0 wz--n- <496.95g 396.40g 

Creación de /dev/sda 

lvcreate --size 396GiB ubuntu-vg --type linear --name LXD 

Después 

root@car-oss:~# lsblk 

NAME                      MAJ:MIN RM   SIZE RO TYPE MOUNTPOINTS 

loop0                       7:0    0  50.1M  1 loop /snap/snapd/27406 

loop1                       7:1    0    74M  1 loop /snap/core22/2411 

loop2                       7:2    0 117.6M  1 loop /snap/lxd/38767 

loop3                       7:3    0  66.8M  1 loop /snap/core24/1643 

loop4                       7:4    0  21.3M  1 loop /snap/microovn/1088 

sda                         8:0    0   500G  0 disk 

|-sda1                      8:1    0     1G  0 part /boot/efi 

|-sda2                      8:2    0     2G  0 part /boot 

`-sda3                      8:3    0 496.9G  0 part 

  |-ubuntu--vg-ubuntu--lv 252:0    0   100G  0 lvm  / 

  `-ubuntu--vg-LXD        252:1    0   396G  0 lvm 

sr0                        11:0    1  1024M  0 rom 

Nuevo volumen lógico 

/dev/mapper/ubuntu--vg-LXD 

 

Cambio conflictivo.