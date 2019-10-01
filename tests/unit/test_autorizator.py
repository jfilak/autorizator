from autorizator import Autorizator, RoleActionPolicy
from autorizator.ldap_user_storage import LDAPUserStorage, LDAPUserAuth
import autorizator.mongodb_session_manager


def test_check_all_roles_of_viewer(user_config, user_service, session_manager, policies):

    autorizator = Autorizator(policies=policies, user_storage=user_service, session_manager=session_manager)

    session_id = autorizator.open_session(user_config.VIEWER_LOGIN, user_config.VIEWER_PASSWORD)

    for action in user_config.VIEWER_ACTIONS:
        assert autorizator.check_user_authorization(session_id, action)

    for action in user_config.SUPER_ACTIONS:
        assert not autorizator.check_user_authorization(session_id, action)

    assert user_config.VIEWER_ACTIONS == autorizator.enumerate_user_actions(session_id)

    autorizator.close_session(session_id)
