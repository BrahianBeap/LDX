---
seccion: Varios
pagina: Cloud-init user-data
capturado: 2026-07-24T18:40:23.894Z
fuente: OneNote "Cluster-OSS" (Norberto Nunez)
---

Cloud-init user-data 

Monday, July 6, 2026 

11:08 PM 

Paquetes a instalar durante la instanciación del contenedor 

config: 

  cloud-init.user-data: | 

    #cloud-config 

    apt: 

      http_proxy: "http://10.150.32.100:3128" 

      https_proxy: "http://10.150.32.100:3128" 

    package_update: true 

    package_upgrade: true 

    packages: 

      - apache2 

      - php8.5 

 

Cambio conflictivo.