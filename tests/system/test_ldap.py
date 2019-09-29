import os
import logging
import pytest

from autorizator.ldap_user_storage import LDAPUserStorage, LDAPUserAuth


logging.basicConfig(level=logging.DEBUG)

@pytest.fixture
def ldap_hostname():
    return os.getenv('AZ_LDAP_HOSTNAME')

@pytest.fixture
def us(ldap_hostname):
    return LDAPUserStorage(f'ldap://{ldap_hostname}:389', 'People', 'company.cz',
                           service_account=LDAPUserAuth('cn=admin,dc=company,dc=cz', 'JonSn0w'))

@pytest.fixture
def std_login():
    return 'jfilak'

@pytest.fixture
def std_password():
    return 'Karel'

@pytest.fixture
def std_role():
    return '1000'

def test_get_user_role_known_user(us, std_login, std_role):
    role = us.get_user_role('jfilak')
    assert role == std_role

def test_authenticate_valid_password(us, std_login, std_password):
    auth_res = us.authenticate(std_login, std_password)
    assert auth_res == True

def test_authenticate_INvalid_password(us, std_login, std_password):
    auth_res = us.authenticate(std_login, std_password + '2')
    assert auth_res == False
