"""This module provides the functionality for getting user information from an
LDAP server.
"""

import ldap

from autorizator.data_types import Login, Password, Role
from autorizator.user_storage import AbstractUserService


class LDAPUserStorage(AbstractUserService):
    """LDAP user storage proxy"""

    def __init__(self, host_uri: str, org_unit: str, domain: str):
        self._host_uri = host_uri
        self._base_dn = ','.join((f'dc={dc}' for dc in domain.split('.')))
        self._ou = f'ou={org_unit},{self._base_dn}'

    def _get_user_part(self, login: Login) -> str:
        return f'uid={login}'

    def authenticate(self, login: Login, password: Password) -> bool:
        conn = ldap.ldapobject.ReconnectLDAPObject(self._host_uri)
        conn.simple_bind_s(who=f'{self._get_user_part(login)},{self._ou}', cred=password)
        conn.unbind()

    def get_user_role(self, login: Login) -> Role:
        conn = ldap.ldapobject.ReconnectLDAPObject(self._host_uri)
        conn.simple_bind_s()

        res = conn.search_st(self._base_dn,
                             ldap.SCOPE_SUBTREE,
                             filterstr=self._get_user_part(login),
                             timeout=60)
        role = res[0]['role']

        conn.unbind()

        return role
