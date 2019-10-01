# Autorizator

Grants permissions ...

## Requirements

 - Python 3.7
 - casbin
 - python-ldap (only when you want to use LDAP User Storage)
 - pymongo (only when you want to use MongoDB Session Manager)

## Installation on Linux

 - OpenLDAP devel packages

## Basic usage

```python
from autorizator import Autorizator, RoleActionPolicy
from autorizator.ldap_user_storage import LDAPUserStorage, LDAPUserAuth
import autorizator.mongodb_session_manager

policy_viewer = RoleActionPolicy(role='viewer', includes=None, actions=['open', 'list'])
policy_super = RoleActionPolicy(role='super', includes=[policy_viewer.role], actions=['add', 'remove'])

autorizator = Autorizator(policies=[policy_viewer, policy_super],
                          user_storage=LDAPUserStorage(host_uri='ldap://172.17.0.2', org_unit='People', domain='example.com',
                                                       service_account=LDAPUserAuth('admin', 'password'))
                          session_manager=autorizator.mongodb_session_manager.from_connection_string('172.17.0.3', 'auditing'))

session_id = autorizator.open_session('login', 'password')

for action in autorizator.enumerate_user_actions(session_id):
    autorizator.check_user_authorization(session_id, action)

autorizator.close_session(session_id)
```

## Developer notes

Autorizator populates Casbin Enforcer with configured roles and policies but
without users (simply because we do not know them).

Upon opening a new session and after successful authorization, Autorizator
fetches the authorized user's role and adds the user to Casbin Enforcer.
Autorizator does that to avoid the need to fetch user roles for every
authorization check requests and to avoid the need to build own user roles
cache.

When a session is closed, Autorizator removes all roles of the corresponding
user and hence all authorization requests will be refused.

This approach causes that any possible changes to user roles do no take effect
until the affected user re-authenticates themselves.

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
dn: uid=jfilak,ou=People,dc=company,dc=cz
cn: Jakub Filak
objectClass: organizationalPerson
sn: Filak
objectClass: posixAccount
uid: jfilak
homeDirectory: /home/jfilak
gidNumber: 1000
uidNumber: 4269
_EOF

cat op_jfilak.ldif | docker exec -i company_ldap ldapadd -x -w JonSn0w -D "cn=admin,dc=company,dc=cz"

docker exec -i company_ldap ldapsearch -x -H ldap://localhost -b "uid=jfilak,ou=People,dc=company,dc=cz" -D "cn=admin,dc=company,dc=cz" -w JonSn0w

docker exec -i company_ldap ldappasswd $LDAP_ADMIN_CMD_AUTH -s Karel "uid=jfilak,ou=People,dc=company,dc=cz"

ldapsearch -x -H ldap://172.17.0.2 -b "uid=jfilak,ou=People,dc=company,dc=cz" -D "cn=admin,dc=company,dc=cz" -w JonSn0w
```
