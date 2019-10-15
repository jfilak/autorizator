"""Declare user store interface and base types"""


from abc import ABC, abstractmethod
from typing import Optional

from autorizator.errors import AutorizatorError
from autorizator.data_types import Login, Password, Role, AuthPIN


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
    def find_user_by_pin(self, pin: AuthPIN) -> Optional[Login]:
        """Knowledge of PIN is considered as good enough to authorize the
        corresponding user.

        Args:
            pin: Secret user information

        Returns:
            User login if the given pin is found, otherwise None.
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
