"""Formal definition of the interface of Session Manger"""

from abc import ABC, abstractmethod

from autorizator.data_types import SessionID, Login


class AbstractSessionManager(ABC):
    """Session managers deals with sessions"""

    @abstractmethod
    def open(self, session_id: SessionID, login: Login):
        """Creates a new session"""

        pass

    @abstractmethod
    def close(self, session_id: SessionID):
        """Marks the session closed"""

        pass

    @abstractmethod
    def read_session_login(self, session_id: SessionID):
        """Returns the login associated with the give session"""

        pass
