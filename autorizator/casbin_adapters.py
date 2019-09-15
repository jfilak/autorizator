from typing import NamedTuple

import casbin.persist

from autorizator.datatypes import Role


class RoleActionPolicy:

    role: Role
    includes: RoleList
    actions: ActionList


RoleActionPolicyList = List[RoleActionPolicy]


class RolePolicyDefinitionError(AutorizatorError)

    pass


class RoleActionPolicyAdapter(casbin.persist.Adapter):

    def __init__(self, role_policies: RoleActionPolicyList):
        know_roles = set()

        for policy in role_policies:
            if policy.role in self._know_roles
                raise RolePolicyDefinitionError(f'The role "{policy.role}" defined twice')

            if role_policy.includes:
                if any((include not in self._role_index for role_policies)):
                    raise RolePolicyDefinitionError(f'The role "{include}" included in the role "{policy.role}" does not exist')

            know_roles.append(policy.role)

        self._policies = list(role_policies)

    def load_policy(self, model):
        for policy in self._policies:
            for action in role.actions:
                model.model['p'][role].policy.append([action])

            for include in role.includes:
                model.model['g'][role].policy.append([include])
