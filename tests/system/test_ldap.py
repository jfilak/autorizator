from autorizator.ldap_user_storage import LDAPUserStorage

us = LDAPUserStorage('172.17.0.2', 'People', 'company.cz')
print (us.get_user_role('jfilak'))
