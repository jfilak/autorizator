"""This module provides the functionality for getting user information from an
LDAP server.
"""

from typing import NamedTuple, Optional
import logging

import ldap  # type: ignore

from autorizator.data_types import Login, Password, Role, AuthPIN
from autorizator.user_storage import AbstractUserService


class LDAPUserAuth(NamedTuple):
    """User credentials in LDAP form"""

    who: str
    cred: str


class LDAPConnection:
    """A simple context manager which binds on enter and unbinds on exit"""

    def __init__(self, host_uri, svc_account):
        self._host_uri = host_uri
        self._svc_acnt = svc_account
        self._ldap_conn = None

    def __enter__(self):
        logging.debug('Connecting LDAP to: %s', self._host_uri)
        self._ldap_conn = ldap.initialize(self._host_uri)

        if self._svc_acnt:
            logging.debug('Authenticating to LDAP as: %s', self._svc_acnt.who)
            self._ldap_conn.simple_bind_s(self._svc_acnt.who, self._svc_acnt.cred)
        else:
            logging.debug('Running without Authentication to LDAP')
            self._ldap_conn.simple_bind_s()

        return self._ldap_conn

    def __exit__(self, typ, value, traceback):
        if self._ldap_conn:
            self._ldap_conn.unbind()
            self._ldap_conn = None


def _retrieve_attr_of_matching_object(ldap_conn, base_dn, filter_query, attribute):
    logging.debug('Search: base = %s; filter = %s', base_dn, filter_query)
    res = ldap_conn.search_st(base_dn,
                              # pylint: disable=no-member
                              ldap.SCOPE_SUBTREE,
                              filterstr=filter_query,
                              attrlist=[attribute],
                              timeout=60)

    if not res:
        logging.debug('No Object Found for: base = %s; filter = %s',
                      base_dn, filter_query)
        return None

    if len(res) > 1:
        logging.warning('Too many Objects Found for: base = %s; filter = %s',
                        base_dn, filter_query)

        for obj in res:
            logging.warning('Object DN: %s matches base = %s; filter = %s',
                            obj[0], base_dn, filter_query)

        return None

    logging.debug('Found object: %s', res[0][0])
    return res[0][1][attribute]


class LDAPUserStorageConfig:
    """A simple box for LDAP User Storage configuration"""

    def __init__(self):
        self.role_field = 'employeeRole'
        self.pin_field = 'employeePIN'
        self.login_field = 'uid'
        self.encoding = 'utf-8'


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
        self._config = LDAPUserStorageConfig()

    @property
    def role_field(self) -> str:
        """Name of the filed which holds user's role in User data"""

        return self._config.role_field

    @role_field.setter
    def role_field(self, value: str):
        """Set name of the filed which holds user's role in User data"""

        self._config.role_field = value

    @property
    def pin_field(self) -> str:
        """Name of the filed which holds user's Authentication PIN in User data"""

        return self._config.pin_field

    @pin_field.setter
    def pin_field(self, value: str):
        """Set name of the filed which holds user's Authentication PIN in User data"""

        self._config.pin_field = value

    @property
    def login_field(self) -> str:
        """Name of the filed which holds user's login in User data"""

        return self._config.login_field

    @login_field.setter
    def login_field(self, value: str):
        """Set name of the filed which holds user's login in User data"""

        self._config.login_field = value

    @property
    def encoding(self) -> str:
        """LDAP strings encoding"""

        return self._config.encoding

    @encoding.setter
    def encoding(self, value: str):
        """Set LDAP strings encoding"""

        self._config.encoding = value

    def _get_user_part(self, login: Login) -> str:
        return f'{self.login_field}={login}'

    def _get_pin_part(self, pin: AuthPIN) -> str:
        return f'{self.pin_field}={pin}'

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

    def find_user_by_pin(self, pin: AuthPIN) -> Optional[Login]:
        auth_pin = self._get_pin_part(pin)

        with LDAPConnection(self._host_uri, self._svc_acnt) as conn:
            res = _retrieve_attr_of_matching_object(conn,
                                                    self._base_dn,
                                                    auth_pin,
                                                    self.login_field)
            if res is None:
                return None

            login = res[0].decode(self.encoding)

            return login

    def get_user_role(self, login: Login) -> Role:
        user_id = self._get_user_part(login)

        with LDAPConnection(self._host_uri, self._svc_acnt) as conn:
            res = _retrieve_attr_of_matching_object(conn,
                                                    self._base_dn,
                                                    user_id,
                                                    self.role_field)

            role = res[0].decode(self.encoding)

            return role
