"""Autorizator sessions stored in MongoDB"""

import datetime

import pymongo  # type: ignore

from autorizator.data_types import SessionID, Login
from autorizator.session_manager import AbstractSessionManager


class MongoDBSessionManger(AbstractSessionManager):
    """Store sessions in MongoDB"""

    COLLECTION = 'autorizator_sessions'

    def __init__(self, client: pymongo.MongoClient, db: pymongo.database.Database):
        self._client = client
        self._db = db
        self._sessions = db[MongoDBSessionManger.COLLECTION]

    def _get_current_date(self):
        return datetime.datetime.now()

    def open(self, session_id: SessionID, login: Login):
        session_data = {
            'id': session_id,
            'login': login,
            'start_date': self._get_current_date()
        }

        self._sessions.insert_one(session_data)

    def close(self, session_id: SessionID):

        end_date = {'end_date': self._get_current_date()}

        self._sessions.find_one_and_update({'id': session_id}, {'$set': end_date})

    def read_session_login(self, session_id: SessionID):

        session_data = self._sessions.find_one({'id': session_id}, {'login': 1})
        return session_data['login']


def from_connection_string(host: str, database: str):
    """Creates an instance of MongoDB Session Manager for the give connection
       string and sets the database to the give database string.
    """

    client = pymongo.MongoClient(f'mongodb://{host}/')
    db = client[database]

    return MongoDBSessionManger(client, db)
