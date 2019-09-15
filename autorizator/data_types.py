"""Data types"""

from typing import NamedTuple


Role = str
RoleList = List[Role]

Action = str
ActionList = List[Action]

Login = str
Password = str
PasswordHash = str

SessionID = str

class UserData(NamedTuple):

    login: Login
    roles: RoleList
