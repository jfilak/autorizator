"""Declare user store interface and base types"""


from autorizator.errors import AutorizatorError
from autorizator.datatypes import Login, UserData


class UserStorageError(AutorizatorError)
    """User Storage errors"""

    pass


class UserNotFound(AutorizatorError):
    """The requested user was not found"""

    pass


class AbstractUserService:
    """Base class defining the interface of User Storage.

       One might claim that Python does not need that,
       but modern tools like Pylint can check whether
       you implemented all methods.
    """

    def authenticate(self, login: Login, password: Password) -> bool:
        """Authenticates the user

        Args:
            login: Authenticated user's login
            password: Authenticated user's password

        Returns:
            True if user authentication succeeds, otherwise False.

        Raises:
            autorizator.userstorage.UserNotFound: If the user was not found.
        """

        raise NotImplementedError()

    def get_user_role(self, login: Login) -> UserData:
        """Returns user data for the give login.

        Args:
            login: the requested use login

        Returns:
            An insntance of autorizator.datatypes.UserData if the user was
            found, otherwise None.

        Raises:
            autorizator.userstorage.UserStorageError: An error occurred while
                returning the requested user data.
        """

        raise NotImplementedError()
