"""Declare user store interface and base types"""


from abc import ABC, abstractmethod

from autorizator.errors import AutorizatorError
from autorizator.data_types import Login, Password, Role


class UserStorageError(AutorizatorError):
    """User Storage errors"""

    pass


class UserNotFoundError(AutorizatorError):
    """The requested user was not found"""

    pass


class AbstractUserService(ABC):
    """Base class defining the interface of User Storage.

       One might claim that Python does not need that,
       but modern tools like Pylint can check whether
       you implemented all methods.
    """

    @abstractmethod
    def authenticate(self, login: Login, password: Password) -> bool:
        """Authenticates the user

        Args:
            login: Authenticated user's login
            password: Authenticated user's password

        Returns:
            True if user authentication succeeds, otherwise False.

        Raises:
            autorizator.user_storage.UserNotFoundError: If the user was not found.
        """

        raise NotImplementedError()

    @abstractmethod
    def get_user_role(self, login: Login) -> Role:
        """Returns user data for the give login.

        Args:
            login: the requested use login

        Returns:
            The associated role if the user was
            found, otherwise None.

        Raises:
            autorizator.user_storage.UserStorageError: An error occurred while
                returning the requested user data.
        """

        raise NotImplementedError()
