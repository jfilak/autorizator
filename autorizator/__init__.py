"""Autorizator"""

import uuid
import logging
from typing import Optional, Dict
from collections import defaultdict

import casbin  # type: ignore
import casbin.model  # type: ignore

from autorizator.data_types import Login, Password, SessionID, Action, ActionList
from autorizator.user_storage import AbstractUserService, UserNotFoundError
from autorizator.session_manager import AbstractSessionManager
from autorizator.casbin_adapters import RoleActionPolicy  # noqa: F401
from autorizator.casbin_adapters import RoleActionPolicyList, RoleActionPolicyAdapter


def _build_casbin_model():

    model = casbin.model.Model()
    model.add_def("r", "r", "sub, act")
    model.add_def("p", "p", "sub, act")
    model.add_def("g", "g", "_, _")
    model.add_def("e", "e", "some(where (p.eft == allow))")
    model.add_def("m", "m", "g(r.sub, p.sub) && r.act == p.act")

    return model


def _build_casbin_enforcer(policies: RoleActionPolicyList):
    policy_adapter = RoleActionPolicyAdapter(policies)

    model = _build_casbin_model()

    return casbin.Enforcer(model, policy_adapter)


class Autorizator:
    """Authenticates and authorizes users"""

    def __init__(self, policies: RoleActionPolicyList, user_storage: AbstractUserService,
                 session_manager: AbstractSessionManager):
        self._user_storage = user_storage
        self._session_manager = session_manager
        self._enforcer = _build_casbin_enforcer(policies)
        self._user_index : Dict[str, int] = defaultdict(int)

    def open_session(self, login: Login, password: Password) -> Optional[SessionID]:
        """Creates a session for the given user if authentication succeeds for
        the give password.

        Args:
            login: user's name
            password: user's password

        Returns:
            A unique Session Identifier is returned if authentication succeeds,
            otherwise None is returned.
        """

        try:
            if not self._user_storage.authenticate(login, password):
                logging.warning('Failed authorization: login "%s" wrong password', login)
                return None
        except UserNotFoundError:
            logging.warning('Failed authorization: login "%s" not found', login)
            return None

        session_id = str(uuid.uuid4())
        self._session_manager.open(session_id, login)

        nr = self._user_index[login]
        if nr == 0:
            # TODO: handle not found users
            role = self._user_storage.get_user_role(login)
            self._enforcer.add_role_for_user(login, role)

        self._user_index[login] = nr + 1

        return session_id

    def close_session(self, session_id: SessionID):
        """Updates the give session which will no longer be usable for enumerationg
        available actions nor authorizating excecuted actions.

        Args:
            session_id: the session to be closed
        """

        # TODO: handle not found sessions
        # TODO: handle closed sessions
        login = self._session_manager.read_session_login(session_id)

        nr = self._user_index[login]

        if nr == 1:
            # TODO: handle not policies - must not happen!!!
            self._enforcer.delete_roles_for_user(login)

            del self._user_index[login]
        else:
            self._user_index[login] = nr - 1

        # TODO: handle not found sessions
        # TODO: handle closed sessions
        self._session_manager.close(session_id)

    def enumerate_user_actions(self, session_id: SessionID) -> ActionList:
        """Returns the list of actions available for the give session by
        analyzing the role of the session user.

        Args:
            session_id: the requested session
        """

        # TODO: handle not found sessions
        # TODO: handle closed sessions
        login = self._session_manager.read_session_login(session_id)

        return [perm[1] for perm in self._enforcer.get_implicit_permissions_for_user(login)]

    def check_user_authorization(self, session_id: SessionID, action: Action) -> bool:
        """Checks the session user authorization to perform the give action.

        Args:
            session_id: the requested session
        """
        # TODO: detect closed sessions
        # TODO: handle not found sessions
        login = self._session_manager.read_session_login(session_id)

        # TODO: handle unknown roles
        # TODO: handle unknown actions
        return self._enforcer.enforce(login, action)
