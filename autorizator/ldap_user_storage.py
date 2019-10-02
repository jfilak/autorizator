"""This module provides the functionality for getting user information from an
LDAP server.
"""

from typing import NamedTuple
import logging

import ldap  # type: ignore

from autorizator.data_types import Login, Password, Role
from autorizator.user_storage import AbstractUserService


class LDAPUserAuth(NamedTuple):
    """User credentials in LDAP form"""

    who: str
    cred: str


class LDAPUserStorage(AbstractUserService):
    """LDAP user storage proxy"""

    def __init__(self, host_uri: str, org_unit: str, domain: str, service_account: LDAPUserAuth = None):
        """Initializes LDAP storage

        Args:
            host_uri: scheme + host + port; e.g. ldap://172.17.0.2:389
            org_unit: Organization Unit name where all users belongs into; will
                      be used in LDAP search for ou= part
            domain:   Domain
            service_account: User Credentials when search requires authentication
        """

        self._host_uri = host_uri
        self._svc_acnt = service_account
        self._base_dn = ','.join((f'dc={dc}' for dc in domain.split('.')))
        self._ou = f'ou={org_unit},{self._base_dn}'
        self._role_field = 'gidNumber'
        self._login_field = 'uid'
        self._encoding = 'utf-8'

    @property
    def role_field(self) -> str:
        """Name of the filed which holds user's role in User data"""

        return self._role_field

    @role_field.setter
    def role_field(self, value: str):
        """Set name of the filed which holds user's role in User data"""

        self._role_field = value

    @property
    def login_field(self) -> str:
        """Name of the filed which holds user's login in User data"""

        return self._login_field

    @login_field.setter
    def login_field(self, value: str):
        """Set name of the filed which holds user's login in User data"""

        self._login_field = value

    @property
    def encoding(self) -> str:
        """LDAP strings encoding"""

        return self.encoding

    @encoding.setter
    def encoding(self, value: str):
        """Set LDAP strings encoding"""

        self._encoding = value

    def _get_user_part(self, login: Login) -> str:
        return f'{self._login_field}={login}'

    def authenticate(self, login: Login, password: Password) -> bool:
        result = False
        conn = ldap.initialize(self._host_uri)

        who = f'{self._get_user_part(login)},{self._ou}'
        logging.debug('Authenticating user %s', who)

        try:
            conn.simple_bind_s(who, cred=password)
        # pylint: disable=no-member
        except ldap.INVALID_CREDENTIALS:
            logging.warning('Failed to authenticate user %s: invalid credentials', login)
        else:
            result = True

        conn.unbind()

        return result

    def get_user_role(self, login: Login) -> Role:
        logging.debug('Connecting LDAP to: %s', self._host_uri)
        conn = ldap.initialize(self._host_uri)

        if self._svc_acnt:
            logging.debug('Authenticating to LDAP as: %s', self._svc_acnt.who)
            conn.simple_bind_s(self._svc_acnt.who, self._svc_acnt.cred)
        else:
            logging.debug('Running without Authentication to LDAP')
            conn.simple_bind_s()

        user_id = self._get_user_part(login)

        logging.debug('Search: base = %s; filter = %s', self._base_dn, user_id)
        res = conn.search_st(self._base_dn,
                             # pylint: disable=no-member
                             ldap.SCOPE_SUBTREE,
                             filterstr=user_id,
                             timeout=60)

        role = res[0][1][self._role_field][0].decode(self._encoding)

        conn.unbind()

        return role
