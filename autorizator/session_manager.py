"""Formal definition of the interface of Session Manger"""


from autorizator.data_types import SessionID, Login


class AbstractSessionManager:
    """Session managers deals with sessions"""

    def create(self, session_id: SessionID, login: Login, **kwargs):
        """Creates a new session and saves the supported kwargs"""

        raise NotImplementedError()

    def update(self, session_id: SessionID, **kwargs):
        """Updates session attributes"""

        raise NotImplementedError()

    def read_session_login(self, session_id: SessionID):
        """Returns the login associated with the give session"""

        raise NotImplementedError()
