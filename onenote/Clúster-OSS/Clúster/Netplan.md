---
seccion: Clúster
pagina: Netplan
capturado: 2026-07-24T18:39:58.712Z
fuente: OneNote "Cluster-OSS" (Norberto Nunez)
---

Netplan 

Monday, July 6, 2026 

10:59 PM 

pfr-oss 

cat > /etc/netplan/00-installer-config.yaml <<HERE 

network: 

 version: 2 

 ethernets: 

  nic_srv1: 

   match: 

     macaddress: 00:50:56:a1:ca:80 

   set-name: nic_srv1 

   dhcp4: false 

   dhcp6: false 

  ens192: 

   dhcp4: false 

   addresses: 

    - 10.143.11.228/29 

   routes: 

    - to: default 

      via: 10.143.11.225 

   nameservers: 

    addresses: 

      - 10.129.4.176 

      - 10.129.4.177 

 tunnels: 

    wg0: 

      addresses: 

        - 169.254.0.2/32 

      route: 

        - to: 169.254.0.1 

        - to: 169.254.0.0 

        - to: 169.254.0.3 

        - to: 169.254.0.4 

      mode: wireguard 

      key: /etc/wireguard/private.key 

      port: 51820 

      peers: 

        - keys: 

            public: <CLAVE_PUBLICA_WIREGUARD_CAR1> 

          endpoint: 192.168.91.116:51820 

          allowed-ips: 

            - 0.0.0.0/0 

            - "::/0" 

HERE 

netplan try 

 

car-oss 

cat > /etc/netplan/00-installer-config.yaml <<HERE 

network: 

  version: 2 

  ethernets: 

    nic_oam: 

      match: 

        macaddress: 00:50:56:a3:32:f1 

      set-name: nic_oam 

      dhcp4: false 

      dhcp6: false 

      addresses: 

        - 192.168.91.116/27 

      nameservers: 

        addresses: 

          - 10.129.4.176 

          - 10.129.4.177 

      routes: 

        - to: default 

          via: 192.168.91.97 

    nic_srv1: 

      accept-ra: true 

      match: 

        macaddress: 00:50:56:a3:c4:d3 

      set-name: nic_srv1 

      dhcp4: false 

      dhcp6: false 

 tunnels: 

    wg0: 

      addresses: 

        - 169.254.0.1/32 

      route: 

        - to: 169.254.0.0 

        - to: 169.254.0.2 

        - to: 169.254.0.3 

        - to: 169.254.0.4 

      mode: wireguard 

      key: /etc/wireguard/private.key 

      port: 51820 

      peers: 

        - keys: 

            public: <CLAVE_PUBLICA_WIREGUARD_PFR1> 

          endpoint: 10.143.11.228:51820 

          allowed-ips: 

            - 0.0.0.0/0 

            - "::/0" 

HERE 

netplan try 

 

 

fdo-oss 

cat > /etc/netplan/00-installer-config.yaml <<HERE 

network: 

 version: 2 

 ethernets: 

  nic_srv1: 

   match: 

     macaddress: 00:50:56:a3:c4:e3  

   set-name: nic_srv1 

   dhcp4: false 

   dhcp6: false 

  nic_oam: 

   match: 

     macaddress: 00:50:56:a3:d6:5e  

   set-name: nic_oam 

   dhcp4: false 

   addresses: 

    - 10.150.32.101/24 

   routes: 

    - to: default 

      via: 10.150.32.1 

   nameservers:  

    addresses: 

      - 10.129.4.176 

      - 10.129.4.177 

# tunnels: 

#    wg0: 

#      addresses: 

#        - 169.254.0.0/32 

#      route: 

#        - to: 169.254.0.1 

#        - to: 169.254.0.2 

#      mode: wireguard 

#      key: /etc/wireguard/private.key 

#      port: 51820 

#      peers: 

#        - keys: 

#            public: <CLAVE_PUBLICA_WIREGUARD_CAR1> 

#          endpoint: 192.168.91.116:51820 

#          allowed-ips: 

#            - 0.0.0.0/0 

#            - "::/0" 

HERE 

netplan try 

 

 

 

Cambio conflictivo.