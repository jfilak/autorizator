"""casbin adapter"""


from typing import List, NamedTuple

import casbin.persist

from autorizator.errors import AutorizatorError
from autorizator.data_types import Role, RoleList, ActionList


class RoleActionPolicy(NamedTuple):
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
            if policy.role in know_roles:
                raise RolePolicyDefinitionError(f'The role "{policy.role}" defined twice')

            if policy.includes:
                include = next((include for include in policy.includes if include not in know_roles), None)
                if include is not None:
                    raise RolePolicyDefinitionError(
                        f'The role "{include}" included in the role "{policy.role}" does not exist')

            know_roles.add(policy.role)

        self._policies = list(role_policies)

    def load_policy(self, model):
        for policy in self._policies:
            if policy.includes is not None:
                for include in policy.includes:
                    model.model['g']['g'].policy.append([policy.role, include])

            for action in policy.actions:
                model.model['p']['p'].policy.append([policy.role, action])

    # pylint: disable=unused-argument
    def add_policy(self, sec, ptype, rule):
        pass

    # pylint: disable=unused-argument
    def remove_policy(self, sec, ptype, rule):
        pass
