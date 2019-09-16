#pylint: disable=invalid-name
"""casbin adapter"""


from typing import NamedTuple, List

import casbin.persist

from autorizator.data_types import Role, RoleList, ActionList


class RoleActionPolicy:
    """Policy definition"""

    role: Role
    # included roles
    includes: RoleList
    actions: ActionList


RoleActionPolicyList = List[RoleActionPolicy]


class RolePolicyDefinitionError(AutorizatorError):
    """Invalid policy definition"""

    pass


class RoleActionPolicyAdapter(casbin.persist.Adapter):
    """The adapter"""

    def __init__(self, role_policies: RoleActionPolicyList):
        know_roles = set()

        for policy in role_policies:
            if policy.role in self._know_roles:
                raise RolePolicyDefinitionError(f'The role "{policy.role}" defined twice')

            if role_policy.includes:
                if any((include not in know_roles for include in role_policy.includes)):
                    raise RolePolicyDefinitionError(
                        f'The role "{include}" included in the role "{policy.role}" does not exist')

            know_roles.add(policy.role)

        self._policies = list(role_policies)

    def load_policy(self, model):
        for policy in self._policies:
            for action in role.actions:
                model.model['p'][role].policy.append([action])

            for include in role.includes:
                model.model['g'][role].policy.append([include])
