---
seccion: Proyectos
pagina: Proyecto PRJ-OSS
capturado: 2026-07-24T18:40:19.351Z
fuente: OneNote "Cluster-OSS" (Norberto Nunez)
---

Proyecto PRJ-OSS 

miércoles, 1 de julio de 2026 

12:08 

Definición 

lxc project create PRJ-OSS 

 

Features 

lxc project set PRJ-OSS \ 

limits.networks=2 \ 

restricted.networks.access=nic_srv1,OVN_1 \ 

restricted.devices.nic=allow \ 

features.networks=false features.networks.zones=true \ 

restricted=true 

 

Perfil PRF-PFR-OSS-GW-SRV 

lxc profile create PRF-PFR-OSS-GW-SRV --project PRJ-OSS <<HERE 

lxc profile edit PRF-PFR-OSS-GW-SRV --project PRJ-OSS <<HERE 

name: PRF-PFR-OSS-GW-SRV 

description: Perfil para Gateway de networking para servicios entre los contenedores y la red corporativa 

devices: 

  eth0: 

    network: OVN_1 

    type: nic 

  eth1: 

    mode: l2 

    nictype: ipvlan 

    parent: nic_srv1 

    type: nic 

  root: 

    path: / 

    pool: local 

    size: 5GiB 

    type: disk 

config: 

  limits.cpu: '1' 

  limits.memory: 1GiB 

  limits.processes: '500' 

  cloud-init.user-data: | 

    #cloud-config 

    apt: 

      http_proxy: "http://10.150.32.100:3128" 

      https_proxy: "http://10.150.32.100:3128" 

    package_update: true 

    package_upgrade: true 

    packages: 

      - firewalld 

  cloud-init.network-config: | 

    #cloud-config 

    version: 2 

    ethernets: 

      eth0: 

        dhcp4: false 

        dhcp6: false 

        addresses: 

          - 192.168.0.1/24 

        routes: 

          - to: 10.150.32.100 

            via: 192.168.0.6 

      eth1: 

        dhcp4: false 

        dhcp6: false 

        addresses: 

          - 10.143.11.8/26 

        nameservers: 

          addresses: 

            - 10.129.4.176 

            - 10.129.4.177 

        routes: 

          - to: default 

            via: 10.143.11.1 

HERE 

 

Instancia PFR-OSS-GW-SRV 

lxc launch ubuntu-minimal:resolute PFR-OSS-GW-SRV --profile PRF-PFR-OSS-GW-SRV --project PRJ-OSS 

lxc shell PFR-OSS-GW-SRV --project PRJ-OSS 

systemctl disable ssh sshd-unix-local.socket 

systemctl stop    ssh sshd-unix-local.socket 

systemctl mask    ssh sshd-unix-local.socket 

firewall-cmd  --permanent --set-default-zone drop 

firewall-cmd --permanent --zone external --change-interface eth1 

firewall-cmd --permanent --zone external --remove-service ssh 

firewall-cmd --permanent --zone internal --change-interface eth0 

firewall-cmd --permanent --zone internal --remove-service ssh 

firewall-cmd --permanent --zone internal --remove-service samba-client 

firewall-cmd --permanent --zone internal --remove-service mdns 

firewall-cmd --permanent --zone internal --remove-service dhcpv6-client 

firewall-cmd --permanent --zone external --set-target=ACCEPT 

firewall-cmd --permanent --zone internal --set-target=ACCEPT 

firewall-cmd --reload 

 

Perfil PRF-CAR-OSS-GW-SRV 

lxc profile create PRF-CAR-OSS-GW-SRV --project PRJ-OSS 

lxc profile edit   PRF-CAR-OSS-GW-SRV --project PRJ-OSS <<HERE 

name: PRF-CAR-OSS-GW-SRV 

description: Perfil para Gateway de networking para servicios entre los contenedores y la red corporativa 

devices: 

  eth0: 

    network: OVN_1 

    type: nic 

  eth1: 

    mode: l2 

    nictype: ipvlan 

    parent: nic_srv1 

    type: nic 

  root: 

    path: / 

    pool: local 

    size: 5GiB 

    type: disk 

config: 

  limits.cpu: '1' 

  limits.memory: 1GiB 

  limits.processes: '500' 

  cloud-init.user-data: | 

    #cloud-config 

    apt: 

      http_proxy: "http://10.150.32.100:3128" 

      https_proxy: "http://10.150.32.100:3128" 

    package_update: true 

    package_upgrade: true 

    packages: 

      - firewalld 

  cloud-init.network-config: | 

    #cloud-config 

    version: 2 

    ethernets: 

      eth0: 

        dhcp4: false 

        dhcp6: false 

        addresses: 

          - 192.168.0.2/24 

        routes: 

          - to: 10.150.32.100 

            via: 192.168.0.6 

      eth1: 

        dhcp4: false 

        dhcp6: false 

        addresses: 

          - 192.168.91.117/27 

        nameservers: 

          addresses: 

            - 10.129.4.176 

            - 10.129.4.177 

        routes: 

          - to: default 

            via: 192.168.91.97 

HERE 

 

Instancia CAR-OSS-GW-SRV 

lxc copy PFR-OSS-GW-SRV CAR-OSS-GW-SRV --profile PRF-CAR-OSS-GW-SRV --target car.1 --project PRJ-OSS 

lxc shell CAR-OSS-GW-SRV --project PRJ-OSS 

systemctl disable ssh sshd-unix-local.socket 

systemctl stop    ssh sshd-unix-local.socket 

systemctl mask    ssh sshd-unix-local.socket 

firewall-cmd --permanent --set-default-zone drop 

firewall-cmd --permanent --zone external --change-interface eth1 

firewall-cmd --permanent --zone external --remove-service ssh 

firewall-cmd --permanent --zone internal --change-interface eth0 

firewall-cmd --permanent --zone internal --remove-service ssh 

firewall-cmd --permanent --zone internal --remove-service samba-client 

firewall-cmd --permanent --zone internal --remove-service mdns 

firewall-cmd --permanent --zone internal --remove-service dhcpv6-client 

firewall-cmd --permanent --zone external --set-target=ACCEPT 

firewall-cmd --permanent --zone internal --set-target=ACCEPT 

firewall-cmd --reload 

Cambio conflictivo.