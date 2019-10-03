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

## Configuration

### LDAP

This section contains description of configuration for a hypothetical company
example with the domain *example.com*. The company LDAP has organizational unit
*staff* and stores their data in UTF-8.

The Autorizator LDAP connector expects that user names are stored in
the field *uid* and authorization uses the bind DN for the user randomjoe
as:

    uid=randomjoe,ou=staff,dc=example,dc=com

The class *LDAPUserStorage* allows you to change the login filed via
the property *login_field*. In case where you have the role stored
in a different field and you cannot change LDAP, you can instruct Autorizator
to read the right field.

The LDAP connector expects that the user role is stored in the field *employeeRole*
but you can overwrite the default configuration via the property *role_field*.

It is also possible to change encoding from UTF-8 to your desired 
encoding via the property *enconding*.

**Example:**

1. define a new objectClass with employeeRole

```
$ sudo ldapadd -Y EXTERNAL -H ldapi:/// <<_EOF
dn: cn=employee,cn=schema,cn=config
objectClass: olcSchemaConfig
cn: employee
olcAttributeTypes: {0}( 1.3.6.1.4.1.42.2.27.4.1.6 NAME 'employeeRole' DESC '
 Employee role' EQUALITY caseExactMatch SYNTAX 1.3.6.1.4.1.1466.115.121.1.15
  SINGLE-VALUE )
olcObjectClasses: {0}( 1.3.6.1.4.1.42.2.27.4.2.1 NAME 'employee' DESC 'Emplo
 yee' SUP organizationalPerson STRUCTURAL MUST ( cn $ employeeRole ) )
_EOF
```

We use `-Y EXTERNAL -H ldapi:///` in order to allow root user to modify
schema because the LDAP user admin doe snot have the required rights.

2. create employees with the objectClass employee

```
$ sudo ldapadd -x -W -D "cn=admin,dc=example,dc=com" <<_EOF
dn: uid=randomjoe,ou=staff,dc=example,dc=com
cn: Joe Random
objectClass: organizationalPerson
objectClass: posixAccount
objectClass: employee
sn: Random
uid: randomjoe
employeeRole: super
_EOF
```

### MongoDB

TODO

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
