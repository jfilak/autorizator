import pytest
from collections import namedtuple

from autorizator import RoleActionPolicy
from autorizator.user_storage import AbstractUserService, UserStorageError
from autorizator.session_manager import AbstractSessionManager, SessionAlreadyExists, SessionNotFound, SessionIsClosed


class UserConfig():

    VIEWER_LOGIN='jfilak'
    VIEWER_PASSWORD='karel'
    VIEWER_ROLE='viewer'
    VIEWER_PIN='42'
    VIEWER_ACTIONS=['open', 'list']

    SUPER_LOGIN='kalifj'
    SUPER_PASSWORD='lerak'
    SUPER_ROLE='super'
    SUPER_PIN='69'
    SUPER_ACTIONS=['add', 'remove']


class LocalUserStorage(AbstractUserService):

    def authenticate(self, login, password):
        try:
            return {UserConfig.VIEWER_LOGIN: UserConfig.VIEWER_PASSWORD,
                    UserConfig.SUPER_LOGIN: UserConfig.SUPER_PASSWORD}[login] == password
        except KeyError:
            raise UserStorageError('Not found')

    def find_user_by_pin(self, pin):
        return {UserConfig.VIEWER_PIN: UserConfig.VIEWER_LOGIN,
                UserConfig.SUPER_PIN: UserConfig.SUPER_LOGIN}.get(pin, None)

    def get_user_role(self, login):
        try:
            return {UserConfig.VIEWER_LOGIN: UserConfig.VIEWER_ROLE,
                    UserConfig.SUPER_LOGIN: UserConfig.SUPER_ROLE}[login]
        except KeyError:
            raise UserStorageError()


class LocalSessionManager(AbstractSessionManager):

    class Data:
        """Full class because NamedTuple is immutable"""

        def __init__(self, login, open):
            self.login = login
            self.open = open


    def __init__(self):
        self._sessions = {}

    def open(self, session_id, login):
        if session_id in self._sessions:
            raise SessionAlreadyExists(session_id)

        self._sessions[session_id] = LocalSessionManager.Data(login, True)

    def _get_open_session(self, session_id):
        try:
            session = self._sessions[session_id]
        except KeyError:
            raise SessionNotFound(session_id)
        else:
            if not session.open:
                raise SessionIsClosed(session_id)

        return session

    def close(self, session_id):
        self._get_open_session(session_id).open = False

    def read_session_login(self, session_id):
        return self._get_open_session(session_id).login


@pytest.fixture
def user_config():
    return UserConfig


@pytest.fixture
def policy_viewer(user_config):
    return RoleActionPolicy(role=user_config.VIEWER_ROLE, includes=None, actions=user_config.VIEWER_ACTIONS)


@pytest.fixture
def policy_super(user_config):
    return RoleActionPolicy(role=user_config.SUPER_ROLE, includes=[user_config.VIEWER_ROLE], actions=user_config.SUPER_ACTIONS)


@pytest.fixture
def policies(policy_viewer, policy_super):
    return [policy_viewer, policy_super]


@pytest.fixture
def user_service():
    return LocalUserStorage()


@pytest.fixture
def session_manager():
    return LocalSessionManager()
