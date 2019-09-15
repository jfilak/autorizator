# Autorizator

Grants permissions ...

## Requirements

 - Python 3.7

## Installation

 - OpenLDAP devel packages

## How to test

```bash
docker pull osixia/openldap

docker run -e LDAP_ORGANISATION="Company" -e LDAP_DOMAIN="company.cz" -e LDAP_ADMIN_PASSWORD="JonSn0w" -d --name company_ldap osixia/openldap

docker exec -it company_ldap slapcat -n 0

cd /var/tmp

cat > ou_users.ldiff <<_EOF
dn: ou=People,dc=company,dc=cz
objectClass: organizationalUnit
ou: People
description: Users
_EOF

cat ou_users.ldif | docker exec -i company_ldap ldapadd -x -w JonSn0w -D "cn=admin,dc=company,dc=cz"

cat > op_jfilak.ldiff <<_EOF
dn: cn=Jakub Filak,ou=People,dc=company,dc=cz
cn: Jakub Filak
objectClass: organizationalPerson
sn: Filak
objectClass: posixAccount
uid: jfilak
homeDirectory: /home/jfilak
gidNumber: 4269
uidNumber: 4269
_EOF

cat op_jfilak.ldif | docker exec -i company_ldap ldapadd -x -w JonSn0w -D "cn=admin,dc=company,dc=cz"

docker exec -i company_ldap ldapsearch -x -H ldap://localhost -b "cn=Jakub Filak,ou=People,dc=company,dc=cz" -D "cn=admin,dc=company,dc=cz" -w JonSn0w

docker exec -i company_ldap slappasswd

cat > op_jfilak_password.ldif <<_EOF
dn: cn=Jakub Filak,ou=People,dc=company,dc=cz
changetype: modify
replace: userPassword
userPassword: {SSHA}XLiGkBVqXHjmNuUPqDEbH6tv6fZTQzg9
_EOF


cat op_jfilak_password.ldif | docker exec -i company_ldap ldapmodify -x -D "cn=admin,dc=company,dc=cz" -w JonSn0w

ldapsearch -x -H ldap://172.17.0.2 -b "cn=Jakub Filak,ou=People,dc=company,dc=cz" -D "cn=admin,dc=company,dc=cz" -w JonSn0w
```
