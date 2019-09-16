"""Autorizator"""


from autorizator.userstorage import AbstractUserService
from autorizator.sessionmanager import AbstractSessionManager


import casbin
import casbin.model


class Autorizator:

    def __init__(self, policies: RoleActionPolicyList, user_storage: AbstractUserService, session_manager: AbstractSessionManager):
        self._user_storage = user_storage
        self._session_manager = session_manager

        policy_adapter = RoleActionPolicyAdapter(policies)

        model = casbin.Model()
        model.add_def("r", "r", "sub, act")
        model.add_def("p", "p", "sub, act")
        model.add_def("g", "g", "_, _")
        model.add_def("e", "e", "some(where (p.eft == allow))")
        model.add_def("m", "m", "g(r.sub, p.sub) && r.act == p.act")

        self._enforcer = casbin.Enforcer(model, policy_adapter)

    def open_session(self, login: Login, password: Password) -> SessionID:
        user_data = self._user_storage.authenticate(login, password)

        if user_data is None:
            return AutorizatorUserNotFound()

        session_id = uuid.uuid4()
        self._session_manager.create(session_id, user=login, start_date=datetime.now())

    def close_session(self, session_id: SessionID):
        self._session_manager.update(session_id, close_date=datetime.now())

    def enumerate_user_actions(self, session_id: SessionID) -> ActionList:
        login = self._session_manager.read_session_login(session_id)
        role = self._user_storage.get_user_role(session_data.login)

        return self._enforcer.get_actions(role, action)

    def check_user_authorization(self, session_id: SessionID, action: Action) -> bool:
        login = self._session_manager.read_session_login(session_id)
        role = self._user_storage.get_user_role(login)

        return self._enforcer.enforce(role, action)
