---
seccion: Clúster
pagina: SSSD
capturado: 2026-07-24T18:40:07.568Z
fuente: OneNote "Cluster-OSS" (Norberto Nunez)
---

SSSD 

lunes, 6 de julio de 2026 

17:16 

Certificado LDAP 

wget ftp://10.129.6.5/pub/ldap_certificate_chain.crt 

Verificación de certificado 

openssl x509 -in /usr/local/share/ca-certificates/ldap_certificate_chain.crt -noout -dates 

 

Ubuntu 26.04LTS 

# 

# https://documentation.ubuntu.com/server/how-to/sssd/with-ldap/ 

# 

apt-get update 

apt-get install -y sssd sssd-ldap libsss-sudo oddjob-mkhomedir 

cp ldap_certificate_chain.crt /usr/local/share/ca-certificates/ 

update-ca-certificates 

# 

cat > /etc/sssd/sssd.conf <<HERE 

[sssd] 

config_file_version = 2 

domains = personal.com.py 

 

[domain/personal.com.py] 

id_provider = ldap 

auth_provider = ldap 

sudo_provider = ldap 

ldap_uri = ldap://ldap.sis.personal.net.py 

ldap_tls_cacertdir = /etc/ssl/certs 

cache_credentials = True 

ldap_id_use_start_tls = True 

ldap_tls_reqcert = never 

ldap_search_base = dc=sis,dc=personal,dc=net,dc=py 

ldap_sudo_search_base = ou=sudoers,dc=sis,dc=personal,dc=net,dc=py 

simple_allow_groups = seguridad,css,SVA,sva_tec_ps,SegInf_ps,SegInf,nunezno_opr,AK402_opr 

HERE 

# 

chmod 600 /etc/sssd/sssd.conf 

systemctl enable sssd 

systemctl restart sssd 

pam-auth-update --enable mkhomedir 

# 

# Opción sudo.ws 

# 

update-alternatives --config sudo 

 

Cambio conflictivo.