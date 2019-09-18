"""Autorizator sessions stored in MongoDB"""

import pymongo

from autorizator.data_types import SessionID, Login
from autorizator.session_manager import AbstractSessionManager

class MongoDBSessionManger(AbstractSessionManager):
    """Store sessions in MongoDB"""

    def __init__(self, client, db):
        self._client = client
        self._db = db
        self._sessions = db['autorizator_sessions']

    def create(self, session_id: SessionID, login: Login, **kwargs):

        session_data = {'id': session_id, 'login': login}
        session_data.update(kwargs)

        self._sessions.insert_one(session_data)

    def update(self, session_id: SessionID, **kwargs):

        self._sessions.find_one_and_update({'id': session_id}, {'$inc': kwargs})

    def read_session_login(self, session_id: SessionID):

        login = self._sessions.find_one({'id': session_id}, {'login': 0})
        return login


def from_connection(host: str, database: str):
    """Creates an instance of MongoDB Session Manager for the give connection
       string and sets the database to the give database string.
    """

    client = pymongo.MongoClient(f'mongodb://{host}/')
    db = client[database]

    return MongoDBSessionManger(client, db)
