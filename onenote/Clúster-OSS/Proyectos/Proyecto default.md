---
seccion: Proyectos
pagina: Proyecto default
capturado: 2026-07-24T18:40:20.604Z
fuente: OneNote "Cluster-OSS" (Norberto Nunez)
---

Proyecto default 

miércoles, 1 de julio de 2026 

12:06 

Redes 

OVN para conectividad este-oeste entre contenedores 

lxc network create UplinkOvn1 --type=bridge ipv4.address=none ipv6.address=none ipv4.routes=192.168.0.0/24 

lxc network create OVN_1      --type=ovn    network=UplinkOvn1  ipv4.address=none 

Bridge para salida por interface de gestión 

lxc network create lxdbr_OAM --type=bridge 

Bridge para conectividad este-oeste con Wireguard 

lxc network create lxdbr_wg0 --type bridge bridge.external_interfaces=wg0 --target pfr.1 

lxc network create lxdbr_wg0 --type bridge bridge.external_interfaces=wg0 --target car.1 

lxc network create lxdbr_wg0 --type=bridge ipv4.address=none ipv6.address=none 

 

Perfil PRF-GW-OAM 

lxc profile create PRF-GW-OAM 

lxc profile edit   PRF-GW-OAM <<HERE 

name: PRF-Proxy 

description: Salida por la interface de gestión del host 

devices: 

  eth0: 

    network: lxdbr_OAM 

    type: nic 

  eth1: 

    network: OVN_1 

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

HERE 

 

Instancia PFR-GW-OAM 

lxc launch local:deafe0d30bd9 PFR-GW-OAM --profile PRF-GW-OAM <<HERE 

config: 

  cloud-init.network-config: | 

    #cloud-config 

    version: 2 

    ethernets: 

      eth0: 

        dhcp4: true 

        dhcp6: false 

      eth1: 

        dhcp4: false 

        dhcp6: false 

        addresses: 

          - 192.168.0.6/24 

HERE 

lxc shell PFR-GW-OAM 

systemctl stop ssh ssh.socket 

systemctl disable ssh ssh.socket 

systemctl mask ssh 

firewall-cmd --permanent --set-default-zone drop 

firewall-cmd --permanent --zone external --change-interface eth0 

firewall-cmd --permanent --zone external --remove-service ssh 

firewall-cmd --permanent --zone internal --change-interface eth1 

firewall-cmd --permanent --zone internal --remove-service ssh 

firewall-cmd --permanent --zone internal --remove-service samba-client 

firewall-cmd --permanent --zone internal --remove-service mdns 

firewall-cmd --permanent --zone internal --remove-service dhcpv6-client 

firewall-cmd --permanent --zone external --set-target=ACCEPT 

firewall-cmd --permanent --zone internal --set-target=ACCEPT 

firewall-cmd --reload 

 

Instancia CAR-GW-OAM 

lxc copy PFR-GW-OAM CAR-GW-OAM --profile PRF-GW-OAM --target car.1 

lxc config set CAR-GW-OAM cloud-init.network-config='#cloud-config 

version: 2 

ethernets: 

  eth0: 

    dhcp4: true 

    dhcp6: false 

  eth1: 

    dhcp4: false 

    dhcp6: false 

    addresses: 

      - 192.168.0.8/24' 

lxc shell CAR-GW-OAM 

systemctl disable ssh sshd-unix-local.socket 

systemctl stop ssh sshd-unix-local.socket 

systemctl disable ssh sshd-unix-local.socket 

firewall-cmd --permanent --set-default-zone drop 

firewall-cmd --permanent --zone external --change-interface eth0 

firewall-cmd --permanent --zone external --remove-service ssh 

firewall-cmd --permanent --zone internal --change-interface eth1 

firewall-cmd --permanent --zone internal --remove-service ssh 

firewall-cmd --permanent --zone internal --remove-service samba-client 

firewall-cmd --permanent --zone internal --remove-service mdns 

firewall-cmd --permanent --zone internal --remove-service dhcpv6-client 

firewall-cmd --permanent --zone external --set-target=ACCEPT 

firewall-cmd --permanent --zone internal --set-target=ACCEPT 

firewall-cmd --reload 

Cambio conflictivo.