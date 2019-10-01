"""Formal definition of the interface of Session Manger"""

from abc import ABC, abstractmethod

from autorizator.data_types import SessionID, Login
from autorizator.errors import AutorizatorError


class SessionManagerError(AutorizatorError):
    """Session Manager errors"""

    pass


class SessionManagerSessionError(SessionManagerError):
    """Cannot re-create session"""

    def __init__(self, session_id, error_message):
        super(SessionManagerSessionError, self).__init__()

        self.session_id = session_id
        self.error_message = error_message

    def __str__(self):
        return f'Session "{self.session_id}": {self.error_message}'


class SessionAlreadyExists(SessionManagerError):
    """Cannot re-create session"""

    def __init__(self, session_id):
        super(SessionAlreadyExists, self).__init__(session_id, 'already exists')


class SessionNotFound(SessionManagerError):
    """When the requested session is not known to the manager"""

    def __init__(self, session_id):
        super(SessionNotFound, self).__init__(session_id, 'not found')


class SessionIsClosed(SessionManagerError):
    """When trying perform an action on a closed session"""

    def __init__(self, session_id):
        super(SessionIsClosed, self).__init__(session_id, 'already closed')


class AbstractSessionManager(ABC):
    """Session managers deals with sessions"""

    @abstractmethod
    def open(self, session_id: SessionID, login: Login):
        """Creates a new session.

        Raises:
            autorizator.session_manager.SessionAlreadyExists: If the give session_id already exists.
        """

        pass

    @abstractmethod
    def close(self, session_id: SessionID) -> Login:
        """Marks the session closed.

        Raises:
            autorizator.session_manager.SessionNotFound: If the corresponding session is not know.
            autorizator.session_manager.SessionIsClosed: If the corresponding session is already closed.
        """

        pass

    @abstractmethod
    def read_session_login(self, session_id: SessionID) -> Login:
        """Returns the login associated with the give session

        Raises:
            autorizator.session_manager.SessionNotFound: If the corresponding session is not know.
            autorizator.session_manager.SessionIsClosed: If the corresponding session is already closed.
        """

        pass
