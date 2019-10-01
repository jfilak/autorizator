from autorizator import Autorizator, RoleActionPolicy, _build_casbin_model, _build_casbin_enforcer


def test_build_casbin_model():
    model = _build_casbin_model()
    assert model is not None


def test_build_casbin_enforcer(user_config, policies):
    enforcer = _build_casbin_enforcer(policies)

    assert enforcer is not None

    for viewer_action in user_config.VIEWER_ACTIONS:
        assert enforcer.enforce(user_config.VIEWER_ROLE, viewer_action)
        assert enforcer.enforce(user_config.SUPER_ROLE, viewer_action)

    for super_action in user_config.SUPER_ACTIONS:
        assert enforcer.enforce(user_config.VIEWER_ROLE, super_action) == False
        assert enforcer.enforce(user_config.SUPER_ROLE, super_action)
