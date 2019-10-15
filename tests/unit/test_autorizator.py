import pytest

from autorizator import Autorizator, RoleActionPolicy
from autorizator.ldap_user_storage import LDAPUserStorage, LDAPUserAuth
import autorizator.mongodb_session_manager

@pytest.fixture
def autorizator(user_service, session_manager, policies):
    return Autorizator(policies=policies, user_storage=user_service, session_manager=session_manager)


def assert_viewer_actions(session_id, autorizator, user_config):
    for action in user_config.VIEWER_ACTIONS:
        assert autorizator.check_user_authorization(session_id, action)

    for action in user_config.SUPER_ACTIONS:
        assert not autorizator.check_user_authorization(session_id, action)

    assert user_config.VIEWER_ACTIONS == autorizator.enumerate_user_actions(session_id)


def test_check_all_roles_of_viewer(user_config, autorizator):
    session_id = autorizator.open_session(user_config.VIEWER_LOGIN, user_config.VIEWER_PASSWORD)

    assert_viewer_actions(session_id, autorizator, user_config)

    autorizator.close_session(session_id)


def test_open_session_with_pin_for_viewer(user_config, autorizator):
    session_id = autorizator.open_session_with_pin(user_config.VIEWER_PIN)

    assert_viewer_actions(session_id, autorizator, user_config)

    autorizator.close_session(session_id)


def test_open_session_with_pin_not_found(user_config, autorizator):
    session_id = autorizator.open_session_with_pin('20380119031408')
    assert session_id is None


def test_open_open_close_check_viewer(user_config, autorizator):
    session_id = autorizator.open_session(user_config.VIEWER_LOGIN, user_config.VIEWER_PASSWORD)

    session_id_2 = autorizator.open_session(user_config.VIEWER_LOGIN, user_config.VIEWER_PASSWORD)
    autorizator.close_session(session_id_2)

    assert_viewer_actions(session_id, autorizator, user_config)

    autorizator.close_session(session_id)
