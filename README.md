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

It is also possible to authorize user using a secret value (PIN) known only to
the authorized user without providing login - this actually means that
the configured user storage must not contain duplicate PINs.

```python
session_id = autorizator.open_session_with_pin('197001010000')
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

The LDAP connector expects that:

- the user role is stored in the field *IVisionRole* but you can overwrite the
  default configuration via the property *role_field*.

- the user Authentication PIN is stored in the field *IVisionPIN*
  but you can overwrite the default configuration via the property *pin_field*.

It is also possible to change encoding from UTF-8 to your desired 
encoding via the property *enconding*.

**Example:**

1. define a new objectClass named ClassIndustrialVision with IVisionRole and
   IVisionPIN

```
$ sudo ldapadd -Y EXTERNAL -H ldapi:/// <<_EOF
dn: cn=industrialvisionuser,cn=schema,cn=config
objectClass: olcSchemaConfig
cn: industrialvisionuser
olcAttributeTypes: ( 1.1.2.1.1 NAME 'IVisionRole' DESC 'Industrial Vison 
 user role' EQUALITY caseExactMatch SYNTAX 1.3.6.1.4.1.1466.115.121.1.15 SIN
 GLE-VALUE )
olcAttributeTypes: ( 1.1.2.1.2 NAME 'IVisionPIN' DESC 'Industrial Vision 
 user PIN' EQUALITY caseExactMatch SYNTAX 1.3.6.1.4.1.1466.115.121.1.15 SING
 LE-VALUE )
olcObjectClasses: ( 1.1.2.2.1 NAME 'ClassIndustrialVision' DESC 'Indistri
 al Vision User' SUP organizationalPerson STRUCTURAL MUST ( cn $ IVisionRole
  $ IVisionPIN ) )
_EOF
```

We use `-Y EXTERNAL -H ldapi:///` in order to allow root user to modify
schema because the LDAP user admin doe snot have the required rights.

2. add a new organizational unit called IVisionUsers, where the user data will
   be stored:

```
$ sudo ldapadd -x -W -D "cn=admin,dc=example,dc=com" <<<_EOF
dn: ou=IVisionUsers,dc=example,dc=com
objectClass: organizationalUnit
ou: IVisionUsers
description: Industrial Vision Users
_EOF
```

3. create employees with the objectClass employee

```
$ sudo ldapadd -x -W -D "cn=admin,dc=example,dc=com" <<_EOF
dn: uid=randomjoe,ou=IVisionUsers,dc=example,dc=com
cn: Joe Random
objectClass: organizationalPerson
objectClass: posixAccount
objectClass: ClassIndustrialVision
sn: Random
uid: randomjoe
IVisionRole: super
IVisionPIN: Y2K38
_EOF
```

### MongoDB

TODO

## How to test

Please, read the script [start_ldap](tests/system/start_ldap)

## How to deploy

The directory [service](service) contains [a configuration file](service/docker-compose.yml)
for [docker-compose](https://docs.docker.com/compose/)/.

If you don't need to change any names, you can use the command
`docker-compose up` which will bring up 2 containers:

- service_ldap_1 (the LDAP service)
- service_phpldapadmin_1 (administration UI)

Before issuing the up command, please, fill variables in
the file [ldap-service-variables.env](service/ldap-service-variables.env)

### LDAP Administration

You need to get IP of the phpldapadmin-host with the command:

```bash
sudo docker inspect --format '{{ .NetworkSettings.Networks.service_ldapnet.IPAddress }}' service_phpldapadmin_1
```

the you have to open `http://$CONTAINER_IP/` in your browser and login as `cn=admin,dn=example,dn=com`
(replace `dn=example,dn=com` with your domain configured in the file [ldap-service-variables.env](service/ldap-service-variables.env))
