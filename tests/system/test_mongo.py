import os
import logging
import pytest

import autorizator.mongodb_session_manager


logging.basicConfig(level=logging.DEBUG)


@pytest.fixture
def db_hostname():
    mongo_host = os.getenv('AZ_MONGO_HOSTNAME')
    logging.info('MongoDB host: %s', mongo_host)
    return mongo_host

@pytest.fixture
def db_database():
    return 'autorizator_sessions'

@pytest.fixture
def manager(db_hostname, db_database):
    return autorizator.mongodb_session_manager.from_connection_string(db_hostname, db_database)

def test_open_read_close(manager):
    sid = '12345'
    login = 'jfilak'

    manager.open(sid, login)

    read_login = manager.read_session_login(sid)

    manager.close(sid)

    assert read_login == login
