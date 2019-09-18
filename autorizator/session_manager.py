"""Formal definition of the interface of Session Manger"""

from abc import ABC, abstractmethod

from autorizator.data_types import SessionID, Login


class AbstractSessionManager(ABC):
    """Session managers deals with sessions"""

    @abstractmethod
    def create(self, session_id: SessionID, login: Login, **kwargs):
        """Creates a new session and saves the supported kwargs"""

        pass

    @abstractmethod
    def update(self, session_id: SessionID, **kwargs):
        """Updates session attributes"""

        pass

    @abstractmethod
    def read_session_login(self, session_id: SessionID):
        """Returns the login associated with the give session"""

        pass
