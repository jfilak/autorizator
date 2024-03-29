import os
import logging
import pytest

from autorizator.user_storage import UserStorageError
from autorizator.ldap_user_storage import LDAPUserStorage, LDAPUserAuth


logging.basicConfig(level=logging.DEBUG)

@pytest.fixture
def ldap_hostname():
    return os.getenv('AZ_LDAP_HOSTNAME')

@pytest.fixture
def us(ldap_hostname):
    return LDAPUserStorage(f'ldap://{ldap_hostname}:389', 'IVisionUsers', 'company.cz',
                           service_account=LDAPUserAuth('cn=admin,dc=company,dc=cz', 'JonSn0w'))

@pytest.fixture
def std_login():
    return 'jfilak'

@pytest.fixture
def std_pin():
    return '1969'

@pytest.fixture
def std_pin_duplicates():
    return '6666'

@pytest.fixture
def std_password():
    return 'Karel'

@pytest.fixture
def std_role():
    return 'super'

def test_get_user_role_known_user(us, std_login, std_role):
    role = us.get_user_role('jfilak')
    assert role == std_role

def test_get_user_role_UNknown_user(us, std_login, std_role):
    with pytest.raises(UserStorageError):
        role = us.get_user_role('pedro')

def test_get_user_login_by_pin(us, std_login, std_pin):
    login = us.find_user_by_pin(std_pin)
    assert login == std_login

def test_get_user_login_by_bin_unknown(us, std_pin):
    login = us.find_user_by_pin('20380191031408')
    assert login is None

def test_get_user_login_by_pin_duplicate(us, std_pin_duplicates):
    login = us.find_user_by_pin(std_pin_duplicates)
    assert login is None

def test_authenticate_valid_password(us, std_login, std_password):
    auth_res = us.authenticate(std_login, std_password)
    assert auth_res == True

def test_authenticate_INvalid_password(us, std_login, std_password):
    auth_res = us.authenticate(std_login, std_password + '2')
    assert auth_res == False
