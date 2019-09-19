import logging

from autorizator.ldap_user_storage import LDAPUserStorage, LDAPUserAuth


logging.basicConfig(level=logging.DEBUG)

us = LDAPUserStorage('ldap://172.17.0.2:389', 'People', 'company.cz',
                     service_account=LDAPUserAuth('cn=admin,dc=company,dc=cz', 'JonSn0w'))

print (us.get_user_role('jfilak'))
